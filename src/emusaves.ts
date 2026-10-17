/**
 * Where an emulator keeps one game's saves, so Saves & Folders and the RomM
 * cloud sync (cloudsaves.ts) can treat them like a PC game's prefix.
 *
 * All three emulators Knarr knows file saves under the game's title id, which
 * Knarr reads from the installed game:
 *
 *   Eden     <data>/nand/user/save/0000000000000000/<profile>/<title id>/   id: the base NSP's [01…000]
 *   RPCS3    <config>/dev_hdd0/home/<user>/savedata/<title id>…/           id: PARAM.SFO TITLE_ID (BLUS30767)
 *   shadPS4  <data>/home/<user>/savedata/<title id>/                       id: sce_sys/param.sfo TITLE_ID (CUSA10454)
 *
 * A zip holds the game's folders relative to that save directory, so it
 * restores into another machine's directory as is — including Eden's, whose
 * profile id differs per install. Linux only for now (Windows/macOS keep these
 * elsewhere).
 *
 * No electron imports here so the module is unit-testable standalone.
 */
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import type { SaveLayout } from './saves';
import { pickGameFile } from './emulators';

export type EmuKind = 'eden' | 'rpcs3' | 'shadps4';

const LABEL: Record<EmuKind, string> = { eden: 'Eden', rpcs3: 'RPCS3', shadps4: 'shadPS4' };

/** Which emulator a program is, by its file name. */
export function emulatorKind(program: string): EmuKind | null {
  const name = path.basename(program).toLowerCase();
  if (name.includes('eden')) return 'eden';
  if (name.includes('rpcs3')) return 'rpcs3';
  if (name.includes('shadps4')) return 'shadps4';
  return null;
}

/** `dir/a/b` matching each part case-insensitively, or null. */
function findPath(dir: string, parts: string[]): string | null {
  let cur = dir;
  for (const part of parts) {
    let names: string[];
    try { names = fs.readdirSync(cur); } catch { return null; }
    const hit = names.find((n) => n.toLowerCase() === part.toLowerCase());
    if (!hit) return null;
    cur = path.join(cur, hit);
  }
  return cur;
}

/**
 * A string field of a PlayStation PARAM.SFO (PS3 and PS4 share the format):
 * header "\0PSF", key table and data table offsets, then 16-byte index
 * entries (key offset u16, format u16, length u32, max length u32, data offset u32).
 */
export function readSfoString(file: string, key: string): string | null {
  let buf: Buffer;
  try { buf = fs.readFileSync(file); } catch { return null; }
  if (buf.length < 20 || buf.readUInt32BE(0) !== 0x00505346) return null;
  const keyTable = buf.readUInt32LE(8);
  const dataTable = buf.readUInt32LE(12);
  const count = buf.readUInt32LE(16);
  for (let i = 0; i < count; i++) {
    const at = 20 + i * 16;
    if (at + 16 > buf.length) return null;
    const keyStart = keyTable + buf.readUInt16LE(at);
    const keyEnd = buf.indexOf(0, keyStart);
    if (keyEnd < 0 || buf.toString('utf8', keyStart, keyEnd) !== key) continue;
    const len = buf.readUInt32LE(at + 4);
    const start = dataTable + buf.readUInt32LE(at + 12);
    if (start + len > buf.length) return null;
    return buf.toString('utf8', start, start + len).replace(/\0+$/, '') || null;
  }
  return null;
}

/** The game's title id, read from what Knarr installed. */
export function gameTitleId(kind: EmuKind, installed: string): string | null {
  if (kind === 'eden') {
    const game = pickGameFile(installed);
    const m = game && path.basename(game).match(/\[(01[0-9a-f]{11}000)\]/i);
    return m ? m[1].toUpperCase() : null;
  }
  const sfoPaths = kind === 'rpcs3' ? [['PS3_GAME', 'PARAM.SFO'], ['PARAM.SFO']] : [['sce_sys', 'param.sfo']];
  for (const parts of sfoPaths) {
    const sfo = findPath(installed, parts);
    const id = sfo ? readSfoString(sfo, 'TITLE_ID') : null;
    if (id && /^[A-Z0-9]{4,12}$/.test(id)) return id;
  }
  return null;
}

export interface SaveEnv {
  homedir: string;
  xdgDataHome?: string;
  xdgConfigHome?: string;
  /** The emulator's program folder (Eden looks there for a portable `user/` dir). */
  programDir?: string;
}

export function realSaveEnv(programDir?: string): SaveEnv {
  return { homedir: os.homedir(), xdgDataHome: process.env.XDG_DATA_HOME, xdgConfigHome: process.env.XDG_CONFIG_HOME, programDir };
}

const isDir = (p: string) => { try { return fs.statSync(p).isDirectory(); } catch { return false; } };
const subdirs = (p: string) => { try { return fs.readdirSync(p, { withFileTypes: true }).filter((e) => e.isDirectory()).map((e) => e.name); } catch { return []; } };

export interface EmuSaveDir {
  kind: EmuKind;
  titleId: string;
  /** The emulator's save directory (zip paths are relative to it). */
  dir: string;
  /** Does a top-level folder name belong to this game? */
  isGameFolder: (name: string) => boolean;
  /** "Eden saves · 01004A4010FEA000", for the Saves & Folders dialog. */
  label: string;
}

/** The save directory for this game on this machine, or why there isn't one. */
export function locateSaveDir(kind: EmuKind, titleId: string, env: SaveEnv): EmuSaveDir | { error: string } {
  const data = env.xdgDataHome || path.join(env.homedir, '.local', 'share');
  const conf = env.xdgConfigHome || path.join(env.homedir, '.config');
  let dir: string | null = null;
  let isGameFolder: (name: string) => boolean;
  if (kind === 'eden') {
    // Portable install: a user/ folder beside the program (Knarr starts it from there)
    const portable = env.programDir ? path.join(env.programDir, 'user') : '';
    const base = path.join(portable && isDir(portable) ? portable : path.join(data, 'eden'), 'nand', 'user', 'save', '0000000000000000');
    // One folder per Eden profile; its id is random per install. With several, the one used last.
    const profiles = subdirs(base).filter((n) => /^[0-9A-F]{32}$/i.test(n));
    if (profiles.length) {
      const newest = profiles.map((n) => ({ n, t: fs.statSync(path.join(base, n)).mtimeMs })).sort((a, b) => b.t - a.t)[0].n;
      dir = path.join(base, newest);
    }
    isGameFolder = (name) => name.toUpperCase() === titleId;
  } else if (kind === 'rpcs3') {
    const home = path.join(conf, 'rpcs3', 'dev_hdd0', 'home');
    const users = subdirs(home).filter((n) => /^\d{8}$/.test(n)).sort();
    const user = users.includes('00000001') ? '00000001' : users[0];
    if (user) dir = path.join(home, user, 'savedata');
    // One game can have several save folders: BLUS30767-AUTO_0-, BLUS30767SAVE01, …
    isGameFolder = (name) => name.toUpperCase().startsWith(titleId);
  } else {
    const root = path.join(data, 'shadPS4');
    let user = '1000';
    try {
      const users = JSON.parse(fs.readFileSync(path.join(root, 'users.json'), 'utf8'))?.Users?.user;
      const first = Array.isArray(users) ? [...users].sort((a, b) => (a.player_index ?? 99) - (b.player_index ?? 99))[0] : null;
      if (first?.user_id) user = String(first.user_id);
    } catch { /* default user */ }
    if (isDir(path.join(root, 'home', user))) dir = path.join(root, 'home', user, 'savedata');
    isGameFolder = (name) => name.toUpperCase() === titleId;
  }
  if (!dir) return { error: `Open ${LABEL[kind]} once first — it creates its user folder on first run.` };
  return { kind, titleId, dir, isGameFolder, label: `${LABEL[kind]} saves · ${titleId}` };
}

/** The save layout cloudsaves.ts / saves.ts work with: the game's folders in the save directory. */
export function saveLayout(s: EmuSaveDir): SaveLayout {
  return { profile: s.dir, roots: {}, direct: true, requireScope: false, topMatch: s.isGameFolder };
}

/** The game's save folders that exist right now. */
export function gameFolders(s: EmuSaveDir): string[] {
  return subdirs(s.dir).filter(s.isGameFolder).map((n) => path.join(s.dir, n));
}
