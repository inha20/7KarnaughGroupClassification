# -*- coding: utf-8 -*-
"""Vector figures redrawn for the web (all colours come from CSS classes -> theme aware)."""
import math, html
from lib import e

GRAY = ['00', '01', '11', '10']


# ------------------------------------------------------------------ orbit ring art
def hero_rings():
    """Cover motif of the deck: concentric orbit rings with three dots (decorative)."""
    return '''<svg class="rings" viewBox="-260 -260 520 520" aria-hidden="true" focusable="false">
  <g class="ring r1"><circle r="236"/><circle class="dot d-teal" cx="170" cy="-164" r="11"/></g>
  <g class="ring r2"><circle r="168"/><circle class="dot d-red" cx="168" cy="0" r="14"/></g>
  <g class="ring r3"><circle r="108"/><circle class="dot d-amber" cx="-108" cy="0" r="10"/></g>
  <circle class="core" r="64"/>
</svg>'''


def ring_badge(n, total=20, size=56):
    """Talk number inside a ring; the dot marks where the talk sits in the series."""
    ang = -math.pi / 2 + (n - 1) / total * 2 * math.pi
    cx = cy = size / 2
    r = size / 2 - 5
    dx, dy = cx + r * math.cos(ang), cy + r * math.sin(ang)
    return ('<svg class="rbadge" viewBox="0 0 %d %d" aria-hidden="true" focusable="false">'
            '<circle class="rb-ring" cx="%.1f" cy="%.1f" r="%.1f"/>'
            '<circle class="rb-dot" cx="%.2f" cy="%.2f" r="4.2"/>'
            '<text class="rb-n" x="%.1f" y="%.1f" text-anchor="middle" dominant-baseline="central">%d</text></svg>'
            % (size, size, cx, cy, r, dx, dy, cx, cy + 1, n))


def arrow_block(w=120, h=64):
    return ('<svg class="arrow-block" viewBox="0 0 120 64" aria-hidden="true" focusable="false">'
            '<path d="M4 20h64V6l48 26-48 26V44H4z"/></svg>')


# ------------------------------------------------------------------ Karnaugh maps
def kmap(grid, rows='AB', cols='CD', ones=None, label=None, cls='', cs=44):
    """grid: 4x4 list of 0/1 (rows & columns in Gray order 00 01 11 10)."""
    x0, y0 = 62, 54
    W, H = x0 + 4 * cs + 10, y0 + 4 * cs + 10
    out = ['<svg class="kmap %s" viewBox="0 0 %d %d" role="img" aria-label="%s">' % (cls, W, H, e(label or ''))]
    out.append('<text class="ax" x="%d" y="16" text-anchor="middle">%s</text>' % (x0 + 2 * cs, e(cols)))
    out.append('<text class="ax" x="16" y="%d" text-anchor="middle" dominant-baseline="central">%s</text>' % (y0 + 2 * cs, e(rows)))
    for j, g in enumerate(GRAY):
        out.append('<text class="lb" x="%d" y="%d" text-anchor="middle">%s</text>' % (x0 + j * cs + cs // 2, y0 - 10, g))
    for i, g in enumerate(GRAY):
        out.append('<text class="lb" x="%d" y="%d" text-anchor="end" dominant-baseline="central">%s</text>' % (x0 - 10, y0 + i * cs + cs // 2, g))
    for i in range(4):
        for j in range(4):
            v = grid[i][j]
            out.append('<rect class="cell%s" x="%d" y="%d" width="%d" height="%d" rx="3"/>' % (' one' if v else '', x0 + j * cs + 1, y0 + i * cs + 1, cs - 2, cs - 2))
            out.append('<text class="cv%s" x="%d" y="%d" text-anchor="middle" dominant-baseline="central">%d</text>' % (' one' if v else '', x0 + j * cs + cs // 2, y0 + i * cs + cs // 2 + 1, v))
    out.append('</svg>')
    return ''.join(out)


def bits(i):
    return format(i, '04b')


def kmap_from_func(fn, rows_vars, cols_vars, **kw):
    """fn(a,b,c,d)->0/1 ; rows_vars/cols_vars are strings like 'AC','BD'."""
    idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    grid = []
    for rg in GRAY:
        row = []
        for cg in GRAY:
            x = [0, 0, 0, 0]
            for k, v in enumerate(rows_vars):
                x[idx[v]] = int(rg[k])
            for k, v in enumerate(cols_vars):
                x[idx[v]] = int(cg[k])
            row.append(fn(*x))
        grid.append(row)
    return grid


def gray_cycle():
    """00 -> 01 -> 11 -> 10 -> 00 on a 2x2 loop, edges labelled by the bit they share."""
    nodes = {'00': (84, 46), '01': (216, 46), '11': (216, 148), '10': (84, 148)}
    out = ['<svg class="gcycle" viewBox="0 0 300 194" role="img" aria-label="Gray 코드 순환: 00, 01, 11, 10, 다시 00. 이웃한 코드는 정확히 한 비트만 다르다.">',
           '<defs><marker id="gcarrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>']
    order = ['00', '01', '11', '10', '00']
    labels = ['0−', '−1', '1−', '−0']
    lp = [(150, 22), (262, 97), (150, 186), (38, 97)]
    for k in range(4):
        (x1, y1), (x2, y2) = nodes[order[k]], nodes[order[k + 1]]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        # leave a gap for the pill (half-width 30 horizontally / half-height 17 vertically)
        gap = 36 if abs(dx) > abs(dy) else 24
        out.append('<line class="ed" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" marker-end="url(#gcarrow)"/>' % (x1 + ux * gap, y1 + uy * gap, x2 - ux * (gap + 4), y2 - uy * (gap + 4)))
        out.append('<text class="el" x="%d" y="%d" text-anchor="middle" dominant-baseline="central">%s</text>' % (lp[k][0], lp[k][1], labels[k]))
    for b, (x, y) in nodes.items():
        out.append('<rect class="nd" x="%d" y="%d" width="56" height="32" rx="16"/>' % (x - 28, y - 16))
        out.append('<text class="nt" x="%d" y="%d" text-anchor="middle" dominant-baseline="central">%s</text>' % (x, y + 1, b))
    out.append('</svg>')
    return ''.join(out)


# ------------------------------------------------------------------ Hasse diagram (sigma = (1234))
HASSE_NODES = [  # id, label, x, y
    ('a', '{1,2,3,4}', 220, 36),
    ('b', '{1,2,3}', 220, 118),
    ('c', '{1,2}', 112, 200),
    ('d', '{1,3}', 328, 200),
    ('e', '{1}', 220, 282),
    ('f', '∅', 220, 364),
]
HASSE_EDGES = [('a', 'b'), ('b', 'c'), ('b', 'd'), ('c', 'e'), ('d', 'e'), ('e', 'f')]


def hasse(selected=('a', 'b', 'c')):
    pos = {i: (x, y) for i, _, x, y in HASSE_NODES}
    out = ['<svg class="hasse" viewBox="0 0 440 400" role="group" aria-label="σ = (1234)의 궤도 순서집합 P<sub>σ</sub>. 위쪽이 큰 원소.">']
    for a, b in HASSE_EDGES:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        out.append('<line class="hed" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (x1, y1 + 18, x2, y2 - 18))
    for i, lab, x, y in HASSE_NODES:
        on = i in selected
        out.append('<g class="hn%s" data-node="%s" role="button" tabindex="0" aria-pressed="%s" aria-label="%s">'
                   '<rect x="%d" y="%d" width="120" height="38" rx="19"/>'
                   '<text x="%d" y="%d" text-anchor="middle" dominant-baseline="central">%s</text></g>'
                   % (' on' if on else '', i, 'true' if on else 'false', e(lab), x - 60, y - 19, x, y + 1, e(lab)))
    out.append('</svg>')
    return ''.join(out)


# ------------------------------------------------------------------ bar charts
def _top_round(x, y, w, h, r):
    r = min(r, w / 2, h)
    return 'M%.1f %.1fv%.1fq0 %.1f %.1f %.1fh%.1fq%.1f 0 %.1f %.1fv%.1fz' % (
        x, y + h, -(h - r), -r, r, -r, w - 2 * r, r, r, r, h - r)


def barchart(cats, series, title, xtitle, colors, w=560, h=380, ymax=None, ticks=None, fmt=lambda v: '{:,}'.format(int(v)),
             legend=False, label_series=False, tipfmt=None, cls=''):
    """cats: list[str]; series: list[(name, values)]; colors: list of css classes ('s1','s2'...)."""
    ml, mr, mt, mb = 46, 14, 34, 60
    pw, ph = w - ml - mr, h - mt - mb
    vmax = ymax or max(max(v) for _, v in series)
    n, m = len(cats), len(series)
    gw = pw / n
    bw = min(64, gw * 0.62 / m)
    out = ['<svg class="bars %s" viewBox="0 0 %d %d" role="img" aria-label="%s">' % (cls, w, h, e(title))]
    out.append('<text class="ct" x="%d" y="18" text-anchor="middle">%s</text>' % (w // 2, title))
    for t in (ticks or []):
        y = mt + ph - ph * t / vmax
        out.append('<line class="gl" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (ml, y, w - mr, y))
        out.append('<text class="yl" x="%d" y="%.1f" text-anchor="end" dominant-baseline="central">%s</text>' % (ml - 8, y, '{:,}'.format(t)))
    out.append('<line class="bl" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (ml, mt + ph, w - mr, mt + ph))
    for i, c in enumerate(cats):
        cx = ml + gw * (i + 0.5)
        total = bw * m + 6 * (m - 1)
        for j, (sname, vals) in enumerate(series):
            v = vals[i]
            bh = max(ph * v / vmax, 2)
            x = cx - total / 2 + j * (bw + 6)
            y = mt + ph - bh
            tip = (tipfmt(c, sname, v) if tipfmt else '%s · %s' % (c, fmt(v)))
            out.append('<g class="cbar %s" tabindex="0" data-tip="%s"><title>%s</title><path d="%s"/></g>' % (colors[j], e(tip), e(tip), _top_round(x, y, bw, bh, 5)))
            out.append('<text class="vl" x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (x + bw / 2, y - 7, fmt(v)))
        out.append('<text class="xl" x="%.1f" y="%d" text-anchor="middle">%s</text>' % (cx, mt + ph + 22, c))
    out.append('<text class="xt" x="%d" y="%d" text-anchor="middle">%s</text>' % (ml + pw // 2, h - 8, xtitle))
    out.append('</svg>')
    svg = ''.join(out)
    if legend:
        lg = ''.join('<li><i class="lgsw %s"></i>%s</li>' % (colors[j], s) for j, (s, _) in enumerate(series))
        svg = '<ul class="legend">%s</ul>' % lg + svg
    # table alternative
    head = '<tr><th scope="col">%s</th>%s</tr>' % (e(xtitle), ''.join('<th scope="col">%s</th>' % s for s, _ in series))
    rows = ''.join('<tr><th scope="row">%s</th>%s</tr>' % (c, ''.join('<td>%s</td>' % fmt(v[i]) for _, v in series)) for i, c in enumerate(cats))
    table = '<details class="chart-table"><summary>표로 보기</summary><table class="dt mini">%s%s</table></details>' % (head, rows)
    return svg + table
