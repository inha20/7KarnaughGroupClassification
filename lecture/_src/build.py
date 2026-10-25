# -*- coding: utf-8 -*-
"""Build the lecture site:  python3 build.py [out_dir]"""
import os, re, sys, html, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import *
import figures as F
import slides as S
from talks import TALKS, SLIDE2TALK, BUDGET, EXPLAINERS

ASSETS = os.path.join(HERE, 'assets') if os.path.isdir(os.path.join(HERE, 'assets')) else os.path.join(HERE, '..', 'assets')
if len(sys.argv) > 1:
    OUT = os.path.abspath(sys.argv[1])
else:
    OUT = os.path.abspath(os.path.join(HERE, '..')) if os.path.basename(HERE) == '_src' else os.path.abspath(os.path.join(HERE, '..', 'site_out'))

SITE = 'S₄ 궤도 분류 강의'                       # plain text (titles, attributes)
SITE_HTML = 'S<sub>4</sub> 궤도 분류 강의'            # visible brand
PAPER_SITE = 'https://inha20.github.io/7KarnaughGroupClassification/'
PAPER_REPO = 'https://github.com/inha20/7KarnaughGroupClassification'
TOTAL_MIN = sum(t['minutes'] for t in TALKS)

SUBMAP = dict(zip('0123456789+−=()aeoxhklmnpst', '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜ'))
SUPMAP = dict(zip('0123456789+−=()ni', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ'))


def uni(s):
    """HTML with <sub>/<sup> -> plain text with Unicode sub/superscripts (for <title>, aria and attributes)."""
    s = re.sub(r'<sub>(.*?)</sub>', lambda m: ''.join(SUBMAP.get(c, c) for c in m.group(1)), s)
    s = re.sub(r'<sup>(.*?)</sup>', lambda m: ''.join(SUPMAP.get(c, c) for c in m.group(1)), s)
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s)


def talk_file(n):
    return 'talk-%02d.html' % n


# ------------------------------------------------------------------ cross references
def resolve(htmlstr, here_talk=None):
    def href(n):
        t = SLIDE2TALK[n]
        return ('#s%d' % n) if t == here_talk else '%s#s%d' % (talk_file(t), n)
    htmlstr = re.sub(r'href="\{\{s(\d+)\}\}"', lambda m: 'href="%s"' % href(int(m.group(1))), htmlstr)
    htmlstr = re.sub(r'\{\{s(\d+)\}\}', lambda m: '<a class="xref" href="%s">%s장</a>' % (href(int(m.group(1))), m.group(1)), htmlstr)
    return htmlstr


NOTE_FIX = {
    2: [('답(10, 30, 32)은 12장과 19장에서 공개합니다', '답(10, 30, 32)은 {{s21}}과 {{s32}}에서 공개합니다')],
    4: [('마지막 한 장(22장)만 7번 논문에서 확장된 내용(입력 반전까지 허용한 B₄)을 짧게 소개합니다.',
         '입력 반전까지 허용한 B₄ 확장({{s35}}~{{s36}})만 7번 논문에서 새로 정리된 내용입니다. 카르노맵 변수 배치의 결론(24가지 배치가 3개 동치류로 나뉜다)은 {{s18}}에서 짧게 소개합니다.')],
    16: [('(20장에서 다시 언급)', '({{s33}}에서 다시 언급)')],
    21: [('2장의 질문의 답이', '{{s2}}의 질문의 답이'), ('이어지는 13~18장에서', '이어지는 {{s22}}~{{s31}}에서'), ('15장의 주제입니다', '{{s25}}~{{s26}}의 주제입니다')],
    24: [('(19장)', '({{s32}})')],
    29: [('C₅는 앞 장에서 8', 'C₅는 {{s28}}에서 8')],
    30: [('(24장에서 한계로 다시)', '({{s37}}에서 한계로 다시)')],
    32: [('2장에서 물었던', '{{s2}}에서 물었던')],
    34: [('한계(24장)', '한계({{s37}})')],
}


def notes_html(n, skip=None):
    raw = (SLIDES[n].get('notes') or '').strip()
    if not raw:
        return None
    for old, new in NOTE_FIX.get(n, []):
        assert old in raw, ('note fix did not match', n, old)
        raw = raw.replace(old, new)
    if skip:
        raw = '\n'.join(l for l in raw.split('\n') if l.strip() not in [x.strip() for x in skip])
    ps = note_html(raw)
    ps[0] = re.sub(r'^【(\d+)분】\s*', r'<span class="tm">\1분</span>', ps[0])
    if n == 38:
        ps.append('정답과 해설은 각 문제 아래의 ‘정답과 해설’을 눌러 펼칩니다.')
    return ps


# ------------------------------------------------------------------ page chrome
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hahmlet:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600'
         '&family=IBM+Plex+Sans+KR:wght@400;500;600;700&display=swap">')
THEME_INIT = "<script>try{var t=localStorage.getItem('s4orb-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>"
BRAND_SVG = ('<svg viewBox="-20 -20 40 40" aria-hidden="true" focusable="false"><circle r="17" fill="none" stroke="currentColor" stroke-opacity=".4" stroke-width="1.6"/>'
             '<circle r="10" fill="none" stroke="currentColor" stroke-opacity=".4" stroke-width="1.6"/><circle cx="12" cy="-12" r="3.6" fill="#17A398"/>'
             '<circle cx="10" cy="0" r="3.6" fill="#E4572E"/><circle cx="-5" cy="8.66" r="3" fill="#F2A93B"/></svg>')
ICON_THEME = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
              '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')
ICON_PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M7 4.5v15l13-7.5z"/></svg>'
ICON_NOTE = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
             '<path d="M5 3h10l4 4v14H5z"/><path d="M9 12h6M9 16h6"/></svg>')


def head(title, desc, base_css=True):
    return ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="color-scheme" content="light dark">\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            '<title>%s</title>\n<meta name="description" content="%s">\n<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n'
            '%s\n%s\n<link rel="stylesheet" href="assets/site.css">\n</head>\n' % (e(title), e(desc), THEME_INIT, FONTS))


def bar(talk=False):
    right = ('<a class="btn" href="index.html">목록</a>' if talk else '')
    notes = ('<button type="button" class="btn" data-act="notes" aria-pressed="true">%s<span class="lbl-wide">노트</span></button>' % ICON_NOTE) if talk else ''
    play = ('<button type="button" class="btn primary" data-act="present">%s<span>발표 시작</span></button>' % ICON_PLAY) if talk else ''
    return ('<header class="bar"><div class="bar-in"><a class="brand" href="index.html" aria-label="강의 목록으로 가기">%s<span>%s</span></a><span class="bar-sp"></span>%s%s'
            '<button type="button" class="btn icon" data-act="theme" aria-label="어두운 화면" aria-pressed="false">%s</button>%s</div></header>'
            % (BRAND_SVG, SITE_HTML, right, notes, ICON_THEME, play))


def foot():
    return ('<footer class="site-foot"><p>%s · 최종훈 (Jonghun Choi) · 독립 연구자</p>'
            '<p>바탕이 된 논문 「카르노맵 위의 4변수 부울 함수 공간의 군론적 분류」: <a href="%s" rel="noopener">웹 페이지</a> · <a href="%s" rel="noopener">GitHub 저장소</a></p></footer>'
            % (SITE_HTML, PAPER_SITE, PAPER_REPO))


# ------------------------------------------------------------------ talk page
def slide_html(n, talk, k, nt):
    d = S.R[n]()
    body = resolve(d['body'], talk['n'])
    dens = S.DENSITY.get(n, '')
    cls = ' '.join(x for x in ('slide', d.get('cls', ''), dens) if x)
    budget = talk['budget'][k]
    lead = resolve(d['lead'], talk['n'])
    nts = notes_html(n, skip=d.get('notes_skip'))
    notes = ''
    if nts:
        notes = ('<section class="notes" aria-label="슬라이드 %d 발표자 노트"><h3>발표자 노트 · 슬라이드 %d</h3>%s</section>'
                 % (n, n, ''.join('<p>%s</p>' % resolve(p, talk['n']) for p in nts)))
    return ('<div class="sw" id="w%d" data-budget="%d"><article class="%s" id="s%d" data-n="%d" data-steps="%d" aria-labelledby="t%d">'
            '<header class="s-head"><span class="s-badge" aria-hidden="true">%d</span><span class="s-part">%s</span>'
            '<button type="button" class="s-play" data-act="present-here" aria-label="이 슬라이드부터 발표">%s<span>여기서 발표</span></button><span class="s-no">%d / 40</span></header>'
            '<h2 class="s-title" id="t%d">%s</h2>%s<div class="s-body">%s</div></article>%s</div>'
            % (n, budget, cls, n, n, d['steps'], n, part_no(n), part_tag(n), ICON_PLAY, n, n, resolve(d['title'], talk['n']),
               ('<p class="s-lead">%s</p>' % lead) if lead else '', body, notes))


def talk_page(t):
    n = t['n']
    prv = TALKS[n - 2] if n > 1 else None
    nxt = TALKS[n] if n < len(TALKS) else None
    title_txt = uni(t['title'])
    first, last = t['slides'][0], t['slides'][-1]
    rng = ('슬라이드 %d' % first) if first == last else ('슬라이드 %d–%d' % (first, last))
    smap = ''.join('<li><a href="%s"%s aria-label="발표 %d">%d</a></li>' % (talk_file(x['n']), ' aria-current="page"' if x['n'] == n else '', x['n'], x['n']) for x in TALKS)
    total_sec = sum(t['budget'])
    deck_attrs = ('id="deck" data-total="%d" data-title="%s" data-q="%s" data-a="%s" data-next="%s" data-next-title="%s"'
                  % (total_sec, e('발표 %d · %s' % (n, title_txt)), e(t['q']), e(t['a']),
                     talk_file(n + 1) if nxt else '', e(uni(nxt['title'])) if nxt else ''))
    slides_html = ''.join(slide_html(s, t, k, nxt) for k, s in enumerate(t['slides']))
    pager = '<nav class="pager" aria-label="발표 이동">%s%s</nav>' % (
        ('<a class="prev" href="%s"><small>이전 발표 %d</small><b>%s</b></a>' % (talk_file(n - 1), n - 1, prv['title'])) if prv else '<span class="gap"></span>',
        ('<a class="next" href="%s"><small>다음 발표 %d</small><b>%s</b></a>' % (talk_file(n + 1), n + 1, nxt['title'])) if nxt else '')
    hero = ('<section class="thero" aria-labelledby="h1">%s<div><p class="thero-meta"><span>발표 <b>%d</b> / %d</span><span>%s</span><span>약 %d분</span><span>%s</span></p>'
            '<h1 id="h1">%s</h1><div class="qa"><p><span class="tag">질문</span><span class="q">%s</span></p><p class="a"><span class="tag">한 줄 답</span><span>%s</span></p></div></div></section>'
            % (F.ring_badge(n, len(TALKS), 76), n, len(TALKS), t['part'], t['minutes'], rng, t['title'], t['q'], resolve(t['a'], n)))
    tools = ('<p class="smap-l">전체 발표</p><ol class="smap">%s</ol>' % smap)
    page = (head('%s · %s' % (title_txt, SITE), '발표 %d/%d · %s · 약 %d분. %s' % (n, len(TALKS), uni(t['q']), t['minutes'], uni(t['a'])))
            + '<body>\n<a class="skip" href="#main">본문으로 건너뛰기</a>\n' + bar(True)
            + '<main id="main" class="wrap">' + hero + tools + '<div class="deck" %s>%s</div>' % (deck_attrs, slides_html) + pager + foot() + '</main>\n'
            + '<script src="assets/site.js"></script>\n</body>\n</html>\n')
    return page


# ------------------------------------------------------------------ index page
def index_page():
    groups = {}
    for t in TALKS:
        groups.setdefault(part_no(t['slides'][0]), []).append(t)
    GT = {0: '도입', 1: '1부 · 준비', 2: '2부 · 전체 공간', 3: '3부 · 세 가지 클론', 4: '4부 · 검증과 확장', 5: '5부 · 정리'}
    blocks = []
    for g in sorted(groups):
        ts = groups[g]
        rows = []
        for t in ts:
            first, last = t['slides'][0], t['slides'][-1]
            rng = ('슬라이드 %d' % first) if first == last else ('슬라이드 %d–%d' % (first, last))
            rows.append('<li><a class="trow" href="%s">%s<div><div class="t-title">%s</div><div class="t-q">%s</div></div><div class="t-meta"><b>%d분</b>%s</div></a></li>'
                        % (talk_file(t['n']), F.ring_badge(t['n'], len(TALKS), 52), t['title'], t['q'], t['minutes'], rng))
        span = ('발표 %d' % ts[0]['n']) if len(ts) == 1 else '발표 %d–%d' % (ts[0]['n'], ts[-1]['n'])
        blocks.append('<section class="part-block" aria-labelledby="g%d"><div class="part-head"><h2 id="g%d">%s</h2><span>%s · %d분</span></div><ol class="tlist">%s</ol></section>'
                      % (g, g, GT[g], span, sum(t['minutes'] for t in ts), ''.join(rows)))
    q = lead_of(2)
    num1, num2 = strip_b(paras(2, 'stat-all')[0]), strip_b(paras(2, 'stat-orbits')[0])
    about = note_html(SLIDES[1]['notes'])
    scope = [p for p in about if p.startswith('이 강의는')][0]
    prereq = [p for p in about if p.startswith('선수 지식')][0].replace('부족하면 4~7장에서 보충합니다.', '부족하면 1부(발표 2~6)에서 보충합니다.')
    scope = scope.replace('그림의 종류는 다루지 않습니다.', '그림의 종류는 다루지 않습니다(변수 배치의 결론만 {{s18}}에서 짧게 소개합니다).')
    hero = ('<section class="hero" aria-labelledby="h1">%s<div class="hero-in"><h1 id="h1">4변수 부울 함수 공간의<br>S<sub>4</sub> 궤도 분류</h1>'
            '<p class="sub">번사이드 보조정리와 세 가지 클론<br>(아핀 · 단조 · 자기쌍대)</p>'
            '<p class="src">논문 「카르노맵 위의 4변수 부울 함수 공간의 군론적 분류」 5장 중심 강의 교안<br><b>최종훈 (Jonghun Choi)</b> · 인하공업전문대학 2학년 재학 · 독립 연구자</p>'
            '<div class="hero-cta"><a class="btn primary" href="talk-01.html">첫 발표 보기</a><a class="btn" href="#talks">발표 %d개 목록</a></div></div></section>'
            % (F.hero_rings(), len(TALKS)))
    strip = ('<section class="question-strip" aria-label="오늘의 질문"><div class="qs-num"><b>%s</b><span>4변수 부울 함수의 개수 (2<sup>16</sup>)</span></div>'
             '<div class="qs-arrow">%s<span>변수 이름을 바꿔<br>같아지는 것끼리 묶기</span></div><div class="qs-num res"><b>%s</b><span>서로 다른 종류 (궤도의 수)</span></div></section>'
             % (num1, F.arrow_block(), num2))
    how = ('<div class="howto"><section><h3>이렇게 쓰세요</h3><p>발표 하나는 슬라이드 1~3장, 약 4~5분입니다. 각 발표는 질문 하나로 시작해 한 줄 답으로 끝납니다. 슬라이드 아래에는 발표자 노트가 붙어 있고, 위쪽의 노트 버튼으로 숨길 수 있습니다.</p>'
           '<ul><li>화면 오른쪽 위 <b>발표 시작</b>: 슬라이드를 한 장씩 크게 보여 주고 타이머를 켭니다.</li><li>연습문제(슬라이드 38)의 정답은 문제마다 펼쳐 볼 수 있습니다.</li><li>어두운 화면과 밝은 화면은 오른쪽 위 달 모양 버튼으로 바꿉니다.</li></ul></section>'
           '<section><h3>발표 모드 단축키</h3><p><kbd>→</kbd> <kbd>Space</kbd> 다음 · <kbd>←</kbd> 이전 · <kbd>N</kbd> 노트 · <kbd>P</kbd> 타이머 멈춤 · <kbd>F</kbd> 전체화면 · <kbd>?</kbd> 도움말 · <kbd>Esc</kbd> 종료</p>'
           '<p style="margin-top:.6em">슬라이드 안의 일부 항목은 단계별로 나타납니다. 오른쪽 위 원형 시계의 눈금은 슬라이드마다 계획한 시간을 나타냅니다.</p></section></div>')
    page = (head(SITE, '4변수 부울 함수 65,536개가 S₄ 아래에서 3,984개의 궤도로 묶이는 과정을, 5분짜리 발표 20개로 나눈 강의 사이트입니다.')
            + '<body>\n<a class="skip" href="#main">본문으로 건너뛰기</a>\n' + bar(False)
            + hero + '<main id="main" class="wrap"><div class="qline" style="margin-top:36px"><h2 style="font-size:1.35rem">오늘의 질문</h2><p style="color:var(--ink-2);margin-top:6px">%s</p></div>%s'
            % (q, strip)
            + '<section class="howto" style="margin-top:28px;grid-template-columns:1fr"><section><h3>이 강의에 대해</h3><p>%s</p><p style="margin-top:.6em">%s</p>'
              '<p style="margin-top:.6em">발표 %d개, 합계 약 %d분 분량입니다.</p></section></section>' % (resolve(scope), prereq, len(TALKS), TOTAL_MIN)
            + '<div id="talks">%s</div>' % ''.join(blocks) + '<div style="margin-top:48px">%s</div>' % how + foot() + '</main>\n'
            + '<script src="assets/site.js"></script>\n</body>\n</html>\n')
    return resolve(page)


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1B2440"/>'
           '<circle cx="32" cy="32" r="22" fill="none" stroke="#3A4876" stroke-width="2.5"/><circle cx="32" cy="32" r="13" fill="none" stroke="#3A4876" stroke-width="2.5"/>'
           '<circle cx="48" cy="17" r="5" fill="#17A398"/><circle cx="45" cy="32" r="5" fill="#E4572E"/><circle cx="25" cy="43" r="4" fill="#F2A93B"/></svg>')


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    for f in ('site.css', 'site.js'):
        src, dst = os.path.join(ASSETS, f), os.path.join(OUT, 'assets', f)
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):      # in the delivered site, assets/ is the source
            shutil.copyfile(src, dst)
    open(os.path.join(OUT, 'assets', 'favicon.svg'), 'w', encoding='utf-8').write(FAVICON)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(index_page())
    for t in TALKS:
        open(os.path.join(OUT, talk_file(t['n'])), 'w', encoding='utf-8').write(resolve(talk_page(t), t['n']))
    print('built', len(TALKS) + 1, 'pages ->', OUT)


if __name__ == '__main__':
    main()
