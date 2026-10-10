// Repointing 2.x Steam shortcuts at Knarr, and writing library artwork, against a fake Steam
// install. HOME points at a temp folder, so steam.ts finds ~/.local/share/Steam there.
// (Assumes no Steam client is running on the test machine: with Steam running the file is
// rightly left alone, which the "steamRunning" branch reports.)
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const home = fs.mkdtempSync(path.join(os.tmpdir(), 'knarr-home-'));
process.env.HOME = home;
const steam = require('../dist/steam.js');

const configDir = path.join(home, '.local', 'share', 'Steam', 'userdata', '12345', 'config');
const shortcutsPath = path.join(configDir, 'shortcuts.vdf');

function writeShortcuts(entries) {
  fs.mkdirSync(configDir, { recursive: true });
  const shortcuts = {};
  entries.forEach((e, i) => { shortcuts[String(i)] = e; });
  fs.writeFileSync(shortcutsPath, steam.serializeVdf({ shortcuts }));
}
const read = () => steam.parseVdf(fs.readFileSync(shortcutsPath)).shortcuts;

test('repointLegacyShortcuts moves a 2.x shortcut to Knarr in place, games untouched', async (t) => {
  if (await steam.isSteamRunning()) return t.skip('a Steam client is running here');
  // Named after the file, as Steam names a shortcut added live (the Deck's real case)
  const old = steam.buildShortcutEntry('/home/deck/Applications/RomM2SteamDeck.appimage', 'RomM2SteamDeck.AppImage', { tags: ['RomM'], overlayOff: true });
  old.LastPlayTime = 1700000000;
  const renamed = steam.buildShortcutEntry('/home/deck/Downloads/RomM2SteamDeck-2.2.30.AppImage', 'My Game Library');
  const game = steam.buildShortcutEntry('/games/Balls/balls.exe', 'Balls');
  writeShortcuts([old, game, renamed]);
  assert.equal(steam.findLegacyShortcuts().length, 2);

  const knarr = '/home/deck/Applications/Knarr.AppImage';
  const res = await steam.repointLegacyShortcuts(knarr);
  assert.equal(res.ok, true);
  assert.equal(res.repointed.length, 2);
  assert.equal(res.backups.length, 1);
  assert.ok(fs.existsSync(res.backups[0]));

  const after = read();
  assert.equal(after['0'].Exe, `"${knarr}"`);
  assert.equal(after['0'].StartDir, '/home/deck/Applications/');
  assert.equal(after['0'].AppName, 'Knarr', 'default name follows the rename');
  assert.equal(after['0'].appid, old.appid, 'same appid: playtime, collections and artwork stay');
  assert.equal(after['0'].LastPlayTime, 1700000000);
  assert.equal(after['0'].LaunchOptions, steam.OVERLAY_STRIP_LAUNCH_OPTS);
  assert.equal(after['2'].AppName, 'My Game Library', 'a name the user chose is kept');
  assert.equal(after['2'].Exe, `"${knarr}"`);
  assert.deepEqual(after['1'], game, 'game shortcuts are left exactly as they were');

  assert.equal(steam.findLegacyShortcuts().length, 0);
  const again = await steam.repointLegacyShortcuts(knarr);
  assert.deepEqual({ ok: again.ok, n: again.repointed.length, b: again.backups.length }, { ok: true, n: 0, b: 0 });
});

test('writeGridArtwork names files after the unsigned appid and keeps the user\'s own', () => {
  const appId = -1234567890; // shortcuts.vdf stores it signed
  const id = appId >>> 0;
  const grid = path.join(configDir, 'grid');
  fs.mkdirSync(grid, { recursive: true });
  fs.writeFileSync(path.join(grid, `${id}_hero.png`), 'mine');
  const art = { capsule: Buffer.from('c'), wide: Buffer.from('w'), hero: Buffer.from('h'), logo: Buffer.from('l'), icon: Buffer.from('i') };
  const out = steam.writeGridArtwork(configDir, appId, art);
  assert.deepEqual(Object.keys(out).sort(), ['capsule', 'icon', 'logo', 'wide']);
  assert.equal(fs.readFileSync(path.join(grid, `${id}p.png`), 'utf8'), 'c');
  assert.equal(fs.readFileSync(path.join(grid, `${id}.png`), 'utf8'), 'w');
  assert.equal(fs.readFileSync(path.join(grid, `${id}_logo.png`), 'utf8'), 'l');
  assert.equal(fs.readFileSync(path.join(grid, `${id}_hero.png`), 'utf8'), 'mine', 'existing artwork kept');
  steam.writeGridArtwork(configDir, appId, art, true);
  assert.equal(fs.readFileSync(path.join(grid, `${id}_hero.png`), 'utf8'), 'h', 'replace=true overwrites');
});

test('missingGridArtwork leaves out every kind the shortcut already has (png or jpg)', () => {
  const appId = 777;
  const grid = path.join(configDir, 'grid');
  fs.mkdirSync(grid, { recursive: true });
  fs.writeFileSync(path.join(grid, '777p.jpg'), 'user capsule');
  fs.writeFileSync(path.join(grid, '777_logo.png'), 'user logo');
  const art = { capsule: Buffer.from('c'), wide: Buffer.from('w'), hero: Buffer.from('h'), logo: Buffer.from('l') };
  assert.deepEqual(Object.keys(steam.missingGridArtwork(configDir, appId, art)).sort(), ['hero', 'wide']);
});

test('configDirForShortcut finds the Steam user that owns a shortcut', () => {
  writeShortcuts([steam.buildShortcutEntry('/home/deck/Applications/Knarr.AppImage', 'Knarr')]);
  assert.equal(steam.configDirForShortcut('/home/deck/Applications/Knarr.AppImage'), configDir);
  assert.equal(steam.configDirForShortcut('/nowhere/else.AppImage'), null);
});
