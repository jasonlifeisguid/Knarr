/**
 * "Play with": a platform's games launched by the emulator the user picked for
 * that platform — one Knarr installed from RomM (a download from the
 * `emulators` platform) or any program on disk.
 *
 * Knarr only starts the emulator with the game and notices when it closes. The
 * emulator's own setup — keys, firmware, controls, its game list — stays the
 * emulator's business (see firmware.ts for fetching keys/firmware from RomM).
 *
 * No electron imports here so the module is unit-testable standalone.
 */
import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import type { EmulatorSetup } from './config';
import { whenSpawned } from './fsutil';
import { listExes } from './shortcuts';

/** Arguments for emulators we know; anything else just gets the game. */
export function suggestArgs(program: string): string {
  const name = path.basename(program).toLowerCase();
  if (name.includes('eden')) return '-f -g {rom}'; // fullscreen, then the game
  return '{rom}';
}

type RecordLookup = (romId: number) => { filePath: string; defaultExe?: string; romName?: string } | undefined;

/** Helper programs that ship next to the real one. */
const NOT_THE_APP = /cli|updater|uninst|crash|setup|install|room/i;

/** The emulator's program inside a folder Knarr extracted it to. */
export function findProgramIn(dir: string, platform: NodeJS.Platform = process.platform): string | null {
  let found: string[] = [];
  if (platform === 'win32') {
    found = listExes(dir).map((e) => e.path);
  } else {
    // AppImages (Linux) or .app bundles (macOS), at most two levels down
    const want = platform === 'darwin' ? (n: string, isDir: boolean) => isDir && n.endsWith('.app')
      : (n: string, isDir: boolean) => !isDir && /\.appimage$/i.test(n);
    const walk = (d: string, depth: number) => {
      let entries: fs.Dirent[];
      try { entries = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
      for (const e of entries) {
        const full = path.join(d, e.name);
        if (want(e.name, e.isDirectory())) found.push(full);
        else if (e.isDirectory() && depth < 2) walk(full, depth + 1);
      }
    };
    walk(dir, 1);
  }
  const depth = (p: string) => path.relative(dir, p).split(path.sep).length;
  found.sort((a, b) =>
    Number(NOT_THE_APP.test(path.basename(a))) - Number(NOT_THE_APP.test(path.basename(b)))
    || depth(a) - depth(b)
    || path.basename(a).length - path.basename(b).length);
  return found[0] || null;
}

/** The program to run for a platform's "Play with" setting. */
export function resolveProgram(
  emu: EmulatorSetup | undefined,
  findRecord: RecordLookup,
  platform: NodeJS.Platform = process.platform
): { ok: true; program: string } | { ok: false; error: string } {
  if (!emu) return { ok: false, error: 'No emulator is set for this platform — choose one under Play with in Platform Folders.' };
  if (emu.romId) {
    const rec = findRecord(emu.romId);
    if (!rec || !rec.filePath || !fs.existsSync(rec.filePath)) {
      return { ok: false, error: 'The emulator chosen for this platform isn\'t installed on this machine — download it again, or pick another in Platform Folders.' };
    }
    if (fs.statSync(rec.filePath).isFile()) return { ok: true, program: rec.filePath };
    if (rec.defaultExe && fs.existsSync(rec.defaultExe)) return { ok: true, program: rec.defaultExe };
    const program = findProgramIn(rec.filePath, platform);
    return program ? { ok: true, program } : { ok: false, error: `No program found in ${rec.filePath}` };
  }
  if (emu.path && fs.existsSync(emu.path)) return { ok: true, program: emu.path };
  return { ok: false, error: `The emulator for this platform wasn't found: ${emu.path || '(none)'}` };
}

/** Switch dumps; the base game's title id ends in 000 (updates 800, DLC others). */
const SWITCH_EXT = /\.(nsp|xci|nsz|xcz)$/i;
const BASE_TITLE_ID = /\[01[0-9a-f]{11}000\]/i;
/** Never the game: RomM's generated playlist for Switch folders, notes, art. */
const NOT_A_GAME = /\.(txt|nfo|json|xml|md|jpe?g|png|webp|pdf|sfv|md5|sha1|url|ini)$/i;

/**
 * The file to hand the emulator. A downloaded file is the game itself. In a
 * game folder only top-level files count (update/ and dlc/ are the emulator's
 * to find): the Switch base game, else a playlist (multi-disc), else the
 * largest file.
 */
export function pickGameFile(target: string): string | null {
  let stat: fs.Stats;
  try { stat = fs.statSync(target); } catch { return null; }
  if (stat.isFile()) return target;
  let files: { name: string; full: string; size: number }[];
  try {
    files = fs.readdirSync(target, { withFileTypes: true })
      .filter((e) => e.isFile() && !NOT_A_GAME.test(e.name))
      .map((e) => { const full = path.join(target, e.name); return { name: e.name, full, size: fs.statSync(full).size }; });
  } catch { return null; }
  const bySize = (list: typeof files) => [...list].sort((a, b) => b.size - a.size)[0];
  const switchFiles = files.filter((f) => SWITCH_EXT.test(f.name));
  if (switchFiles.length) return (switchFiles.find((f) => BASE_TITLE_ID.test(f.name)) || bySize(switchFiles)).full;
  const playlist = files.find((f) => /\.m3u$/i.test(f.name));
  if (playlist) return playlist.full;
  return files.length ? bySize(files).full : null;
}

/**
 * Split an argument template into argv with the game put in for {rom}. Double
 * quotes group words ("--title {rom}" stays one argument). A template without
 * {rom} gets the game appended, so a bare "-f" still launches something.
 */
export function buildArgs(template: string, game: string): string[] {
  const args: string[] = [];
  let cur = '';
  let quoted = false;
  let started = false;
  for (const ch of template.trim()) {
    if (ch === '"') { quoted = !quoted; started = true; continue; }
    if (!quoted && /\s/.test(ch)) {
      if (started) { args.push(cur); cur = ''; started = false; }
      continue;
    }
    cur += ch;
    started = true;
  }
  if (started) args.push(cur);
  const hasRom = args.some((a) => a.includes('{rom}'));
  const out = args.map((a) => a.split('{rom}').join(game));
  if (!hasRom) out.push(game);
  return out;
}

/** Command + argv. A macOS .app goes through `open -W`, which waits for the app to quit. */
export function buildCommand(program: string, args: string[], platform: NodeJS.Platform = process.platform): { command: string; args: string[] } {
  if (platform === 'darwin' && program.endsWith('.app')) return { command: 'open', args: ['-W', '-a', program, '--args', ...args] };
  return { command: program, args };
}

/**
 * The environment for the emulator: Knarr's own AppImage variables removed, so
 * an AppImage emulator doesn't see Knarr's mount as its own or load its libraries.
 */
export function hostEnv(env: NodeJS.ProcessEnv = process.env): NodeJS.ProcessEnv {
  const out = { ...env };
  const appdir = env.APPDIR;
  for (const k of ['APPDIR', 'APPIMAGE', 'ARGV0', 'OWD']) delete out[k];
  if (appdir && out.LD_LIBRARY_PATH) {
    const kept = out.LD_LIBRARY_PATH.split(':').filter((p) => p && !p.startsWith(appdir));
    if (kept.length) out.LD_LIBRARY_PATH = kept.join(':'); else delete out.LD_LIBRARY_PATH;
  }
  return out;
}

export interface EmulatedLaunch {
  ok: boolean;
  error?: string;
  pid?: number;
  /** For the UI: what was started with what. */
  emulator?: string;
  game?: string;
}

/**
 * Start the platform's emulator with an installed game. `onExit` fires when the
 * emulator closes — the child is the emulator itself (or `open -W` for it).
 */
export async function launchEmulated(
  installed: string,
  emu: EmulatorSetup | undefined,
  findRecord: RecordLookup,
  opts: { onExit?: () => void; spawnFn?: typeof spawn; platform?: NodeJS.Platform } = {}
): Promise<EmulatedLaunch> {
  const platform = opts.platform ?? process.platform;
  const prog = resolveProgram(emu, findRecord, platform);
  if (!prog.ok) return { ok: false, error: prog.error };
  const game = pickGameFile(installed);
  if (!game) return { ok: false, error: `No game file found in ${installed}` };
  const template = emu?.args || suggestArgs(prog.program);
  const res = await startProgram(prog.program, buildArgs(template, game), { ...opts, platform });
  return res.ok ? { ...res, game: path.basename(game) } : res;
}

/**
 * Open the emulator on its own — no game — to set it up or use its own library.
 * Not followed as a game: Knarr stays where it is.
 */
export async function openEmulator(
  emu: EmulatorSetup | undefined,
  findRecord: RecordLookup,
  opts: { spawnFn?: typeof spawn; platform?: NodeJS.Platform } = {}
): Promise<EmulatedLaunch> {
  const platform = opts.platform ?? process.platform;
  const prog = resolveProgram(emu, findRecord, platform);
  if (!prog.ok) return { ok: false, error: prog.error };
  return startProgram(prog.program, [], { ...opts, platform });
}

/** Start a program detached, from its own folder, outside Knarr's AppImage environment. */
async function startProgram(
  program: string,
  programArgs: string[],
  opts: { onExit?: () => void; spawnFn?: typeof spawn; platform: NodeJS.Platform }
): Promise<EmulatedLaunch> {
  const { command, args } = buildCommand(program, programArgs, opts.platform);
  if (opts.platform !== 'win32' && /\.appimage$/i.test(program)) {
    try { fs.chmodSync(program, 0o755); } catch { /* best effort */ }
  }
  let child;
  try {
    child = (opts.spawnFn ?? spawn)(command, args, {
      cwd: path.dirname(program),
      detached: true,
      stdio: 'ignore',
      windowsHide: false,
      env: hostEnv(),
    });
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : String(err) };
  }
  if (opts.onExit) { const onExit = opts.onExit; child.on('exit', () => onExit()); }
  const err = await whenSpawned(child);
  if (err) return { ok: false, error: `Could not start ${path.basename(program)}: ${err.message}` };
  child.unref();
  return { ok: true, pid: child.pid, emulator: path.basename(program) };
}
