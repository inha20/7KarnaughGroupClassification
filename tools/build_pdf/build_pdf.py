#!/usr/bin/env python3
"""
build_pdf.py
============
논문 원고(paper/KarnaughGroupClassification.md)에서 PDF(paper/01_KarnaughGroupClassification.pdf)를 만든다.

파이프라인: Markdown (markdown-it-py + dollarmath) -> HTML (수식은 KaTeX) -> PDF (Chromium, Playwright).

이전 PDF를 만든 저자의 원래 스크립트는 저장소에 없어서, 이 스크립트는 이전 PDF를 재서 같은 형식으로
다시 짠 것이다. 이전 PDF에서 잰 값:
    용지 A4, 여백 좌우 22mm / 위 22mm / 아래 20mm, 본문 Noto Sans KR 10pt, 줄 간격 1.6, 양쪽 맞춤,
    제목 1.9em / 1.4em / 1.15em, 표 0.86em, 그림 설명 0.88em, 쪽 번호는 아래 가운데 7pt.
이전 PDF와 줄바꿈이나 쪽 나눔이 조금 다를 수 있다.

사용법 (저장소 루트에서):
    cd tools/build_pdf && npm ci        # 처음 한 번: KaTeX와 글꼴 설치
    pip install -r tools/build_pdf/requirements.txt
    python tools/build_pdf/build_pdf.py

인자 없이 실행하면 paper/의 원고로 paper/의 PDF를 덮어쓴다. 옵션과 주의점은 tools/build_pdf/README.md.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from mdit_py_plugins.dollarmath import dollarmath_plugin
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent.parent
NM = ROOT / "node_modules"
KATEX = NM / "katex" / "dist"

TITLE = "카르노맵 위의 4변수 부울 함수 공간의 군론적 분류"
AUTHOR = "최종훈 (Jonghun Choi)"
CREATOR = "Markdown → HTML (KaTeX) → Chromium; Noto Sans KR"

CSS = r"""
@page { size: A4; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0;
  font-family: 'Noto Sans KR', sans-serif;
  font-size: @FS@;
  line-height: @LH@;
  letter-spacing: @LS@;
  color: #111;
  text-align: justify;
  word-break: keep-all;
  overflow-wrap: break-word;
}
h1, h2, h3, h4 { font-weight: 700; text-align: left; break-after: avoid; line-height: 1.3; }
h1 { font-size: 1.9em; margin: 0 0 0.48em; }
h2 { font-size: 1.4em; margin: 1.74em 0 0.54em; }
h3 { font-size: 1.15em; margin: 1.35em 0 0.52em; }
h4 { font-size: 1.05em; margin: 0.8em 0 0.3em; }
p { margin: 0 0 0.55em; }
hr { border: 0; border-top: 0.75pt solid #222; margin: 1.15em 0 0.3em; break-after: avoid; }
a { color: #0b3d91; text-decoration: none; }
strong { font-weight: 700; }
ul, ol { margin: 0 0 0.55em; padding-left: 2em; }
li { margin: 0 0 0.2em; }
li > p { margin: 0 0 0.3em; }
blockquote { margin: 0 0 0.55em; padding: 0 0 0 0.9em; border-left: 2.5pt solid #cfd4da; color: #444; }

code {
  font-family: 'Noto Sans Mono', monospace;
  font-size: 0.876em;
  background: #f1f2f4;
  border-radius: 3pt;
  padding: 0.1em 0.3em;
  word-break: break-all;
  text-align: left;
}
pre {
  background: #f4f5f7;
  border: 0.75pt solid #e4e6ea;
  border-radius: 4pt;
  padding: 0.5em 0.8em;
  margin: 0 0 0.6em;
  break-inside: avoid;
  text-align: left;
}
pre code {
  background: none; padding: 0; border-radius: 0;
  font-size: 0.8em; line-height: 1.5; word-break: normal; white-space: pre;
}

table {
  border-collapse: collapse;
  width: 100%;
  margin: 0 0 0.6em;
  font-size: 0.86em;
  line-height: 1.45;
  text-align: left;
  word-break: keep-all;
}
thead { display: table-header-group; }
tr { break-inside: avoid; }
th, td { border: 0.75pt solid #9aa0a8; padding: 2.25pt 5.25pt; vertical-align: top; }
th { vertical-align: middle; }
th { background: #e9ecf0; font-weight: 700; }
td img { max-width: 100%; height: auto; display: block; margin: 0 auto; }
td code, th code { font-size: 0.8965em; word-break: normal; white-space: nowrap; }

img { max-width: 100%; height: auto; }
p.figure { text-align: center; margin: 0.8em 0 0.3em; break-after: avoid; }
p.figure img { display: inline-block; vertical-align: top; }
p.caption { font-size: 0.88em; line-height: 1.6; text-align: center; color: #333; margin: 0 0 0.9em; }

/* KaTeX */
.katex { font-size: @MATH@; text-indent: 0; font-family: KaTeX_Main, 'Noto Sans KR', 'Times New Roman', serif; }
.katex-display { margin: 0.7em 0; text-align: center; break-inside: avoid; }
.katex-display > .katex { font-size: @MATH@; }
.math.nb .katex, .math.nb .katex-html { white-space: nowrap; }
.math-error { color: #cc0000; outline: 1pt solid #cc0000; }
"""

SCRIPT = r"""
window.__mathStats = {ok: 0, fail: [], warn: []};
(function () {
  const w0 = console.warn;
  console.warn = function () { window.__mathStats.warn.push(Array.prototype.join.call(arguments, ' ')); };
  const els = Array.from(document.querySelectorAll('.math'));
  els.forEach((el, i) => {
    const tex = el.textContent.replace(/^\s+|\s+$/g, '');
    const display = el.classList.contains('block');
    try {
      katex.render(tex, el, {displayMode: display, throwOnError: true, strict: 'warn', output: 'html'});
      window.__mathStats.ok++;
    } catch (e) {
      window.__mathStats.fail.push({i: i, display: display, tex: tex.slice(0, 240), err: String(e.message || e)});
      el.classList.add('math-error');
      try { katex.render(tex, el, {displayMode: display, throwOnError: false, output: 'html'}); } catch (_) {}
    }
  });
  window.__mathStats.total = els.length;
  console.warn = w0;
})();
window.__atomizeInline = function (maxPx) {
  // Keep short inline formulas (e.g. 4 x 4) on one line; long ones may still wrap after a relation.
  let n = 0;
  document.querySelectorAll('.math:not(.block)').forEach((m) => {
    const bases = Array.from(m.querySelectorAll('.katex-html > .katex-base'));
    if (bases.length < 2) return;
    const w = bases.reduce((s, b) => s + b.getBoundingClientRect().width, 0);
    if (w <= maxPx) { m.classList.add('nb'); n++; }
  });
  return n;
};
window.__fitDisplay = function (maxFrac) {
  const fitted = [];
  document.querySelectorAll('.katex-display').forEach((d) => {
    const k = d.querySelector(':scope > .katex');
    const h = k.querySelector('.katex-html');
    const avail = d.clientWidth;
    const need = h.scrollWidth;
    if (need > avail * maxFrac) {
      const f = (avail * maxFrac) / need;
      k.style.fontSize = f.toFixed(4) + 'em';
      fitted.push({text: h.textContent.slice(0, 40), scale: Math.round(f * 1000) / 1000});
    }
  });
  return fitted;
};
"""


def figure_rule(state):
    """Mark image-only paragraphs as figures and the paragraph right after one as its caption."""
    prev_fig = False
    for i, t in enumerate(state.tokens):
        if t.level != 0 or t.nesting == -1:
            continue
        is_fig = False
        if t.type == "paragraph_open":
            kids = state.tokens[i + 1].children or []
            is_fig = len(kids) == 1 and kids[0].type == "image"
            if is_fig:
                t.attrJoin("class", "figure")
            elif prev_fig:
                t.attrJoin("class", "caption")
        prev_fig = is_fig


def md_to_html(text: str) -> tuple[str, dict]:
    md = (
        MarkdownIt("commonmark", {"html": True, "linkify": True})
        .enable(["table", "strikethrough"])
        .use(dollarmath_plugin, allow_space=False, allow_digits=True, allow_blank_lines=False, double_inline=True)
    )

    # "$$...$$" written on its own line inside a paragraph: keep it as a display block *inside* the <p>
    # (a <div> there would make the HTML parser split the paragraph).
    def render_inline_double(self, tokens, idx, options, env):
        return '<span class="math block">' + escapeHtml(tokens[idx].content) + "</span>"

    md.add_render_rule("math_inline_double", render_inline_double)
    md.core.ruler.push("figure_caption", figure_rule)
    body = md.render(text)

    # stray '$' left outside math/code = math that did not parse
    probe = re.sub(r'<span class="math inline">.*?</span>', "", body, flags=re.S)
    probe = re.sub(r'<div class="math block">.*?</div>', "", probe, flags=re.S)
    probe = re.sub(r'<span class="math block">.*?</span>', "", probe, flags=re.S)
    probe = re.sub(r"<code>.*?</code>", "", probe, flags=re.S)
    probe = re.sub(r"<[^>]+>", "", probe)
    stray = [m.start() for m in re.finditer(r"\$", probe)]
    return body, {"stray_dollars": len(stray), "stray_context": [probe[max(0, s - 30): s + 30] for s in stray[:8]]}


def build_html(body: str, base: pathlib.Path, params: dict) -> str:
    css_links = "\n".join(
        f'<link rel="stylesheet" href="{(p).as_uri()}">'
        for p in [
            KATEX / "katex.min.css",
            NM / "@fontsource" / "noto-sans-kr" / "400.css",
            NM / "@fontsource" / "noto-sans-kr" / "500.css",
            NM / "@fontsource" / "noto-sans-kr" / "700.css",
            NM / "@fontsource" / "noto-sans-mono" / "400.css",
            NM / "@fontsource" / "noto-sans-mono" / "700.css",
        ]
    )
    css = CSS
    for k, v in params.items():
        css = css.replace("@" + k + "@", v)
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>{TITLE}</title>
<base href="{base.as_uri()}/">
{css_links}
<style>{css}</style>
</head><body>
<article>
{body}
</article>
<script src="{(KATEX / 'katex.min.js').as_uri()}"></script>
<script>{SCRIPT}</script>
</body></html>
"""


FOOTER = (
    '<div style="width:100%;text-align:center;font-size:7pt;color:#444;'
    'font-family:\'DejaVu Sans\',sans-serif;padding-top:{pad}pt;"><span class="pageNumber"></span></div>'
)


def find_chrome():
    """Chrome/Chromium to print with. CHROME_PATH or --chrome win; otherwise Playwright's bundled Chromium."""
    env = os.environ.get("CHROME_PATH")
    if env:
        return env
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return mac if pathlib.Path(mac).exists() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manuscript", nargs="?", default=str(REPO / "paper" / "KarnaughGroupClassification.md"))
    ap.add_argument("base", nargs="?", default=str(REPO / "paper"),
                    help="relative image paths in the manuscript are resolved against this directory")
    ap.add_argument("out", nargs="?", default=str(REPO / "paper" / "01_KarnaughGroupClassification.pdf"))
    ap.add_argument("--html", help="keep the intermediate HTML here (default: a temporary file that is deleted)")
    ap.add_argument("--top", default="22mm")
    ap.add_argument("--bottom", default="20mm")
    ap.add_argument("--footer-pad", default="0")
    ap.add_argument("--fs", default="10pt")
    ap.add_argument("--lh", default="1.6")
    ap.add_argument("--ls", default="-0.001em")
    ap.add_argument("--math", default="1.05em")
    ap.add_argument("--atomic", type=float, default=120, help="keep inline math up to this many px unbroken (0 = off)")
    ap.add_argument("--chrome", help="Chrome/Chromium executable (default: CHROME_PATH, a Chrome on PATH, else Playwright's Chromium)")
    ap.add_argument("--no-sandbox", action="store_true", help="pass --no-sandbox to Chrome (needed when running as root, e.g. in containers)")
    ap.add_argument("--report", help="write JSON report here")
    a = ap.parse_args()

    text = pathlib.Path(a.manuscript).read_text(encoding="utf-8")
    base = pathlib.Path(a.base).resolve()
    body, lint = md_to_html(text)
    html_doc = build_html(body, base, {"FS": a.fs, "LH": a.lh, "LS": a.ls, "MATH": a.math})
    # Chrome has to load the page from disk. Unless --html is given, use a temporary file and delete it afterwards,
    # so that no stray .html is left next to the PDF (css/js are absolute file URLs, images go through <base>).
    tmp = None
    if a.html:
        html_path = pathlib.Path(a.html).resolve()
    else:
        tmp = tempfile.TemporaryDirectory(prefix="build_pdf_")
        html_path = pathlib.Path(tmp.name) / "paper.html"
    html_path.write_text(html_doc, encoding="utf-8")

    console = []
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=a.chrome or find_chrome(), args=["--no-sandbox"] if a.no_sandbox else [])
        browser_version = br.version
        pg = br.new_page(viewport={"width": 627, "height": 1000})
        pg.emulate_media(media="print")
        pg.on("console", lambda m: console.append((m.type, m.text)))
        pg.on("pageerror", lambda e: console.append(("pageerror", str(e))))
        failed_req = []
        pg.on("requestfailed", lambda r: failed_req.append(r.url))
        pg.goto(html_path.as_uri(), wait_until="load")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        stats = pg.evaluate("window.__mathStats")
        atomized = pg.evaluate(f"window.__atomizeInline({a.atomic})") if a.atomic > 0 else 0
        fitted = pg.evaluate("window.__fitDisplay(0.975)")
        overflow = pg.evaluate(
            """() => {
              const art = document.querySelector('article');
              const W = art.getBoundingClientRect().width, L = art.getBoundingClientRect().left;
              const bad = [];
              document.querySelectorAll('article *').forEach((el) => {
                const r = el.getBoundingClientRect();
                if (r.width > 0 && (r.right - L) - W > 1)
                  bad.push({tag: el.tagName, cls: String(el.className || ''), over: Math.round((r.right - L) - W), text: (el.textContent || '').trim().slice(0, 40)});
              });
              return {scrollWidth: document.documentElement.scrollWidth, articleWidth: W, offenders: bad.slice(0, 8), n: bad.length};
            }"""
        )
        fonts = pg.evaluate(
            "Array.from(document.fonts).filter(f=>f.status==='loaded').map(f=>f.family+' '+f.weight)"
        )
        imgs = pg.evaluate(
            "Array.from(document.images).filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute('src'))"
        )
        pg.pdf(
            path=a.out,
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=FOOTER.format(pad=a.footer_pad),
            margin={"top": a.top, "bottom": a.bottom, "left": "22mm", "right": "22mm"},
        )
        br.close()
    if tmp is not None:
        tmp.cleanup()

    # metadata
    import pikepdf

    with pikepdf.open(a.out, allow_overwriting_input=True) as pdf:
        prod = str(pdf.docinfo.get("/Producer", ""))
        pdf.docinfo["/Title"] = TITLE
        pdf.docinfo["/Author"] = AUTHOR
        pdf.docinfo["/Creator"] = CREATOR
        if prod:
            pdf.docinfo["/Producer"] = prod
        pdf.save(a.out)

    report = {
        "math_total": stats.get("total"),
        "math_ok": stats.get("ok"),
        "math_fail": stats.get("fail"),
        "browser": browser_version,
        "display_fitted": fitted,
        "inline_atomized": atomized,
        "overflow_preflight": overflow,
        "math_warn_count": len(stats.get("warn", [])),
        "math_warn_sample": stats.get("warn", [])[:12],
        "stray_dollars": lint,
        "fonts_loaded": sorted(set(fonts)),
        "broken_images": imgs,
        "failed_requests": failed_req[:10],
        "console_errors": [c for c in console if c[0] in ("error", "pageerror")][:10],
    }
    if a.report:
        pathlib.Path(a.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
