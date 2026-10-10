#!/usr/bin/env python3
"""Wordmark candidates beside the refined mark, flat gold with a drop shadow on navy.
Writes knarr-wordmark-preview.svg."""
NEW_D = ['M100,15 V190', 'M100,30 L60,70 H130', 'M100,130 L130,100', 'M100,130 L130,160', 'M40,190 H150 L175,165']
GOLD, NAVY, BONE = '#e2b64e', '#14243a', '#efe6d2'
def mark(c):
    return ''.join(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="14" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="3"/>' for d in NEW_D)
DROP = ('<filter id="drop" x="-30%" y="-30%" width="170%" height="170%"><feGaussianBlur in="SourceAlpha" stdDeviation="4"/>'
        '<feOffset dx="5" dy="7"/><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.55 0"/>'
        '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
OPTIONS = [  # (label, family, weight, size, letter-spacing, text, note)
    ('1 · Sans caps (the old mockup)', 'Noto Sans', 800, 92, 16, 'KNARR', 'closest to the German company'),
    ('2 · Sans, title case', 'Noto Sans', 700, 100, 2, 'Knarr', 'friendly, modern'),
    ('3 · Bookman', 'URW Bookman', 700, 100, 0, 'Knarr', 'sturdy, old-world'),
    ('4 · Palatino-style', 'P052', 700, 104, 1, 'Knarr', 'classical, bookish'),
    ('5 · Serif caps', 'P052', 700, 84, 12, 'KNARR', 'carved-inscription feel'),
    ('6 · Century', 'C059', 700, 100, 0, 'Knarr', 'solid, readable'),
]
RW, RH = 760, 190
W, H = 40 + 2 * (RW + 30), 40 + 3 * (RH + 50)
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{DROP}</defs>',
     f'<rect width="{W}" height="{H}" fill="#f3f1ec"/>']
for i, (label, fam, wt, sz, ls, text, note) in enumerate(OPTIONS):
    ox, oy = 40 + (i % 2) * (RW + 30), 30 + (i // 2) * (RH + 50)
    p.append(f'<rect x="{ox}" y="{oy}" width="{RW}" height="{RH}" rx="14" fill="{NAVY}"/>')
    p.append(f'<g filter="url(#drop)"><g transform="translate({ox+30},{oy+20}) scale(0.72)">{mark(GOLD)}</g>'
             f'<text x="{ox+200}" y="{oy+128}" font-family="{fam}" font-weight="{wt}" font-size="{sz}" letter-spacing="{ls}" fill="{BONE}">{text}</text></g>')
    p.append(f'<text x="{ox}" y="{oy+RH+26}" font-family="Noto Sans" font-size="17" font-weight="700" fill="#222">{label}</text>'
             f'<text x="{ox+RW}" y="{oy+RH+26}" font-family="Noto Sans" font-size="15" fill="#666" text-anchor="end">{note}</text>')
p.append('</svg>')
open('knarr-wordmark-preview.svg', 'w').write(''.join(p))
