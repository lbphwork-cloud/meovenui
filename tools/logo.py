# Vẽ lại logo Mèo về núi (SVG). Chạy: python3 tools/logo.py <thư mục chứa Montserrat_wght_900/200/500.ttf> src/img/brand
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FD = sys.argv[1]; OUT = sys.argv[2]

def text_path(fontfile, text, x, baseline, size, tracking=0, fit_width=None):
    f = TTFont(fontfile); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
    s = size / upm
    names = [cmap[ord(c)] for c in text]
    adv = [gs[n].width * s for n in names]
    total = sum(adv) + tracking * (len(text) - 1)
    if fit_width:
        k = fit_width / total; s *= k; adv = [a * k for a in adv]; tracking *= k
    d = []; cx = x
    for n, a in zip(names, adv):
        pen = SVGPathPen(gs)
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, cx, baseline)))
        d.append(pen.getCommands()); cx += a + tracking
    return ' '.join(d), cx - tracking

def bounds(fontfile, text, size):
    f = TTFont(fontfile); gs = f.getGlyphSet(); cmap = f.getBestCmap(); s = size / f['head'].unitsPerEm
    return [gs[cmap[ord(c)]].width * s for c in text]

BLACK = f'{FD}/Montserrat_wght_900.ttf'; LIGHT = f'{FD}/Montserrat_wght_200.ttf'; MED = f'{FD}/Montserrat_wght_500.ttf'

# Chữ M mặt mèo: hai đỉnh có khía tai, hai mắt và miệng cười
M = ("M46 163 L82 15 L91 15 L96 23 L101 15 L110 15 L146 124 L182 15 L191 15 L196 23 L201 15 L210 15 "
     "L246 163 L216 163 L196 76 L161 163 L131 163 L96 76 L76 163 Z")
eyes = '<circle cx="101" cy="146" r="7.5"/><circle cx="191" cy="146" r="7.5"/>'
smile = '<path d="M130 172 Q146 190 162 172" fill="none" stroke-width="7" stroke-linecap="round"/>'

eo, eo_end = text_path(BLACK, 'eo', 250, 163, 92, tracking=-2)
venui, _ = text_path(LIGHT, 'venui', 236, 96, 52, tracking=1)
caps, caps_end = text_path(MED, 'QUANG TRI TOUR', 240, 44, 16.5, tracking=1.6)
# Đuôi mèo nối từ chữ o
tx = eo_end - 4
tail = (f'<path d="M{tx:.1f} 131 C{tx+16:.1f} 131 {tx+24:.1f} 124 {tx+38:.1f} 124 C{tx+50:.1f} 124 {tx+56:.1f} 131 {tx+53:.1f} 137 '
        f'C{tx+50:.1f} 142 {tx+43:.1f} 140 {tx+44:.1f} 134" fill="none" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
W = max(tx + 64, caps_end + 6)

def svg(main, soft, ink):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="36 6 {W - 30:.0f} 190" role="img" aria-label="Mèo về núi - Quang Tri Tour">
<g fill="{main}" stroke="{main}"><path d="{M}" stroke="none"/><g stroke="none">{eyes}</g>{smile}<path d="{eo}" stroke="none"/>{tail}</g>
<path d="{venui}" fill="{soft}"/>
<path d="{caps}" fill="{ink}"/>
</svg>
'''
open(f'{OUT}/logo.svg', 'w').write(svg('#2f513c', '#6a9472', '#253f30'))
open(f'{OUT}/logo-light.svg', 'w').write(svg('#fafbf6', '#d4e5d5', '#ecd59e'))
# Favicon: chỉ chữ M mặt mèo
open(f'{OUT}/favicon.svg', 'w').write(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 0 232 200"><g fill="#2f513c" stroke="#2f513c"><path d="{M}" stroke="none"/><g stroke="none">{eyes}</g>{smile}</g></svg>
''')
print('W', round(W), 'eo_end', round(eo_end), 'caps_end', round(caps_end))
