"""
verify_general_n.py
===================
보충 노트 paper/GeneralizationNote.md 의 명제와 수치를 n = 2..6 에서 열거로 대조한다.

논문 본문의 수치(4변수)는 다른 verify_*.py 가 검증하며, 이 스크립트는 본문을 검증하지 않는다.
다만 n = 4 에서 본문의 값 (3,984 / 402 / 805 / 3,220 / 36,204 / 26,112) 을 그대로 재현하는지를
구현의 자체 점검으로 함께 확인한다.

두 가지 n변수 카르노맵 모델
  모델 A (층 쌓기)    : 지도 = 4-사이클(변수 2개, Gray 순서)의 곱. n 이 홀수이면 2-사이클 하나를 더한다.
                        5변수 = 4x4 지도 두 장, 6변수 = 4x4 지도 네 장. 4-사이클 = 2-큐브이므로 인접 그래프는 Q_n 이다.
  모델 B (한 축 다변수): 6변수 8x8 지도처럼 한 축에 변수 m 개를 Gray 순서의 2^m-사이클로 둔다.

검증 항목
  [A1] 모델 A 의 격자 대칭군 W_n = N x| Stab(변수 쌍 분할) 은 B_n 의 부분군이다. 위수, 지표, 배치 동치류 수.
  [A2] 그림 종류 수 = Stab_{B_n}(f) 의 S_n-상이 쌍 분할 위에 일으키는 궤도 수 (정의로 센 값과 비교).
  [C ] 궤도 수: S_n, B_n, W_n 아래 전체 / 아핀 / 자기쌍대.
  [F ] 대칭을 가진 함수의 비율.
  [B ] 모델 B: 축 하나의 이면체 대칭 중 부호 순열의 수, W' 의 위수, W' ∩ B_n, 배치 동치류, <S_n, W'> 의 위수.

기호: 입력점 x 는 정수 0..2^n-1 (x 의 j번째 비트 = 변수 j). B_n 의 원소 (pi, c) 는 점의 치환
      g(x)_j = x_{pi[j]} xor c_j 이고 c = 0 이면 S_n 의 원소이다. 함수 f 는 값 벡터이며 (f o g)(x) = f(g(x)).

사용법: python scripts/verify_general_n.py [--quick]     (--quick: 표본 수를 줄여 빠르게 돈다)
의존성: Python 3.8+, 표준 라이브러리만 사용. (선택: sympy 가 있으면 [B] 에서 군의 위수를 계산한다.)
실행 시간: 약 30초 (--quick 이면 약 10초). 환경에 따라 다르다.
"""
import itertools
import math
import random
import sys
import time
from collections import Counter
from fractions import Fraction

QUICK = "--quick" in sys.argv
T0 = time.time()
FAILS = []

# 노트에 적힌 값 (다른 구현(numpy)으로도 같은 값을 얻었다). 앞의 두 열은 OEIS A003180, A000616 의 값이다.
EXPECT_TOTALS = {  # n: (S_n 아래 궤도 수, B_n 아래 궤도 수, W_n 아래 궤도 수)  -- 전체 함수 2^(2^n)개
    2: (12, 6, 6),
    3: (80, 22, 34),
    4: (3984, 402, 805),
    5: (37333248, 1228158, 17107114),
    6: (25626412338274304, 400507806843728, 6005363762644688),
}
EXPECT_SELFDUAL = {2: (2, 1), 3: (8, 3), 4: (32, 7), 5: (1088, 83), 6: (6385408, 109950)}  # (S_n, B_n)
EXPECT_TYPES = {  # n: {그림 종류 수: 함수 개수}  (전수 계산한 n 만)
    2: {1: 16},
    3: {1: 52, 2: 204},
    4: {1: 3220, 2: 36204, 3: 26112},
}


def check(label, ok, detail=""):
    print(f"  [{'OK' if ok else '불일치'}] {label}" + (f"  -- {detail}" if detail else ""))
    if not ok:
        FAILS.append(label)


def section(title):
    print(f"\n=== {title}  [{time.time() - T0:.1f}s]", flush=True)


# ------------------------------------------------------------------ 기본 도구
def compose(p, q):
    """(p o q)[x] = p[q[x]]"""
    return tuple(p[i] for i in q)


def invert(p):
    r = [0] * len(p)
    for i, v in enumerate(p):
        r[v] = i
    return tuple(r)


def closure(gens):
    ident = tuple(range(len(gens[0])))
    seen = {ident}
    frontier = [ident]
    while frontier:
        new = []
        for g in frontier:
            for h in gens:
                k = compose(h, g)
                if k not in seen:
                    seen.add(k)
                    new.append(k)
        frontier = new
    return seen


def cycle_info(g):
    """(순환 수, 원소의 위수, 점마다의 순환 번호)"""
    cid = [-1] * len(g)
    c, order = 0, 1
    for s in range(len(g)):
        if cid[s] < 0:
            length, x = 0, s
            while cid[x] < 0:
                cid[x] = c
                x = g[x]
                length += 1
            order = order // math.gcd(order, length) * length
            c += 1
    return c, order, cid


def burnside(perms):
    s = sum(1 << cycle_info(g)[0] for g in perms)
    assert s % len(perms) == 0
    return s // len(perms)


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        p = self.p
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def pi_point_perm(n, pi):
    """변수 순열 pi 가 점에 일으키는 치환 P_pi(x)_j = x_{pi[j]}"""
    out = []
    for x in range(1 << n):
        y = 0
        for j in range(n):
            y |= ((x >> pi[j]) & 1) << j
        out.append(y)
    return out


def build_Bn(n):
    """B_n 의 모든 원소 (pi, c, g).  g(x) = P_pi(x) xor c.  c = 0 인 원소들이 S_n."""
    N = 1 << n
    elems = []
    for pi in itertools.permutations(range(n)):
        P = pi_point_perm(n, pi)
        for c in range(N):
            elems.append((pi, c, tuple(p ^ c for p in P)))
    return elems


def generators_S_B(n):
    swap = list(range(n))
    swap[0], swap[1] = swap[1], swap[0]
    cyc = [(i + 1) % n for i in range(n)]
    gS = [tuple(pi_point_perm(n, swap)), tuple(pi_point_perm(n, cyc))]
    neg0 = tuple(x ^ 1 for x in range(1 << n))
    return gS, gS + [neg0]


def structures(n):
    """변수 {0..n-1} 을 두 개씩 묶는 방법 (n 이 홀수이면 외톨이 변수 하나 포함)"""
    out = set()

    def rec(rem, cur, single):
        if not rem:
            out.add(frozenset(cur))
            return
        a, rest = rem[0], rem[1:]
        for j, b in enumerate(rest):
            rec(rest[:j] + rest[j + 1:], cur + [frozenset((a, b))], single)
        if n % 2 and not single:
            rec(rest, cur + [frozenset((a,))], True)

    rec(list(range(n)), [], False)
    return list(out)


def hbar_orbits(pis, structs):
    """변수 순열들의 집합 pis 가 (생성하는 군이) 쌍 분할 집합 위에 일으키는 궤도 수"""
    idx = {s: i for i, s in enumerate(structs)}
    dsu = DSU(len(structs))
    for pi in pis:
        for s in structs:
            img = frozenset(frozenset(pi[a] for a in blk) for blk in s)
            dsu.union(idx[s], idx[img])
    return len({dsu.find(i) for i in range(len(structs))})


# 함수를 정수(비트 마스크)로 보고 점의 치환을 바이트 표로 적용한다: (h o g)(x) = h(g(x))
def make_tables(g):
    N = len(g)
    ginv = invert(g)
    tabs = []
    for b in range((N + 7) // 8):
        t = [0] * 256
        for v in range(1, 256):
            low = v & -v
            y = 8 * b + low.bit_length() - 1
            t[v] = t[v ^ low] | ((1 << ginv[y]) if y < N else 0)
        tabs.append(t)
    return tabs


def apply_tables(tabs, h):
    r, b = 0, 0
    while h:
        r |= tabs[b][h & 255]
        h >>= 8
        b += 1
    return r


def all_function_orbits(n, gens):
    """2^(2^n) 개 함수 전체에 대한 궤도 (생성원으로 합집합-찾기). 각 함수의 대표원 번호를 돌려준다."""
    M = 1 << (1 << n)
    dsu = DSU(M)
    for g in gens:
        tabs = make_tables(g)
        for h in range(M):
            dsu.union(h, apply_tables(tabs, h))
    return [dsu.find(h) for h in range(M)]


def orbit_count_of_set(funcs, gens):
    """군에 닫힌 함수 집합의 궤도 수 (닫혀 있지 않으면 KeyError)"""
    index = {f: i for i, f in enumerate(funcs)}
    dsu = DSU(len(funcs))
    for g in gens:
        tabs = make_tables(g)
        for f, i in index.items():
            dsu.union(i, index[apply_tables(tabs, f)])
    return len({dsu.find(i) for i in range(len(funcs))})


def affine_functions(n):
    N = 1 << n
    par = [bin(x).count("1") & 1 for x in range(N)]
    out = []
    for c0 in (0, 1):
        for a in range(N):
            f = 0
            for x in range(N):
                if c0 ^ par[a & x]:
                    f |= 1 << x
            out.append(f)
    return out


def selfdual_functions(n):
    """f(~x) = 1 - f(x) 인 함수 전부 (2^(2^(n-1)) 개)"""
    N = 1 << n
    half = N // 2
    out = []
    for low in range(1 << half):
        f = low
        for x in range(half):
            if not (low >> x) & 1:
                f |= 1 << (N - 1 - x)
        out.append(f)
    return out


# ------------------------------------------------------------------ 모델 A : 4-사이클의 곱
GRAY = ((0, 0), (0, 1), (1, 1), (1, 0))
D4 = [[(e * i + k) % 4 for i in range(4)] for e in (1, 3) for k in range(4)]  # 4-사이클의 이면체 대칭 8개


def cells_of(n):
    k = n // 2
    return list(itertools.product(*([range(4)] * k + ([range(2)] if n % 2 else []))))


def arrangement_map(n, sigma, cells):
    """변수 배치 sigma: k번째 축은 변수 sigma[2k], sigma[2k+1] (Gray 순서, 앞이 상위 비트). 홀수 n 이면 마지막 변수가 층 변수."""
    k = n // 2
    out = []
    for cell in cells:
        x = 0
        for a in range(k):
            b0, b1 = GRAY[cell[a]]
            x |= (b0 << sigma[2 * a]) | (b1 << sigma[2 * a + 1])
        if n % 2:
            x |= cell[k] << sigma[n - 1]
        out.append(x)
    return tuple(out)


def grid_cell_generators(n, cells):
    """격자 대칭군의 생성원 (셀 치환): 각 축의 회전·반사, 이웃한 축 맞바꿈, (홀수 n) 층 뒤집기"""
    k = n // 2
    idx = {c: i for i, c in enumerate(cells)}

    def make(ds, tau, fl):
        w = []
        for c in cells:
            new = list(c)
            for a in range(k):
                new[tau[a]] = D4[ds[a]][c[a]]
            if n % 2:
                new[k] = c[k] ^ fl
            w.append(idx[tuple(new)])
        return tuple(w)

    ident_ds, ident_tau = (0,) * k, tuple(range(k))
    gens = []
    for a in range(k):
        for d in (1, 4):  # D4[1]: i -> i+1,  D4[4]: i -> -i
            ds = list(ident_ds)
            ds[a] = d
            gens.append(make(tuple(ds), ident_tau, 0))
    for a in range(k - 1):
        tau = list(ident_tau)
        tau[a], tau[a + 1] = tau[a + 1], tau[a]
        gens.append(make(ident_ds, tuple(tau), 0))
    if n % 2:
        gens.append(make(ident_ds, ident_tau, 1))
    return gens


def cell_perm_to_point_perm(w, P0):
    g = [0] * len(w)
    for k, wk in enumerate(w):
        g[P0[k]] = P0[wk]
    return tuple(g)


def random_symmetric_function(n, rng):
    """무작위 부호 순열 1~2개로 불변인 함수 (궤도마다 무작위 값)"""
    N = 1 << n
    gens = []
    for _ in range(rng.choice((1, 2))):
        m = min(n, rng.choice((2, 2, 3, 4, n)))
        els = rng.sample(range(n), m)
        pi = list(range(n))
        if rng.random() < 0.5:
            for a, b in zip(els[0::2], els[1::2]):
                pi[a], pi[b] = pi[b], pi[a]
        else:
            for a, b in zip(els, els[1:] + els[:1]):
                pi[a] = b
        c = rng.randrange(N) if rng.random() < 0.7 else 0
        gens.append(tuple(p ^ c for p in pi_point_perm(n, pi)))
    dsu = DSU(N)
    for g in gens:
        for x in range(N):
            dsu.union(x, g[x])
    val = {}
    out = []
    for x in range(N):
        r = dsu.find(x)
        if r not in val:
            val[r] = rng.randrange(2)
        out.append(val[r])
    return tuple(out)


def picture_types_by_definition(fv, Sn, Wgens):
    """정의: f 를 모든 변수 배치로 그렸을 때 W_n 의 작용을 무시하고 서로 다른 그림의 수.
    = {f o s : s in S_n} 안에서 W_n-궤도(오른쪽 작용)의 수"""
    remaining = {tuple(map(fv.__getitem__, s)) for s in Sn}
    types = 0
    while remaining:
        h = next(iter(remaining))
        orbit = {h}
        frontier = [h]
        while frontier:
            new = []
            for u in frontier:
                for g in Wgens:
                    v = tuple(map(u.__getitem__, g))
                    if v not in orbit:
                        orbit.add(v)
                        new.append(v)
            frontier = new
        remaining -= orbit
        types += 1
    return types


def stabilizer_pis(fv, elems):
    get = fv.__getitem__
    return {pi for pi, c, g in elems if tuple(map(get, g)) == fv}


def dfact(m):
    return math.prod(range(m, 0, -2)) if m > 0 else 1


SUMMARY = {}


def analyze(n):
    N = 1 << n
    k = n // 2
    nfact = math.factorial(n)
    section(f"모델 A, n = {n}  (입력점 {N}개, |B_n| = {2 ** n * nfact})")
    elems = build_Bn(n)
    nB = len(elems)

    # ---- B_n 전체를 한 번 훑어 순환 수, 위수, 자기쌍대 Fix 를 모은다
    sumB = sumS = sdB = sdS = 0
    bound = Fraction(0)
    for pi, c, g in elems:
        cc, order, cid = cycle_info(g)
        term = 1 << cc
        sd = 0 if any(cid[x] == cid[N - 1 - x] for x in range(N)) else 1 << (cc // 2)
        sumB += term
        sdB += sd
        if c == 0:
            sumS += term
            sdS += sd
        if order > 1 and all(order % q for q in range(2, int(order ** 0.5) + 1)):  # 소수 위수
            bound += Fraction(term, (order - 1) << N)
    assert sumS % nfact == 0 and sumB % nB == 0 and sdS % nfact == 0 and sdB % nB == 0

    # ---- [A1] 격자 대칭군
    cells = cells_of(n)
    P0 = arrangement_map(n, tuple(range(n)), cells)
    cell_gens = grid_cell_generators(n, cells)
    Wcell = closure(cell_gens)
    expected_W = 8 ** k * math.factorial(k) * (2 if n % 2 else 1)
    check(f"|W_n| = 8^k k!{' x 2' if n % 2 else ''} = {expected_W}", len(Wcell) == expected_W, f"계산 {len(Wcell)}")
    Wgens = [cell_perm_to_point_perm(w, P0) for w in cell_gens]
    W = [cell_perm_to_point_perm(w, P0) for w in Wcell]
    Wset = set(W)
    blocks = [frozenset((2 * a, 2 * a + 1)) for a in range(k)] + ([frozenset((n - 1,))] if n % 2 else [])
    bset = set(blocks)
    preserves = {pi: all(frozenset(pi[a] for a in b) in bset for b in blocks) for pi in itertools.permutations(range(n))}
    stab = {g for pi, c, g in elems if preserves[pi]}
    check("W_n = N x| Stab(쌍 분할)  (점의 치환으로 집합이 같다; 따라서 W_n 은 B_n 의 부분군)", Wset == stab)
    negs = {tuple(x ^ c for x in range(N)) for c in range(N)}
    check("W_n 은 입력 반전군 N 전체를 포함한다  =>  <S_n, W_n> = B_n", negs <= Wset)
    structs = structures(n)
    formula = dfact(n - 1) if n % 2 == 0 else dfact(n)
    check(f"[B_n : W_n] = 쌍 분할의 수 = {'(n-1)!!' if n % 2 == 0 else 'n!!'} = {formula}",
          nB % len(W) == 0 and nB // len(W) == len(structs) == formula, f"지표 {nB // len(W)}, 쌍 분할 {len(structs)}")

    # ---- 배치 동치류: P_sigma o w = P_sigma' 인 w in W_n 이 있으면 같은 류 (셀 치환으로 직접 확인)
    arrs = list(itertools.permutations(range(n)))
    amap = {sg: arrangement_map(n, sg, cells) for sg in arrs}
    lookup = {v: sg for sg, v in amap.items()}
    ws = sum(1 for g in W if g[0] == 0)  # W_n 중 순수한 변수 순열 (c = 0) 의 수
    sample = arrs if n <= 5 else random.Random(7).sample(arrs, 12)
    sizes = set()
    for sg in sample:
        Ps = amap[sg]
        cls = set()
        for w in Wcell:
            q = tuple(Ps[i] for i in w)
            if q in lookup:
                cls.add(lookup[q])
        sizes.add(len(cls))
    check(f"배치 동치류의 크기 = |W_n ∩ S_n| = {ws}  (배치 {len(sample)}개를 직접 확인)", sizes == {ws}, f"크기 {sorted(sizes)}")
    check(f"배치 동치류 수 = n!/|W_n ∩ S_n| = {nfact // ws} (= 지표)", nfact // ws == len(structs))

    # ---- [C] 궤도 수
    s_orb, b_orb, w_orb = sumS // nfact, sumB // nB, burnside(W)
    check(f"전체 함수의 궤도 수 (S_n, B_n, W_n) = {EXPECT_TOTALS[n]}", (s_orb, b_orb, w_orb) == EXPECT_TOTALS[n],
          f"계산 {(s_orb, b_orb, w_orb)}")
    gS, gB = generators_S_B(n)
    aff = affine_functions(n)
    a_s, a_b = orbit_count_of_set(aff, gS), orbit_count_of_set(aff, gB)
    check(f"아핀 함수의 궤도 수 (S_n, B_n) = (2(n+1), n+2) = {(2 * (n + 1), n + 2)}", (a_s, a_b) == (2 * (n + 1), n + 2), f"계산 {(a_s, a_b)}")
    sd_s, sd_b = sdS // nfact, sdB // nB
    check(f"자기쌍대 함수의 궤도 수 (S_n, B_n) = {EXPECT_SELFDUAL[n]}  (Fix = 0 또는 2^(c/2) 공식)", (sd_s, sd_b) == EXPECT_SELFDUAL[n],
          f"계산 {(sd_s, sd_b)}")
    if n <= 5:  # 공식을 열거와 대조
        sdf = selfdual_functions(n)
        e_s, e_b = orbit_count_of_set(sdf, gS), orbit_count_of_set(sdf, gB)
        check(f"자기쌍대 궤도 수를 함수 {len(sdf)}개 열거로 대조", (e_s, e_b) == (sd_s, sd_b), f"열거 {(e_s, e_b)}")

    # ---- [A2] 그림 종류 수
    Sn = [g for pi, c, g in elems if c == 0]
    free = None
    if n <= 4:
        M = 1 << N
        rootB = all_function_orbits(n, gB)
        rootS = all_function_orbits(n, gS)
        rootW = all_function_orbits(n, Wgens)
        check("열거로 센 궤도 수 (S_n, B_n, W_n) 가 Burnside 와 같다",
              (len(set(rootS)), len(set(rootB)), len(set(rootW))) == (s_orb, b_orb, w_orb))
        S_tabs = [make_tables(s) for s in Sn]
        rep = {}
        for f in range(M):
            rep.setdefault(rootB[f], f)
        crit = {}
        for r, f in rep.items():
            fv = tuple((f >> x) & 1 for x in range(N))
            crit[r] = hbar_orbits(stabilizer_pis(fv, elems), structs)
        dist = Counter()
        mism = 0
        for f in range(M):
            t_def = len({rootW[apply_tables(t, f)] for t in S_tabs})
            dist[t_def] += 1
            if t_def != crit[rootB[f]]:
                mism += 1
        check(f"모든 함수 {M}개에서 (정의로 센 그림 종류 수) = (안정화군 상의 궤도 수)", mism == 0, f"불일치 {mism}개")
        check(f"그림 종류별 함수 개수 = {EXPECT_TYPES[n]}", dict(dist) == EXPECT_TYPES[n], f"계산 {dict(sorted(dist.items()))}")
        osize = Counter(rootB)
        free = sum(s for s in osize.values() if s == nB)
        print(f"  B_n-안정화군이 자명한 함수: {free} / {M}  (대칭이 있는 함수의 비율 {1 - free / M:.6f})")
    else:
        rng = random.Random(20261025)
        count = 8 if QUICK else 40
        funcs = [random_symmetric_function(n, rng) for _ in range(count)]
        layers = [rng.randrange(2) for _ in range(n + 1)]
        funcs.append(tuple(layers[bin(x).count("1")] for x in range(N)))  # 완전 대칭 함수
        funcs.append(tuple(bin(x).count("1") & 1 for x in range(N)))  # 패리티
        funcs.append(tuple(rng.randrange(2) for _ in range(N)))  # 무작위 함수
        seen, mism = Counter(), 0
        for fv in funcs:
            t_def = picture_types_by_definition(fv, Sn, Wgens)
            t_crit = hbar_orbits(stabilizer_pis(fv, elems), structs)
            seen[(t_def, t_crit)] += 1
            mism += t_def != t_crit
        check(f"대칭 있는 함수 등 {len(funcs)}개에서 (정의로 센 값) = (안정화군 상의 궤도 수)", mism == 0,
              f"불일치 {mism}개; 관측된 그림 종류 수 {sorted({a for a, _ in seen})}")

    # ---- [F] 대칭을 가진 함수의 비율
    print(f"  [F] B_n-안정화군이 자명하지 않은 함수의 비율의 상계(소수 위수 순환부분군들의 합집합 경계) = {float(bound):.6f}")
    if n == 5:
        rng = random.Random(5)
        samples = 400 if QUICK else 3000
        non_id = [g for pi, c, g in elems if not (c == 0 and pi == tuple(range(n)))]
        hits = 0
        for _ in range(samples):
            fv = tuple(rng.randrange(2) for _ in range(N))
            get = fv.__getitem__
            if any(tuple(map(get, g)) == fv for g in non_id):
                hits += 1
        p = hits / samples
        print(f"      무작위 함수 {samples}개 표본: 대칭이 있는 비율 약 {p:.4f} (±{1.96 * (p * (1 - p) / samples) ** 0.5:.4f})")
    SUMMARY[n] = (len(W), len(structs), s_orb, b_orb, w_orb, float(bound), free)


# ------------------------------------------------------------------ 모델 B : 한 축에 변수 m 개
def gray_code(m):
    return [i ^ (i >> 1) for i in range(1 << m)]


def is_signed_perm(g, n):
    c = g[0]
    imgs = []
    for t in range(n):
        v = g[1 << t] ^ c
        if v == 0 or v & (v - 1):
            return False
        imgs.append(v)
    if len(set(imgs)) != n:
        return False
    for x in range(1 << n):
        y = 0
        for t in range(n):
            if (x >> t) & 1:
                y ^= imgs[t]
        if g[x] != y ^ c:
            return False
    return True


def arrangement_map_B(m, sigma, g):
    L = 1 << m
    out = []
    for i in range(L):
        for j in range(L):
            x = 0
            for t in range(m):
                x |= ((g[i] >> (m - 1 - t)) & 1) << sigma[t]
                x |= ((g[j] >> (m - 1 - t)) & 1) << sigma[m + t]
            out.append(x)
    return tuple(out)


def model_B(m):
    n, L = 2 * m, 1 << m
    N = 1 << n
    section(f"모델 B, n = {n}: {L}x{L} Gray 토러스 (한 축에 변수 {m}개)")
    g = gray_code(m)
    ginv = {v: i for i, v in enumerate(g)}
    cnt = 0
    for e in (1, L - 1):
        for kk in range(L):
            img = [g[(e * ginv[x] + kk) % L] for x in range(L)]
            cnt += is_signed_perm(img, m)
    print(f"  축 하나({L}-사이클)의 이면체 대칭 {2 * L}개 중 부호 순열(= 부울 구조를 보존)인 것: {cnt}개")
    expect_axis = {2: 8, 3: 8, 4: 8}[m]
    check(f"그 수는 {expect_axis}", cnt == expect_axis)

    cells = [(i, j) for i in range(L) for j in range(L)]
    P0 = arrangement_map_B(m, tuple(range(n)), g)

    def cell_gen(f):
        return tuple(f(i, j)[0] * L + f(i, j)[1] for i, j in cells)

    cgens = [cell_gen(lambda i, j: ((i + 1) % L, j)), cell_gen(lambda i, j: ((-i) % L, j)),
             cell_gen(lambda i, j: (i, (j + 1) % L)), cell_gen(lambda i, j: (i, (-j) % L)),
             cell_gen(lambda i, j: (j, i))]
    Wcell = closure(cgens)
    check(f"|W'| = 2^(2m+3) = {2 ** (2 * m + 3)}  (D_{L} wr Z_2)", len(Wcell) == 2 ** (2 * m + 3), f"계산 {len(Wcell)}")
    Wgens = [cell_perm_to_point_perm(w, P0) for w in cgens]
    W = [cell_perm_to_point_perm(w, P0) for w in Wcell]
    inB = [w for w in W if is_signed_perm(w, n)]
    inS = [w for w in inB if w[0] == 0]
    shift_in_B = is_signed_perm(Wgens[0], n)
    print(f"  |W'| = {len(W)},  |W' ∩ B_n| = {len(inB)},  |W' ∩ S_n| = {len(inS)},  한 칸 이동이 B_n 의 원소인가: {shift_in_B}")
    Wset = set(W)
    n_in_W = sum(1 for c in range(N) if tuple(x ^ c for x in range(N)) in Wset)
    print(f"  W' 에 드는 입력 반전: {n_in_W} / {N}  ({'N 전체를 포함' if n_in_W == N else 'N 전체를 포함하지 않는다'})")
    check("W' 에 드는 입력 반전은 16개 (m=2 에서는 N 전체, m>=3 에서는 N 의 일부)", n_in_W == 16)
    expect = {2: (128, 8), 3: (128, 2), 4: (128, 2)}[m]
    check(f"(|W' ∩ B_n|, |W' ∩ S_n|) = {expect}", (len(inB), len(inS)) == expect)
    check("한 칸 이동은 부호 순열이 아니다" if m >= 3 else "m=2 에서는 격자 대칭이 모두 B_n 에 든다", shift_in_B == (m == 2))
    nfact = math.factorial(n)
    print(f"  변수 배치 {nfact}가지는 W' 아래 {nfact // len(inS)}개의 류로 나뉜다 (모델 A 였다면 {dfact(n - 1)}개)")
    if m <= 3:
        arrs = list(itertools.permutations(range(n)))
        sample = arrs if m == 2 else random.Random(3).sample(arrs, 24)
        lookup = {arrangement_map_B(m, sg, g): sg for sg in arrs}
        sizes = set()
        for sg in sample:
            Ps = arrangement_map_B(m, sg, g)
            sizes.add(len({lookup[q] for q in (tuple(Ps[i] for i in w) for w in Wcell) if q in lookup}))
        check(f"배치 동치류의 크기 = |W' ∩ S_n| = {len(inS)}  (배치 {len(sample)}개를 직접 확인)", sizes == {len(inS)}, f"크기 {sorted(sizes)}")
    if m <= 3:
        s = burnside(W)
        print(f"  W' 아래 서로 다른 그림(함수 궤도)의 수: {s}")
        # 짝/홀수 무게 점의 분할을 보존(또는 맞바꿈)하는가
        gS, _ = generators_S_B(n)
        par = [bin(x).count("1") & 1 for x in range(N)]
        ok = all(len({par[h[x]] ^ par[x] for x in range(N)}) == 1 for h in list(Wgens) + list(gS))
        check("모든 생성원이 짝수/홀수 무게 점의 분할을 보존하거나 맞바꾼다", ok)
        try:
            from sympy.combinatorics import Permutation, PermutationGroup
        except ImportError:
            print("  (sympy 가 없어 군의 위수는 건너뜀: pip install sympy 후 다시 실행하면 <S_n, W'> 의 위수를 계산한다)")
        else:
            G = PermutationGroup([Permutation(list(x)) for x in list(gS) + list(Wgens)])
            order = G.order()
            GB = PermutationGroup([Permutation(list(x)) for x in list(gS) + inB])
            half = N // 2
            target = 2 ** n * nfact if m == 2 else math.factorial(half) ** 2 // 2
            print(f"  |<S_n, W'>| = {order}")
            check(f"|<S_n, W'>| = {'|B_n| = 384' if m == 2 else '(' + str(half) + '!)^2 / 2'}", order == target)
            check(f"|<S_n, W' ∩ B_n>| = |B_n| = {2 ** n * nfact}", GB.order() == 2 ** n * nfact)
            if m == 3:
                print("  => 군이 짝/홀수 무게 점 32개씩의 분할을 보존하고 위수가 (32!)^2/2 이므로, 분할을 고정하는 부분군은"
                      " Alt(32) x Alt(32) 이고 함수는 (두 부류의 1의 개수) 쌍으로만 구분된다: 동치류 33*34/2 = 561개 (노트 3절의 논증)")


def main():
    section("모델 A : 4-사이클의 곱 (층 쌓기)")
    for n in range(2, 7):
        analyze(n)
    model_B(2)
    model_B(3)
    if not QUICK:
        model_B(4)
    section("요약 (노트 2.3절 표)")
    print("   n | |W_n|  | 지표 | S_n 궤도 | B_n 궤도 | W_n 궤도 | 대칭 있는 함수 비율(상계 / 정확)")
    for n, (w, idx, s, b, wo, bound, free) in sorted(SUMMARY.items()):
        exact = f"정확 {1 - free / (1 << (1 << n)):.4f}" if free is not None else f"상계 {bound:.6f}"
        print(f"  {n:2d} | {w:6d} | {idx:4d} | {s} | {b} | {wo} | {exact}")
    print(f"\n총 {time.time() - T0:.1f}초. " + ("모든 항목이 일치한다." if not FAILS else f"불일치 {len(FAILS)}건: {FAILS}"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
