#!/usr/bin/env python3
"""Pixel-art Knarr: a 32x32 ship whose sail is a game cartridge.
Writes knarr-pixel.svg (icon), knarr-pixel-wordmark.svg and knarr-pixel-preview.svg.
Colours are mostly the Sweetie 16 palette (GrafxKid) plus three hull browns."""

P = {
    '.': '#1a1c2c',  # night sky
    '*': '#94b0c2',  # star
    'w': '#f4f4f4',  # sail
    's': '#94b0c2',  # sail shade
    'y': '#ffcd75',  # label / contacts
    'k': '#1a1c2c',  # play triangle
    'r': '#b13e53',  # pennant
    'm': '#5a3a28',  # mast, yard
    'l': '#c28a5a',  # hull highlight
    'h': '#8f563b',  # hull
    'H': '#5a3a28',  # hull dark
    '1': '#29366f',  # deep sea
    '2': '#3b5dc9',  # sea
    '3': '#41a6f6',  # wave
    '4': '#73eff7',  # foam
}
N = 32
g = [['.'] * N for _ in range(N)]

def put(r, c, ch):
    if 0 <= r < N and 0 <= c < N:
        g[r][c] = ch

def hline(r, c0, c1, ch):
    for c in range(c0, c1 + 1):
        put(r, c, ch)

# stars
for r, c in [(2, 4), (1, 25), (6, 28), (9, 2), (11, 27), (4, 12)]:
    put(r, c, '*')
# mast, pennant, yard
for r in range(1, 19):
    put(r, 15, 'm')
hline(1, 16, 18, 'r'); hline(2, 16, 17, 'r')
hline(4, 7, 24, 'm')
# sail = cartridge: notched top-right corner, shaded right edge
for r, (c0, c1) in {5: (8, 20), 6: (8, 21), 7: (8, 22)}.items():
    hline(r, c0, c1, 'w')
for r in range(8, 17):
    hline(r, 8, 23, 'w')
for r in range(7, 17):
    put(r, 23 if r > 7 else 22, 's')
put(6, 21, 's'); put(5, 20, 's')
# label with a play triangle
for r in range(8, 15):
    hline(r, 10, 20, 'y')
for i, (c0, c1) in enumerate([(14, 14), (14, 15), (14, 16), (14, 17), (14, 16), (14, 15), (14, 14)]):
    hline(8 + i, c0, c1, 'k')
# gold contacts under the sail
for c in (9, 11, 13, 18, 20, 22):
    put(17, c, 'y')
# hull: a crescent whose stem and stern rise and curl inward (left half, mirrored)
HULL = {
    10: '...hh...........',
    11: '..h..h..........',
    12: '..h.............',
    13: '..hl............',
    14: '..hh............',
    15: '..hhl...........',
    16: '...hhl..........',
    17: '...hhhl.........',
    18: '....hhhll.......',
    19: '....hhhhllllllll',
    20: '.....hhhhhhhhhhh',
    21: '......HHHHHHHHHH',
    22: '.......hhhhhhhhh',
    23: '.........hhhhhhh',
}
for r, row in HULL.items():
    for c, ch in enumerate(row):
        if ch != '.':
            put(r, c, ch); put(r, N - 1 - c, ch)
# sea: everything below the waterline that isn't hull
for r in range(24, N):
    for c in range(N):
        if g[r][c] in '.*':
            g[r][c] = '1' if r > 27 else '2'
for c in range(N):
    if c % 8 in (0, 1, 2):
        put(24, c, '3') if g[24][c] == '2' else None
    if c % 8 in (1,):
        put(23, c, '4') if g[23][c] in '.*' else None
    if (c + 4) % 8 in (0, 1, 2):
        put(28, c, '3')
    if (c + 4) % 8 == 1:
        put(27, c, '2')
hline(24, 8, 23, '3')     # wake along the hull
put(24, 7, '4'); put(24, 24, '4')

# pixel-rounded icon corners (radius 6 px): drop pixels outside the curve
R = 6
def inside(r, c):
    for (cr, cc) in [(R, R), (R, N - 1 - R), (N - 1 - R, R), (N - 1 - R, N - 1 - R)]:
        if (r < R and c < R and (r, c) < (R, R) and cr == R and cc == R) or False:
            pass
    rr = R - r if r < R else (r - (N - 1 - R) if r > N - 1 - R else 0)
    cc = R - c if c < R else (c - (N - 1 - R) if c > N - 1 - R else 0)
    return rr * rr + cc * cc <= R * R + 2

def rects(scale, ox=0, oy=0):
    out = []
    for r in range(N):
        for c in range(N):
            if inside(r, c):
                out.append(f'<rect x="{ox + c*scale}" y="{oy + r*scale}" width="{scale}" height="{scale}" fill="{P[g[r][c]]}"/>')
    return ''.join(out)

open('knarr-pixel.svg', 'w').write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" shape-rendering="crispEdges">{rects(8)}</svg>')

# 5x7 pixel font for the wordmark
FONT = {
    'K': ['X...X', 'X..X.', 'X.X..', 'XX...', 'X.X..', 'X..X.', 'X...X'],
    'N': ['X...X', 'XX..X', 'X.X.X', 'X..XX', 'X...X', 'X...X', 'X...X'],
    'A': ['.XXX.', 'X...X', 'X...X', 'XXXXX', 'X...X', 'X...X', 'X...X'],
    'R': ['XXXX.', 'X...X', 'X...X', 'XXXX.', 'X.X..', 'X..X.', 'X...X'],
}
def word(text, px, ox, oy, fill, shadow=None):
    cells = [(ox + (i * 7 + c) * px, oy + r * px)
             for i, ch in enumerate(text) for r, row in enumerate(FONT[ch]) for c, bit in enumerate(row) if bit == 'X']
    out = [f'<rect x="{x+px}" y="{y+px}" width="{px}" height="{px}" fill="{shadow}"/>' for x, y in cells] if shadow else []
    out += [f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{fill}"/>' for x, y in cells]
    return ''.join(out)

wm = (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="150" viewBox="0 0 900 150" shape-rendering="crispEdges">'
      f'<rect width="900" height="150" fill="#1a1c2c"/>{rects(4, 20, 11)}'
      f'{word("KNARR", 10, 175, 25, "#ffcd75", "#5d275d")}'
      f'<text x="177" y="128" font-family="monospace" font-size="20" font-weight="700" fill="#73eff7" shape-rendering="auto">YOUR ROMM LIBRARY, READY TO PLAY</text></svg>')
open('knarr-pixel-wordmark.svg', 'w').write(wm)

pv = ['<svg xmlns="http://www.w3.org/2000/svg" width="980" height="500" viewBox="0 0 980 500" shape-rendering="crispEdges">',
      '<rect width="980" height="500" fill="#f3f1ec"/>',
      rects(8, 40, 30), rects(4, 330, 30), rects(2, 480, 30), rects(1, 550, 30),
      f'<g transform="translate(330,170)">{rects(3)}</g>',
      '<text x="330" y="290" font-family="Noto Sans" font-size="16" fill="#555" shape-rendering="auto">256 · 128 · 64 · 32 px, and 96 px</text>',
      f'<g transform="translate(40,320)">{wm.split(">", 1)[1].rsplit("</svg>", 1)[0]}</g>', '</svg>']
open('knarr-pixel-preview.svg', 'w').write(''.join(pv))
