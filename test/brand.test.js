// The 3.0.0 rename (RomM2SteamDeck -> Knarr): old names still recognised, settings folder moved.
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const brand = require('../dist/brand.js');

test('env: KNARR_ wins, the 2.x R2SD_ name still works', () => {
  delete process.env.KNARR_TESTVAR; delete process.env.R2SD_TESTVAR;
  assert.equal(brand.env('TESTVAR'), undefined);
  process.env.R2SD_TESTVAR = 'old';
  assert.equal(brand.env('TESTVAR'), 'old');
  process.env.KNARR_TESTVAR = 'new';
  assert.equal(brand.env('TESTVAR'), 'new');
  process.env.KNARR_TESTVAR = '';           // set but empty is still set (KNARR_FLAGS="" = no flags)
  assert.equal(brand.env('TESTVAR'), '');
  delete process.env.KNARR_TESTVAR; delete process.env.R2SD_TESTVAR;
});

test('isOwnAppImage: Knarr and 2.x AppImages, quoted or not, any case; not games', () => {
  for (const exe of ['"/home/deck/Applications/Knarr.AppImage"', '/home/j/Knarr.AppImage',
    '"/home/deck/Applications/RomM2SteamDeck.appimage"', '"/home/j/Downloads/RomM2SteamDeck-2.2.38.AppImage"']) {
    assert.ok(brand.isOwnAppImage(exe), exe);
  }
  for (const exe of ['"/games/Knarr Quest/game.exe"', '"/games/x/NotKnarr.AppImage"', '"C:\\\\Knarr\\\\Knarr.exe"', '"/games/x/x.exe"']) {
    assert.ok(!brand.isOwnAppImage(exe), exe);
  }
});

test('isLegacyLauncher: only 2.x RomM2SteamDeck launchers (AppImage or .exe)', () => {
  assert.ok(brand.isLegacyLauncher('"/home/deck/Applications/RomM2SteamDeck.appimage"'));
  assert.ok(brand.isLegacyLauncher('"C:\\Users\\J\\AppData\\Local\\Programs\\romm2steamdeck\\RomM2SteamDeck.exe"'));
  assert.ok(!brand.isLegacyLauncher('"/home/deck/Applications/Knarr.AppImage"'));
  assert.ok(!brand.isLegacyLauncher('"/games/RomM2SteamDeck Fan Game/data/game.bin"'));
});

function tmpAppData() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'knarr-appdata-'));
}

test('migrateUserDataDir moves the 2.x folder whole, Local State included', () => {
  const appData = tmpAppData();
  const legacy = path.join(appData, brand.LEGACY_USER_DATA_DIR);
  fs.mkdirSync(path.join(legacy, 'covers'), { recursive: true });
  fs.writeFileSync(path.join(legacy, 'config.json'), '{"baseUrl":"http://romm"}');
  fs.writeFileSync(path.join(legacy, 'Local State'), '{"os_crypt":{}}');
  const res = brand.migrateUserDataDir(appData);
  assert.deepEqual(res, { dir: path.join(appData, 'knarr'), moved: true });
  assert.equal(fs.readFileSync(path.join(res.dir, 'config.json'), 'utf8'), '{"baseUrl":"http://romm"}');
  assert.ok(fs.existsSync(path.join(res.dir, 'Local State')));
  assert.ok(fs.existsSync(path.join(res.dir, 'covers')));
  assert.equal(fs.existsSync(legacy), false);
  // second start: nothing left to move
  assert.deepEqual(brand.migrateUserDataDir(appData), { dir: res.dir, moved: false });
});

test('migrateUserDataDir: fresh install, and an existing knarr folder is never overwritten', () => {
  const fresh = tmpAppData();
  assert.deepEqual(brand.migrateUserDataDir(fresh), { dir: path.join(fresh, 'knarr'), moved: false });
  const both = tmpAppData();
  fs.mkdirSync(path.join(both, 'knarr'));
  fs.writeFileSync(path.join(both, 'knarr', 'config.json'), '{"theme":"knarr"}');
  fs.mkdirSync(path.join(both, brand.LEGACY_USER_DATA_DIR));
  assert.deepEqual(brand.migrateUserDataDir(both), { dir: path.join(both, 'knarr'), moved: false });
  assert.ok(fs.existsSync(path.join(both, brand.LEGACY_USER_DATA_DIR)), 'old folder left alone');
});

test('migrateUserDataDir: the AppImage launcher\'s eulaAccepted (and stale locks) do not block the move', () => {
  const appData = tmpAppData();
  const dir = path.join(appData, 'knarr');
  const legacy = path.join(appData, brand.LEGACY_USER_DATA_DIR);
  fs.mkdirSync(dir);
  fs.writeFileSync(path.join(dir, 'eulaAccepted'), '');
  fs.symlinkSync('otherhost-123', path.join(dir, 'SingletonLock')); // dangling, as Chromium leaves it
  fs.mkdirSync(legacy);
  fs.writeFileSync(path.join(legacy, 'config.json'), '{"theme":"oled-limited"}');
  const res = brand.migrateUserDataDir(appData);
  assert.deepEqual(res, { dir, moved: true });
  assert.equal(fs.readFileSync(path.join(dir, 'config.json'), 'utf8'), '{"theme":"oled-limited"}');
  assert.ok(fs.existsSync(path.join(dir, 'eulaAccepted')), 'licence acceptance kept');
  assert.equal(fs.existsSync(path.join(dir, 'SingletonLock')), false);
  assert.equal(fs.existsSync(legacy), false);
});

test('migrateUserDataDir: a failed move keeps using the 2.x folder', () => {
  const fakeFs = {
    existsSync: (p) => p.endsWith(brand.LEGACY_USER_DATA_DIR),
    renameSync: () => { throw new Error('EPERM: operation not permitted'); },
    readdirSync: () => [], rmSync: () => {}, rmdirSync: () => {}, writeFileSync: () => {},
  };
  const res = brand.migrateUserDataDir('/appdata', fakeFs);
  assert.equal(res.dir, path.join('/appdata', brand.LEGACY_USER_DATA_DIR));
  assert.equal(res.moved, false);
  assert.match(res.error, /EPERM/);
});
