#!/usr/bin/env python3
"""Balancing the classic Knarr mark, and the hull-base mark in a shield and a seal.
Writes knarr-balance-<name>.svg and knarr-balance-preview.svg."""
import math

INK, BONE, NAVY, GOLD = '#1a1c2c', '#efe6d2', '#14243a', '#e2b64e'

def draw(paths, colour, w=13):
    return ''.join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" '
                   f'stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="3"/>' for d in paths)

K = ['M100,122 L138,88', 'M100,122 L138,156']
V = {
    # the original, for comparison
    'original': ['M100,22 V170', 'M100,36 L64,80 H130', *K, 'M74,196 L100,168 L126,196'],
    # grounded: feet spread as wide as the flag, so the base matches the top
    'grounded': ['M100,22 V164', 'M100,36 L64,80 H130', *K, 'M58,198 L100,164 L142,198'],
    # lighter top: the four's bar stops at the staff and the K grows, moving weight down and right
    'lighter':  ['M100,22 V170', 'M100,36 L66,80 H106', 'M100,128 L142,90', 'M100,128 L142,166', 'M64,198 L100,168 L136,198'],
    # hull: 5 from before, the hull widened so the staff stands at its middle
    'hull':     ['M100,22 V172', 'M100,36 L64,80 H130', *K, 'M48,178 H146 L164,150'],
}

def shield(colour, w=8):
    return (f'<path d="M30,14 H170 V112 C170,160 136,190 100,206 C64,190 30,160 30,112 Z" '
            f'fill="none" stroke="{colour}" stroke-width="{w}"/>')

def seal(colour):
    s = (f'<circle cx="100" cy="110" r="98" fill="none" stroke="{colour}" stroke-width="5"/>'
         f'<circle cx="100" cy="110" r="70" fill="none" stroke="{colour}" stroke-width="3"/>')
    for ch, a in zip('KNARR', (-130, -110, -90, -70, -50)):
        x, y = 100 + 80 * math.cos(math.radians(a)), 110 + 80 * math.sin(math.radians(a))
        s += (f'<text transform="translate({x:.1f},{y:.1f}) rotate({a + 90})" font-family="Noto Sans" font-weight="800" '
              f'font-size="21" text-anchor="middle" dominant-baseline="central" fill="{colour}">{ch}</text>')
    for a in (45, 67.5, 90, 112.5, 135):
        s += f'<circle cx="{100 + 84 * math.cos(math.radians(a)):.1f}" cy="{110 + 84 * math.sin(math.radians(a)):.1f}" r="3.5" fill="{colour}"/>'
    return s

files = {k: draw(p, INK) for k, p in V.items()}
files['hull-shield'] = shield(INK) + f'<g transform="translate(24,26) scale(0.76)">{draw(V["hull"], INK, 15)}</g>'
files['hull-seal'] = seal(INK) + f'<g transform="translate(51,54) scale(0.49)">{draw(V["hull"], INK, 19)}</g>'
for k, c in files.items():
    open(f'knarr-balance-{k}.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220" width="200" height="220">{c}</svg>')

labels = {'original': 'A · Original 1', 'grounded': 'B · Grounded', 'lighter': 'C · Lighter top',
          'hull': 'D · Hull (5)', 'hull-shield': 'E · Hull in shield', 'hull-seal': 'F · Hull in seal'}
cols, tw, th = 6, 230, 300
W = 40 + cols * tw
H = th + 260
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#f3f1ec"/>']
for i, k in enumerate(files):
    ox = 40 + i * tw
    p.append(f'<rect x="{ox}" y="30" width="{tw-30}" height="{th-70}" rx="10" fill="{BONE}"/>')
    # faint centre line to show balance about the staff
    p.append(f'<line x1="{ox+100}" y1="34" x2="{ox+100}" y2="{th-44}" stroke="#c9bfa8" stroke-width="1" stroke-dasharray="4 4"/>')
    p.append(f'<g transform="translate({ox+5},35) scale(0.95)">{files[k]}</g>')
    p.append(f'<text x="{ox+(tw-30)/2}" y="{th-10}" font-family="Noto Sans" font-size="19" font-weight="700" text-anchor="middle" fill="#222">{labels[k]}</text>')
    # as an app icon underneath
    p.append(f'<rect x="{ox+30}" y="{th+20}" width="140" height="140" rx="32" fill="{NAVY}"/>')
    p.append(f'<g transform="translate({ox+46},{th+30}) scale(0.54)">{files[k].replace(INK, GOLD)}</g>')
    p.append(f'<rect x="{ox+80}" y="{th+180}" width="40" height="40" rx="9" fill="{NAVY}"/>')
    p.append(f'<g transform="translate({ox+84},{th+182}) scale(0.16)">{files[k].replace(INK, GOLD).replace("stroke-width=\"13\"", "stroke-width=\"20\"")}</g>')
p.append('</svg>')
open('knarr-balance-preview.svg', 'w').write(''.join(p))
