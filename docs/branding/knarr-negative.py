#!/usr/bin/env python3
"""Highlight the negative spaces in the refined D mark. Writes knarr-negative-preview.svg."""
NEW_D = ['M100,15 V190', 'M100,30 L60,70 H130', 'M100,130 L130,100', 'M100,130 L130,160', 'M40,190 H150 L175,165']
INK, BONE = '#1a1c2c', '#efe6d2'

def strokes(colour, w=14):
    return ''.join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" stroke-linecap="butt" '
                   f'stroke-linejoin="miter" stroke-miterlimit="3"/>' for d in NEW_D)

SPACES = [  # (polygon, colour, label, label position)
    ('100,30 60,70 100,70', '#e2b64e', 'pennant', (24, 46)),
    ('100,70 130,70 130,100 100,130', '#4a90d9', 'sail', (140, 88)),
    ('100,130 130,100 130,160', '#b13e53', 'arrow', (140, 136)),
    ('100,130 130,160 160,190 100,190', '#38b764', 'hull', (112, 214)),
]
PARALLEL = [(100, 30, 60, 70), (100, 130, 130, 100), (150, 190, 175, 165)]

def panel(ox, body):
    return f'<g transform="translate({ox},40)"><rect x="-20" y="-20" width="260" height="280" rx="10" fill="{BONE}"/>{body}</g>'

W, H = 880, 400
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#f3f1ec"/>']
# 1 the mark
p.append(panel(40, strokes(INK)))
# 2 the negative spaces filled in
fills = ''.join(f'<polygon points="{pts}" fill="{c}" opacity="0.75"/>' for pts, c, _, _ in SPACES)
labels = ''.join(f'<text x="{x}" y="{y}" font-family="Noto Sans" font-size="15" font-weight="700" fill="{c}">{t}</text>'
                 for _, c, t, (x, y) in SPACES)
p.append(panel(330, fills + strokes(INK) + labels))
# 3 the parallel diagonals
par = ''.join(f'<line x1="{x1 - (x2-x1)*0.6}" y1="{y1 - (y2-y1)*0.6}" x2="{x2 + (x2-x1)*0.6}" y2="{y2 + (y2-y1)*0.6}" '
              f'stroke="#d9534f" stroke-width="2" stroke-dasharray="5 4"/>' for x1, y1, x2, y2 in PARALLEL)
p.append(panel(620, strokes(INK) + par))
for x, t in [(160, 'The mark'), (450, 'Its negative spaces'), (740, 'Three parallel diagonals')]:
    p.append(f'<text x="{x}" y="{H-50}" font-family="Noto Sans" font-size="19" font-weight="700" text-anchor="middle" fill="#222">{t}</text>')
p.append('</svg>')
open('knarr-negative-preview.svg', 'w').write(''.join(p))
