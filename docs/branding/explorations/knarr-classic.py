#!/usr/bin/env python3
"""Variations on the classic Knarr merchant's mark (staff, sign of four, K, base).
Writes knarr-classic-<name>.svg and knarr-classic-preview.svg."""

INK, BONE, NAVY, GOLD = '#1a1c2c', '#efe6d2', '#14243a', '#e2b64e'

STAFF = 'M100,22 V170'
FOUR = 'M100,36 L64,80 H130'
K = ['M100,122 L138,88', 'M100,122 L138,156']
FEET = 'M74,196 L100,168 L126,196'

V = {
    'classic':  [STAFF, FOUR, *K, FEET],
    'mirrored': [STAFF, 'M100,36 L136,80 H70', 'M100,122 L62,88', 'M100,122 L62,156', FEET],
    'footcross': ['M100,22 V196', FOUR, *K, 'M70,178 H130'],
    'waves':    ['M100,22 V176', FOUR, *K, 'M50,192 q12.5,-14 25,0 t25,0 t25,0 t25,0'],
    'hull':     ['M100,22 V172', FOUR, *K, 'M54,178 H140 L158,152'],
}
WIDTH = {}

def draw(paths, colour, w=13):
    return ''.join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" '
                   f'stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="3"/>' for d in paths)

def shield(colour):
    return (f'<path d="M30,14 H170 V112 C170,160 136,190 100,206 C64,190 30,160 30,112 Z" '
            f'fill="none" stroke="{colour}" stroke-width="8"/>')

def seal(colour):
    # ring with KNARR over the top and the tagline-free dots under the bottom
    return (f'<circle cx="100" cy="110" r="98" fill="none" stroke="{colour}" stroke-width="5"/>'
            f'<circle cx="100" cy="110" r="70" fill="none" stroke="{colour}" stroke-width="3"/>'
            + ''.join(
                f'<text transform="translate({100 + 80 * __import__("math").cos(__import__("math").radians(a)):.1f},'
                f'{110 + 80 * __import__("math").sin(__import__("math").radians(a)):.1f}) rotate({a + 90:.1f})" '
                f'font-family="Noto Sans" font-weight="800" font-size="21" text-anchor="middle" dominant-baseline="central" fill="{colour}">{ch}</text>'
                for ch, a in zip('KNARR', (-130, -110, -90, -70, -50)))
            + ''.join(f'<circle cx="{100 + 84 * __import__("math").cos(a):.1f}" cy="{110 + 84 * __import__("math").sin(a):.1f}" r="3.5" fill="{colour}"/>'
                      for a in [__import__("math").radians(d) for d in (45, 67.5, 90, 112.5, 135)]))

# 16x18 pixel version of the classic
PIX = ['.......X........',
       '......XX........',
       '.....X.X........',
       '....X..X........',
       '...X...X........',
       '..XXXXXXXXX.....',
       '.......X........',
       '.......X...X....',
       '.......X..X.....',
       '.......X.X......',
       '.......XX.......',
       '.......X.X......',
       '.......X..X.....',
       '.......X...X....',
       '.......X........',
       '......X.X.......',
       '.....X...X......',
       '....X.....X.....']
def pixel(colour, s=11, ox=12, oy=12):
    return ''.join(f'<rect x="{ox+c*s}" y="{oy+r*s}" width="{s}" height="{s}" fill="{colour}"/>'
                   for r, row in enumerate(PIX) for c, ch in enumerate(row) if ch == 'X')

def tile(content):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 200 220" width="200" height="220">{content}</svg>'

files = {k: draw(p, INK, WIDTH.get(k, 13)) for k, p in V.items()}
files['shield'] = shield(INK) + f'<g transform="translate(26,22) scale(0.74)">{draw(V["classic"], INK, 15)}</g>'
files['seal'] = seal(INK) + f'<g transform="translate(50,52) scale(0.5)">{draw(V["classic"], INK, 18)}</g>'
files['pixel'] = f'<g shape-rendering="crispEdges">{pixel(INK)}</g>'
for k, c in files.items():
    open(f'knarr-classic-{k}.svg', 'w').write(tile(c))

labels = {'classic': 'Classic', 'mirrored': 'Mirrored', 'footcross': 'Foot cross', 'waves': 'Wave base',
          'hull': 'Hull base', 'bold': 'Bold', 'shield': 'In a shield', 'seal': 'Seal', 'pixel': 'Pixel'}
cols, tw, th = 5, 230, 290
order = list(files)
rows = -(-len(order) // cols)
W, H = 40 + cols * tw, 40 + rows * th + 330
p = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#f3f1ec"/>']
for i, k in enumerate(order):
    ox, oy = 40 + (i % cols) * tw, 30 + (i // cols) * th
    p.append(f'<rect x="{ox}" y="{oy}" width="{tw-30}" height="{th-60}" rx="10" fill="{BONE}"/>')
    p.append(f'<g transform="translate({ox+5},{oy+5}) scale(0.95)">{files[k]}</g>')
    p.append(f'<text x="{ox+(tw-30)/2}" y="{oy+th-30}" font-family="Noto Sans" font-size="19" font-weight="700" text-anchor="middle" fill="#222">{i+1} · {labels[k]}</text>')

# bottom row: as app icons (gold on navy) and a horizontal logo
by = 40 + rows * th
for j, k in enumerate(['classic', 'waves', 'pixel']):
    ox = 40 + j * 180
    p.append(f'<rect x="{ox}" y="{by}" width="150" height="150" rx="34" fill="{NAVY}"/>')
    inner = files[k].replace(INK, GOLD)
    p.append(f'<g transform="translate({ox+22},{by+12}) scale(0.53)">{inner}</g>')
    p.append(f'<rect x="{ox+160-60}" y="{by+170}" width="40" height="40" rx="9" fill="{NAVY}"/>')
    p.append(f'<g transform="translate({ox+106},{by+173}) scale(0.155)">{files[k].replace(INK, GOLD).replace("stroke-width=\"13\"", "stroke-width=\"20\"")}</g>')
lx = 40 + 3 * 180 + 20
p.append(f'<rect x="{lx}" y="{by}" width="{W-lx-40}" height="150" rx="20" fill="{NAVY}"/>')
p.append(f'<g transform="translate({lx+24},{by+14}) scale(0.56)">{files["classic"].replace(INK, GOLD)}</g>')
p.append(f'<text x="{lx+150}" y="{by+92}" font-family="Noto Sans" font-size="64" font-weight="800" letter-spacing="14" fill="{BONE}">KNARR</text>')
p.append(f'<text x="{lx+153}" y="{by+124}" font-family="Noto Sans" font-size="19" fill="#7fb3d5">Your RomM library, ready to play</text>')
p.append(f'<text x="40" y="{H-36}" font-family="Noto Sans" font-size="16" fill="#555">Bottom: classic, wave base and pixel as app icons (150 px and 40 px), and a horizontal logo.</text>')
p.append('</svg>')
open('knarr-classic-preview.svg', 'w').write(''.join(p))
