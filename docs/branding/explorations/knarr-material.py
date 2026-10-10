#!/usr/bin/env python3
"""D (hull) and E (hull in shield) tried against Material Design 3:
product icons, adaptive-icon masks, themed (monochrome) icons, and a 24 px symbol in an app bar.
Writes knarr-material-preview.svg. Colours are hand-picked M3-style tonal roles, not generator output."""

HULL = ['M100,22 V172', 'M100,36 L64,80 H130', 'M100,122 L138,88', 'M100,122 L138,156', 'M48,178 H146 L164,150']
SHIELD = 'M30,14 H170 V112 C170,160 136,190 100,206 C64,190 30,160 30,112 Z'

# M3-style roles: navy primary, gold tertiary
DARK = dict(surface='#111318', on_surface='#e2e2e9', pc='#264777', on_pc='#d6e3ff', tc='#5a4300', on_tc='#ffdf9e')
LIGHT = dict(surface='#f9f9ff', on_surface='#191c20', pc='#d6e3ff', on_pc='#0b2b55', tc='#ffdf9e', on_tc='#261a00')

def strokes(paths, colour, w, style):
    cap, join = ('round', 'round') if style == 'rounded' else ('butt', 'miter')
    return ''.join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" stroke-linecap="{cap}" '
                   f'stroke-linejoin="{join}" stroke-miterlimit="3"/>' for d in paths)

def mark(kind, colour, style='sharp', w=14):
    """Mark in a 200x220 box."""
    if kind == 'D':
        return strokes(HULL, colour, w, style)
    sh = f'<path d="{SHIELD}" fill="none" stroke="{colour}" stroke-width="{w*0.62:.1f}" stroke-linejoin="{"round" if style == "rounded" else "miter"}"/>'
    return sh + f'<g transform="translate(24,26) scale(0.76)">{strokes(HULL, colour, w * 1.12, style)}</g>'

def masked(shape, size, x, y, bg, inner, cid):
    s = size
    clip = {'circle': f'<circle cx="{s/2}" cy="{s/2}" r="{s/2}"/>',
            'squircle': (f'<path d="M{s/2},0 C{s*0.92},0 {s},{s*0.08} {s},{s/2} C{s},{s*0.92} {s*0.92},{s} {s/2},{s} '
                         f'C{s*0.08},{s} 0,{s*0.92} 0,{s/2} C0,{s*0.08} {s*0.08},0 {s/2},0 Z"/>'),
            'rounded': f'<rect width="{s}" height="{s}" rx="{s*0.22}"/>'}[shape]
    return (f'<g transform="translate({x},{y})"><defs><clipPath id="{cid}">{clip}</clipPath></defs>'
            f'<g clip-path="url(#{cid})"><rect width="{s}" height="{s}" fill="{bg}"/>{inner}</g></g>')

def fit(kind, colour, size, style='sharp', w=14, frac=0.62):
    """Mark centred inside the adaptive-icon safe zone (66/108 of the icon)."""
    box = size * frac
    sc = box / 220
    ox, oy = (size - 200 * sc) / 2, (size - 220 * sc) / 2
    return f'<g transform="translate({ox:.1f},{oy:.1f}) scale({sc:.4f})">{mark(kind, colour, style, w)}</g>'

W, H = 1180, 1080
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#eceef4"/>']
def head(y, t, sub):
    p.append(f'<text x="40" y="{y}" font-family="Noto Sans" font-size="22" font-weight="700" fill="#191c20">{t}</text>')
    p.append(f'<text x="40" y="{y+24}" font-family="Noto Sans" font-size="15" fill="#555">{sub}</text>')

n = 0
def cid():
    global n; n += 1; return f'c{n}'

# Row 1 — product icons, sharp vs rounded, dark and light
head(40, 'Material 3 app icons', 'Squircle mask, primary-container background. Sharp (Material Symbols "Sharp") vs rounded ("Rounded") strokes.')
x = 40
for kind in ('D', 'E'):
    for style in ('sharp', 'rounded'):
        for pal in (DARK, LIGHT):
            p.append(masked('squircle', 120, x, 84, pal['pc'], fit(kind, pal['on_pc'], 120, style, 15, 0.66), cid()))
            x += 134
    x += 6
for i, t in enumerate(['D · sharp', 'D · rounded', 'E · sharp', 'E · rounded']):
    p.append(f'<text x="{40 + i*274 + 127}" y="228" font-family="Noto Sans" font-size="16" font-weight="700" text-anchor="middle" fill="#333">{t}</text>')

# Row 2 — adaptive masks with the 66/108 safe zone
head(280, 'Adaptive icon shapes', 'The launcher picks the mask. Dashed circle = the safe zone the mark must stay inside.')
x = 40
for kind in ('D', 'E'):
    for shape in ('circle', 'squircle', 'rounded'):
        inner = fit(kind, DARK['on_tc'], 140, 'sharp', 15, 0.6)
        p.append(masked(shape, 140, x, 324, DARK['tc'], inner, cid()))
        if shape == 'circle':
            p.append(f'<circle cx="{x+70}" cy="{324+70}" r="{70*66/108:.1f}" fill="none" stroke="#ffffff" stroke-opacity="0.6" stroke-width="1.5" stroke-dasharray="4 4"/>')
        x += 180
    x += 20

# Row 3 — themed (monochrome) icons, as Android tints them
head(520, 'Themed icons (Material You)', 'The launcher recolours a one-colour version of the icon to match the wallpaper. Light and dark.')
x = 40
for kind in ('D', 'E'):
    for bg, fg in (('#d8e2ff', '#001a41'), ('#ffdcc1', '#2e1500'), ('#c4eed0', '#00210f'), ('#1f2b45', '#b1c5ff'), ('#3d2b1c', '#ffb878')):
        p.append(masked('circle', 96, x, 564, bg, fit(kind, fg, 96, 'sharp', 17, 0.6), cid()))
        x += 108
    x += 30

# Row 4 — 24 px symbol in a Material top app bar, plus enlarged on a 24-unit grid
head(710, 'As a 24 px symbol', 'In a Material top app bar (dark and light), and D enlarged on a 24-unit grid with a 2-unit stroke.')
for i, pal in enumerate((DARK, LIGHT)):
    y = 754 + i * 84
    p.append(f'<rect x="40" y="{y}" width="640" height="64" rx="0" fill="{pal["surface"]}"/>')
    p.append(f'<path d="M64,{y+24} h18 M64,{y+32} h18 M64,{y+40} h18" stroke="{pal["on_surface"]}" stroke-width="2.5"/>')
    p.append(f'<g transform="translate(108,{y+20}) scale({24/220:.4f})">{mark("D", pal["on_surface"], "sharp", 20)}</g>')
    p.append(f'<text x="144" y="{y+40}" font-family="Noto Sans" font-size="22" fill="{pal["on_surface"]}">Knarr</text>')
    p.append(f'<circle cx="628" cy="{y+32}" r="5" fill="none" stroke="{pal["on_surface"]}" stroke-width="2.5"/><path d="M632,{y+36} l6,6" stroke="{pal["on_surface"]}" stroke-width="2.5"/>')
# enlarged 24-grid
gx, gy, u = 740, 754, 7
p.append(f'<rect x="{gx}" y="{gy}" width="{24*u}" height="{24*u}" fill="#ffffff"/>')
for i in range(25):
    p.append(f'<line x1="{gx+i*u}" y1="{gy}" x2="{gx+i*u}" y2="{gy+24*u}" stroke="#dde1ea" stroke-width="1"/>')
    p.append(f'<line x1="{gx}" y1="{gy+i*u}" x2="{gx+24*u}" y2="{gy+i*u}" stroke="#dde1ea" stroke-width="1"/>')
p.append(f'<rect x="{gx+2*u}" y="{gy+2*u}" width="{20*u}" height="{20*u}" fill="none" stroke="#f4a3a3" stroke-width="1"/>')
p.append(f'<g transform="translate({gx+2*u + (20*u - 200*20*u/220)/2:.1f},{gy+2*u}) scale({20*u/220:.4f})">{mark("D", "#191c20", "sharp", 22)}</g>')
p.append(f'<text x="{gx+24*u+16}" y="{gy+20}" font-family="Noto Sans" font-size="14" fill="#555">24-unit grid,</text>')
p.append(f'<text x="{gx+24*u+16}" y="{gy+38}" font-family="Noto Sans" font-size="14" fill="#555">red = 20-unit live area</text>')
p.append('</svg>')
open('knarr-material-preview.svg', 'w').write(''.join(p))
