#!/usr/bin/env python3
"""Knarr crate concepts: a 3/4-view cargo crate with a play mark, at sea.
Writes knarr-crate-<name>.svg and knarr-crate-preview.svg."""

P = {'.': '#1a1c2c', '*': '#94b0c2', 'w': '#f4f4f4', 's': '#94b0c2', 'y': '#ffcd75', 'r': '#b13e53',
     'm': '#3d2618', 'l': '#c28a5a', 'h': '#8f563b', 'H': '#6b3f2a', 'D': '#4e2d1d',
     '1': '#29366f', '2': '#3b5dc9', '3': '#41a6f6', '4': '#73eff7', 'g': '#94b0c2', 'G': '#566c86'}
N = 32

def new():
    return [['.'] * N for _ in range(N)]
def put(g, r, c, ch):
    if 0 <= r < N and 0 <= c < N:
        g[r][c] = ch
def hl(g, r, c0, c1, ch):
    for c in range(c0, c1 + 1):
        put(g, r, c, ch)

def crate(g, top, left, size=15, d=5):
    """Oblique crate: front face size x size at (top, left), top and right faces d px deep."""
    bot, right = top + size - 1, left + size - 1
    for i in range(1, d + 1):                    # top face (lighter)
        hl(g, top - i, left + i, right + i, 'l')
        put(g, top - i, left + i, 'm'); put(g, top - i, right + i, 'm')
    hl(g, top - d, left + d, right + d, 'm')
    for i in range(1, d + 1):                    # right face (darker)
        for r in range(top - i, bot - i + 1):
            put(g, r, right + i, 'D')
        put(g, bot - i, right + i, 'm')
    for r in range(top - d, bot - d + 1):
        put(g, r, right + d, 'm')
    for r in range(top, bot + 1):                # front face: planks
        hl(g, r, left, right, 'h')
    for r in range(top + 3, bot, 4):
        hl(g, r, left, right, 'H')
    for r in range(top, bot + 1):
        put(g, r, left, 'm'); put(g, r, right, 'm')
    hl(g, top, left, right, 'm'); hl(g, bot, left, right, 'm')
    for (r, c) in [(top, left), (top, right), (bot, left), (bot, right)]:   # iron corners
        put(g, r, c, 'G')
    put(g, top + 1, left + 1, 'g'); put(g, top + 1, right - 1, 'g')
    put(g, bot - 1, left + 1, 'g'); put(g, bot - 1, right - 1, 'g')
    # play mark: gold panel, dark inset, gold triangle
    pr0, pc0, ps = top + 3, left + 3, size - 6
    for r in range(pr0, pr0 + ps):
        hl(g, r, pc0, pc0 + ps - 1, 'y')
    for r in range(pr0 + 1, pr0 + ps - 1):
        hl(g, r, pc0 + 1, pc0 + ps - 2, 'D')
    th = ps - 4 if (ps - 4) % 2 else ps - 5
    tr0 = pr0 + (ps - th) // 2
    for i in range(th):
        hl(g, tr0 + i, pc0 + 3, pc0 + 3 + min(i, th - 1 - i), 'y')
    return top - d, right + d

def sea(g, top):
    for r in range(top, N):
        for c in range(N):
            if g[r][c] in '.*' or r > top:     # below the waterline the crate is submerged
                g[r][c] = '1' if r > top + 3 else '2'
    for c in range(N):
        if c % 8 in (0, 1, 2) and g[top][c] == '2':
            g[top][c] = '3'
        if (c + 4) % 8 in (0, 1, 2) and top + 5 < N and g[top + 5][c] == '1':
            g[top + 5][c] = '3'

def stars(g, pts):
    for r, c in pts:
        if g[r][c] == '.':
            g[r][c] = '*'

out = {}

# A — adrift: the crate bobbing in the waves, sea washing against it
g = new()
stars(g, [(3, 4), (2, 25), (6, 29), (11, 2), (8, 9)])
crate(g, 10, 6)
sea(g, 22)
hl(g, 22, 5, 26, '3')
for (r, c) in [(21, 4), (21, 27), (22, 3), (22, 28), (20, 26)]:
    put(g, r, c, '4')
out['adrift'] = g

# B — crate raft: the crate IS the ship, a mast and square sail rising from its lid
g = new()
stars(g, [(2, 3), (4, 28), (9, 2), (1, 14)])
crate(g, 13, 4)
for r in range(1, 11):
    put(g, r, 16, 'm')
hl(g, 1, 17, 19, 'r'); hl(g, 2, 17, 18, 'r')
hl(g, 3, 9, 26, 'm')
for r in range(4, 10):
    hl(g, r, 10, 25 if 5 <= r <= 8 else 24, 'w'); put(g, r, 25 if 5 <= r <= 8 else 24, 's')
for r in range(4, 10):
    for c in (13, 19):
        put(g, r, c, 'r')                     # striped sail, the one nod to the classic look
sea(g, 25)
hl(g, 25, 3, 25, '3')
for (r, c) in [(24, 2), (24, 26), (25, 1), (25, 27), (23, 27)]:
    put(g, r, c, '4')
out['raft'] = g

# C — pennant: the crate at sea with just the knarr's red pennant flying from its corner
g = new()
stars(g, [(3, 4), (2, 22), (7, 29), (12, 2), (9, 11)])
crate(g, 11, 5)
for r in range(1, 7):
    put(g, r, 25, 'm')
hl(g, 1, 26, 29, 'r'); hl(g, 2, 26, 28, 'r'); put(g, 3, 26, 'r')
sea(g, 23)
hl(g, 23, 4, 25, '3')
for (r, c) in [(22, 3), (22, 26), (23, 2), (23, 27), (21, 25)]:
    put(g, r, c, '4')
out['pennant'] = g

R = 6
def inside(r, c):
    rr = R - r if r < R else (r - (N - 1 - R) if r > N - 1 - R else 0)
    cc = R - c if c < R else (c - (N - 1 - R) if c > N - 1 - R else 0)
    return rr * rr + cc * cc <= R * R + 2
def rects(g, s, ox=0, oy=0):
    return ''.join(f'<rect x="{ox+c*s}" y="{oy+r*s}" width="{s}" height="{s}" fill="{P[g[r][c]]}"/>'
                   for r in range(N) for c in range(N) if inside(r, c))

for k, g in out.items():
    open(f'knarr-crate-{k}.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" shape-rendering="crispEdges">{rects(g, 8)}</svg>')
names = {'adrift': 'A · Adrift', 'raft': 'B · Crate raft', 'pennant': 'C · Pennant'}
pv = ['<svg xmlns="http://www.w3.org/2000/svg" width="860" height="380" viewBox="0 0 860 380" shape-rendering="crispEdges">',
      '<rect width="860" height="380" fill="#f3f1ec"/>']
for i, (k, g) in enumerate(out.items()):
    ox = 24 + i * 280
    pv.append(rects(g, 8, ox, 20))
    pv.append(f'<text x="{ox+128}" y="306" font-family="Noto Sans" font-size="20" font-weight="700" text-anchor="middle" fill="#222" shape-rendering="auto">{names[k]}</text>')
    pv.append(rects(g, 2, ox + 64, 318)); pv.append(rects(g, 1, ox + 150, 334))
pv.append('</svg>')
open('knarr-crate-preview.svg', 'w').write(''.join(pv))
