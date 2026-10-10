#!/usr/bin/env python3
"""Four pixel-art directions for Knarr after the front-on ship read as a grin.
Writes knarr-p2-<name>.svg and knarr-p2-preview.svg."""

P = {'.': '#1a1c2c', '*': '#94b0c2', 'w': '#f4f4f4', 's': '#94b0c2', 'y': '#ffcd75', 'k': '#1a1c2c',
     'r': '#b13e53', 'm': '#5a3a28', 'l': '#c28a5a', 'h': '#8f563b', 'H': '#5a3a28',
     '1': '#29366f', '2': '#3b5dc9', '3': '#41a6f6', '4': '#73eff7',
     'g': '#566c86', 'G': '#333c57', 'q': '#94b0c2', 'o': '#ef7d57', 'O': '#a85a32', 't': '#257179', 'T': '#38b764'}
N = 32

def new(bg='.'):
    return [[bg] * N for _ in range(N)]
def put(g, r, c, ch):
    if 0 <= r < N and 0 <= c < N:
        g[r][c] = ch
def hl(g, r, c0, c1, ch):
    for c in range(c0, c1 + 1):
        put(g, r, c, ch)
def box(g, r0, r1, c0, c1, ch):
    for r in range(r0, r1 + 1):
        hl(g, r, c0, c1, ch)
def sprite(g, r0, c0, rows):
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != ' ':
                put(g, r0 + r, c0 + c, ch)
def sea(g, top, deep):
    for r in range(top, N):
        for c in range(N):
            if g[r][c] in '.*t':
                g[r][c] = '1' if r >= deep else '2'
    for c in range(N):
        if c % 8 in (0, 1, 2) and g[top][c] == '2':
            g[top][c] = '3'
        if (c + 4) % 8 in (0, 1, 2) and g[deep][c] == '1':
            g[deep][c] = '3'
def stars(g, pts):
    for r, c in pts:
        if g[r][c] == '.':
            g[r][c] = '*'
def label_play(g, r0, c0, h=7):
    for i in range(h):
        hl(g, r0 + i, c0, c0 + min(i, h - 1 - i), 'k')

out = {}

# 1 — the ship in profile, sailing right: one bow post, low stern, sail filled by the wind
g = new()
stars(g, [(2, 3), (1, 24), (5, 28), (9, 30), (11, 2)])
for r in range(2, 20):
    put(g, r, 12, 'm')
hl(g, 1, 13, 15, 'r'); hl(g, 2, 13, 14, 'r')
hl(g, 4, 5, 20, 'm')
for r in range(5, 18):
    c1 = {5: 18, 6: 19, 7: 20}.get(r, 21)
    if 9 <= r <= 13:
        c1 = 22                      # belly of the sail
    hl(g, r, 6, c1, 'w'); put(g, r, c1, 's')
box(g, 8, 14, 8, 18, 'y'); label_play(g, 8, 12)
sprite(g, 14, 25, ['   hh',
                   '  hh ',
                   '  hh ',
                   '  hh ',
                   ' hhh ',
                   'lll  '])
sprite(g, 17, 1, ['h ', 'hh'])
hl(g, 19, 2, 27, 'l'); put(g, 19, 2, 'h')
hl(g, 20, 3, 27, 'h')
hl(g, 21, 4, 26, 'H')
hl(g, 22, 6, 25, 'h')
sea(g, 23, 27)
hl(g, 23, 5, 25, '3'); sprite(g, 20, 28, ['4  ', ' 4 ', '44 4'])
sprite(g, 23, 0, ['44'])
out['profile'] = g

# 2 — just the sail: mast, pennant and a cartridge sail over the waves
g = new()
stars(g, [(3, 4), (2, 26), (8, 29), (13, 2), (6, 6)])
for r in range(2, 25):
    put(g, r, 15, 'm')
hl(g, 2, 16, 19, 'r'); hl(g, 3, 16, 18, 'r'); put(g, 4, 16, 'r')
hl(g, 6, 5, 26, 'm')
for r in range(7, 23):
    c1 = {7: 22, 8: 23, 9: 24}.get(r, 25)
    hl(g, r, 6, c1, 'w'); put(g, r, c1, 's')
box(g, 10, 18, 9, 22, 'y'); label_play(g, 10, 14, 9)
for c in (8, 10, 12, 19, 21, 23):
    put(g, 23, c, 'y')
sea(g, 25, 28)
out['sail'] = g

# 3 — cargo crate: an item box with the play mark stencilled on
g = new('t')
for r, c in [(3, 4), (2, 26), (27, 3), (28, 27), (14, 2)]:
    put(g, r, c, 'T')
box(g, 6, 25, 6, 25, 'h')
for r in (6, 11, 16, 21, 25):
    hl(g, r, 6, 25, 'H')
for r in (7, 12, 17, 22):
    hl(g, r, 7, 24, 'l')
for c in (6, 25):
    for r in range(6, 26):
        put(g, r, c, 'H')
for i in range(18):                     # diagonal brace
    put(g, 7 + i, 7 + i, 'O'); put(g, 7 + i, 8 + i, 'O')
for (r, c) in [(6, 6), (6, 24), (24, 6), (24, 24)]:   # iron corners
    box(g, r, r + 1, c, c + 1, 'g')
box(g, 10, 21, 10, 21, 'y'); box(g, 11, 20, 11, 20, 'H')
label_play(g, 12, 14, 8)
for r in range(12, 20):
    for c in range(14, 21):
        if g[r][c] == 'k':
            g[r][c] = 'y'
hl(g, 26, 7, 25, 'G')                   # shadow
out['crate'] = g

# 4 — a game cartridge whose label art is a little ship at sea
g = new('t')
for r, c in [(3, 3), (2, 27), (29, 2), (28, 28)]:
    put(g, r, c, 'T')
box(g, 3, 28, 6, 25, 'g')
for r, c1 in [(3, 22), (4, 23), (5, 24)]:
    hl(g, r, 23 if c1 == 22 else c1 + 1, 25, 't')      # notched corner
for r in range(3, 29):
    put(g, r, 25 if r > 5 else {3: 22, 4: 23, 5: 24}[r], 'G')
hl(g, 28, 6, 25, 'G')
box(g, 6, 18, 8, 23, '.')                # label window: night sea
box(g, 15, 18, 8, 23, '2'); hl(g, 15, 8, 23, '3')
hl(g, 17, 9, 11, '3'); hl(g, 17, 17, 19, '3')
put(g, 7, 10, '*'); put(g, 9, 21, '*')
sprite(g, 6, 11, ['  rr      ',
                  '  m       ',
                  'wwwww     ',
                  'wwwwww    ',
                  'wwwwww    ',
                  'wwwww    h',
                  '  m     hh',
                  'llllllllh ',
                  ' hhhhhhh  '])
for r in (21, 23, 25):                   # grip ridges
    hl(g, r, 11, 20, 'G')
for c in range(8, 24, 3):                # contacts peeking out
    put(g, 29, c, 'y'); put(g, 30, c, 'y')
out['cartridge'] = g

R = 6
def inside(r, c):
    rr = R - r if r < R else (r - (N - 1 - R) if r > N - 1 - R else 0)
    cc = R - c if c < R else (c - (N - 1 - R) if c > N - 1 - R else 0)
    return rr * rr + cc * cc <= R * R + 2
def rects(g, s, ox=0, oy=0):
    return ''.join(f'<rect x="{ox+c*s}" y="{oy+r*s}" width="{s}" height="{s}" fill="{P[g[r][c]]}"/>'
                   for r in range(N) for c in range(N) if inside(r, c))

for k, g in out.items():
    open(f'knarr-p2-{k}.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" shape-rendering="crispEdges">{rects(g, 8)}</svg>')

names = {'profile': '1 · Ship in profile', 'sail': '2 · Sail', 'crate': '3 · Cargo crate', 'cartridge': '4 · Cartridge'}
pv = ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="380" viewBox="0 0 1120 380" shape-rendering="crispEdges">',
      '<rect width="1120" height="380" fill="#f3f1ec"/>']
for i, (k, g) in enumerate(out.items()):
    ox = 24 + i * 274
    pv.append(rects(g, 8, ox, 20))
    pv.append(f'<text x="{ox+128}" y="306" font-family="Noto Sans" font-size="20" font-weight="700" text-anchor="middle" fill="#222" shape-rendering="auto">{names[k]}</text>')
    pv.append(rects(g, 2, ox + 64, 318)); pv.append(rects(g, 1, ox + 150, 334))
pv.append('</svg>')
open('knarr-p2-preview.svg', 'w').write(''.join(pv))
