# Knarr — branding

Decided 2026-10-09: RomM2SteamDeck (R2SD) will be renamed **Knarr**, released as **version 3.0.0**. The rename itself has not
started; this folder records the name, the mark, and why.

## Name

- **Knarr**: the Viking cargo ship that crossed open sea to carry goods home. Knarr carries your
  games from your RomM server to wherever you play.
- **Said** "nar" (the Norse original sounds the K: "k-nar"). Put "(k)nar" in the README once.
- **Tagline:** *Your RomM library, ready to play.* RomM goes in the tagline and the repo
  description, not the name: community clients commonly do this (romm-tender, romm-mobile, ...).
- **About text:** "An unofficial client for RomM; not affiliated with the RomM project."
- **Conflicts checked 2026-10-09:** no app named Knarr on Flathub, only small unrelated GitHub repos.
  Knarr is also a 2023 board game (Bombyx, on Board Game Arena): same games space, different kind
  of product.
- **US trademarks (USPTO), searched 2026-10-09:** no live "KNARR" mark in any class. Only one was
  ever filed: Knarr Analytics, class 42 (data-analysis software), abandoned in 2019 without being
  used. Nearby live marks are in unrelated fields: KNARRTEK (software consulting), KNARRATIVE
  (education), KNAR (footwear), and KNORR (Unilever food; Knorr-Bremse brakes).
- **EU and international (TMview), searched by the user 2026-10-09:** live KNARR marks belong to
  **Knarr Vertriebs GmbH** (Helmbrechts, Germany), a distributor of machines, tools and standard
  parts for tool and mould making. Registered with EUIPO, WIPO (Madrid), Germany and the UK, in
  classes 6, 7, 35, 37, 40 and 42. Their logo is "KNARR" in caps with a small angular symbol on
  the left. Different field, so confusion is unlikely; keep the Knarr mark visually distinct from
  theirs, and don't offer Knarr as a hosted service (class 42). No KNARR mark in class 28 (games)
  in any office TMview covers.
- **Classes 9 (software) and 41 (entertainment), all 13 results reviewed:** no mark is "Knarr" on
  its own. Every hit is a longer word that happens to contain it: KNARRHULT (Leif Carlsson; metal
  and household goods, DK/NO/SE), RISKNARRATIVE (LexisNexis risk software), KNARRATIVE (US
  e-books), KNARRENHOF (a Dutch services company, classes 35–45), KRASSE KNARREN (a Dutch TV
  programme of broadcaster MAX), and Knarrholmen (Swedish events; expired). Different words,
  different fields: no conflict. **Trademark check complete: Knarr is clear for a game client.**

## The mark

A medieval merchant's mark, the line symbol Scandinavian and Hanseatic traders branded onto their
cargo (Norwegian *bumerke*). Built from the traditional parts: a **staff**, the **sign of four** at the
top, the owner's initial (**K**) on the staff, and a base, here a **hull** whose bow rises to the right.

It is a mark designed in that tradition, not a historical symbol. Don't present it, or any part
of it, as an ancient Viking symbol.

### Forms

| Form | File | Use |
|---|---|---|
| **D** · mark alone | `knarr-refined-D.svg` | Logo beside the wordmark, README header |
| **E** · mark in a shield | `knarr-refined-E.svg` | App icon (Windows, Linux, Steam) |
| Seal (mark in a KNARR ring) | `explorations/knarr-balance-hull-seal.svg` | Badges, About screen. Not yet redrawn with the refined mark. |
| **A2** · D refined at small sizes | `small/knarr-small-A2-refined.svg` | 16–32 px: tray, favicon, small icon sizes. Exactly D refined scaled to a 24 grid, stroke 2. The K goes soft at true 16 px; accepted, since modern screens mostly scale up (decided 2026-10-09). |

### Construction (keep these when editing)

The geometry is in `knarr-refined.py`, on a 200 × 220 box:

- **One angle:** every diagonal is 45°. Three of them are parallel: the 4's slope, the K's upper arm,
  and the bow.
- **10-unit grid:** every line starts and ends on it.
- **Stroke 14**, butt ends, mitred joins.
- **Equal gaps:** the 4's bar to the K's upper tip, and the K's lower tip to the hull, are both 30.
- **E:** the shield line matches the mark's stroke at its scale (0.66), and the mark sits on the
  shield's optical centre (y = 104), not its geometric centre (y = 110).

### The hidden ship

Because of the 45° rule, the empty spaces between the strokes draw a ship: a **pennant** at the
masthead, a **sail** hanging from the 4's bar, and a **hull** under the K
(`knarr-negative-preview.png`). Leave it to be discovered; the brand story can say
"look between the lines".

## Wordmark (decided 2026-10-09)

**Knarr** in title case, Noto Sans Bold: the **K in the mark's gold** (`#e2b64e`), "narr" in bone
(`#efe6d2`). Spelled normally, so the logo matches how the name is written in text; the gold K ties
the name to the K in the mark. In one colour it is simply "Knarr". In running text the name is
always plain "Knarr". Title case also keeps it distinct from Knarr Vertriebs GmbH's logo (bold sans
capitals). In artwork the name is drawn as outlines (`wordmark/knarr-wordmark.json`, K and "narr"
as separate paths), so no font is needed. Candidates considered: `knarr-wordmark-preview.png`,
`knarr-casing-preview.png` (kNarr, kNARR, knarr ...).

## Depth (decided 2026-10-09)

Large and hero uses (README banner, splash/About, Steam artwork) use the flat gold mark with a
**soft drop shadow** on navy: simple SVG, clean, easy to read. Icons and in-app marks stay flat.
The struck-brass, embossed, engraved and branded versions are in `knarr-depth.py`
(`knarr-depth-preview.png`) for occasional accents.

## App icon set

`knarr-icons.py` builds `icons/`: **E** on a navy tile for 48 px and up, **A2** on a slimmer tile
at ~80% for 16–32 px; PNGs at 16–1024 and a multi-size `icon.ico` (every size stored as PNG,
15 KB). These replace `build/icon.png` and `build/icon.ico` during the rename.

## Steam artwork and README banner

`knarr-steam.py` (after `knarr-wordmark-outline.py`, which needs fontTools) builds `steam/`:
portrait capsule 600×900, wide capsule 920×430, hero 1920×620 (PNG at 3840×1240, no logo: Steam
lays the logo over it), a transparent logo, and `knarr-banner.png` for the README. All use the
flat mark with a soft drop shadow. Preview: `knarr-steam-preview.png`.

## Colours

| Role | Hex |
|---|---|
| Navy (backgrounds) | `#14243a` |
| Gold (the mark on dark) | `#e2b64e` |
| Bone (light backgrounds, text on dark) | `#efe6d2` |
| Ink (the mark on light) | `#1a1c2c` |
| Sea foam (secondary text) | `#7fb3d5` |

## Next steps

1. ~~Trademark search~~: done 2026-10-09, clear.
2. ~~Small symbol~~ (A2, done); redraw the seal with the refined mark.
3. ~~App icon set~~ (done: `icons/`, from `knarr-icons.py`). Still to do: the in-app header mark,
   a Knarr colour theme, README banner and Steam artwork (done, `steam/`, `knarr-banner.png`);
   the app still has to *apply* the Steam artwork when it adds itself (code).
4. The rename: move the `romm2steamdeck-app` settings folder on first run; keep existing Steam
   shortcuts working (they point at `RomM2SteamDeck.AppImage`, on the Deck `.appimage`); Windows
   installer app ID; rename the repos on Gitea and GitHub (both redirect old URLs).

## Files

- `knarr-refined-*` and `knarr-refined.py`: the chosen marks and their construction.
- `knarr-negative-*` and `knarr-negative.py`: the negative-space diagram.
- `explorations/`: everything tried on the way: other names (Lares, Ludoteca, Mnemophore, Umbra),
  Viking ships, pixel art, crates, merchant's-mark variations, the Material Design check.
