#!/usr/bin/env python3
"""Knarr merchant's marks, built from the traditional parts: staff, sign of four,
crossbars, feet, and the owner's initial (K). Writes knarr-mark-<n>.svg and knarr-marks-preview.svg."""

MARKS = {
    # 1 — classic: sign of four at the top, K branching off the staff, split feet
    'classic': ['M100,28 V172', 'M100,28 L66,74 H124', 'M100,118 L136,86', 'M100,118 L136,150', 'M76,192 L100,166 L124,192'],
    # 2 — mast: a yard across the top like a ship's mast, K arms, and a hull whose bow rises to the right
    'mast': ['M100,24 V156', 'M64,50 H136', 'M100,104 L136,76', 'M100,104 L136,132', 'M52,158 H146 L162,134'],
    # 3 — play flag: the sign of four becomes a play triangle, with the K and feet below
    'play': ['M88,26 V172', 'M88,30 L136,54 L88,78', 'M88,124 L124,96', 'M88,124 L124,152', 'M64,192 L88,166 L112,192'],
    # 4 — play flag, minimal: no initial, just staff, play flag, crossbar and feet (best at small sizes)
    'minimal': ['M92,26 V172', 'M92,30 L140,56 L92,82', 'M64,128 H120', 'M68,192 L92,166 L116,192'],
}

def mark(paths, colour, width=13):
    return ''.join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
                   f'stroke-linecap="square" stroke-linejoin="miter"/>' for d in paths)

for k, paths in MARKS.items():
    open(f'knarr-mark-{k}.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220" width="200" height="220">{mark(paths, "#1a1c2c")}</svg>')

names = {'classic': '1 · Classic', 'mast': '2 · Mast', 'play': '3 · Play flag', 'minimal': '4 · Minimal'}
W = 40 + 250 * len(MARKS)
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="540" viewBox="0 0 {W} 540">',
     f'<rect width="{W}" height="540" fill="#f3f1ec"/>',
     '<defs><pattern id="wood" width="200" height="22" patternUnits="userSpaceOnUse">'
     '<rect width="200" height="22" fill="#a86b40"/><rect y="20" width="200" height="2" fill="#7a4a2b"/>'
     '<path d="M0,8 C50,5 90,12 200,7" stroke="#95603a" stroke-width="2" fill="none"/></pattern></defs>']
for i, (k, paths) in enumerate(MARKS.items()):
    ox = 40 + i * 250
    # ink on parchment
    p.append(f'<rect x="{ox}" y="20" width="210" height="230" rx="10" fill="#efe6d2"/>')
    p.append(f'<g transform="translate({ox+5},25)">{mark(paths, "#1a1c2c")}</g>')
    p.append(f'<text x="{ox+105}" y="280" font-family="Noto Sans" font-size="20" font-weight="700" text-anchor="middle" fill="#222">{names[k]}</text>')
    # branded onto a crate plank
    p.append(f'<rect x="{ox}" y="300" width="130" height="143" rx="6" fill="url(#wood)"/>')
    p.append(f'<g transform="translate({ox+15},307) scale(0.5)" opacity="0.85">{mark(paths, "#2b1a10", 15)}</g>')
    # small sizes
    p.append(f'<g transform="translate({ox+150},330) scale(0.22)">{mark(paths, "#1a1c2c", 16)}</g>')
    p.append(f'<g transform="translate({ox+150},392) scale(0.12)">{mark(paths, "#1a1c2c", 20)}</g>')
p.append(f'<text x="40" y="490" font-family="Noto Sans" font-size="16" fill="#555">Top: ink on parchment. Bottom: branded onto a crate plank, plus small sizes.</text>')
p.append('</svg>')
open('knarr-marks-preview.svg', 'w').write(''.join(p))
