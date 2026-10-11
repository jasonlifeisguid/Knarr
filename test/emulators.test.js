// "Play with" (emulators.ts) and "Get firmware" (firmware.ts).
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const emulators = require('../dist/emulators.js');
const firmware = require('../dist/firmware.js');
const config = require('../dist/config.js');
const path7za = require('../dist/sevenzip.js').sevenZipPath();

const roots = [];
test.after(() => { for (const r of roots) fs.rmSync(r, { recursive: true, force: true }); });
function tree(files) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'knarr-emu-'));
  roots.push(root);
  for (const [rel, content] of Object.entries(files)) {
    const full = path.join(root, rel);
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, content);
  }
  return root;
}

// ── Which file is the game ──────────────────────────────────────────────

test('pickGameFile: Switch folder → the base game, never update/ or dlc/ or the RomM playlist', () => {
  const root = tree({
    'Game [0100ABF008968800][v458752].nsp': 'u'.repeat(50), // a stray update at the top, bigger than the base
    'Game [0100ABF008968000][v0].nsp': 'b'.repeat(10),
    'update/Game [0100ABF008968800][v1].nsp': 'x'.repeat(99),
    'dlc/Game [DLC] [0100ABF008969001][v0].nsp': 'd',
    'Game.m3u': 'Game [0100ABF008968000][v0].nsp',
  });
  assert.equal(emulators.pickGameFile(root), path.join(root, 'Game [0100ABF008968000][v0].nsp'));
});

test('pickGameFile: no title ids → the largest Switch file; plain names, a single file, a playlist, nothing', () => {
  const sw = tree({ 'SMG1.nsp': 'x'.repeat(30), 'extra.nsp': 'y', 'notes.txt': 'z'.repeat(99) });
  assert.equal(emulators.pickGameFile(sw), path.join(sw, 'SMG1.nsp'));
  const discs = tree({ 'Game (Disc 1).chd': 'a'.repeat(9), 'Game (Disc 2).chd': 'b'.repeat(9), 'Game.m3u': 'x' });
  assert.equal(emulators.pickGameFile(discs), path.join(discs, 'Game.m3u'));
  const big = tree({ 'game.iso': 'x'.repeat(40), 'readme.txt': 'y'.repeat(90), 'cover.jpg': 'z'.repeat(99) });
  assert.equal(emulators.pickGameFile(big), path.join(big, 'game.iso'));
  assert.equal(emulators.pickGameFile(path.join(big, 'game.iso')), path.join(big, 'game.iso'));
  assert.equal(emulators.pickGameFile(tree({ 'only.txt': 'x' })), null);
  assert.equal(emulators.pickGameFile(path.join(big, 'missing')), null);
});

// ── Arguments ────────────────────────────────────────────────────────────

test('buildArgs: {rom} becomes one argument even with spaces; quotes group; no {rom} → game last', () => {
  const game = '/home/u/Roms/Switch/Animal Crossing/AC [0100][v0].nsp';
  assert.deepEqual(emulators.buildArgs('-f -g {rom}', game), ['-f', '-g', game]);
  assert.deepEqual(emulators.buildArgs('--game={rom}', game), [`--game=${game}`]);
  assert.deepEqual(emulators.buildArgs('-c "/my config/x.ini"', game), ['-c', '/my config/x.ini', game]);
  assert.deepEqual(emulators.buildArgs('', game), [game]);
  assert.deepEqual(emulators.buildArgs('  -f   ', game), ['-f', game]);
});

test('suggestArgs knows Eden; anything else just gets the game', () => {
  assert.equal(emulators.suggestArgs('/home/u/Emulators/Eden-Linux-v0.2.1-amd64-clang-pgo.AppImage'), '-f -g {rom}');
  assert.equal(emulators.suggestArgs('Eden - Windows'), '-f -g {rom}');
  assert.equal(emulators.suggestArgs('/usr/bin/retroarch'), '{rom}');
});

test('buildCommand: a macOS .app goes through open -W; anything else runs directly', () => {
  assert.deepEqual(emulators.buildCommand('/Applications/Eden.app', ['-g', 'x'], 'darwin'),
    { command: 'open', args: ['-W', '-a', '/Applications/Eden.app', '--args', '-g', 'x'] });
  assert.deepEqual(emulators.buildCommand('/e/Eden.AppImage', ['x'], 'linux'), { command: '/e/Eden.AppImage', args: ['x'] });
});

test('hostEnv drops Knarr\'s AppImage variables and its library dirs, keeps the rest', () => {
  const env = emulators.hostEnv({
    APPDIR: '/tmp/.mount_KnarrX', APPIMAGE: '/a/Knarr.AppImage', ARGV0: 'Knarr', OWD: '/home/u',
    LD_LIBRARY_PATH: '/tmp/.mount_KnarrX/usr/lib:/opt/lib', HOME: '/home/u', PATH: '/usr/bin',
  });
  assert.deepEqual(env, { LD_LIBRARY_PATH: '/opt/lib', HOME: '/home/u', PATH: '/usr/bin' });
  assert.equal('LD_LIBRARY_PATH' in emulators.hostEnv({ APPDIR: '/m', LD_LIBRARY_PATH: '/m/usr/lib' }), false);
  assert.deepEqual(emulators.hostEnv({ HOME: '/h' }), { HOME: '/h' });
});

// ── Which program ────────────────────────────────────────────────────────

test('resolveProgram: an installed AppImage, a Windows folder (not eden-cli), the chosen exe, a path, and the errors', () => {
  const root = tree({
    'Eden.AppImage': 'x',
    'Eden - Windows/eden-cli.exe': 'MZ', 'Eden - Windows/eden.exe': 'MZ', 'Eden - Windows/LICENSES/x.txt': '',
    'Mac/Eden.app/Contents/Info.plist': '',
    'Nested/eden/Eden-x86_64.AppImage': 'x',
  });
  const recs = {
    1: { filePath: path.join(root, 'Eden.AppImage') },
    2: { filePath: path.join(root, 'Eden - Windows') },
    3: { filePath: path.join(root, 'Eden - Windows'), defaultExe: path.join(root, 'Eden - Windows', 'eden-cli.exe') },
    4: { filePath: path.join(root, 'gone.AppImage') },
    5: { filePath: path.join(root, 'Nested') },
  };
  const find = (id) => recs[id];
  assert.deepEqual(emulators.resolveProgram({ romId: 1, args: '' }, find, 'linux'), { ok: true, program: recs[1].filePath });
  assert.deepEqual(emulators.resolveProgram({ romId: 2, args: '' }, find, 'win32'), { ok: true, program: path.join(root, 'Eden - Windows', 'eden.exe') });
  assert.deepEqual(emulators.resolveProgram({ romId: 3, args: '' }, find, 'win32'), { ok: true, program: recs[3].defaultExe });
  assert.deepEqual(emulators.resolveProgram({ romId: 5, args: '' }, find, 'linux'), { ok: true, program: path.join(root, 'Nested', 'eden', 'Eden-x86_64.AppImage') });
  assert.equal(emulators.findProgramIn(path.join(root, 'Mac'), 'darwin'), path.join(root, 'Mac', 'Eden.app'));
  assert.deepEqual(emulators.resolveProgram({ path: recs[1].filePath, args: '' }, find), { ok: true, program: recs[1].filePath });
  assert.match(emulators.resolveProgram({ romId: 4, args: '' }, find).error, /isn't installed on this machine/);
  assert.match(emulators.resolveProgram({ romId: 9, args: '' }, find).error, /isn't installed on this machine/);
  assert.match(emulators.resolveProgram(undefined, find).error, /No emulator is set/);
  assert.match(emulators.resolveProgram({ path: path.join(root, 'nope'), args: '' }, find).error, /wasn't found/);
});

test('normalizeEmulator keeps a rom id or a path (+ args), drops junk', () => {
  assert.deepEqual(config.normalizeEmulator({ romId: 18900, args: ' -f -g {rom} ', extra: 1 }), { romId: 18900, args: '-f -g {rom}' });
  assert.deepEqual(config.normalizeEmulator({ path: ' /opt/eden ', args: 7 }), { path: '/opt/eden', args: '' });
  assert.equal(config.normalizeEmulator({ romId: 'x' }), undefined);
  assert.equal(config.normalizeEmulator(null), undefined);
  assert.equal(config.normalizeEmulator('eden'), undefined);
});

// ── Launch ───────────────────────────────────────────────────────────────

test('launchEmulated runs the program with the base game, from its folder, without Knarr\'s AppImage env, and reports the exit', { skip: process.platform === 'win32' }, async () => {
  const root = tree({
    'Switch/Game/Game [0100000000010000][v0].nsp': 'base',
    'Switch/Game/update/Game [0100000000010800][v1].nsp': 'u',
  });
  // A stand-in emulator: records its argv, cwd and APPDIR, then exits
  const emu = path.join(root, 'Emu.AppImage');
  const out = path.join(root, 'out.json');
  fs.writeFileSync(emu, `#!/bin/sh\nprintf '%s\\n' "$PWD" "\${APPDIR:-none}" "$@" > "${out}"\n`);
  fs.chmodSync(emu, 0o644); // as downloaded: launchEmulated restores the exec bit
  const saved = process.env.APPDIR;
  process.env.APPDIR = '/tmp/.mount_Knarr';
  let exited;
  const done = new Promise((r) => { exited = r; });
  try {
    const res = await emulators.launchEmulated(path.join(root, 'Switch', 'Game'), { romId: 7, args: '-f -g {rom}' },
      (id) => (id === 7 ? { filePath: emu } : undefined), { onExit: () => exited() });
    assert.equal(res.ok, true, res.error);
    assert.equal(res.emulator, 'Emu.AppImage');
    assert.equal(res.game, 'Game [0100000000010000][v0].nsp');
  } finally {
    if (saved === undefined) delete process.env.APPDIR; else process.env.APPDIR = saved;
  }
  await done;
  const lines = fs.readFileSync(out, 'utf8').trimEnd().split('\n');
  assert.deepEqual(lines, [root, 'none', '-f', '-g', path.join(root, 'Switch', 'Game', 'Game [0100000000010000][v0].nsp')]);
});

test('launchEmulated: a program that can\'t start is an error, not a launch', { skip: process.platform === 'win32' }, async () => {
  const root = tree({ 'game.iso': 'x' });
  fs.mkdirSync(path.join(root, 'broken.AppImage')); // exists, but nothing the OS can run
  const res = await emulators.launchEmulated(path.join(root, 'game.iso'), { path: path.join(root, 'broken.AppImage'), args: '' }, () => undefined);
  assert.equal(res.ok, false);
  assert.match(res.error, /Could not start broken\.AppImage/);
});

// ── Firmware ─────────────────────────────────────────────────────────────

function fakeRomm(files) {
  const calls = [];
  return {
    calls,
    listFirmware: async (pid) => files.filter((f) => f.platform_id === pid),
    openFirmwareStream: async (id) => {
      calls.push(id);
      const f = files.find((x) => x.id === id);
      return new Response(new Blob([fs.readFileSync(f.src)]));
    },
  };
}

test('firmwareDir: beside the games — first install path when extracting, else the download folder', () => {
  assert.equal(firmware.firmwareDir({ folder: '/roms/gba', autoExtract: false, installPaths: [] }), path.join('/roms/gba', 'firmware'));
  assert.equal(firmware.firmwareDir({ folder: '', autoExtract: true, installPaths: ['/Roms/Switch', '/sd/Switch'] }), path.join('/Roms/Switch', 'firmware'));
  assert.equal(firmware.firmwareDir({ folder: '', autoExtract: true, installPaths: [] }), '');
  assert.equal(firmware.firmwareDir(undefined), '');
});

test('getFirmware: keys copied, the firmware archive unpacked to a flat folder, and a second run fetches only what changed', async () => {
  const src = tree({ 'fw/firmware/a.nca': 'A', 'fw/firmware/b.cnmt.nca': 'B', 'prod.keys': 'k1', 'title.keys': 't1' });
  const archive = path.join(src, 'firmware 20.3.0.7z');
  assert.equal(spawnSync(path7za, ['a', '-t7z', archive, 'firmware'], { cwd: path.join(src, 'fw') }).status, 0);
  const files = [
    { id: 124, platform_id: 154, file_name: 'prod.keys', md5_hash: 'm1', src: path.join(src, 'prod.keys') },
    { id: 125, platform_id: 154, file_name: 'title.keys', md5_hash: 'm2', src: path.join(src, 'title.keys') },
    { id: 126, platform_id: 154, file_name: 'firmware 20.3.0.7z', md5_hash: 'm3', src: archive },
    { id: 999, platform_id: 1, file_name: 'gba_bios.bin', md5_hash: 'x', src: path.join(src, 'prod.keys') },
  ];
  const romm = fakeRomm(files);
  const dest = path.join(tree({}), 'Roms', 'Switch', 'firmware');

  const r1 = await firmware.getFirmware(romm, 154, dest);
  assert.deepEqual(r1.files.map((f) => [f.name, f.status]), [['prod.keys', 'downloaded'], ['title.keys', 'downloaded'], ['firmware 20.3.0.7z', 'unpacked']]);
  assert.equal(fs.readFileSync(path.join(dest, 'prod.keys'), 'utf8'), 'k1');
  assert.deepEqual(fs.readdirSync(path.join(dest, 'firmware 20.3.0')).sort(), ['a.nca', 'b.cnmt.nca'], 'the archive\'s one top folder is lifted out');
  assert.equal(fs.existsSync(path.join(dest, 'firmware 20.3.0.7z')), false, 'archive removed after unpacking');
  assert.deepEqual(fs.readdirSync(dest).sort(), ['.knarr-firmware.json', 'firmware 20.3.0', 'prod.keys', 'title.keys']);

  // Second run: only the key whose md5 changed on the server is fetched again
  fs.writeFileSync(files[0].src, 'k2');
  files[0].md5_hash = 'm1b';
  romm.calls.length = 0;
  const r2 = await firmware.getFirmware(romm, 154, dest);
  assert.deepEqual(romm.calls, [124]);
  assert.deepEqual(r2.files.map((f) => f.status), ['downloaded', 'unchanged', 'unchanged']);
  assert.equal(fs.readFileSync(path.join(dest, 'prod.keys'), 'utf8'), 'k2');

  // Deleted locally → fetched again even though RomM's copy didn't change
  fs.rmSync(path.join(dest, 'firmware 20.3.0'), { recursive: true });
  romm.calls.length = 0;
  await firmware.getFirmware(romm, 154, dest);
  assert.deepEqual(romm.calls, [126]);
});

test('getFirmware: a server file name can\'t write outside the folder; no folder or no firmware is an error', async () => {
  const src = tree({ 'k': 'x' });
  const dest = path.join(tree({}), 'firmware');
  const romm = fakeRomm([{ id: 1, platform_id: 5, file_name: '../../evil.keys', md5_hash: 'a', src: path.join(src, 'k') }]);
  const r = await firmware.getFirmware(romm, 5, dest);
  assert.equal(path.dirname(r.files[0].path), dest);
  await assert.rejects(firmware.getFirmware(romm, 5, ''), /Set a folder or install path/);
  await assert.rejects(firmware.getFirmware(romm, 6, dest), /no firmware for this platform/);
});
