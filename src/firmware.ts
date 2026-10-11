/**
 * "Get firmware": copy a platform's firmware files from RomM (keys, system
 * firmware, BIOS) into a folder next to its games, unpacking archives so the
 * emulator's own "install firmware from folder" can take them.
 *
 * Knarr doesn't put anything into the emulator — that stays a step in the
 * emulator (Eden: Tools → Install Decryption Keys / Install Firmware).
 *
 * A manifest (.knarr-firmware.json: file name → RomM md5) makes a second run
 * fetch only what changed on the server.
 */
import * as fs from 'fs';
import * as path from 'path';
import { Readable } from 'stream';
import { pipeline } from 'stream/promises';
import type { PlatformSetup } from './config';
import { run7za } from './downloads';
import { safeFileName } from './fsutil';
import type { RommFirmware } from './romm';

export const FIRMWARE_DIR = 'firmware';
const MANIFEST = '.knarr-firmware.json';
const ARCHIVE = /\.(zip|7z)$/i;

/** Where a platform's firmware goes: a firmware/ folder beside its games. */
export function firmwareDir(setup: PlatformSetup | undefined): string {
  if (!setup) return '';
  const base = setup.autoExtract ? setup.installPaths[0] : setup.folder;
  return base ? path.join(base, FIRMWARE_DIR) : '';
}

export interface FirmwareSource {
  listFirmware(platformId: number): Promise<RommFirmware[]>;
  openFirmwareStream(id: number, fileName: string, signal?: AbortSignal): Promise<Response>;
}

export interface FirmwareResult {
  dest: string;
  files: { name: string; status: 'downloaded' | 'unpacked' | 'unchanged'; path: string }[];
}

function readManifest(dest: string): Record<string, string> {
  try {
    const m = JSON.parse(fs.readFileSync(path.join(dest, MANIFEST), 'utf8'));
    return m && typeof m === 'object' ? m : {};
  } catch { return {}; }
}

/** Unpack an archive into dest/<archive name>; a single top folder inside is
 *  lifted out, so the folder holds the files themselves (an emulator's "from
 *  folder" install usually doesn't look into subfolders). */
async function unpack(archive: string, dest: string): Promise<string> {
  const target = path.join(dest, path.basename(archive).replace(ARCHIVE, ''));
  const staging = path.join(dest, `.knarr-unpack-${process.pid}`);
  fs.rmSync(staging, { recursive: true, force: true });
  fs.mkdirSync(staging, { recursive: true });
  try {
    await run7za(archive, staging, () => { /* small; no progress */ });
    const tops = fs.readdirSync(staging);
    const source = tops.length === 1 && fs.statSync(path.join(staging, tops[0])).isDirectory()
      ? path.join(staging, tops[0]) : staging;
    fs.rmSync(target, { recursive: true, force: true });
    fs.renameSync(source, target);
  } finally {
    fs.rmSync(staging, { recursive: true, force: true });
  }
  return target;
}

export async function getFirmware(source: FirmwareSource, platformId: number, dest: string): Promise<FirmwareResult> {
  if (!dest) throw new Error('Set a folder or install path for this platform first — firmware goes next to its games.');
  const files = await source.listFirmware(platformId);
  if (!files.length) throw new Error('RomM has no firmware for this platform.');
  fs.mkdirSync(dest, { recursive: true });
  const manifest = readManifest(dest);
  const result: FirmwareResult = { dest, files: [] };

  for (const f of files) {
    // RomM picks the name; reduce it to a plain file name so it can't leave dest
    const name = safeFileName(f.file_name, `firmware-${f.id}`);
    const isArchive = ARCHIVE.test(name);
    const out = isArchive ? path.join(dest, name.replace(ARCHIVE, '')) : path.join(dest, name);
    if (f.md5_hash && manifest[name] === f.md5_hash && fs.existsSync(out)) {
      result.files.push({ name, status: 'unchanged', path: out });
      continue;
    }
    const file = path.join(dest, name);
    const part = `${file}.part`;
    try {
      const res = await source.openFirmwareStream(f.id, f.file_name);
      await pipeline(Readable.fromWeb(res.body as never), fs.createWriteStream(part));
      fs.renameSync(part, file);
    } finally {
      fs.rmSync(part, { force: true });
    }
    if (isArchive) {
      try { await unpack(file, dest); } finally { fs.rmSync(file, { force: true }); }
    }
    manifest[name] = f.md5_hash;
    fs.writeFileSync(path.join(dest, MANIFEST), JSON.stringify(manifest, null, 1));
    result.files.push({ name, status: isArchive ? 'unpacked' : 'downloaded', path: out });
  }
  return result;
}
