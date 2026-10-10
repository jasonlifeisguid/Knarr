#!/usr/bin/env python3
"""Steam library artwork and the README banner, in the decided style: the refined mark in gold and
'Knarr' (outlines, from wordmark/knarr-wordmark.json) in bone, flat with a soft drop shadow, on navy.
Writes steam/*.svg + *.png and knarr-banner.svg/.png. Needs rsvg-convert."""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'steam')
os.makedirs(OUT, exist_ok=True)

GOLD, BONE, FOAM = '#e2b64e', '#efe6d2', '#7fb3d5'
NAVY_TOP, NAVY_BOT = '#1c3150', '#0e1a2b'
NEW_D = ['M100,15 V190', 'M100,30 L60,70 H130', 'M100,130 L130,100', 'M100,130 L130,160', 'M40,190 H150 L175,165']
MX0, MY0, MW, MH = 40, 15, 140, 182          # the mark's visual box inside its 200x220 drawing
WM = json.load(open(os.path.join(HERE, 'wordmark', 'knarr-wordmark.json')))

def mark(x, y, h, colour=GOLD):
    s = h / MH
    paths = ''.join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="14" stroke-linecap="butt" '
                    f'stroke-linejoin="miter" stroke-miterlimit="3"/>' for d in NEW_D)
    return f'<g transform="translate({x - MX0 * s:.2f},{y - MY0 * s:.2f}) scale({s:.4f})">{paths}</g>', MW * s

def word(x, baseline, cap, colour=BONE, k_colour=GOLD):
    """'Knarr' as outlines; the K in the mark's gold ties the name to the K in the mark."""
    s = cap / WM['capHeight']
    t = f'transform="translate({x:.2f},{baseline:.2f}) scale({s:.5f})"'
    return (f'<path {t} d="{WM["d_k"]}" fill="{k_colour}"/><path {t} d="{WM["d_rest"]}" fill="{colour}"/>',
            WM['width'] * s)

def lockup_h(cx, cy, h):
    """Mark with the name to its right, centred on (cx, cy); h = mark height."""
    cap, gap = h * 0.5, h * 0.26
    mw, ww = MW * h / MH, WM['width'] * cap / WM['capHeight']
    x0 = cx - (mw + gap + ww) / 2
    m, _ = mark(x0, cy - h / 2, h)
    w, _ = word(x0 + mw + gap, cy + cap / 2, cap)
    return m + w, (x0, x0 + mw + gap + ww)

def lockup_v(cx, top, h):
    """Mark above the name, centred on cx; returns (svg, bottom y)."""
    cap = h * 0.36
    m, mw = mark(cx - MW * h / MH / 2, top, h)
    ww = WM['width'] * cap / WM['capHeight']
    w, _ = word(cx - ww / 2, top + h + h * 0.18 + cap, cap)
    return m + w, top + h + h * 0.18 + cap

def drop(fid, k):
    """Soft drop shadow scaled to the artwork (k = 1 for a ~200 px mark)."""
    return (f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur in="SourceAlpha" stdDeviation="{4*k:.1f}"/>'
            f'<feOffset dx="{5*k:.1f}" dy="{7*k:.1f}"/><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.55 0"/>'
            f'<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>')

def background(w, h):
    return (f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{NAVY_TOP}"/>'
            f'<stop offset="1" stop-color="{NAVY_BOT}"/></linearGradient></defs><rect width="{w}" height="{h}" fill="url(#bg)"/>')

def tagline(cx, y, size, anchor='middle'):
    return (f'<text x="{cx:.1f}" y="{y:.1f}" font-family="Noto Sans" font-size="{size}" fill="{FOAM}" '
            f'text-anchor="{anchor}" letter-spacing="{size*0.04:.1f}">Your RomM library, ready to play</text>')

def svg(w, h, body, defs=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>'

def save(name, w, h, body, defs='', png_w=None):
    path = os.path.join(OUT if not name.startswith('../') else HERE, name.replace('../', '') + '.svg')
    open(path, 'w').write(svg(w, h, body, defs))
    subprocess.run(['rsvg-convert', '-w', str(png_w or w), path, '-o', path[:-4] + '.png'], check=True)

# Portrait library capsule, 600x900: the mark large, the name under it, the tagline low
k = 1.6
body, bottom = lockup_v(300, 250, 300)
save('knarr-capsule-600x900', 600, 900, background(600, 900) + f'<g filter="url(#d)">{body}</g>' + tagline(300, 800, 26), drop('d', k))

# Wide capsule, 920x430: the horizontal lockup
body, _ = lockup_h(460, 200, 200)
save('knarr-wide-920x430', 920, 430, background(920, 430) + f'<g filter="url(#d)">{body}</g>' + tagline(460, 365, 24), drop('d', 1.1))

# Hero, 1920x620 (Steam lays the logo over it, bottom left): calm sea-night, a faint large mark on the right
hero_mark, _ = mark(1380, 60, 520, '#ffffff')
waves = ''.join(f'<path d="M0,{y} ' + ' '.join(f'q60,-{a} 120,0 t120,0' for _ in range(1)) + ''.join(' t120,0' for _ in range(16)) +
                f'" fill="none" stroke="{FOAM}" stroke-opacity="{o}" stroke-width="3"/>'
                for y, a, o in [(520, 10, 0.10), (560, 12, 0.07), (600, 14, 0.05)])
save('knarr-hero-1920x620', 1920, 620, background(1920, 620) + f'<g opacity="0.07">{hero_mark}</g>' + waves, png_w=3840)

# Logo, transparent: the horizontal lockup, for Steam to place over the hero
body, _ = lockup_h(640, 180, 260)
save('knarr-logo', 1280, 360, f'<g filter="url(#d)">{body}</g>', drop('d', 1.3))

# README banner, 1280x320
body, (x0, x1) = lockup_h(560, 140, 170)
save('../knarr-banner', 1280, 320, background(1280, 320) + f'<g filter="url(#d)">{body}</g>' + tagline(x0 + (x1 - x0) / 2, 270, 26), drop('d', 0.9))
print('ok')
