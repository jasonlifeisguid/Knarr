#!/usr/bin/env python3
"""The refined D mark with depth: blind emboss, engraved, V-cut chiselled, branded, brass, drop shadow.
Writes knarr-depth-preview.svg. Light comes from the top left throughout."""
import math

NEW_D = [[(100, 15), (100, 190)], [(100, 30), (60, 70), (130, 70)], [(100, 130), (130, 100)],
         [(100, 130), (130, 160)], [(40, 190), (150, 190), (175, 165)]]
W = 14

def path_d(pts):
    return 'M' + ' L'.join(f'{x},{y}' for x, y in pts)

def mark(fill, extra=''):
    return ''.join(f'<path d="{path_d(p)}" fill="none" stroke="{fill}" stroke-width="{W}" stroke-linecap="butt" '
                   f'stroke-linejoin="miter" stroke-miterlimit="3" {extra}/>' for p in NEW_D)

def shading_filter(fid, invert=False, k=2.2, blur=3.2, scale=3):
    """Edge shading from the mark's own outline: white where a slope faces the light, black where it
    faces away, transparent on flat areas. invert=True lights it as a hollow (engraved) instead of a bump."""
    az = 45 if invert else 225
    flat = 0.766  # sin(50 deg): brightness of a flat surface under this light
    return (f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{blur}" result="bump"/>'
            f'<feDiffuseLighting in="bump" surfaceScale="{scale}" diffuseConstant="1" lighting-color="#fff" result="L">'
            f'<feDistantLight azimuth="{az}" elevation="50"/></feDiffuseLighting>'
            f'<feColorMatrix in="L" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  {k} 0 0 0 {-flat*k}" result="hi"/>'
            f'<feColorMatrix in="L" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  {-k} 0 0 0 {flat*k}" result="lo"/>'
            f'<feMerge><feMergeNode in="lo"/><feMergeNode in="hi"/></feMerge></filter>')

def texture(fid, base, freq, octaves, opacity, stretch=1):
    return (f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq} {freq*stretch}" numOctaves="{octaves}" seed="4" result="n"/>'
            f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {opacity} 0" result="a"/>'
            f'<feFlood flood-color="{base}"/><feComposite in2="a" operator="over"/></filter>')

def vcut(light='#d9d4ca', dark='#45413b', w=W):
    """Chiselled V-groove: each stroke split along its centre into two facets; the facet that faces
    the light (top left) is pale, the other is in shadow, shaded by how directly it faces."""
    L = (-1 / math.sqrt(2), -1 / math.sqrt(2))
    out = ''
    for pts in NEW_D:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            dx, dy = x2 - x1, y2 - y1
            ln = math.hypot(dx, dy)
            nx, ny = -dy / ln, dx / ln
            # extend each segment by half a stroke so facets meet at the joins
            ex, ey = dx / ln * w / 2, dy / ln * w / 2
            a, b = (x1 - ex, y1 - ey), (x2 + ex, y2 + ey)
            for sgn in (1, -1):
                # this facet slopes down towards the centre line: its surface normal points to -sgn*n
                dot = (-sgn * nx) * L[0] + (-sgn * ny) * L[1]
                t = (dot + 1) / 2
                col = mix(dark, light, t)
                ox, oy = sgn * nx * w / 2, sgn * ny * w / 2
                out += (f'<polygon points="{a[0]},{a[1]} {b[0]},{b[1]} {b[0]+ox},{b[1]+oy} {a[0]+ox},{a[1]+oy}" '
                        f'fill="{col}"/>')
    return out

def mix(c1, c2, t):
    a = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(a, b))

defs = (shading_filter('raise') + shading_filter('sink', invert=True) + shading_filter('raise-brass', k=1.5, blur=1.4, scale=2.5)
        + texture('paper', '#efe6d2', 0.9, 2, 0.06) + texture('stone', '#9a958c', 0.5, 4, 0.22)
        + texture('wood', '#b07a4a', 0.012, 3, 0.28, stretch=14)
        + '<filter id="char" x="-20%" y="-20%" width="140%" height="140%"><feMorphology in="SourceAlpha" operator="dilate" radius="2.5"/>'
          '<feGaussianBlur stdDeviation="3.5"/><feColorMatrix type="matrix" values="0 0 0 0 0.24  0 0 0 0 0.12  0 0 0 0 0.05  0 0 0 0.75 0"/></filter>'
        + '<filter id="drop" x="-30%" y="-30%" width="170%" height="170%"><feGaussianBlur in="SourceAlpha" stdDeviation="5"/>'
          '<feOffset dx="7" dy="9"/><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.55 0"/>'
          '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        + '<linearGradient id="brass" gradientUnits="userSpaceOnUse" x1="40" y1="15" x2="175" y2="195"><stop offset="0" stop-color="#f6d98a"/>'
          '<stop offset="0.45" stop-color="#d4a640"/><stop offset="0.7" stop-color="#a57a22"/><stop offset="1" stop-color="#e9c46a"/></linearGradient>')

PW, PH = 320, 330
panels = [
    ('Blind emboss', 'Raised from paper', 'url(#paper)',
     mark('#efe6d2') + f'<g filter="url(#raise)">{mark("#efe6d2")}</g>'),
    ('Engraved', 'Cut into stone', 'url(#stone)',
     mark('#6f6a62') + f'<g filter="url(#sink)">{mark("#000")}</g>'),
    ('Chiselled (V-cut)', 'Like a stone inscription', 'url(#stone)',
     f'<g filter="url(#sink)" opacity="0.7">{mark("#000")}</g>' + vcut()),
    ('Branded', 'Burned into wood', 'url(#wood)',
     f'<g filter="url(#char)">{mark("#000")}</g>' + mark('#2a160b') + f'<g filter="url(#sink)" opacity="0.6">{mark("#000")}</g>'),
    ('Struck brass', 'A raised metal badge', '#14243a',
     f'<g filter="url(#drop)">{mark("url(#brass)")}</g>' + f'<g filter="url(#raise-brass)">{mark("#000")}</g>'),
    ('Drop shadow', 'Flat gold, lifted off the page', '#14243a',
     f'<g filter="url(#drop)">{mark("#e2b64e")}</g>'),
]
cols = 3
TW, TH = 40 + cols * (PW + 30), 40 + 2 * (PH + 80)
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{TW}" height="{TH}" viewBox="0 0 {TW} {TH}"><defs>{defs}</defs>',
     f'<rect width="{TW}" height="{TH}" fill="#f3f1ec"/>']
for i, (title, sub, bg, body) in enumerate(panels):
    ox, oy = 40 + (i % cols) * (PW + 30), 30 + (i // cols) * (PH + 80)
    fill = f'fill="{bg}"' if bg.startswith('#') else ''
    if bg.startswith('url'):
        p.append(f'<rect x="{ox}" y="{oy}" width="{PW}" height="{PH}" rx="12" fill="#888" filter="{bg}"/>')
    else:
        p.append(f'<rect x="{ox}" y="{oy}" width="{PW}" height="{PH}" rx="12" {fill}/>')
    p.append(f'<g transform="translate({ox + (PW - 200*1.25)/2 - 6},{oy + 22}) scale(1.25)">{body}</g>')
    p.append(f'<text x="{ox + PW/2}" y="{oy + PH + 30}" font-family="Noto Sans" font-size="20" font-weight="700" text-anchor="middle" fill="#222">{title}</text>')
    p.append(f'<text x="{ox + PW/2}" y="{oy + PH + 54}" font-family="Noto Sans" font-size="15" text-anchor="middle" fill="#555">{sub}</text>')
p.append('</svg>')
open('knarr-depth-preview.svg', 'w').write(''.join(p))
