#!/usr/bin/env python3
"""'Knarr' in Noto Sans Bold, converted to an SVG path (no font needed afterwards).
Needs fontTools (pip install fonttools). Writes wordmark/knarr-wordmark.json: {d, width, ascent}
(d_k: the K, d_rest: 'narr') in font units (1000/em), y pointing down, baseline at y=0."""
import json, os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT = sys.argv[1] if len(sys.argv) > 1 else '/usr/share/fonts/noto/NotoSans-Bold.ttf'
TEXT = 'Knarr'
f = TTFont(FONT)
gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
# The K and the rest are kept as separate paths, so the K can take the mark's gold
pens = {'k': SVGPathPen(gs), 'rest': SVGPathPen(gs)}
x = 0
for i, ch in enumerate(TEXT):
    g = cmap[ord(ch)]
    gs[g].draw(TransformPen(pens['k' if i == 0 else 'rest'], (1, 0, 0, -1, x, 0)))   # flip y: SVG y points down
    x += hmtx[g][0]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wordmark')
os.makedirs(out, exist_ok=True)
data = {'d_k': pens['k'].getCommands(), 'd_rest': pens['rest'].getCommands(), 'width': x, 'capHeight': f['OS/2'].sCapHeight, 'font': os.path.basename(FONT)}
json.dump(data, open(os.path.join(out, 'knarr-wordmark.json'), 'w'))
print('width', x, 'capHeight', data['capHeight'])
