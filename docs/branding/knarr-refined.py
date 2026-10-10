#!/usr/bin/env python3
"""D and E refined with classic construction rules: one 45-degree angle for every diagonal,
a 10-unit grid, equal gaps, one stroke weight, and optical centring in the shield.
Writes knarr-refined-D.svg, knarr-refined-E.svg and knarr-refined-preview.svg."""
import math

INK, BONE, NAVY, GOLD, GUIDE, RED = '#1a1c2c', '#efe6d2', '#14243a', '#e2b64e', '#4a90d9', '#d9534f'
W_STROKE = 14

OLD_D = ['M100,22 V172', 'M100,36 L64,80 H130', 'M100,122 L138,88', 'M100,122 L138,156', 'M48,178 H146 L164,150']
# every diagonal at 45 deg, every point on the 10-unit grid, gaps bar->K tip and K tip->hull both 30
NEW_D = ['M100,15 V190', 'M100,30 L60,70 H130', 'M100,130 L130,100', 'M100,130 L130,160', 'M40,190 H150 L175,165']
SHIELD = 'M30,14 H170 V112 C170,160 136,190 100,206 C64,190 30,160 30,112 Z'

def strokes(paths, colour, w=W_STROKE):
    return ''.join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" stroke-linecap="butt" '
                   f'stroke-linejoin="miter" stroke-miterlimit="3"/>' for d in paths)

def old_E(colour):
    return (f'<path d="{SHIELD}" fill="none" stroke="{colour}" stroke-width="8"/>'
            f'<g transform="translate(24,26) scale(0.76)">{strokes(OLD_D, colour, 15)}</g>')

S = 0.66  # mark scale inside the shield; the shield's line matches the mark's line (14 * 0.62)
def new_E(colour):
    # optical centre: the shield's visual mass sits above its mid-height, so the mark's centre goes to y=104, not 110
    cx, cy = 107.5, 102.5                       # centre of the refined mark's bounding box
    tx, ty = 100 - cx * S, 104 - cy * S
    return (f'<path d="{SHIELD}" fill="none" stroke="{colour}" stroke-width="{W_STROKE * S:.1f}"/>'
            f'<g transform="translate({tx:.1f},{ty:.1f}) scale({S})">{strokes(NEW_D, colour)}</g>')

def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220" width="200" height="220">{body}</svg>'
open('knarr-refined-D.svg', 'w').write(svg(strokes(NEW_D, INK)))
open('knarr-refined-E.svg', 'w').write(svg(new_E(INK)))

def grid():
    g = ''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="220" stroke="{GUIDE}" stroke-opacity="0.18" stroke-width="1"/>' for x in range(0, 201, 10))
    g += ''.join(f'<line x1="0" y1="{y}" x2="200" y2="{y}" stroke="{GUIDE}" stroke-opacity="0.18" stroke-width="1"/>' for y in range(0, 221, 10))
    return g

def angle_guides(paths_pts):
    out = ''
    for (x1, y1, x2, y2) in paths_pts:
        a = abs(math.degrees(math.atan2(y2 - y1, x2 - x1))) % 180
        a = min(a, 180 - a)
        out += (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 3"/>'
                f'<text x="{(x1+x2)/2 + 8}" y="{(y1+y2)/2 - 4}" font-family="Noto Sans" font-size="13" font-weight="700" fill="{RED}">{a:.0f}°</text>')
    return out

OLD_DIAG = [(100, 36, 64, 80), (100, 122, 138, 88), (100, 122, 138, 156), (146, 178, 164, 150)]
NEW_DIAG = [(100, 30, 60, 70), (100, 130, 130, 100), (100, 130, 130, 160), (150, 190, 175, 165)]

def gap(x, y1, y2):
    return (f'<path d="M{x-5},{y1} h10 M{x},{y1} V{y2} M{x-5},{y2} h10" stroke="{GUIDE}" stroke-width="2"/>')

W, H = 1180, 820
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#f3f1ec"/>']
panels = [
    ('D · now', strokes(OLD_D, INK) + angle_guides(OLD_DIAG) + gap(150, 87, 115) + gap(150, 163, 171),
     'Three different angles; uneven gaps'),
    ('D · refined', grid() + strokes(NEW_D, INK) + angle_guides(NEW_DIAG) + gap(150, 77, 107) + gap(150, 167, 183),
     'One angle (45°), on a grid, equal gaps'),
    ('E · now', old_E(INK) + f'<line x1="0" y1="110" x2="200" y2="110" stroke="{RED}" stroke-dasharray="5 3" stroke-width="1.5"/>',
     'Shield line thinner than the mark'),
    ('E · refined', new_E(INK) + f'<line x1="0" y1="104" x2="200" y2="104" stroke="{GUIDE}" stroke-dasharray="5 3" stroke-width="1.5"/>'
     f'<line x1="0" y1="110" x2="200" y2="110" stroke="{RED}" stroke-dasharray="2 4" stroke-width="1.5"/>',
     'One line weight; optically centred'),
]
for i, (t, body, sub) in enumerate(panels):
    ox = 40 + i * 280
    p.append(f'<rect x="{ox}" y="30" width="250" height="270" rx="10" fill="{BONE}"/>')
    p.append(f'<g transform="translate({ox+25},55)">{body}</g>')
    p.append(f'<text x="{ox+125}" y="330" font-family="Noto Sans" font-size="20" font-weight="700" text-anchor="middle" fill="#222">{t}</text>')
    p.append(f'<text x="{ox+125}" y="354" font-family="Noto Sans" font-size="15" text-anchor="middle" fill="#555">{sub}</text>')

# clean refined versions, side by side with the old, as icons and with the wordmark
y0 = 400
p.append(f'<text x="40" y="{y0}" font-family="Noto Sans" font-size="18" font-weight="700" fill="#222">Before → after, as icons (150 and 40 px)</text>')
for j, (body, lab) in enumerate([(strokes(OLD_D, GOLD), 'D now'), (strokes(NEW_D, GOLD), 'D refined'),
                                 (old_E(GOLD), 'E now'), (new_E(GOLD), 'E refined')]):
    ox = 40 + j * 200
    p.append(f'<rect x="{ox}" y="{y0+20}" width="150" height="150" rx="34" fill="{NAVY}"/>')
    p.append(f'<g transform="translate({ox+22},{y0+32}) scale(0.53)">{body}</g>')
    p.append(f'<rect x="{ox+55}" y="{y0+184}" width="40" height="40" rx="9" fill="{NAVY}"/>')
    p.append(f'<g transform="translate({ox+59},{y0+186}) scale(0.16)">{body.replace(f"stroke-width=\"{W_STROKE}\"", "stroke-width=\"20\"")}</g>')
    p.append(f'<text x="{ox+75}" y="{y0+246}" font-family="Noto Sans" font-size="15" text-anchor="middle" fill="#555">{lab}</text>')
lx = 860
p.append(f'<rect x="{lx}" y="{y0+20}" width="280" height="150" rx="20" fill="{NAVY}"/>')
p.append(f'<g transform="translate({lx+14},{y0+33}) scale(0.5)">{strokes(NEW_D, GOLD)}</g>')
p.append(f'<text x="{lx+118}" y="{y0+110}" font-family="Noto Sans" font-size="38" font-weight="800" letter-spacing="5" fill="{BONE}">KNARR</text>')
p.append(f'<text x="40" y="{H-40}" font-family="Noto Sans" font-size="15" fill="#555">Red dashes: angles and the shield\'s geometric centre. Blue: grid, gaps, and the optical centre the refined mark sits on.</text>')
p.append('</svg>')
open('knarr-refined-preview.svg', 'w').write(''.join(p))
