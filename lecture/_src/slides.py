# -*- coding: utf-8 -*-
"""Per-slide renderers. Text comes from slides.json (normalised); only the documented corrections are written by hand."""
import re, html
from lib import *
import figures as F
from talks import SLIDE2TALK

R = {}            # n -> function returning dict(title, lead, body, cls, steps)
DENSITY = {}      # n -> 'dense' | 'xdense'   (present-mode font tuning, filled after overflow QA)


def r(n):
    def deco(fn):
        R[n] = fn
        return fn
    return deco


def X(n):
    """cross-reference token -> resolved later: link to the talk page that contains slide n."""
    return '{{s%d}}' % n


def st(k):
    return ' data-step="%d"' % k


# ------------------------------------------------------------------ small parsers
TAGRE = re.compile(r'^<b>\[(.*?)\]\s*(.*?)</b>$', re.S)
BULRE = re.compile(r'^<b>•\s*(.*?)\s*</b>\s*(.*)$', re.S)
PLAINBUL = re.compile(r'^•\s*(.*)$', re.S)


def card_texts(n):
    """Paragraph lists of the text boxes that follow each 'content-card' shape."""
    out, sh = [], shapes(n)
    for i, s in enumerate(sh):
        if s['name'] == 'content-card':
            for t in sh[i + 1:]:
                if t.get('paras'):
                    out.append([normalise(p) for p in t['paras']])
                    break
    return out


def parse_card(ps):
    """-> (tag, title, [(label, text)])"""
    m = TAGRE.match(ps[0])
    tag, title = (m.group(1), m.group(2)) if m else ('', strip_b(ps[0]))
    items = []
    for p in ps[1:]:
        m = BULRE.match(p)
        if m:
            items.append((m.group(1), m.group(2)))
            continue
        m = PLAINBUL.match(p)
        items.append(('', m.group(1) if m else p))
    return tag, title, items


def li(label, text, extra=''):
    lab = '<b class="pl">%s</b> ' % label if label else ''
    return '<li%s>%s%s</li>' % (extra, lab, text)


def card_html(tag, title, items, k=None, extra_cls=''):
    lis = ''.join(li(a, b) for a, b in items)
    return ('<div class="card%s"%s><span class="c-tag">%s</span><h3 class="c-title">%s</h3><ul class="points">%s</ul></div>'
            % (extra_cls, st(k) if k else '', tag, title, lis))


def base(n):
    return dict(title=strip_b(title_of(n)), lead=lead_of(n), cls='', steps=0)


def explain3(n, overrides=None):
    d = base(n)
    cards = [parse_card(c) for c in card_texts(n)]
    if overrides:
        cards = overrides(cards)
    d['body'] = '<div class="cards3">%s</div>' % ''.join(card_html(t, ti, it, k=i + 1) for i, (t, ti, it) in enumerate(cards))
    d['steps'] = len(cards)
    return d


def table_html(n, name, cls='dt', head_cls=None, row_fn=None, caption=None, col_cls=None, wrap=True):
    t = table_of(n, name)
    head = ''.join('<th scope="col">%s</th>' % strip_b(c) for c in t[0])
    rows = []
    for ri, row in enumerate(t[1:]):
        cells = []
        for ci, c in enumerate(row):
            raw = c
            is_b = raw.startswith('<b>')
            inner = strip_b(raw)
            klass = (col_cls or {}).get(ci, '')
            if row_fn:
                inner, klass2 = row_fn(ri, ci, inner, is_b)
                klass = (klass + ' ' + klass2).strip()
            if ci == 0:
                cells.append('<th scope="row"%s>%s</th>' % (' class="%s"' % klass if klass else '', inner))
            else:
                cells.append('<td%s>%s</td>' % (' class="%s"' % klass if klass else '', inner))
        rows.append('<tr>%s</tr>' % ''.join(cells))
    tb = '<table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (cls, head, ''.join(rows))
    return '<div class="tablewrap">%s</div>' % tb if wrap else tb


# ------------------------------------------------------------------ S2  오늘의 질문
@r(2)
def s2():
    d = base(2)
    big1 = strip_b(paras(2, 'stat-all')[0])
    big2 = strip_b(paras(2, 'stat-orbits')[0])
    cap1, cap2 = para1(2, 'Text 7'), para1(2, 'Text 12')
    arrow_txt = para1(2, 'Text 9')
    qs = []
    for nm, cl in (('Text 14', 'l'), ('Text 17', 'm'), ('Text 20', 'd')):
        ps = paras(2, nm)
        qs.append('<div class="qcard %s"><div><b>%s</b><span>%s</span></div>'
                  '<a class="q" href="{{s21}}" data-ref="21" title="답은 21장(세 클론의 Burnside 표)에서 나옵니다">%s</a></div>'
                  % (cl, strip_b(ps[0]), ps[1], '? 종류'))
    d['body'] = (
        '<div class="stat-row"%s>'
        '<div class="stat"><span class="big">%s</span><span class="cap">%s</span></div>'
        '<div class="arrowcol">%s<span>%s</span></div>'
        '<div class="stat res"><span class="big">%s</span><span class="cap">%s</span></div></div>'
        '<div class="qcards"%s>%s</div>'
        % (st(1), big1, cap1, F.arrow_block(), arrow_txt, big2, cap2, st(2), ''.join(qs)))
    d['steps'] = 2
    return d


# ------------------------------------------------------------------ S3  카르노맵이란
@r(3)
def s3():
    d = base(3)
    left = parse_card(card_texts(3)[0])
    tag, title = TAGRE.match(paras(3, 'TextBox 9')[0]).groups()
    ones = [[1 if (i == 0 and j == 0) else 0 for j in range(4)] for i in range(4)]
    figs = ('<div class="card"%s><span class="c-tag">%s</span><h3 class="c-title">%s</h3>'
            '<div class="figcol">'
            '<figure class="fig">%s</figure>'
            '<figure class="fig">%s<figcaption>입력이 0000일 때만 1인 함수의 카르노맵</figcaption></figure>'
            '</div></div>'
            % (st(2), tag, title, F.gray_cycle(),
               F.kmap(ones, 'AB', 'CD', label='표준 카르노맵. 행 AB와 열 CD는 00, 01, 11, 10 순서이고 왼쪽 위 칸만 1이다.', cs=40)))
    d['body'] = '<div class="split">%s%s</div>' % (card_html(left[0], left[1], left[2], k=1), figs)
    d['steps'] = 2
    return d


# ------------------------------------------------------------------ S4  학습 목표와 범위
@r(4)
def s4():
    d = base(4)
    goals = [para1(4, nm) for nm in ('Text 8', 'Text 12', 'Text 16')]
    ps = paras(4, 'Text 19')
    secs, cur = [], None
    for p in ps:
        if p.startswith('<b>') and p.endswith('</b>'):
            cur = [strip_b(p), []]
            secs.append(cur)
        else:
            cur[1].append(p)
    # scope correction: the Theorem-1 conclusion is shown in slide 18
    fixed = []
    for p in secs[1][1]:
        if p.startswith('카르노맵 변수 배치와 격자 대칭'):
            p += ' — 결론만 %s에서 소개' % X(18)
        fixed.append(p)
    secs[1][1] = fixed
    chip_targets = [5, 14, 19, 33, 37]
    chips = [strip_b(paras(4, nm)[0]) for nm in ('Text 22', 'Text 24', 'Text 26', 'Text 28', 'Text 30')]
    chip_html = ''.join('<li><a href="{{s%d}}" data-ref="%d">%s</a></li>' % (t, t, c) for t, c in zip(chip_targets, chips))
    d['body'] = (
        '<div class="split s-3-2">'
        '<div%s><h3 class="h-sm">%s</h3><ol class="goals">%s</ol></div>'
        '<div class="panel"%s><h3 class="h-sm">%s</h3>'
        '<span class="sub">%s</span><ul class="plist">%s</ul>'
        '<span class="sub no">%s</span><ul class="plist no">%s</ul></div></div>'
        '<div%s><h3 class="h-sm">%s</h3><ul class="chips agenda">%s</ul></div>'
        % (st(1), strip_b(paras(4, 'Text 4')[0]), ''.join('<li>%s</li>' % g for g in goals),
           st(2), strip_b(paras(4, 'Text 18')[0]),
           secs[0][0], ''.join('<li>%s</li>' % x for x in secs[0][1]),
           secs[1][0], ''.join('<li>%s</li>' % x for x in secs[1][1]),
           st(3), strip_b(paras(4, 'Text 20')[0]), chip_html))
    d['steps'] = 3
    return d


# ------------------------------------------------------------------ S5  4변수 부울 함수 공간
@r(5)
def s5():
    d = base(5)
    sh = shapes(5)
    vals = {}
    k = 0
    for i, s in enumerate(sh):
        if s['name'] == 'bit-cell':
            v = int(strip_b(normalise(sh[i + 1]['paras'][0])))
            lab = sh[i + 2]['paras'][0]
            vals[int(lab, 2)] = v
    assert all(vals[i] == bin(i).count('1') % 2 for i in range(16)), 'slide 5 grid must be 4-variable XOR'
    cells = ''.join('<button type="button" class="bit" aria-pressed="%s" data-i="%d" aria-label="입력점 %s, 함수값 %d"><b>%d</b><i>%s</i></button>'
                    % ('true' if vals[i] else 'false', i, format(i, '04b'), vals[i], vals[i], format(i, '04b')) for i in range(16))
    info = paras(5, 'Text 55')
    items = ''.join('<li>%s</li>' % x for x in info[1:])
    d['body'] = (
        '<div class="split s-2-3">'
        '<div class="bitbox" data-widget="bitgrid"><div class="bitgrid">%s</div>'
        '<p class="bitout" aria-live="polite"></p>'
        '<div class="bit-tools"><button type="button" class="mini-btn" data-act="xor">4변수 XOR</button>'
        '<button type="button" class="mini-btn" data-act="zero">모두 0</button>'
        '<button type="button" class="mini-btn" data-act="rand">무작위</button></div>'
        '<p class="tnote">%s</p></div>'
        '<div class="panel"%s><h4>%s</h4><ul class="plist">%s</ul></div></div>'
        % (cells, para1(5, 'Text 53'), st(1), strip_b(info[0]), items))
    d['steps'] = 1
    return d


# ------------------------------------------------------------------ S6, S7, S10, S13, S15, S20, S23, S26, S27, S39, S36
for _n in (6, 7, 10, 13, 15, 20, 23, 26, 27, 36, 39):
    R[_n] = (lambda n: (lambda: explain3(n)))(_n)


# ------------------------------------------------------------------ S11  (6 of 8 possible sizes)
@r(11)
def s11():
    def fix(cards):
        tag, title, items = cards[2]
        items = list(items)
        assert items[2][0].startswith('공간의 분할')
        items[2] = ('공간의 분할:', '65,536개의 전체 함수 공간은 이 8가지 가운데 실제로 나타나는 6가지(1, 3, 4, 6, 12, 24) 크기의 궤도 조각들로 채워집니다. 크기 2와 8은 가능하지만 나타나지 않습니다.')
        cards[2] = (tag, title, items)
        return cards
    return explain3(11, fix)


# ------------------------------------------------------------------ S31  (corrected reasoning — see README)
@r(31)
def s31():
    def fix(cards):
        c1, c2, c3 = cards
        keep = c2[2]
        assert keep[0][0].startswith('오직 AND와 OR의 세계') and keep[2][1].startswith('예를 들어')
        c2n = ('관찰된 구조', '2. 대칭이 숨어 있는 방식', [
            keep[0],
            ('흔한 경우: 대칭 변수 쌍.', '예를 들어 x<sub>1</sub>(x<sub>2</sub> ∨ x<sub>3</sub>)에서 x<sub>2</sub>와 x<sub>3</sub>를 맞바꾸어도 x<sub>1</sub>(x<sub>3</sub> ∨ x<sub>2</sub>) = x<sub>1</sub>(x<sub>2</sub> ∨ x<sub>3</sub>)으로 식이 그대로입니다.'),
            ('대칭이 두 변수의 맞바꿈이 아닐 수도 있다:', 'x<sub>1</sub>x<sub>2</sub> ∨ x<sub>2</sub>x<sub>3</sub> ∨ x<sub>3</sub>x<sub>4</sub>를 바꾸지 않는 순열은 항등과 (14)(23)뿐입니다. 변수 두 개를 맞바꾸는 전위는 하나도 들어 있지 않습니다.'),
        ])
        c3n = ('열린 문제', '3. 최대 크기가 12인 이유', [
            ('크기 공식:', '안정화군이 항등원만 있는 단조 함수가 없다면 궤도 크기는 24 / |Stab| ≤ 24 / 2 = 12입니다.'),
            ('열거로 확인한 사실:', '안정화군의 위수가 24, 8, 6, 4, 2인 단조 함수는 각각 6, 6, 36, 36, 84개이고 그 밖의 위수는 없습니다(합 168). 궤도 크기로는 1×6, 3×2, 4×9, 6×6, 12×7입니다.'),
            ('증명은 아직 없다:', '왜 안정화군이 자명한 단조 함수가 없는지를 설명하는 닫힌 증명은 열린 문제입니다(%s).' % X(37)),
        ])
        return [c1, c2n, c3n]
    d = explain3(31, fix)
    # the deck's lead ("every monotone function has a symmetric variable pair") is false: 12 of the 168 have none
    d['lead'] = '모든 단조 함수는 자명하지 않은 변수 대칭을 최소한 하나는 가진다 (4변수에서 열거로 확인한 사실)'
    return d


# ------------------------------------------------------------------ S8  변수를 바꾸면 함수가 옮겨진다
@r(8)
def s8():
    d = base(8)
    fc = paras(8, 'Text 6')[0]
    m = re.match(r'<b>(.*?)\s*</b>(.*?)<b>\s*(.*?)\s*</b>(.*)$', fc, re.S)
    l1, f1, l2, f2 = [x.strip() for x in m.groups()]
    sh = shapes(8)
    rows, cur = [], None
    for i, s in enumerate(sh):
        if i < 7 or not s.get('paras') or s['name'] in ('orbit-chip', 'Slide Number Placeholder 0'):
            continue
        txt = normalise(s['paras'][0])
        prev = sh[i - 1]['name']
        t = strip_b(txt)
        if prev == 'orbit-chip':
            cur['chips'].append(t)
        elif t.startswith('f ='):
            cur = dict(fn=t, chips=[], size='')
            rows.append(cur)
        elif t.startswith('궤도 크기'):
            cur['size'] = t
    out = []
    for k, rw in enumerate(rows):
        fixed = '고정점' in rw['size']
        out.append('<div class="orbit-row"%s><div class="fn">%s</div><div class="ochips">%s</div><div class="sz%s">%s</div></div>'
                   % (st(k + 1), rw['fn'], ''.join('<span class="ochip">%s</span>' % c for c in rw['chips']),
                      ' fixed' if fixed else '', rw['size']))
    d['body'] = ('<div class="formula-card"><div class="eq"><b>%s</b>%s</div><div class="eq"><b>%s</b>%s</div></div>%s'
                 % (l1.rstrip(':') + ':', f1, l2.rstrip(':') + ':', f2, ''.join(out)))
    d['steps'] = len(rows)
    return d


# ------------------------------------------------------------------ S9  궤도 · 안정화군 · 고정점
@r(9)
def s9():
    d = base(9)
    defs = []
    for k, nm in enumerate(('Text 6', 'Text 8', 'Text 10', 'Text 12')):
        ps = paras(9, nm)
        defs.append('<div class="def"%s><div class="n">%s</div><div class="f">%s</div><div class="d">%s</div></div>'
                    % (st(k + 1 if k < 2 else k), strip_b(ps[0]), strip_b(ps[1]), ps[2]))

    def rf(ri, ci, inner, is_b):
        return inner, ''
    tbl = table_html(9, 'stab-table', cls='dt big')
    d['body'] = ('<div class="split s-1-1-top"><div class="defs">%s</div>'
                 '<div%s>%s<p class="tnote">%s</p></div></div>'
                 % (''.join(defs), st(3), tbl, para1(9, 'Text 13')))
    d['steps'] = 4
    return d


# ------------------------------------------------------------------ S12  번사이드 보조정리
@r(12)
def s12():
    d = base(12)
    formula = strip_b(paras(12, 'burnside-formula')[0])
    fixdef = para1(12, 'Text 7')
    kp = paras(12, 'Text 9')
    wp = paras(12, 'Text 11')
    d['body'] = (
        '<div class="callout"><div class="eq lg">%s</div><div class="eq">%s</div></div>'
        '<div class="split">'
        '<div class="panel"%s><h4>%s</h4><p>%s</p><p class="eq">%s</p><p>%s</p></div>'
        '<div class="panel"%s><h4>%s</h4><p>%s</p><p>%s</p><p class="eq"><b>%s</b></p></div></div>'
        % (formula, fixdef,
           st(1), strip_b(kp[0]), kp[1], strip_b(kp[2]), kp[3],
           st(2), strip_b(wp[0]), wp[1], wp[2], strip_b(wp[3])))
    d['steps'] = 2
    return d


# ------------------------------------------------------------------ S14  5개 켤레류
@r(14)
def s14():
    d = base(14)
    d['body'] = '%s<p class="eq"%s>%s</p>' % (table_html(14, 'class-table', cls='dt big', col_cls={4: 'hl'}), st(1), para1(14, 'Text 5'))
    d['steps'] = 1
    return d


# ------------------------------------------------------------------ S16  3,984개의 궤도
@r(16)
def s16():
    d = base(16)
    terms = []
    for nm in ('Text 6', 'Text 8', 'Text 10', 'Text 12', 'Text 14'):
        ps = paras(16, nm)
        terms.append('<div class="term"><span class="k">%s</span><span class="g">%s</span><span class="v">%s</span></div>'
                     % (strip_b(ps[0]), ps[1], strip_b(ps[2])))
    d['body'] = (
        '<div class="terms"%s>%s</div>'
        '<p class="sumline"%s>%s</p><p class="resline"%s><b>%s</b></p><p class="tnote"%s>%s</p>'
        % (st(1), ''.join(terms), st(2), para1(16, 'sum-line'), st(3), strip_b(paras(16, 'result-line')[0]), st(3), para1(16, 'Text 17')))
    d['steps'] = 3
    return d


# ------------------------------------------------------------------ S17  궤도 크기 분포
@r(17)
def s17():
    d = base(17)
    ch = chart_of(17)
    cats = ch['cats']
    vals = [int(v) for v in ch['series'][0][1]]
    svg = F.barchart(cats, [('궤도 수', vals)], '궤도 크기별 궤도의 수', '궤도 크기', ['s1'], w=560, h=400,
                     ymax=2000, ticks=[0, 500, 1000, 1500, 2000],
                     tipfmt=lambda c, s, v: '크기 %s인 궤도 · %s개' % (c, '{:,}'.format(int(v))))
    facts = []
    for nm in ('Text 6', 'Text 8', 'Text 10'):
        ps = paras(17, nm)
        facts.append('<div class="stat"><span class="big" style="font-size:2.2em">%s</span><span class="cap">%s</span></div>' % (strip_b(ps[0]), ps[1]))
    d['body'] = ('<div class="split s-3-2"><div class="chartbox">%s</div>'
                 '<div class="factcol"%s>%s</div></div>' % (svg, st(1), ''.join(facts)))
    d['steps'] = 1
    return d


# ------------------------------------------------------------------ S18  카르노맵 배치 3개 동치류 (corrected figure caption)
@r(18)
def s18():
    d = base(18)
    tag, title, items = parse_card(card_texts(18)[0])
    pre = items[:4]
    cls_items = items[4:]
    lis = ''.join(li(a, b) for a, b in pre)
    nested = ''.join('<li><b class="pl">%s</b> %s</li>' % (a, b) for a, b in cls_items)
    left = ('<div class="card"%s><span class="c-tag">%s</span><h3 class="c-title">%s</h3>'
            '<ul class="points">%s</ul><ul class="points nest">%s</ul></div>' % (st(1), tag, title, lis, nested))
    fn = lambda a, b, c, dd: 1 if (a ^ b) and (c ^ dd) else 0
    maps = []
    for lay, (rv, cv) in (('AB|CD', ('AB', 'CD')), ('AC|BD', ('AC', 'BD')), ('AD|BC', ('AD', 'BC'))):
        g = F.kmap_from_func(fn, rv, cv)
        maps.append('<figure class="fig">%s<figcaption>{%s}</figcaption></figure>'
                    % (F.kmap(g, rv, cv, label='%s 배치의 카르노맵' % lay, cs=30), lay))
    cap = ('좌측부터 {AB|CD}, {AC|BD}, {AD|BC} 배치에서 같은 함수 f = m(5, 6, 9, 10) = (A⊕B)(C⊕D)를 그린 카르노맵입니다. '
           '{AC|BD}와 {AD|BC}의 그림은 같고 {AB|CD}의 그림만 달라서 이 함수의 그림 종류는 2가지입니다. '
           '완전 대칭 함수(XOR 등 32개)는 세 그림이 같고, 세 배치가 모두 다른 그림을 주는 함수는 26,112개입니다.')
    right = ('<div class="card"%s><span class="c-tag">논문 그림 8</span><h3 class="c-title">같은 함수가 3개 배치에서 보이는 그림</h3>'
             '<div class="figrow">%s</div><p class="tnote">%s</p></div>' % (st(2), ''.join(maps), cap))
    d['body'] = '<div class="split">%s%s</div>' % (left, right)
    d['steps'] = 2
    return d


# ------------------------------------------------------------------ S19  세 가지 클론
@r(19)
def s19():
    d = base(19)
    cards = []
    for k, (pill, txt, cl) in enumerate((('Text 7', 'Text 8', 'l'), ('Text 11', 'Text 12', 'm'), ('Text 15', 'Text 16', 'd'))):
        ps = paras(19, txt)
        cards.append('<div class="card"%s><span class="pill %s">%s</span><p class="eq" style="margin-top:.7em"><b>%s</b></p>'
                     '<ul class="points" style="margin-top:.4em">%s</ul></div>'
                     % (st(k + 1), cl, strip_b(paras(19, pill)[0]), strip_b(ps[0]), ''.join('<li>%s</li>' % x for x in ps[1:])))
    d['body'] = '<div class="cards3">%s</div><div class="band"%s>%s</div>' % (''.join(cards), st(4), strip_b(paras(19, 'Text 18')[0]))
    d['steps'] = 4
    return d


# ------------------------------------------------------------------ S21  세 클론의 Burnside 표
@r(21)
def s21():
    d = base(21)
    rows_cls = ['', 'r-l', 'r-m', 'r-d']

    def rf(ri, ci, inner, is_b):
        k = ''
        if ci == 7:
            k = 'hl'
        if ri == 3 and inner == '0':
            k = 'hl'
        return inner, k
    t = table_of(21, 'burnside-table')
    head = ''.join('<th scope="col">%s</th>' % strip_b(c) for c in t[0])
    body = []
    for ri, row in enumerate(t[1:]):
        cells = []
        for ci, c in enumerate(row):
            inner, k = rf(ri, ci, strip_b(c), c.startswith('<b>'))
            if ci == 0:
                cells.append('<th scope="row">%s</th>' % inner)
            else:
                cells.append('<td%s>%s</td>' % (' class="%s"' % k if k else '', inner))
        body.append('<tr class="%s"%s>%s</tr>' % (rows_cls[ri], st(ri + 1), ''.join(cells)))
    tbl = ('<div class="tablewrap"><table class="dt big sticky"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
           % (head, ''.join(body)))
    d['body'] = '%s<p class="tnote"%s>%s</p>' % (tbl, st(4), para1(21, 'Text 5'))
    d['steps'] = 4
    return d


# ------------------------------------------------------------------ S22  아핀 공간 L의 Fix
@r(22)
def s22():
    d = base(22)
    terms = []
    for nm in ('Text 6', 'Text 8', 'Text 10', 'Text 12', 'Text 14'):
        ps = paras(22, nm)
        terms.append('<div class="term"><span class="k">%s</span><span class="g">%s</span><span class="m">%s</span><span class="v">%s</span></div>'
                     % (strip_b(ps[0]), ps[1], ps[2], strip_b(ps[3])))
    rp = paras(22, 'Text 16')
    m = re.match(r'<b>(.*?)</b>\s*(.*)$', rp[0], re.S)
    d['body'] = ('<div class="terms"%s>%s</div><div class="resbox"%s><div class="eq1">%s<small>%s</small></div><div class="eq2">%s</div></div>'
                 % (st(1), ''.join(terms), st(2), m.group(1), m.group(2).strip(), rp[1]))
    d['steps'] = 2
    return d


# ------------------------------------------------------------------ S24  아핀 공간의 10개 궤도
@r(24)
def s24():
    d = base(24)

    def rf(ri, ci, inner, is_b):
        if ci == 4:
            return inner, 'yes' if inner == '예' else ''
        return inner, ''
    d['body'] = '%s<p class="tnote">%s</p>' % (table_html(24, 'affine-orbits', cls='dt mini', row_fn=rf), para1(24, 'Text 5'))
    d['steps'] = 0
    return d


# ------------------------------------------------------------------ S25  자기쌍대 공간 D
@r(25)
def s25():
    d = base(25)
    ps = paras(25, 'Text 13')
    chips = []
    for nm in ('Text 16', 'Text 18', 'Text 20', 'Text 22', 'Text 24'):
        q = paras(25, nm)
        v = strip_b(q[1])
        chips.append('<div class="fchip%s"><span>%s</span><b>%s</b></div>' % (' zero' if v == '0' else '', q[0], v))
    dp = paras(25, 'Text 26')
    left = ('<div class="panel"%s><h4>%s</h4><div class="collide"><div class="collide-row">'
            '<span class="cnode">%s</span><span class="carrow">%s<span>%s</span></span><span class="cnode b">%s</span></div>'
            '<ul class="logic"><li><b>%s</b></li><li>%s</li><li>%s</li><li>%s</li><li class="stop">%s</li></ul></div></div>'
            % (st(1), strip_b(paras(25, 'Text 6')[0]), strip_b(paras(25, 'Text 8')[0]),
               '<svg viewBox="0 0 54 24" aria-hidden="true"><path d="M0 9h38V1l16 11-16 11v-8H0z"/></svg>', para1(25, 'Text 12'),
               strip_b(paras(25, 'Text 10')[0]), strip_b(ps[0]), ps[1], ps[2], ps[3], strip_b(ps[4])))
    right = ('<div class="rightcol"><div class="panel"%s><h4>%s</h4><div class="chips5">%s</div></div>'
             '<div class="panel"%s><p class="eq">%s</p><p class="eq"><b>%s</b></p><p class="eq lg"><b>%s</b></p><p>%s</p><p>%s</p></div></div>'
             % (st(2), strip_b(paras(25, 'Text 14')[0]), ''.join(chips), st(3), dp[0], strip_b(dp[1]), strip_b(dp[2]), dp[3], dp[4]))
    d['body'] = '<div class="split">%s%s</div>' % (left, right)
    d['steps'] = 3
    return d


# ------------------------------------------------------------------ S28  단조 공간 M: 상집합 세기
UPSETS = [(), ('a',), ('a', 'b'), ('a', 'b', 'c'), ('a', 'b', 'd'), ('a', 'b', 'c', 'd'), ('a', 'b', 'c', 'd', 'e'), ('a', 'b', 'c', 'd', 'e', 'f')]


@r(28)
def s28():
    d = base(28)
    t = table_of(28, 'upset-table')
    rows = []
    for i, row in enumerate(t[1:]):
        rows.append('<tr data-sig="%s"><th scope="row">%s</th><td class="l">%s</td></tr>' % (','.join(UPSETS[i]), strip_b(row[0]), row[1]))
    tbl = ('<div class="tablewrap"><table class="dt mini" id="upset-table"><thead><tr><th scope="col">%s</th><th scope="col">%s</th></tr></thead><tbody>%s</tbody></table></div>'
           % (strip_b(t[0][0]), strip_b(t[0][1]), ''.join(rows)))
    d['body'] = (
        '<div class="split">'
        '<div class="panel hasse-wrap" data-widget="hasse"><h4>%s</h4>%s'
        '<p class="hasse-msg" aria-live="polite"></p>'
        '<p class="hasse-hint">%s 칸을 눌러 상집합인지 확인해 보세요.</p></div>'
        '<div><h3 class="h-sm">%s</h3>%s<p class="eq" style="margin-top:.8em"%s><b>%s</b></p></div></div>'
        % (strip_b(paras(28, 'Text 6')[0]), F.hasse(('a', 'b', 'c')), para1(28, 'Text 25'),
           strip_b(paras(28, 'Text 26')[0]), tbl, st(1), strip_b(paras(28, 'Text 27')[0])))
    d['steps'] = 1
    return d


# ------------------------------------------------------------------ S29  단조 Fix의 다섯 값
@r(29)
def s29():
    d = base(29)
    sh = shapes(29)
    rows = []
    i = 0
    while i < len(sh):
        if sh[i]['name'] == 'method-row':
            tx = [normalise(sh[i + k]['paras'][0]) for k in (1, 2, 3, 4)]
            rows.append(tx)
            i += 5
        else:
            i += 1
    assert len(rows) == 5
    out = []
    for k, (a, b, c, e_) in enumerate(rows):
        c = strip_b(c)
        e_ = strip_b(e_) if e_.startswith('<b>') else e_
        if c.startswith('앞 장에서'):
            c = c.replace('앞 장에서', '%s에서' % X(28))     # "the previous slide" -> explicit link
        out.append('<div class="mrow"%s><span class="k">%s</span><span class="p">%s</span><span class="r">%s</span><span class="s">%s</span></div>'
                   % (st(k + 1), strip_b(a), b, c, e_))
    d['body'] = '<div class="methods">%s</div><p class="resline"%s><b>%s</b></p>' % (''.join(out), st(6), strip_b(paras(29, 'result-line')[0]))
    d['steps'] = 6
    return d


# ------------------------------------------------------------------ S30  단조 공간의 30개 궤도
@r(30)
def s30():
    d = base(30)
    ch = chart_of(30)
    vals = [int(v) for v in ch['series'][0][1]]
    svg = F.barchart(ch['cats'], [('궤도 수', vals)], '단조 함수의 궤도 크기 분포 (30개)', '궤도 크기', ['s1'], w=520, h=400,
                     ymax=10, ticks=[0, 2, 4, 6, 8, 10], cls='slate',
                     tipfmt=lambda c, s, v: '크기 %s인 궤도 · %d개' % (c, v))
    d['body'] = ('<div class="split s-1-1-top"><div class="chartbox">%s</div>'
                 '<div%s>%s<p class="eq" style="margin-top:.8em"%s><b>%s</b></p></div></div>'
                 % (svg, st(1), table_html(30, 'monotone-examples', cls='dt mini', col_cls={1: 'l'}), st(2), strip_b(paras(30, 'Text 5')[0])))
    d['steps'] = 2
    return d


# ------------------------------------------------------------------ S32  세 공간 한눈에 보기
@r(32)
def s32():
    d = base(32)
    p1, p2 = paras(32, 'Text 6'), paras(32, 'Text 8')

    def rf(ri, ci, inner, is_b):
        return inner, 'hl' if ci == 2 else ('l' if ci in (3, 4) else '')
    d['body'] = ('<div class="tablewrap">%s</div>'
                 '<div class="split"%s><div class="panel"><p class="eq"><b>%s</b></p><p>%s</p></div>'
                 '<div class="panel"><p class="eq"><b>%s</b></p><p>%s</p></div></div>'
                 % (table_html(32, 'compare-table', cls='dt', row_fn=rf, wrap=False), st(1), strip_b(p1[0]), p1[1], strip_b(p2[0]), p2[1]))
    d['steps'] = 1
    return d


# ------------------------------------------------------------------ S33  검증과 문헌 속 위치
@r(33)
def s33():
    d = base(33)
    tiles = []
    for nm in ('Text 6', 'Text 8', 'Text 10'):
        ps = paras(33, nm)
        tiles.append('<div class="tile"><span class="big">%s</span><span class="cap">%s</span><span class="chk">%s</span></div>'
                     % (strip_b(ps[0]), ps[1], strip_b(ps[2])))
    a, b = paras(33, 'Text 12'), paras(33, 'Text 14')
    d['body'] = ('<div class="tiles"%s>%s</div>'
                 '<div class="split"%s><div class="panel"><h4>%s</h4><ul class="plist">%s</ul></div>'
                 '<div class="panel"><h4>%s</h4><ul class="plist no">%s</ul></div></div>'
                 % (st(1), ''.join(tiles), st(2), strip_b(a[0]), ''.join('<li>%s</li>' % x for x in a[1:]),
                    strip_b(b[0]), ''.join('<li>%s</li>' % x for x in b[1:])))
    d['steps'] = 2
    return d


# ------------------------------------------------------------------ S34  5변수로 늘리면?
@r(34)
def s34():
    d = base(34)
    ch = chart_of(34)
    series = [(normalise(html.escape(n_)), [int(v) for v in vals]) for n_, vals in ch['series']]
    svg = F.barchart(ch['cats'], series, '변수 순열 군 아래 궤도의 수 (n = 4, 5)', '함수 공간', ['s1', 's2'], w=560, h=400,
                     ymax=250, ticks=[0, 50, 100, 150, 200, 250], legend=True,
                     tipfmt=lambda c, s, v: '%s · %s · %d궤도' % (c, s, v))
    ps = paras(34, 'Text 6')
    d['body'] = ('<div class="split s-3-2"><div class="chartbox">%s</div>'
                 '<div class="rightcol"%s>%s<div class="callout" style="margin-top:1em"><p><b>%s</b></p>'
                 '<p class="eq">%s</p><p class="eq">%s</p><p class="muted">%s</p></div></div></div>'
                 % (svg, st(1), table_html(34, 'n5-table', cls='dt mini'), strip_b(ps[0]), ps[1], ps[2], ps[3]))
    d['steps'] = 1
    return d


# ------------------------------------------------------------------ S35  확장: 입력 반전까지 허용하면
@r(35)
def s35():
    d = base(35)
    sub = {}
    for nm in ('Text 6', 'Text 8'):
        ps = paras(35, nm)
        sub[nm] = (strip_b(ps[0]), ps[1])
    names = [('Text 12', 'Text 13', 'Text 14', 'Text 15'), ('Text 18', 'Text 19', 'Text 20', 'Text 21'),
             ('Text 24', 'Text 25', 'Text 26', 'Text 27'), ('Text 30', 'Text 31', 'Text 32', 'Text 33')]
    rows = []
    for k, (a, b, c, e_) in enumerate(names):
        la, va = strip_b(paras(35, a)[0]), strip_b(paras(35, b)[0])
        lc, vc = strip_b(paras(35, c)[0]), strip_b(paras(35, e_)[0])
        undef = vc.startswith('정의되지')
        rows.append('<div class="cmp-row"%s><div class="cmp-c"><span>%s</span><b>%s</b></div>'
                    '<div class="cmp-c%s"><span>%s</span><b>%s</b></div></div>'
                    % (st(k + 1), la, va, ' undef' if undef else ' res', lc, vc))
    d['body'] = ('<div class="cmp"><div class="cmp-head"><div class="cmp-h"><b>%s</b><span>%s</span></div>'
                 '<div class="cmp-h"><b>%s</b><span>%s</span></div></div>%s</div><p class="tnote"%s>%s</p>'
                 % (sub['Text 6'][0], sub['Text 6'][1], sub['Text 8'][0], sub['Text 8'][1], ''.join(rows), st(4), para1(35, 'Text 34')))
    d['steps'] = 4
    return d


# ------------------------------------------------------------------ S37  한계와 열린 문제
@r(37)
def s37():
    d = base(37)
    lim, opn = paras(37, 'Text 7'), paras(37, 'Text 10')
    d['body'] = ('<div class="split">'
                 '<div class="panel"%s><h4>%s</h4><ul class="plist no">%s</ul></div>'
                 '<div class="panel"%s><h4>%s</h4><ul class="plist">%s</ul></div></div>'
                 '<div class="band amber"%s>%s</div>'
                 % (st(1), strip_b(paras(37, 'Text 6')[0]), ''.join('<li>%s</li>' % x for x in lim),
                    st(2), strip_b(paras(37, 'Text 9')[0]), ''.join('<li>%s</li>' % x for x in opn),
                    st(3), strip_b(paras(37, 'Text 12')[0])))
    d['steps'] = 3
    return d


# ------------------------------------------------------------------ S38  연습문제와 토론 (answers attached to each problem)
ANSWER_SPLIT = re.compile(r'^(\d)\)\s*(.*)$|^(토론)\)\s*(.*)$', re.S)


@r(38)
def s38():
    d = base(38)
    probs = [para1(38, nm) for nm in ('Text 7', 'Text 11', 'Text 15', 'Text 19', 'Text 23')]
    raw = SLIDES[38]['notes'].split('\n')
    ans = {}
    for line in raw:
        line = line.strip()
        m = re.match(r'^([1-4])\)\s*(.*)$', line)
        if m:
            ans[int(m.group(1))] = m.group(2)
        elif line.startswith('토론)'):
            ans[5] = line[3:].strip()
    assert sorted(ans) == [1, 2, 3, 4, 5]
    items = []
    for k, p in enumerate(probs):
        a = normalise(html.escape(ans[k + 1], quote=True))
        items.append('<li class="prob"%s><p>%s</p><details><summary>정답과 해설</summary><div class="ans">%s</div></details></li>' % (st(k + 1), p, a))
    d['body'] = '<ol class="probs">%s</ol><p class="tnote">%s</p>' % (''.join(items), para1(38, 'Text 24'))
    d['steps'] = 5
    d['notes_skip'] = [ans_line for ans_line in raw if re.match(r'^([1-4]\)|토론\))', ans_line.strip())]
    return d


# ------------------------------------------------------------------ S40  오늘의 핵심
@r(40)
def s40():
    d = base(40)
    keys = []
    for k, nm in enumerate(('Text 7', 'Text 11', 'Text 15', 'Text 19')):
        ps = paras(40, nm)
        body = ''.join('<p>%s</p>' % x for x in ps[1:])
        keys.append('<div class="key" data-n="%d"%s><h4>%s</h4><div>%s</div></div>' % (k + 1, st(k + 1), strip_b(ps[0]), body))
    d['body'] = '<div class="keys">%s</div><p class="qd"%s>%s</p>' % (''.join(keys), st(5), strip_b(paras(40, 'Text 20')[0]))
    d['cls'] = 'k-dark'
    d['steps'] = 5
    return d
