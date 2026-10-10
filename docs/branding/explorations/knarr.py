#!/usr/bin/env python3
"""Knarr icon concepts + wordmark mockup. Writes knarr-*.svg and knarr-preview.svg."""

SEA1, SEA2 = '#0f2236', '#1d4466'   # night fjord
BONE, RED, WOOD, GOLD, FOAM = '#efe6d2', '#c8423b', '#9a6438', '#e2b64e', '#7fb3d5'

def frame(id_, body, c1=SEA1, c2=SEA2):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">'
            f'<defs><linearGradient id="{id_}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'
            f'<clipPath id="{id_}-c"><rect width="256" height="256" rx="56"/></clipPath></defs>'
            f'<rect width="256" height="256" rx="56" fill="url(#{id_})"/>'
            f'<g clip-path="url(#{id_}-c)">{body}</g></svg>')

# A knarr: broad, deep cargo hull, one square sail, plain curled stem and stern
# (the dragon heads belonged to warships, not traders)
HULL = ('<path d="M34,146 C58,150 74,166 128,168 C182,166 198,150 222,146 '
        'C214,180 178,198 128,198 C78,198 42,180 34,146 Z" fill="' + WOOD + '"/>'
        '<path d="M44,160 C70,174 100,180 128,180 C156,180 186,174 212,160" fill="none" stroke="#000" stroke-opacity="0.22" stroke-width="3"/>'
        '<path d="M52,174 C76,186 102,190 128,190 C154,190 180,186 204,174" fill="none" stroke="#000" stroke-opacity="0.22" stroke-width="3"/>'
        '<path d="M222,146 C230,136 232,122 224,114" fill="none" stroke="' + WOOD + '" stroke-width="9" stroke-linecap="round"/>'
        '<path d="M34,146 C26,136 24,122 32,114" fill="none" stroke="' + WOOD + '" stroke-width="9" stroke-linecap="round"/>')
WAVES = ('<path d="M10,214 q14,-10 28,0 t28,0 t28,0 t28,0 t28,0 t28,0 t28,0 t28,0 t28,0" fill="none" stroke="' + FOAM + '" stroke-opacity="0.55" stroke-width="5" stroke-linecap="round"/>'
         '<path d="M-4,232 q14,-10 28,0 t28,0 t28,0 t28,0 t28,0 t28,0 t28,0 t28,0 t28,0 t28,0" fill="none" stroke="' + FOAM + '" stroke-opacity="0.3" stroke-width="5" stroke-linecap="round"/>')
MAST = (f'<line x1="128" y1="168" x2="128" y2="40" stroke="{WOOD}" stroke-width="6" stroke-linecap="round"/>'
        f'<line x1="70" y1="52" x2="186" y2="52" stroke="{WOOD}" stroke-width="6" stroke-linecap="round"/>')

def sail_path(x0, y0, x1, y1, bulge=10):
    # square sail, bellied by the wind
    return (f'M{x0},{y0} H{x1} C{x1+bulge},{(y0+y1)/2} {x1+bulge},{(y0+y1)/2} {x1},{y1} '
            f'H{x0} C{x0+bulge},{(y0+y1)/2} {x0+bulge},{(y0+y1)/2} {x0},{y0} Z')

out = {}

# A — classic: red-and-bone striped sail
sp = sail_path(76, 54, 180, 146)
stripes = ''.join(f'<rect x="{76+i*26}" y="40" width="13" height="120" fill="{RED}"/>' for i in range(4))
out['classic'] = frame('ka', MAST +
    f'<defs><clipPath id="ka-s"><path d="{sp}"/></clipPath></defs>'
    f'<path d="{sp}" fill="{BONE}"/><g clip-path="url(#ka-s)">{stripes}</g>' + HULL + WAVES)

# B — the sail IS a game cartridge: notched corner, label, gold contacts at its foot
x0, y0, x1, y1, c = 76, 54, 180, 140, 22
cart_sail = (f'<path d="M{x0},{y0} H{x1-c} L{x1},{y0+c} V{y1} H{x0} Z" fill="{BONE}" stroke="{BONE}" stroke-width="6" stroke-linejoin="round"/>'
             f'<rect x="{x0+16}" y="{y0+16}" width="{x1-x0-38}" height="40" rx="5" fill="{GOLD}"/>'
             f'<path d="M{x0+43},{y0+25} L{x0+63},{y0+36} L{x0+43},{y0+47} Z" fill="{SEA1}" stroke="{SEA1}" stroke-width="4" stroke-linejoin="round"/>'
             + ''.join(f'<rect x="{x0+18+i*12}" y="{y1+4}" width="6" height="10" rx="1.5" fill="{GOLD}"/>' for i in range(6)))
out['cartridge-sail'] = frame('kb', MAST + cart_sail + HULL + WAVES)

# C — cargo: no sail, the hull carries a stack of cartridges (the library on board)
def cart(x, y, w, h, fill):
    c = w * 0.24
    return (f'<path d="M{x},{y} H{x+w-c} L{x+w},{y+c} V{y+h} H{x} Z" fill="{fill}" stroke="{fill}" stroke-width="5" stroke-linejoin="round"/>'
            f'<rect x="{x+w*0.18:.1f}" y="{y+h*0.2:.1f}" width="{w*0.6:.1f}" height="{h*0.38:.1f}" rx="3" fill="#fff" opacity="0.9"/>')
cargo = cart(66, 104, 38, 58, RED) + cart(108, 92, 40, 70, GOLD) + cart(152, 104, 38, 58, BONE)
out['cargo'] = frame('kc', cargo + HULL + WAVES)

for k, s in out.items():
    open(f'knarr-{k}.svg', 'w').write(s)

# Preview: three icons, small sizes, and a wordmark lockup
p = ['<svg xmlns="http://www.w3.org/2000/svg" width="980" height="560" viewBox="0 0 980 560">',
     '<rect width="980" height="560" fill="#f3f1ec"/>']
labels = {'classic': 'A · Striped sail', 'cartridge-sail': 'B · Cartridge sail', 'cargo': 'C · Cargo'}
for i, (k, s) in enumerate(out.items()):
    inner = s.split('>', 1)[1].rsplit('</svg>', 1)[0]
    ox = 40 + i * 310
    p.append(f'<g transform="translate({ox},24)">{inner}</g>')
    p.append(f'<text x="{ox+128}" y="310" font-family="Noto Sans" font-size="22" font-weight="700" text-anchor="middle" fill="#222">{labels[k]}</text>')
    p.append(f'<g transform="translate({ox+64},326) scale(0.25)">{inner}</g>')
    p.append(f'<g transform="translate({ox+144},342) scale(0.125)">{inner}</g>')
# wordmark on dark, using icon B
inner = out['cartridge-sail'].split('>', 1)[1].rsplit('</svg>', 1)[0]
p.append(f'<rect x="40" y="410" width="900" height="124" rx="20" fill="{SEA1}"/>')
p.append(f'<g transform="translate(64,428) scale(0.34)">{inner}</g>')
p.append(f'<text x="170" y="490" font-family="Noto Sans" font-size="58" font-weight="800" letter-spacing="10" fill="{BONE}">KNARR</text>')
p.append(f'<text x="172" y="518" font-family="Noto Sans" font-size="19" fill="{FOAM}">Your RomM library, ready to play</text>')
p.append('</svg>')
open('knarr-preview.svg', 'w').write(''.join(p))
