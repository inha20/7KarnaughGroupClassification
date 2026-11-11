# tools/build_pdf — 논문 PDF 만들기

원고 `paper/KarnaughGroupClassification.md`에서 `paper/01_KarnaughGroupClassification.pdf`를 만드는 스크립트이다. `scripts/`의 검증 스크립트와 달리 외부 패키지가 필요해서 따로 두었다. 논문 1.4절의 "표준 라이브러리 전용" 서술은 `scripts/`에만 해당한다.

## 알아둘 점

- **원래 스크립트가 아니다.** 이전 PDF를 만든 저자의 스크립트는 저장소에 없어서, 이전 PDF를 재서 같은 형식으로 다시 짰다(2026-11-11). 용지, 여백, 글꼴 크기, 줄 간격, 제목 크기, 색은 이전 PDF에서 쟀다. 바꾸기 전의 원고를 이 스크립트로 만들면 이전 PDF와 같은 23쪽이 나왔다. 그래도 줄바꿈과 쪽 나눔은 조금 다를 수 있다.
- **Chrome 버전.** `paper/`의 PDF는 Chrome 153으로 만들었다. 다른 버전의 Chrome이나 Chromium으로 만들면 쪽 나눔이 달라질 수 있다.

## 준비

1. Node.js (KaTeX와 글꼴): `cd tools/build_pdf && npm ci`
2. Python 3.10 이상: `pip install -r tools/build_pdf/requirements.txt`
3. Chrome 또는 Chromium. PATH에 Chrome이 있으면 그것을 쓰고, 없으면 `python -m playwright install chromium`으로 받은 Chromium을 쓴다. 다른 실행 파일을 쓰려면 `--chrome 경로`나 환경 변수 `CHROME_PATH`를 지정한다.

## 실행

```
python tools/build_pdf/build_pdf.py            # paper/의 원고로 paper/01_KarnaughGroupClassification.pdf를 덮어쓴다
python tools/build_pdf/build_pdf.py 원고.md 그림이_있는_폴더 출력.pdf
```

| 옵션 | 뜻 |
|:---|:---|
| `--report 파일.json` | 검사 결과를 JSON으로 저장 (화면에도 출력) |
| `--html 파일.html` | 중간 HTML을 저장 (Chrome으로 열어 볼 수 있다) |
| `--atomic PX` | 이 폭(px) 이하의 짧은 인라인 수식은 줄바꿈하지 않는다. 기본 120, 0이면 끈다 |
| `--chrome 경로` | 사용할 Chrome/Chromium |
| `--no-sandbox` | Chrome에 `--no-sandbox`를 넘긴다. root로 실행할 때(컨테이너 등)에 필요하다 |
| `--fs`, `--lh`, `--ls`, `--math`, `--top`, `--bottom` | 본문 글꼴 크기, 줄 간격, 자간, 수식 크기, 위·아래 여백 |

## 실행 후 확인할 것

스크립트는 PDF를 만든 뒤 아래를 검사해 출력한다. 현재 원고의 결과는 수식 1,132개가 모두 KaTeX 오류 없이 그려졌고, 아래 (1)~(4)가 모두 비어 있다.

1. `math_fail`: KaTeX가 읽지 못한 수식
2. `stray_dollars`: 수식으로 읽히지 않고 남은 `$`
3. `broken_images`: 불러오지 못한 그림
4. `console_errors`: 페이지의 콘솔 오류
5. `overflow_preflight`: 페이지 폭을 넘는 요소. Chrome은 폭을 넘는 요소가 하나라도 있으면 문서 전체를 조용히 축소해서 인쇄한다. 현재는 KaTeX 내부 요소 8개가 2px 넘친다고 나오는데, 알려진 현상이고 영향은 0.3% 정도의 축소뿐이다. 이보다 크게 넘치는 요소가 나오면 그 수식이 원인이다. 스크립트는 한 줄에 다 안 들어가는 별행 수식(`$$`)을 본문 폭의 97.5%에 맞춰 줄여서 이를 막는다.

PDF는 만든 뒤 눈으로도 훑어보는 것이 좋다(쪽 나눔과 수식 모양은 이 검사로 알 수 없다).

## 원고를 쓸 때 (GitHub와 PDF에서 수식이 같게 보이도록)

- **가운데 정렬 수식**은 `$$...$$`를 **앞뒤에 빈 줄이 있는 단독 문단**으로 쓴다. 문장 사이에 줄만 바꿔 끼워 넣으면 PDF에서는 가운데 정렬 수식이 되지만 GitHub에서는 문장 속 인라인 수식으로 그려진다. 단독 문단 뒤에는 이어지는 문장을 쓸 수 없으므로, 식 앞 문장은 "다음과 같다."처럼 끝내거나 식 안에 마침표를 넣는다.
- 한 줄에 다 안 들어가는 긴 별행 수식은 `\begin{aligned} ... \\ ... \end{aligned}`로 나눈다. GitHub는 긴 별행 수식을 줄이지 않고 가로 스크롤로 보여 준다.
- **닫는 `$` 바로 뒤에 `)`가 오고 수식도 `)`로 끝나면** GitHub가 그 수식을 읽지 못한다(예: `$a(k-1)$)`). 수식 끝에 `{}`를 붙이면(`$a(k-1){}$)`) 조판 결과는 그대로이고 GitHub에서도 그려진다.
- 표 안의 수식에서 절댓값이나 집합의 크기를 쓸 때는 `|` 대신 `\lvert ... \rvert`를 쓴다. `|`는 표의 열 구분으로 읽힌다.

## 어떻게 만들어지나

1. `markdown-it-py`(commonmark, 표, 취소선, `dollarmath`)가 원고를 HTML로 바꾼다. 그림 한 줄짜리 문단과 그 바로 뒤 문단은 그림과 그림 설명으로 표시한다.
2. 페이지 안에서 KaTeX가 수식을 그린다(`throwOnError`로 오류를 모은다). 글꼴은 `@fontsource`의 Noto Sans KR, Noto Sans Mono를 쓴다.
3. Playwright로 Chrome이 A4 PDF로 인쇄한다(쪽 번호는 아래 가운데). 제목, 저자, 생성 도구는 `pikepdf`로 넣는다.
