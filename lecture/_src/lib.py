# -*- coding: utf-8 -*-
"""Shared helpers: slide data access, text normalisation, small HTML builders."""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SL = json.load(open(os.path.join(HERE, 'slides.json'), encoding='utf-8'))
SLIDES = {s['n']: s for s in SL}

# ---------------------------------------------------------------- text normalisation
SUB = dict(zip('₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜ', '0123456789+−=()aeoxhklmnpst'))
SUP = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ', '0123456789+−=()ni'))
SUP.update({'ᵐ': 'm', 'ᵏ': 'k'})


def _group(s, table, tag):
    out, i = [], 0
    while i < len(s):
        if s[i] in table:
            j = i
            while j < len(s) and s[j] in table:
                j += 1
            out.append('<%s>%s</%s>' % (tag, ''.join(table[c] for c in s[i:j]), tag))
            i = j
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def sub_sup(s):
    """Unicode sub/superscript characters -> real <sub>/<sup> (consecutive chars grouped)."""
    return _group(_group(s, SUB, 'sub'), SUP, 'sup')


def curly(s):
    """&#x27; ... &#x27; pairs -> ‘ ’ ; stray ones -> ’ ; &quot; pairs -> “ ”."""
    def pairs(s, ent, op, cl):
        parts = s.split(ent)
        if len(parts) == 1:
            return s
        if (len(parts) - 1) % 2 == 0:
            out = parts[0]
            for k in range(1, len(parts)):
                out += (op if k % 2 == 1 else cl) + parts[k]
            return out
        return s.replace(ent, cl)
    return pairs(pairs(s, '&#x27;', '‘', '’'), '&quot;', '“', '”')


CARET = [
    (re.compile(r'\^\{([^{}]*)\}'), r'<sup>\1</sup>'),
    (re.compile(r'\^\(((?:[^()]|\([^()]*\))*)\)'), r'<sup>\1</sup>'),
    (re.compile(r'\^([0-9A-Za-z]+)'), r'<sup>\1</sup>'),
    (re.compile(r'_\{([^{}]*)\}'), r'<sub>\1</sub>'),
]
LITERAL = [('P_σ', 'P<sub>σ</sub>'), ('Fix_M', 'Fix<sub>M</sub>')]


def normalise(s):
    """Source HTML fragment (already escaped) -> cleaned site HTML."""
    s = s.replace('</b><b>', '')                     # merge split bold runs
    s = s.replace('::', ':')                         # S26 typo
    s = s.replace('!:', ':')                         # S26 typo ("반대 출력!:")
    s = re.sub(r'¬f\(x\) !\s+\(', '¬f(x) (', s)       # S26: stray "!" after the equation (reads like a factorial)
    for a, b in CARET:
        s = a.sub(b, s)
    for a, b in LITERAL:
        s = s.replace(a, b)
    s = re.sub(r'(?<![0-9A-Za-z])4C2', '<sub>4</sub>C<sub>2</sub>', s)
    s = re.sub(r'(?<![0-9A-Za-z_])B4(?![0-9A-Za-z_])', 'B<sub>4</sub>', s)
    s = s.replace('...', '…')
    s = re.sub(r'<sup>-(?=\d)', '<sup>−', s)
    s = sub_sup(s)
    s = curly(s)
    s = s.replace('</sub><sub>', '').replace('</sup><sup>', '')
    return s


def note_html(text, links=None):
    """Speaker-note plain text -> HTML paragraphs (escaped, normalised)."""
    out = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        line = html.escape(line, quote=True)
        line = normalise(line)
        out.append(line)
    return out


def plain(s):
    """HTML fragment -> plain text with sub/sup flattened (for QA diffing)."""
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = ''.join(SUB.get(c, SUP.get(c, c)) for c in s)
    s = s.replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"').replace('…', '...')
    return re.sub(r'\s+', ' ', s).strip()


# ---------------------------------------------------------------- slide data access
def shapes(n):
    return SLIDES[n]['shapes']


def by_name(n, name):
    for sh in shapes(n):
        if sh['name'] == name:
            return sh
    raise KeyError((n, name))


def paras(n, name):
    return [normalise(p) for p in by_name(n, name).get('paras', [])]


def para1(n, name):
    return ' '.join(paras(n, name))


def title_of(n):
    for nm in ('Title 1', 'Text 1'):
        for sh in shapes(n):
            if sh['name'] == nm and sh.get('paras'):
                return normalise(sh['paras'][0])
    return ''


def strip_b(s):
    """Remove the outer <b>..</b> wrapper (titles are all bold in the deck)."""
    s = re.sub(r'^<b>(.*)</b>$', r'\1', s.strip(), flags=re.S)
    return s.replace('<b>', '').replace('</b>', '')


def part_tag(n):
    t = strip_b(paras(n, 'part-tag')[0])
    return re.sub(r'^\d\s+', '', t)          # S3 starts with a stray "0 "


def part_no(n):
    return int(strip_b(paras(n, 'badge-label')[0]))


def lead_of(n):
    try:
        return para1(n, 'lead')
    except KeyError:
        return ''


def table_of(n, name):
    return [[normalise(c) for c in row] for row in by_name(n, name)['table']]


def chart_of(n):
    for sh in shapes(n):
        if 'chart' in sh:
            return sh['chart']
    raise KeyError(n)


# ---------------------------------------------------------------- tiny HTML helpers
def e(s):
    return html.escape(s, quote=True)


def tag(name, content='', cls=None, **attrs):
    a = ''
    if cls:
        a += ' class="%s"' % cls
    for k, v in attrs.items():
        if v is None or v is False:
            continue
        k = k.replace('_', '-')
        a += ' %s' % k if v is True else ' %s="%s"' % (k, v)
    return '<%s%s>%s</%s>' % (name, a, content, name)


def unbold(s):
    return strip_b(s)
