/**
 * The app's name, and the name it had before. Knarr was called RomM2SteamDeck (R2SD) until 3.0.0.
 *
 * The old name is still recognised wherever an existing install can carry it: the settings
 * folder, R2SD_* environment variables, and Steam shortcuts that point at the old AppImage or
 * .exe. Some 2.x identifiers deliberately keep their old spelling because they are stored data,
 * not names: the cloud-save slot on RomM (cloudsaves.ts), the save-version marker (saves.ts), the
 * hidden download staging/resume files (downloads.ts) and the password obfuscation key (config.ts).
 */
import * as fs from 'fs';
import * as path from 'path';

export const APP_NAME = 'Knarr';
export const LEGACY_APP_NAME = 'RomM2SteamDeck';

/** Settings folder under appData. 2.x used `romm2steamdeck-app`; it is moved on first run. */
export const USER_DATA_DIR = 'knarr';
export const LEGACY_USER_DATA_DIR = 'romm2steamdeck-app';

/** Window class / process name on Linux (electron-builder `executableName`), and the 2.x one. */
export const WINDOW_CLASS = 'knarr';
export const LEGACY_WINDOW_CLASS = 'romm2steamdeck';

/** `KNARR_<name>` from the environment, falling back to the 2.x `R2SD_<name>`. */
export function env(name: string): string | undefined {
  return process.env[`KNARR_${name}`] ?? process.env[`R2SD_${name}`];
}

// A shortcut's Exe as Steam stores it: quoted, any folder, the launcher's own file name.
const OWN_APPIMAGE_RE = /(?:^|[\\/"])(?:Knarr|RomM2SteamDeck)[^\\/"]*\.AppImage"?$/i;
const LEGACY_LAUNCHER_RE = /(?:^|[\\/"])RomM2SteamDeck[^\\/"]*\.(?:AppImage|exe)"?$/i;

/** An AppImage of this app under either name: the Electron shortcut that needs the overlay off. */
export function isOwnAppImage(exe: string): boolean {
  return OWN_APPIMAGE_RE.test(exe);
}

/** A 2.x launcher (RomM2SteamDeck*.AppImage / RomM2SteamDeck.exe): a shortcut to repoint at Knarr. */
export function isLegacyLauncher(exe: string): boolean {
  return LEGACY_LAUNCHER_RE.test(exe);
}

export interface DirFs {
  existsSync(p: string): boolean;
  renameSync(from: string, to: string): void;
}

/**
 * Move the 2.x settings folder to its new name, whole: on Windows the key that decrypts the saved
 * password lives in Chromium's "Local State" file in the same folder, so config.json must never
 * travel alone. Returns the folder to use. If the move fails (the old app still running on
 * Windows, say), the old folder is used as-is, so nothing is lost; the move is retried next start.
 */
export function migrateUserDataDir(appData: string, fsi: DirFs = fs): { dir: string; moved: boolean; error?: string } {
  const dir = path.join(appData, USER_DATA_DIR);
  const legacy = path.join(appData, LEGACY_USER_DATA_DIR);
  if (fsi.existsSync(dir) || !fsi.existsSync(legacy)) return { dir, moved: false };
  try {
    fsi.renameSync(legacy, dir);
    return { dir, moved: true };
  } catch (err) {
    return { dir: legacy, moved: false, error: err instanceof Error ? err.message : String(err) };
  }
}
