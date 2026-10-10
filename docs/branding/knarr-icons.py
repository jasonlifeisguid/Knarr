#!/usr/bin/env python3
"""Final Knarr app-icon set: E (mark in shield) on a navy tile for 48 px and up, A2 (the mark alone)
on the same tile for 16-32 px. Writes icons/knarr-icon-E.svg, icons/knarr-icon-A2.svg, PNGs at every
size, and icons/icon.ico (16-256). Rendering needs rsvg-convert and ImageMagick."""
import os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'icons')
os.makedirs(OUT, exist_ok=True)

NAVY, GOLD = '#14243a', '#e2b64e'

def inner(svg_file, colour):
    s = open(os.path.join(HERE, svg_file)).read()
    body = s.split('>', 1)[1].rsplit('</svg>', 1)[0]
    return body.replace('#1a1c2c', colour).replace('currentColor', colour)

# Tile: 1024 canvas, 40 px transparent margin (as on the old icon), corner radius ~20%
TILE = f'<rect x="40" y="40" width="944" height="944" rx="190" fill="{NAVY}"/>'

def icon_E():
    # refined E lives in a 200x220 box; scale so the shield is ~70% of the tile height
    k = 3.0
    w, h = 200 * k, 220 * k
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">{TILE}'
            f'<g transform="translate({(1024 - w) / 2:.1f},{(1024 - h) / 2 + 6:.1f}) scale({k})">{inner("knarr-refined-E.svg", GOLD)}</g></svg>')

def icon_A2():
    # A2 lives in a 24 grid. At 16-32 px every pixel counts: a slimmer margin and the mark at ~80%
    k = 34.0
    tile = f'<rect x="8" y="8" width="1008" height="1008" rx="200" fill="{NAVY}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">{tile}'
            f'<g transform="translate({(1024 - 24 * k) / 2:.1f},{(1024 - 24 * k) / 2:.1f}) scale({k})">{inner("small/knarr-small-A2-refined.svg", GOLD)}</g></svg>')

def write_ico(pngs, out):
    """ICO with every size stored as PNG (supported since Windows Vista); keeps 256 px small."""
    import struct
    datas = [open(f, 'rb').read() for f in pngs]
    sizes = [int(re.search(r'-(\d+)\.png$', f).group(1)) for f in pngs]
    head = struct.pack('<HHH', 0, 1, len(datas))
    offset = 6 + 16 * len(datas)
    entries, blobs = b'', b''
    for n, d in zip(sizes, datas):
        entries += struct.pack('<BBBBHHII', n % 256, n % 256, 0, 0, 1, 32, len(d), offset + len(blobs))
        blobs += d
    open(out, 'wb').write(head + entries + blobs)

files = {'E': icon_E(), 'A2': icon_A2()}
for k, s in files.items():
    open(os.path.join(OUT, f'knarr-icon-{k}.svg'), 'w').write(s)

SIZES = {16: 'A2', 24: 'A2', 32: 'A2', 48: 'E', 64: 'E', 128: 'E', 256: 'E', 512: 'E', 1024: 'E'}
pngs = []
for n, k in SIZES.items():
    out = os.path.join(OUT, f'knarr-{n}.png')
    subprocess.run(['rsvg-convert', '-w', str(n), '-h', str(n), os.path.join(OUT, f'knarr-icon-{k}.svg'), '-o', out], check=True)
    if n <= 256:
        pngs.append(out)
write_ico(pngs, os.path.join(OUT, 'icon.ico'))
print('wrote', len(SIZES), 'PNGs and icon.ico')
