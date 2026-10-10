#!/usr/bin/env python3
"""Icon concepts for the rename. Writes one SVG per name plus preview.svg."""
import math

def bg(id_, c1, c2):
    return (f'<defs><linearGradient id="{id_}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'
            f'<clipPath id="{id_}-clip"><rect width="256" height="256" rx="56"/></clipPath></defs>'
            f'<rect width="256" height="256" rx="56" fill="url(#{id_})"/>')

def cart(x, y, w, h, fill, label='#ffffff', grips=True, label_box=True, connector=False):
    c = w * 0.22
    s = ''
    if connector:
        tx, tw, th = x + w * 0.12, w * 0.76, h * 0.13
        s += f'<rect x="{tx:.1f}" y="{y+h-4:.1f}" width="{tw:.1f}" height="{th+4:.1f}" rx="3" fill="{fill}" style="filter:brightness(0.8)"/>'
        s += f'<rect x="{tx:.1f}" y="{y+h-4:.1f}" width="{tw:.1f}" height="{th+4:.1f}" rx="3" fill="#000" opacity="0.18"/>'
        n = 6
        for i in range(n):
            cx = tx + tw * (i + 0.5) / n - 2.5
            s += f'<rect x="{cx:.1f}" y="{y+h+2:.1f}" width="5" height="{th-4:.1f}" rx="1.5" fill="#ffd166"/>'
    s += (f'<path d="M{x},{y} H{x+w-c} L{x+w},{y+c} V{y+h} H{x} Z" fill="{fill}" '
         f'stroke="{fill}" stroke-width="6" stroke-linejoin="round"/>')
    if label_box:
        s += (f'<rect x="{x+w*0.16:.1f}" y="{y+h*0.18:.1f}" width="{w*0.62:.1f}" height="{h*0.36:.1f}" '
              f'rx="4" fill="{label}" opacity="0.92"/>')
    if grips:
        for i in range(3):
            gy = y + h * 0.70 + i * 7
            s += (f'<line x1="{x+w*0.26:.1f}" y1="{gy:.1f}" x2="{x+w*0.74:.1f}" y2="{gy:.1f}" '
                  f'stroke="#000" stroke-opacity="0.22" stroke-width="3.5" stroke-linecap="round"/>')
    return s

def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">{body}</svg>'

icons = {}

# Ludoteca: a shelf of game cartridges, one leaning — a library of games
b = bg('lud', '#1d2340', '#2f3b75')
b += '<rect x="38" y="186" width="180" height="13" rx="4" fill="#d39a5b"/>'
b += '<rect x="38" y="196" width="180" height="5" rx="2" fill="#000" opacity="0.18"/>'
b += cart(50, 94, 36, 92, '#ef6351')
b += cart(92, 80, 36, 106, '#f4b942')
b += cart(134, 100, 36, 86, '#3fbfae')
b += f'<g transform="rotate(-9 188 186)">{cart(188, 92, 34, 94, "#8a96ff")}</g>'
icons['Ludoteca'] = svg(b)

# Lares: household gods — a cartridge as the house, a hearth flame as its label
b = bg('lar', '#3b1d2c', '#86402f')
b += '<polyline points="54,128 128,60 202,128" fill="none" stroke="#f7e8cb" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>'
b += cart(82, 112, 92, 86, '#f7e8cb', label_box=False, grips=False, connector=True)
b += ('<path d="M128,128 C141,143 152,153 148,168 C145,179 137,185 128,185 C119,185 110,179 108,168 '
      'C105,156 114,148 119,139 C121,147 125,150 128,153 C131,145 126,137 128,128 Z" fill="#ff7a3d"/>')
b += ('<path d="M128,152 C135,160 139,166 137,173 C135,179 131,181 128,181 C124,181 120,178 119,173 '
      'C118,167 123,163 125,158 C126,162 127,163 128,164 Z" fill="#ffd166"/>')
icons['Lares'] = svg(b)

# Mnemophore: "memory-bearer" — a ROM chip with wings
b = bg('mne', '#0d2433', '#146470')
wing = ('M176,112 C196,88 222,72 242,70 C240,84 232,94 220,100 C232,100 238,102 238,106 '
        'C230,116 218,120 206,121 C214,124 218,127 216,131 C206,139 192,141 178,138 Z')
b += f'<path d="{wing}" fill="#eef4f7"/>'
b += f'<path d="{wing}" fill="#eef4f7" transform="translate(256,0) scale(-1,1)"/>'
for i in range(5):
    px = 95 + i * 15
    b += f'<rect x="{px}" y="70" width="8" height="16" rx="2" fill="#ffd166"/>'
    b += f'<rect x="{px}" y="170" width="8" height="16" rx="2" fill="#ffd166"/>'
b += '<rect x="84" y="82" width="88" height="92" rx="10" fill="#161b21"/>'
b += '<path d="M118,82 a10,10 0 0 0 20,0 Z" fill="#0d2433"/>'
b += '<circle cx="100" cy="100" r="5" fill="#ffd166"/>'
b += '<rect x="100" y="128" width="56" height="6" rx="3" fill="#ffffff" opacity="0.18"/>'
b += '<rect x="100" y="142" width="38" height="6" rx="3" fill="#ffffff" opacity="0.18"/>'
icons['Mnemophore'] = svg(b)

# Umbra: shadow RAM — a cartridge casting a long shadow
b = bg('umb', '#140e22', '#2c1f52')
b = b.replace('</defs>', '<linearGradient id="umb-sh" x1="0" y1="0" x2="1" y2="1">'
              '<stop offset="0" stop-color="#000" stop-opacity="0.55"/>'
              '<stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
              '<radialGradient id="umb-glow" cx="0.2" cy="0.15" r="0.6">'
              '<stop offset="0" stop-color="#b9a6ff" stop-opacity="0.35"/>'
              '<stop offset="1" stop-color="#b9a6ff" stop-opacity="0"/></radialGradient></defs>')
b += '<rect width="256" height="256" rx="56" fill="url(#umb-glow)"/>'
x, y, w, h = 76, 56, 96, 108
c = w * 0.22
d = 220
b += (f'<g clip-path="url(#umb-clip)"><polygon points="{x+w-c},{y} {x+w},{y+c} {x+w+d},{y+c+d} '
      f'{x+w+d},{y+h+d} {x+w*0.88+d},{y+h*1.13+d} {x+w*0.12},{y+h*1.13} {x+w*0.12},{y+h}" fill="url(#umb-sh)"/></g>')
b += cart(x, y, w, h, '#ece7ff', label='#7b5cff', connector=True)
icons['Umbra'] = svg(b)

for name, s in icons.items():
    open(f'{name.lower()}.svg', 'w').write(s)

# Preview sheet: each icon large, then at 64 and 32 px to check it still reads small
W = 300 * len(icons) + 40
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="420" viewBox="0 0 {W} 420">',
     f'<rect width="{W}" height="420" fill="#f3f1ec"/>']
for i, (name, s) in enumerate(icons.items()):
    inner = s.split('>', 1)[1].rsplit('</svg>', 1)[0]
    ox = 40 + i * 300
    p.append(f'<g transform="translate({ox},30)">{inner}</g>')
    p.append(f'<text x="{ox+128}" y="320" font-family="Noto Sans" font-size="26" font-weight="700" text-anchor="middle" fill="#222">{name}</text>')
    p.append(f'<g transform="translate({ox+60},345) scale(0.25)">{inner}</g>')
    p.append(f'<g transform="translate({ox+140},361) scale(0.125)">{inner}</g>')
p.append('</svg>')
open('preview.svg', 'w').write(''.join(p))
