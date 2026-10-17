// Emulator saves (emusaves.ts): title ids from the game files, each emulator's
// save directory, and a zip → RomM → restore round trip into a machine whose
// Eden profile id is different.
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const emusaves = require('../dist/emusaves.js');
const saves = require('../dist/saves.js');
const cloud = require('../dist/cloudsaves.js');

const roots = [];
test.after(() => { for (const r of roots) fs.rmSync(r, { recursive: true, force: true }); });
function tree(files) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'knarr-emusaves-'));
  roots.push(root);
  for (const [rel, content] of Object.entries(files)) {
    const full = path.join(root, rel);
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, content);
  }
  return root;
}

/** A PARAM.SFO with the given string fields (format 0x0204 = UTF-8 string). */
function sfo(fields) {
  const keys = Object.keys(fields);
  let keyTable = Buffer.alloc(0); let data = Buffer.alloc(0);
  const index = Buffer.alloc(16 * keys.length);
  keys.forEach((k, i) => {
    const v = Buffer.from(fields[k] + '\0');
    const max = Math.ceil(v.length / 4) * 4;
    index.writeUInt16LE(keyTable.length, i * 16);
    index.writeUInt16LE(0x0204, i * 16 + 2);
    index.writeUInt32LE(v.length, i * 16 + 4);
    index.writeUInt32LE(max, i * 16 + 8);
    index.writeUInt32LE(data.length, i * 16 + 12);
    keyTable = Buffer.concat([keyTable, Buffer.from(k + '\0')]);
    data = Buffer.concat([data, v, Buffer.alloc(max - v.length)]);
  });
  const header = Buffer.alloc(20);
  header.writeUInt32BE(0x00505346, 0); header.writeUInt32LE(0x101, 4);
  header.writeUInt32LE(20 + index.length, 8);
  header.writeUInt32LE(20 + index.length + keyTable.length, 12);
  header.writeUInt32LE(keys.length, 16);
  return Buffer.concat([header, index, keyTable, data]);
}

test('emulatorKind by program name', () => {
  assert.equal(emusaves.emulatorKind('/e/Eden - Linux/Eden-Linux-v0.2.1-amd64-clang-pgo.AppImage'), 'eden');
  assert.equal(emusaves.emulatorKind('rpcs3-v0.0.43-20284-2ba2f75b_linux64.AppImage'), 'rpcs3');
  assert.equal(emusaves.emulatorKind('shadPS4QtLauncher-qt.AppImage'), 'shadps4');
  assert.equal(emusaves.emulatorKind('/usr/bin/retroarch'), null);
});

test('readSfoString reads a field among others; junk and missing keys are null', () => {
  const root = tree({ 'PARAM.SFO': sfo({ APP_VER: '01.00', CATEGORY: 'DG', TITLE: "Dragon's Crown", TITLE_ID: 'BLUS30767' }), 'junk': 'not an sfo' });
  assert.equal(emusaves.readSfoString(path.join(root, 'PARAM.SFO'), 'TITLE_ID'), 'BLUS30767');
  assert.equal(emusaves.readSfoString(path.join(root, 'PARAM.SFO'), 'TITLE'), "Dragon's Crown");
  assert.equal(emusaves.readSfoString(path.join(root, 'PARAM.SFO'), 'NOPE'), null);
  assert.equal(emusaves.readSfoString(path.join(root, 'junk'), 'TITLE_ID'), null);
  assert.equal(emusaves.readSfoString(path.join(root, 'missing'), 'TITLE_ID'), null);
});

test('gameTitleId: Switch base NSP name, PS3 disc and digital PARAM.SFO, PS4 sce_sys/param.sfo', () => {
  const sw = tree({ 'Bayonetta 3 [01004a4010fea000][v0].nsp': 'b', 'update/Bayonetta 3 [01004A4010FEA800][v65536].nsp': 'u' });
  assert.equal(emusaves.gameTitleId('eden', sw), '01004A4010FEA000');
  assert.equal(emusaves.gameTitleId('eden', tree({ 'SMG1.nsp': 'x' })), null, 'no id in the name');
  const ps3 = tree({ 'PS3_GAME/PARAM.SFO': sfo({ TITLE_ID: 'BLUS30767' }), 'PS3_GAME/USRDIR/EBOOT.BIN': 'e' });
  assert.equal(emusaves.gameTitleId('rpcs3', ps3), 'BLUS30767');
  const ps3digital = tree({ 'param.sfo': sfo({ TITLE_ID: 'NPUB30910' }), 'USRDIR/EBOOT.BIN': 'e' });
  assert.equal(emusaves.gameTitleId('rpcs3', ps3digital), 'NPUB30910');
  const ps4 = tree({ 'eboot.bin': 'e', 'sce_sys/param.sfo': sfo({ TITLE_ID: 'CUSA10454', CONTENT_ID: 'UP…' }) });
  assert.equal(emusaves.gameTitleId('shadps4', ps4), 'CUSA10454');
});

test('locateSaveDir: Eden profile, RPCS3 user 00000001, shadPS4 player 1; missing → "open it once"', () => {
  const home = tree({
    '.local/share/eden/nand/user/save/0000000000000000/C55DA7B14E6525EF3D5D7B7786E02806/01004A4010FEA000/save.bin': 's',
    '.config/rpcs3/dev_hdd0/home/00000001/savedata/BLUS30767-AUTO_0-/SAVE.DAT': 's',
    '.config/rpcs3/dev_hdd0/home/00000001/savedata/BLUS30767SAVE01/SAVE.DAT': 's',
    '.config/rpcs3/dev_hdd0/home/00000001/savedata/BLES00001-OTHER/SAVE.DAT': 'other game',
    '.local/share/shadPS4/users.json': JSON.stringify({ Users: { user: [{ player_index: 2, user_id: 1001 }, { player_index: 1, user_id: 1000 }] } }),
    '.local/share/shadPS4/home/1000/savedata/CUSA10454/SAVEDATA00/SAVE0.DAT': 's',
    '.local/share/shadPS4/home/1001/savedata/.keep': '',
  });
  const env = { homedir: home };
  const eden = emusaves.locateSaveDir('eden', '01004A4010FEA000', env);
  assert.equal(eden.dir, path.join(home, '.local/share/eden/nand/user/save/0000000000000000/C55DA7B14E6525EF3D5D7B7786E02806'));
  assert.equal(eden.label, 'Eden saves · 01004A4010FEA000');
  const ps3 = emusaves.locateSaveDir('rpcs3', 'BLUS30767', env);
  assert.deepEqual(emusaves.gameFolders(ps3).map((p) => path.basename(p)).sort(), ['BLUS30767-AUTO_0-', 'BLUS30767SAVE01']);
  const ps4 = emusaves.locateSaveDir('shadps4', 'CUSA10454', env);
  assert.equal(ps4.dir, path.join(home, '.local/share/shadPS4/home/1000/savedata'));
  const empty = { homedir: tree({}) };
  for (const kind of ['eden', 'rpcs3', 'shadps4']) assert.match(emusaves.locateSaveDir(kind, 'X', empty).error, /once first/);
  // Eden portable: a user/ folder beside the program wins
  const prog = tree({ 'user/nand/user/save/0000000000000000/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/.keep': '' });
  assert.equal(emusaves.locateSaveDir('eden', 'X', { homedir: home, programDir: prog }).dir,
    path.join(prog, 'user/nand/user/save/0000000000000000/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'));
});

test('listing an emulator layout: only the game\'s folders, every file kept', () => {
  const dir = tree({
    'BLUS30767-AUTO_0-/SAVE.DAT': 'progress', 'BLUS30767-AUTO_0-/PARAM.SFO': 'p', 'BLUS30767-AUTO_0-/settings.ini': 'kept too',
    'BLES00001-OTHER/SAVE.DAT': 'another game',
  });
  const layout = emusaves.saveLayout({ kind: 'rpcs3', titleId: 'BLUS30767', dir, isGameFolder: (n) => n.startsWith('BLUS30767'), label: '' });
  const l = saves.listSaveFiles(layout, { configExcludes: [], includeConfig: true });
  assert.deepEqual(l.included.map((f) => f.rel), ['BLUS30767-AUTO_0-/PARAM.SFO', 'BLUS30767-AUTO_0-/SAVE.DAT', 'BLUS30767-AUTO_0-/settings.ini']);
});

/** An in-memory RomM: just the save calls cloudsaves.ts makes. */
function fakeRomm() {
  const store = [];
  let next = 1;
  const md5 = (b) => crypto.createHash('md5').update(b).digest('hex');
  return {
    store,
    async savesSummary(romId) {
      const mine = store.filter((s) => s.rom_id === romId);
      const latest = mine[mine.length - 1];
      return { total_count: mine.length, slots: latest ? [{ slot: cloud.CLOUD_SLOT, count: mine.length, latest }] : [] };
    },
    async uploadSave(romId, fileName, content, opts) {
      const s = { id: next++, rom_id: romId, file_name: fileName, file_size_bytes: content.length, emulator: opts.emulator, slot: opts.slot,
        content_hash: md5(content), updated_at: new Date().toISOString(), origin_device_id: null, content };
      store.push(s);
      return s;
    },
    async downloadSave(id) { return store.find((s) => s.id === id).content; },
    async listSaves(romId) { return store.filter((s) => s.rom_id === romId); },
    async confirmSaveDownloaded() {},
    async listDevices() { return []; },
  };
}

test('round trip: upload Eden saves from one machine, restore on another with a different profile id', async () => {
  const romm = fakeRomm();
  const machineA = tree({
    'eden/nand/user/save/0000000000000000/C55DA7B14E6525EF3D5D7B7786E02806/01004A4010FEA000/save.bin': 'chapter 5',
    'eden/nand/user/save/0000000000000000/C55DA7B14E6525EF3D5D7B7786E02806/0100152000022000/other.bin': 'another game',
  });
  const machineB = tree({ 'eden/nand/user/save/0000000000000000/0123456789ABCDEF0123456789ABCDEF/.keep': '' });
  const at = (data) => {
    const s = emusaves.locateSaveDir('eden', '01004A4010FEA000', { homedir: '/nowhere', xdgDataHome: data });
    return { s, layout: emusaves.saveLayout(s) };
  };
  const a = at(machineA); const b = at(machineB);
  let recA = null; let recB = null;
  const deps = (get, set) => ({ client: romm, rules: { configExcludes: [], includeConfig: true }, deviceId: null, emulator: 'eden', getRecord: get, setRecord: set });

  const up = await cloud.upload(deps(() => recA, (r) => { recA = r; }), 7, a.layout, 'Bayonetta 3');
  assert.equal(up.ok, true, up.error);
  assert.equal(up.files, 1, 'only this game\'s folder');
  assert.equal(romm.store[0].emulator, 'eden');

  assert.equal((await cloud.status(deps(() => recB, (r) => { recB = r; }), 7, b.layout)).state, 'remote-only');
  const down = await cloud.download(deps(() => recB, (r) => { recB = r; }), 7, b.layout);
  assert.equal(down.ok, true, down.error);
  const restored = path.join(b.s.dir, '01004A4010FEA000', 'save.bin');
  assert.equal(fs.readFileSync(restored, 'utf8'), 'chapter 5', 'into machine B\'s own profile folder');
  assert.deepEqual(fs.readdirSync(b.s.dir).sort(), ['.keep', '01004A4010FEA000'], 'nothing else written (no marker folder)');
  assert.equal((await cloud.status(deps(() => recB, (r) => { recB = r; }), 7, b.layout)).state, 'in-sync');

  // Play on B → B is newer; A is behind
  fs.writeFileSync(restored, 'chapter 6');
  fs.utimesSync(restored, new Date(), new Date(Date.now() + 5000));
  assert.equal((await cloud.status(deps(() => recB, (r) => { recB = r; }), 7, b.layout)).state, 'local-newer');
});

test('restore refuses a zip whose folders aren\'t this game\'s', async () => {
  const src = tree({ 'BLES00001-OTHER/SAVE.DAT': 'x' });
  const other = emusaves.saveLayout({ kind: 'rpcs3', titleId: 'BLES00001', dir: src, isGameFolder: (n) => n.startsWith('BLES00001'), label: '' });
  const zip = path.join(tree({}), 'x.zip');
  assert.equal((await saves.zipSaves(other, zip, { configExcludes: [], includeConfig: true })).ok, true);
  const dest = tree({});
  const mine = emusaves.saveLayout({ kind: 'rpcs3', titleId: 'BLUS30767', dir: dest, isGameFolder: (n) => n.startsWith('BLUS30767'), label: '' });
  const r = await saves.restoreSaves(mine, zip);
  assert.equal(r.ok, false);
  assert.match(r.error, /unexpected top-level entries: BLES00001-OTHER/);
  assert.deepEqual(fs.readdirSync(dest), []);
});
