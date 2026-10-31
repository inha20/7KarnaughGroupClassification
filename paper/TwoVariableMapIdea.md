# 아이디어 노트: 4변수 지도를 2변수 지도 4개로 보기 — n≥5 관찰의 가능성

> **상태.** 저자(최종훈)가 낸 아이디어 한 문장을 Claude(AI)가 풀어 쓴 **초안 노트**이다. 논문 원고(`KarnaughGroupClassification.md`)는 수정하지 않았다. 저자가 의도한 형태와 다르면 이 문서를 고친다. 아래 수치는 Claude가 작업 세션에서 **저장소의 `scripts/`를 쓰지 않고 새로 짠 코드**로 계산했고(재현 코드는 부록), 저자의 검토와 외부 검증을 거치지 않았다. 선행 연구 조사는 제한적이어서(OEIS 한 건만 확인) 아래의 어느 것도 새롭다고 주장하지 않는다. 같은 구조의 형식화가 보충 노트 [`GeneralizationNote.md`](GeneralizationNote.md)의 모델 A에 이미 있다.

*2026-10-31 작성.*

## 0. 요약

1. **아이디어(저자).** 4변수 카르노맵(4×4)을 2변수 지도(2×2) 4개로 본다. 이 관점을 쓰면 $n\ge5$ 변수에서도 4변수에서 한 것과 같은 관찰(변수 배치의 동치류, 그림 종류 등)을 해 볼 수 있을 것이다.
2. **확인한 것.** 2변수 지도를 단위로 쌓으면 격자 대칭군 $W_n$은 입력 반전과 변수 순열이 이루는 군 $B_n$ 안에 머문다($n=2\sim8$). 변수 배치 동치류의 수는 변수를 두 개씩 묶는 방법의 수이고, $n=4\sim8$에서 3, 15, 15, 105, 105이다. 한 축에 3비트 이상을 두면 이렇게 되지 않는다.
3. **열린 것.** 그림 종류 수의 $n\ge5$ 분포, 소지도 프로필 불변량의 $n\ge5$ 검사, 분해 차트와의 연결 등(4절). 가설이거나 계산 전이다.

## 1. 아이디어

4변수 카르노맵은 16칸이다. 네 칸씩 묶으면 2변수 지도(2×2) 네 개가 되고, 그 네 개가 놓인 모양도 2변수 지도이다. 곧 **2변수 지도를 칸으로 갖는 2변수 지도**이다. 이 말은 두 가지로 읽을 수 있다.

- **(a) 사분면 읽기.** 표준 배치(행 AB, 열 CD, 순서 00·01·11·10)의 4×4 지도를 2×2 조각 네 개로 자른다. 각 조각은 A·C가 고정되고 B·D가 움직이는 2변수 지도이고, 조각 네 개가 놓인 모양은 A·C의 2변수 지도이다. 격자 대칭 $W$ 128개 중 이 조각 나누기를 그대로 두는 것은 32개이다(지표 4). 이 수치는 모두 $n=4$에서 부록 코드로 확인했다.
- **(b) 곱 읽기.** 행 하나(또는 열 하나)가 이미 2변수 지도 하나(네 칸이 이루는 고리)이고, 4×4 지도는 그런 고리 둘의 곱이다. 논문의 $W$는 이 읽기의 격자 대칭군이고, 보충 노트의 모델 A("층 쌓기")가 이것을 $n$변수로 형식화한다.

**$n$변수로.** 함수 하나는 2변수 지도 $2^{n-2}$개이다(5변수 8개, 6변수 16개). 함수 공간으로 쓰면 $\mathcal F_n\cong\mathcal F_{n-2}^{\,4}$이다(예: $2^{16}=16^4$). 5변수 지도를 4×4 지도 두 장으로, 6변수 지도를 네 장으로 그리는 방식도 같은 구조이다(교재별 사용 현황은 확인하지 않았다).

## 2. 왜 2변수 지도 단위인가

- 2변수 지도의 격자 대칭은 정사각형의 대칭 8개이고, 이것은 두 변수의 부호 순열(변수 맞바꿈과 입력 반전) 전체 $B_2$와 같다(논문 보조정리 1, $D_4=B_2$). 지도를 돌리거나 뒤집는 일이 변수를 맞바꾸거나 입력을 반전하는 일과 같다는 뜻이다.
- 곱 읽기에서 4변수의 $W$는 (한 지도의 대칭 8) × (다른 지도의 대칭 8) × (두 지도의 맞바꿈 2) = 128이고, 군으로는 $B_2\wr S_2$이다. 논문 보조정리 2($W$가 변수 쌍 분할 하나의 안정화군이며 지표가 3)를 곱의 말로 다시 쓴 것이다.
- 한 축에 비트를 셋 이상 두면 달라진다. $k$비트 반사 Gray 부호의 "한 칸 이동"이 부호 순열($B_k$의 원소)인지 검사하면 $k=1,2$에서만 그렇고 $k=3,4,5$에서는 아니다(부록 코드). 그래서 축마다 3비트인 8×8 지도의 격자 대칭은 $B_6$ 밖으로 나가고(논문 7.3절, 노트 3절), 2변수 단위로 쌓는 이 관점은 $B_n$ 안에 머문다.

## 3. $n\ge5$에서 확인된 것

| $n$ | $B_n$의 위수 | $W_n$의 위수 | 지표 $[B_n:W_n]$ | $S_n$-궤도 수 | $B_n$-궤도 수 | $W_n$-궤도 수 |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 8 | 8 | 1 | 12 | 6 | 6 |
| 3 | 48 | 16 | 3 | 80 | 22 | 34 |
| 4 | 384 | 128 | 3 | 3,984 | 402 | 805 |
| 5 | 3,840 | 256 | 15 | 37,333,248 | 1,228,158 | 17,107,114 |
| 6 | 46,080 | 3,072 | 15 | 25,626,412,338,274,304 | 400,507,806,843,728 | 6,005,363,762,644,688 |
| 7 | 645,120 | 6,144 | 105 | — | — | $\approx5.5\times10^{34}$ |
| 8 | 10,321,920 | 98,304 | 105 | — | — | $\approx1.2\times10^{72}$ |

$n=7,8$의 $W_n$-궤도 수의 정확한 값:

```
n=7: 55384499901749875616287366921767936
n=8: 1177898043185589553566363515187728911520072195561127105719342899265540096
```

- 칸의 모양은 $n=2k$이면 $\mathbb Z_4^k$, $n=2k+1$이면 $\mathbb Z_4^k\times\mathbb Z_2$(마지막 좌표는 층)이다. 칸 $(i_1,\dots,i_k)$는 $(x_{2a-1},x_{2a})$가 4-사이클 위의 $i_a$번째 Gray 순서인 점이다. 격자 대칭군 $W_n$은 축마다 회전·반사(8개), 축 맞바꿈, ($n$이 홀수이면) 층 뒤집기가 만든다. 위수는 $8^k\,k!$ ($n=2k$), 그 두 배($n=2k+1$)이다.
- 이 군은 변수를 두 개씩 묶는 방법 하나($n$이 홀수이면 변수 하나가 남는다)를 그대로 두는 부호 순열 전체와 같다. 점의 치환 집합이 같음을 $n=2\sim7$에서 부록 코드로, $n=8$에서 별도 코드로 확인했다. $S_n$과 $W_n$이 생성하는 군이 $B_n$임도 $n=2\sim6$에서 확인했다(부록 코드).
- 따라서 지표 $[B_n:W_n]$, 곧 변수 배치 동치류의 수는 묶는 방법의 수 $(n-1)!!$ ($n$ 짝수), $n!!$ ($n$ 홀수)이다. $n=2\sim8$에서 1, 3, 3, 15, 15, 105, 105.
- $W_n$-궤도 수는 배치 하나를 고정하고 격자 대칭을 같은 그림으로 볼 때 서로 다른 지도 그림의 수이다. $n\le6$은 보충 노트의 표와 같다. $n=4$의 805는 OEIS [A255016](https://oeis.org/A255016)의 $a(4)$와도 같다. 그 수열은 토러스 $n\times n$ 이진 배열을 행·열 각각의 이동·반사와 전치로 묶은 개수이므로 $n=4$에서는 같은 군 작용이다(참고문헌에 Ethier–Lee, *J. Integer Seq.* 18, 2015가 있고 원문은 읽지 않았다). $n=7,8$의 값은 이 저장소의 노트에 없던 값이며, 두 가지 구현(numpy를 쓴 코드와 부록의 표준 라이브러리 코드)이 같은 값을 냈다.
- $S_n$·$B_n$ 열은 $n\le6$에서 다시 계산한 값이다(노트의 표와 같고, 노트는 OEIS A003180, A000616과 같다고 적었다). "—"는 계산하지 않았다는 뜻이다.

## 4. 이 관점으로 해 볼 수 있는 관찰 (가능성)

꼬리표: **[열린 문제]** 저장소 문서에 이미 문제로 적힌 것 · **[가설]** 구조상의 근거는 있으나 확인한 식이 없는 것 · **[n=4만 계산]** 4변수에서만 계산한 것.

1. **그림 종류 수의 $n\ge5$ 분포 [열린 문제].** 곱 읽기에서는 보충 노트의 명제 A2(그림 종류 수 = 함수의 $B_n$-안정화군의 $S_n$ 상이 변수 묶음의 집합에 일으키는 궤도 수)가 논문 정리 5를 $n$변수로 옮긴다. 지표가 $n=5,6$에서 15, $n=7,8$에서 105로 커지므로 4변수의 1·2·3종보다 많은 값이 가능하다. 노트는 표본으로 $n=5$에서 {1, 2, 3, 4, 6, 9, 15}를 관찰했다(가능한 값의 전체 목록이 아니다). 종류별 함수의 수는 계산하지 않았다(노트 6절 1).
2. **2변수 지도 하나를 떼어 내는 재귀 [가설].** $n$에 2를 더하면 묶는 방법의 수가 3 → 15 → 105로 늘어난다. 2변수 지도 하나를 떼어 내면 남는 것이 $(n-2)$변수 지도이므로($W_n\supset B_2\times W_{n-2}$), 궤도 수나 그림 종류 수에 재귀 관계가 있는지 볼 수 있다. 구조 말고는 근거가 없고 확인한 식도 없다.
3. **소지도 프로필 [n=4만 계산].** 변수 쌍 하나를 안쪽으로 잡으면 함수는 2변수 함수 $2^{n-2}$개(소지도)로 갈라진다. 2변수 함수 16개는 $B_2$ 아래 여섯 모양(상수 0, 상수 1, 문자 하나, 두 문자의 곱, 두 문자의 합, XOR·XNOR)으로 나뉜다. 쌍마다 모양별 개수를 세어 $\mathbb N^6$의 벡터를 만들고, 모든 변수 쌍의 벡터를 순서 없이 모으면 $B_n$-불변량이 된다(소지도가 쌍 안의 입력 반전·맞바꿈으로는 모양을 바꾸지 않기 때문이다). $n=4$에서 계산하면 65,536개 함수 모두에서 $B_4$-궤도 안의 값이 같고(불변량임을 전수 확인), 402개 궤도의 값은 386가지이다. 370개 궤도는 값이 다른 궤도와 겹치지 않고 나머지 32개는 16쌍이 값을 공유한다. $n\ge5$는 계산하지 않았다. 변수 쌍별 여인수(cofactor)로 만든 서명과 가까워 보이나 선행 문헌은 확인하지 않았다(부록 코드 2).
4. **분해 차트(Ashenhurst–Curtis)와의 연결 [가설].** 크기 2인 묶음 집합(bound set) $\{a,b\}$마다 분해 차트를 그리면 열 4개와 행 $2^{n-2}$개가 나오고, 행 하나가 곧 소지도 하나이다. $n=4$에서는 세 쌍 분할이 논문의 세 배치(AB|CD, AC|BD, AD|BC)와 맞고, $n\ge5$에서는 묶음 후보가 $\binom n2$개이다. 소지도 프로필과 열 다중도의 관계, 그림 종류 수와의 관계는 확인하지 않았다. 저장소 `TODO.md`의 "응용 맥락 한 가지 연결" 항목이 같은 가설을 $n=4$에서 적고 있다.
5. **사분면 읽기의 형식화 [열린 문제].** 읽기 (a)가 보존하는 격자 대칭은 $n=4$에서 $W$의 지표 4 부분군(32개)이다. 이 부분군이 쌍 묶음의 안정화군과 어떤 관계인지, $n\ge5$에서 곱 읽기와 어떻게 다른 군을 주는지는 모른다.

## 5. 확인하지 않은 것과 한계

- **저자의 의도.** 이 문서는 한 문장의 아이디어를 위 (a), (b) 두 가지로 읽었다. 저자가 의도한 읽기가 (a)인지 (b)인지, 또는 다른 것인지는 확인하지 않았다.
- **증명.** 일반 $n$에서 $W_n$이 변수 쌍 묶음 하나의 안정화군이라는 증명은 보충 노트의 명제 A1에 있고 저자의 검토 전이다. 이 문서는 $n\le8$에서 직접 확인했을 뿐이다.
- **선행 연구.** OEIS A255016 한 건($n=4$의 805)만 확인했다. 군의 구조($B_2\wr S_k$, 쌍 묶음의 안정화군), 소지도 프로필, 분해 차트와의 관계는 모두 선행 문헌이 있을 수 있다.
- **수치.** $n=7,8$의 $W_n$-궤도 수와 $n=4$의 프로필 결과는 외부 값과 대조하지 않았다.
- **계산하지 않은 것.** 그림 종류 수의 분포($n\ge5$), $B_n$-궤도 수($n\ge7$), 프로필 불변량($n\ge5$), 사분면 읽기의 일반 $n$.

## 부록: 재현 코드 (표준 라이브러리만 사용)

<details>
<summary>코드 1 — 군의 위수·궤도 수·Gray 이동·사분면 읽기 (n=8까지 약 12초)</summary>

```python
"""2변수 지도 단위(모델 A)의 격자 대칭군 W_n: 위수, 함수의 궤도 수 등 (표준 라이브러리만 사용).
실행: python appendix_stdlib.py [nmax]   (nmax 기본값 6. n=7, 8은 W_n만 계산하며 n=8은 약 10초, 메모리 약 0.3GB)"""
import itertools
import math
import sys

GRAY = [(0, 0), (0, 1), (1, 1), (1, 0)]  # 4-사이클 축의 칸 i -> (x_{2a-1}, x_{2a})


def point(n, cell):
    """칸 -> 입력점. 비트 j가 변수 x_{j+1}. n이 홀수이면 마지막 좌표는 층(0 또는 1)."""
    x = 0
    for a, i in enumerate(cell[: n // 2]):
        b1, b2 = GRAY[i]
        x |= (b1 << (2 * a)) | (b2 << (2 * a + 1))
    return x | ((cell[-1] << (n - 1)) if n % 2 else 0)


def generators(n):
    """격자 대칭의 생성원(입력점의 치환): 축마다 회전·반사, 축 맞바꿈, (n 홀수) 층 뒤집기."""
    k = n // 2
    cells = list(itertools.product(*[range(4)] * k, *([range(2)] if n % 2 else [])))
    idx = {c: point(n, c) for c in cells}

    def perm(f):
        p = [0] * (1 << n)
        for c in cells:
            p[idx[c]] = idx[f(c)]
        return tuple(p)

    gens = []
    for a in range(k):
        gens.append(perm(lambda c, a=a: c[:a] + ((c[a] + 1) % 4,) + c[a + 1:]))
        gens.append(perm(lambda c, a=a: c[:a] + ((-c[a]) % 4,) + c[a + 1:]))
        if a + 1 < k:
            gens.append(perm(lambda c, a=a: c[:a] + (c[a + 1], c[a]) + c[a + 2:]))
    if n % 2:
        gens.append(perm(lambda c: c[:-1] + (1 - c[-1],)))
    return gens


def sym_generators(n):
    """S_n의 생성원(이웃한 두 변수의 맞바꿈)을 점의 치환으로."""
    def swap(x, j):
        return x ^ ((1 << j) | (1 << (j + 1))) if ((x >> j) ^ (x >> (j + 1))) & 1 else x
    return [tuple(swap(x, j) for x in range(1 << n)) for j in range(n - 1)]


def pair_stabilizer(n):
    """변수를 {x1,x2},{x3,x4},...로 짝지은 모양을 그대로 두는 부호 순열 전체(점의 치환).
    n이 홀수이면 마지막 변수는 혼자 남아 제자리에 있다."""
    k, N, out = n // 2, 1 << n, set()
    for order in itertools.permutations(range(k)):  # 짝들의 순서 바꾸기
        for flips in itertools.product((0, 1), repeat=k):  # 짝 안에서 두 변수를 맞바꿀지
            pi = list(range(n))
            for a in range(k):
                d = 2 * order[a]
                pi[2 * a], pi[2 * a + 1] = (d + 1, d) if flips[a] else (d, d + 1)
            base = [sum(((x >> j) & 1) << pi[j] for j in range(n)) for x in range(N)]
            for eps in range(N):  # 입력 반전
                out.add(tuple(base[x ^ eps] for x in range(N)))
    return out


def group(gens):
    """생성원이 만드는 군의 모든 원소(너비 우선)."""
    e = tuple(range(len(gens[0])))
    seen, todo = {e}, [e]
    while todo:
        g = todo.pop()
        for s in gens:
            h = tuple(s[x] for x in g)
            if h not in seen:
                seen.add(h)
                todo.append(h)
    return seen


def cycles(p):
    seen, c = [False] * len(p), 0
    for i in range(len(p)):
        if not seen[i]:
            c += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = p[j]
    return c


def orbits(G):
    """Burnside: 점 N개 위의 함수 2^N개를 군 G로 묶은 궤도 수 = (1/|G|) * sum 2^(순환 수)."""
    total = sum(1 << cycles(g) for g in G)
    assert total % len(G) == 0
    return total // len(G)


def gray_shift_in_Bk(k):
    """k비트 반사 Gray 부호의 한 칸 이동이 부호 순열(= B_k의 원소)인가."""
    g = [i ^ (i >> 1) for i in range(1 << k)]
    s = {g[i]: g[(i + 1) % len(g)] for i in range(len(g))}
    c = s[0]
    cols = [s[1 << j] ^ c for j in range(k)]
    if any(bin(v).count("1") != 1 for v in cols) or len(set(cols)) != k:
        return False

    def image(x):
        y = c
        for j in range(k):
            if (x >> j) & 1:
                y ^= cols[j]
        return y

    return all(image(x) == s[x] for x in range(1 << k))


def quadrants_n4():
    """n=4 사분면 읽기: 조각마다 움직이는 변수, 조각 나누기를 그대로 두는 W의 원소 수, 조각 사이의 이웃 관계."""
    n = 4
    quads = {}
    for c in itertools.product(range(4), range(4)):
        quads.setdefault((c[0] // 2, c[1] // 2), set()).add(point(n, c))
    blocks = [sorted(q) for q in quads.values()]
    moving = [[j + 1 for j in range(n) if len({(p >> j) & 1 for p in q}) == 2] for q in blocks]
    as_sets = {frozenset(q) for q in blocks}
    W = group(generators(n))
    keep = sum(all(frozenset(g[x] for x in q) in as_sets for q in blocks) for g in W)
    deg = [sum(any(bin(p ^ r).count("1") == 1 for p in bi for r in bj) for bj in blocks if bj is not bi)
           for bi in blocks]
    print(f"사분면 읽기(n=4): 조각마다 움직이는 변수 x번호 {moving}, W의 {keep}/{len(W)}개가 조각 나누기를 보존, "
          f"조각 하나에 이웃한 조각 수 {deg}")


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    for n in range(2, nmax + 1):
        W = group(generators(n))
        k = n // 2
        formula = 8 ** k * math.factorial(k) * (2 if n % 2 else 1)
        Bn = 2 ** n * math.factorial(n)
        line = f"n={n}  |W_n|={len(W)} (식 {formula})  지표={Bn // len(W)}  W_n-궤도 수={orbits(W)}"
        if n <= 7:
            line += f"  W_n이 짝 안정화군과 같은가: {W == pair_stabilizer(n)}"
        if n <= 6:
            S = group(sym_generators(n))
            B = group(sym_generators(n) + [tuple(x ^ 1 for x in range(1 << n))])
            J = group(generators(n) + sym_generators(n))
            line += (f"  S_n-궤도 수={orbits(S)}  B_n-궤도 수={orbits(B)}"
                     f"  |B_n|={len(B)}(식 {Bn})  |<S_n,W_n>|={len(J)}")
        print(line)
    for k in range(1, 6):
        print(f"k={k}: 한 칸 이동이 B_k의 원소인가: {gray_shift_in_Bk(k)}")
    quadrants_n4()
```

`python 파일이름.py 8`처럼 인자로 $n$의 최댓값을 준다(기본 6). 출력의 값이 위 1~3절의 수치이다.

</details>

<details>
<summary>코드 2 — 소지도 프로필 불변량 (n=4, 약 2초)</summary>

```python
"""n=4: 소지도 프로필 불변량이 B4-궤도(402개)를 얼마나 구별하는지 (표준 라이브러리만 사용)."""
import itertools
from collections import Counter, defaultdict

n, N = 4, 16


def bit_perm(pi):  # 변수 순열 pi를 점의 치환으로
    return [sum(((x >> j) & 1) << pi[j] for j in range(n)) for x in range(N)]


GENS = [bit_perm([1, 0, 2, 3]), bit_perm([1, 2, 3, 0]), [x ^ 1 for x in range(N)]]  # B4의 생성원


def apply(mask, p):  # 함수(16비트 마스크)에 점의 치환을 적용
    return sum(((mask >> p[x]) & 1) << x for x in range(N))


def b2_class(g):  # 2변수 함수 g(4비트)의 B_2-궤도 = 모양(대표는 최솟값)
    out = set()
    for swap, fa, fb in itertools.product((0, 1), repeat=3):
        h = 0
        for xa, xb in itertools.product((0, 1), repeat=2):
            ya, yb = xa ^ fa, xb ^ fb
            if swap:
                ya, yb = yb, ya
            h |= ((g >> (2 * yb + ya)) & 1) << (2 * xb + xa)
        out.add(h)
    return min(out)


SHAPE = {g: b2_class(g) for g in range(16)}
SHAPE_ID = {s: i for i, s in enumerate(sorted(set(SHAPE.values())))}  # 모양 6가지
PAIRS = list(itertools.combinations(range(n), 2))


def profile(mask):  # 변수 쌍마다: 안쪽 쌍을 그 둘로 잡았을 때 소지도 4개의 모양별 개수
    prof = []
    for a, b in PAIRS:
        rest = [j for j in range(n) if j not in (a, b)]
        cnt = [0] * len(SHAPE_ID)
        for r in range(4):
            base = sum(((r >> t) & 1) << j for t, j in enumerate(rest))
            g = 0
            for xa, xb in itertools.product((0, 1), repeat=2):
                g |= ((mask >> (base | (xa << a) | (xb << b))) & 1) << (2 * xb + xa)
            cnt[SHAPE_ID[SHAPE[g]]] += 1
        prof.append(tuple(cnt))
    return tuple(sorted(prof))  # 변수 쌍의 순서를 지운다 -> B4-불변량


parent = list(range(1 << N))  # B4-궤도: 합집합-찾기


def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


for m in range(1 << N):
    for p in GENS:
        a, b = find(m), find(apply(m, p))
        if a != b:
            parent[a] = b

inv = defaultdict(set)  # 궤도 -> 그 원소들의 불변량 값
for m in range(1 << N):
    inv[find(m)].add(profile(m))
share = defaultdict(int)  # 불변량 값 -> 그 값을 갖는 궤도 수
for s in inv.values():
    assert len(s) == 1  # 궤도 안에서 값이 같아야 불변량이다
    share[next(iter(s))] += 1
print("B4-궤도", len(inv), "/ 불변량 값", len(share), "/ 값을 공유하는 궤도 수별 개수", dict(Counter(share.values())))
```

</details>

---

*2026-10-31, 저자의 아이디어를 Claude와 함께 정리했다.*
