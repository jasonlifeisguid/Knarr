#!/usr/bin/env python3
"""Small-size symbol options for Knarr, drawn on a 24-unit grid with 45-degree diagonals.
Writes small/knarr-small-<name>.svg; render with rsvg-convert at 16/24/32 px to judge."""
import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'small'))

def s(paths, w=2.0, extra=''):
    body = ''.join(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="{w}" '
                   f'stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="3"/>' for d in paths)
    return body + extra

OPTIONS = {
    # A: the full mark, simplified spacing: staff, 4, K, hull
    'A-full': s(['M10,2 V20', 'M10,4 L6,8 H14', 'M10,14 L13,11', 'M10,14 L13,17', 'M3,20 H15 L18,17']),
    # B: no K: staff, 4 and hull; the ship without the initial
    'B-noK': s(['M11,2 V20', 'M11,4 L6,9 H15', 'M3,20 H16 L19.5,16.5']),
    # C: solid pennant: the 4 becomes a filled triangle, plus the hull
    'C-pennant': s(['M11,2 V20', 'M3,20 H16 L19.5,16.5'],
                   extra='<polygon points="11,3 5,9 11,9" fill="currentColor"/><path d="M11,9 H15" stroke="currentColor" stroke-width="2"/>'),
    # D: in the shield: outline shield, staff, 4 and hull inside
    'D-shield': ('<path d="M3.5,2.5 H20.5 V12 C20.5,17 16.5,20 12,22 C7.5,20 3.5,17 3.5,12 Z" fill="none" stroke="currentColor" stroke-width="1.6"/>'
                 + s(['M12,6 V16', 'M12,7 L9,10 H15', 'M7.5,16 H15 L17,14'], 1.6)),
}
for k, body in OPTIONS.items():
    open(f'knarr-small-{k}.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" color="#1a1c2c">{body}</svg>')
    open(f'knarr-small-{k}-gold.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" color="#e2b64e">'
        f'<rect width="24" height="24" rx="5" fill="#14243a"/>{body}</svg>')

# --- Derived exactly from D refined (knarr-refined.py, 200x220 box), scaled into the 24 grid ----
# Same points, same proportions; only the stroke is heavier, because 14 units scaled down would
# be 1.6 and turn grey at 16 px.
NEW_D = {'staff': [(100, 15), (100, 190)], 'four': [(100, 30), (60, 70), (130, 70)],
         'kup': [(100, 130), (130, 100)], 'kdown': [(100, 130), (130, 160)],
         'hull': [(40, 190), (150, 190), (175, 165)]}
K_SCALE = 20 / 175                        # staff height 175 -> 20 units
def tx(x, y):
    return (round((x - 107.5) * K_SCALE + 12, 2), round((y - 15) * K_SCALE + 2, 2))  # bbox centred
def path(pts):
    (x0, y0), rest = tx(*pts[0]), [tx(*p) for p in pts[1:]]
    return f'M{x0},{y0} ' + ' '.join(f'L{x},{y}' for x, y in rest)
DERIVED = {
    'A2-refined': s([path(NEW_D[k]) for k in ('staff', 'four', 'kup', 'kdown', 'hull')]),
    'B2-refined-noK': s([path(NEW_D[k]) for k in ('staff', 'four', 'hull')]),
}
for k, body in DERIVED.items():
    open(f'knarr-small-{k}.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" color="#1a1c2c">{body}</svg>')
    open(f'knarr-small-{k}-gold.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" color="#e2b64e">'
        f'<rect width="24" height="24" rx="5" fill="#14243a"/>{body}</svg>')
