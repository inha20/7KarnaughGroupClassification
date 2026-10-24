# 7KarnaughGroupClassification

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-blue?style=flat-square&logo=github)](https://inha20.github.io/7KarnaughGroupClassification/)
[![Field](https://img.shields.io/badge/Field-Group%20Theory%20%7C%20Boolean%20Algebra-purple?style=flat-square)](https://inha20.github.io/7KarnaughGroupClassification/)
**논문 제목:** 카르노맵 위의 4변수 부울 함수 공간의 군론적 분류  
**Title:** Group-Theoretic Classification of 4-Variable Boolean Function Spaces on Karnaugh Maps  
**저자:** 최종훈 (Jonghun Choi) — 인하공업전문대학 2학년 재학 · 독립 연구자  
**GitHub Pages:** [웹 논문 및 대화형 분석 포털 보기](https://inha20.github.io/7KarnaughGroupClassification/)  

> 이 저장소의 논문은 필요한 정의와 증명을 본문에 싣는 것을 목표로 하며, 같은 저자의 다른 저장소를 읽지 않아도 따라갈 수 있게 썼습니다. 필요한 배경은 군론의 기초(군의 작용, 부분군의 지표, 반직접곱, 켤레류)와 Burnside 보조정리입니다. 일부 수치는 컴퓨터로 수행한 유한 계산이며 스크립트로 재현합니다.

---

## 📌 Keywords
Karnaugh map, Boolean function space, variable arrangement equivalence, symmetric group $S_4$, signed permutation group (hyperoctahedral group) $B_4$, Burnside's Lemma, Hamming weight layer, orbit classification, affine / monotone / self-dual functions, Post's lattice.

---

## 📖 Abstract (초록)

4변수 부울 함수 공간 $\mathcal{F}_4$ ($2^{16} = 65{,}536$개)에는 변수 순열군 $S_4$, 입력 반전군 $\mathbb{Z}_2^4$, 카르노맵 평면의 격자 대칭이 작용한다. 본 논문은 이 대칭들의 관계를 정리하고 궤도(동치류)의 개수를 모두 계산하며, 아핀(10개)과 단조(30개) 궤도는 목록까지 제시한다.

---

## 🔬 핵심 결과 (Main Results)

| # | 결과 |
|:---:|:---|
| 1 | 4변수 카르노맵의 변수 배치 $4! = 24$가지는 격자 대칭군 $W$ (위수 128; 행과 열 각각의 이동·반사와 행·열 맞바꿈이 만드는 군) 아래 **정확히 3개**의 동치류 $\{AB\|CD\}, \{AC\|BD\}, \{AD\|BC\}$로 나뉜다. $W$는 입력 반전과 변수 순열이 이루는 군 $B_4 = \mathbb{Z}_2^4 \rtimes S_4$ (위수 384)에서 변수 쌍 분할 하나의 안정화군이며 지표가 3이다. 격자의 회전·반사 8개만으로는 12개이다. |
| 2 | 완전 대칭 함수(XOR, 다수결 등 32개)의 카르노맵 그림은 24개 배치 모두에서 같다. 배치에 따라 그림이 달라지는 것은 비대칭 함수이며, 65,536개 중 26,112개가 세 동치류에서 서로 다른 그림이 된다. |
| 3 | $S_4$ 아래의 궤도 수: 전체 **3,984**, 아핀(32개) **10**, 단조(168개) **30**, 자기쌍대(256개) **32**. 모든 Burnside Fix 표를 본문에 제시한다. 3,984(OEIS A003180)와 단조 30(A003182)은 **문헌에 알려진 값의 독립 재계산**이다. |
| 4 | $S_4$와 격자 대칭이 생성하는 군은 직접곱이 아니라 $B_4$ (위수 384)이다. 이 군 아래에서 전체 공간은 **402**, 아핀은 **6**, 자기쌍대는 **7**개의 궤도이다. 402는 문헌의 4변수 NP 동치류 수(Slepian 1953)와 일치한다. |
| 5 | **그림 종류 수의 판정(정리 5).** 함수의 카르노맵 그림이 변수 배치에 따라 몇 종류가 되는지는 그 함수의 $B_4$-안정화군이 세 변수쌍 분할에 작용하는 부분(안정화군의 $S_3$ 상)의 궤도 수와 같다(그 상이 자명→3종, 위수 2→2종, 위수 6→1종). 함수 26,112 / 36,204 / 3,220개가 각각 3 / 2 / 1종이다. |

### 🖼️ 대표 그림

같은 함수 $f = m(5,6,9,10)$의 카르노맵 그림이 변수 배치에 따라 달라진다. 세 대표 배치 $AB/CD$, $AC/BD$, $AD/BC$ 가운데 $AC/BD$와 $AD/BC$의 그림은 같고 $AB/CD$의 그림만 다르다 (그림 종류 2). 논문 6.5절의 그림 8이다.

| $AB/CD$ | $AC/BD$ | $AD/BC$ |
|:---:|:---:|:---:|
| <img src="images/fig07_xorplane_ab_cd.png" alt="m(5,6,9,10), AB/CD 배치" width="220"> | <img src="images/fig08_xorplane_ac_bd.png" alt="m(5,6,9,10), AC/BD 배치" width="220"> | <img src="images/fig09_xorplane_ad_bc.png" alt="m(5,6,9,10), AD/BC 배치" width="220"> |

반면 4변수 XOR 같은 완전 대칭 함수의 그림은 24개 배치 모두에서 같다 (논문 3.5절 명제 1, 그림 5). 논문의 모든 그림은 [`images/`](images/README.md)에 있고, 그림의 값은 `scripts/verify_figures.py`로 확인했다.

> **새로움에 대한 주:** 위 표의 3,984, 402, 30은 이미 알려진 값이다. 격자 대칭군 $W$의 식별(결과 1)과 그림 종류 수(결과 2, 5)가 카르노맵에 특화된 부분이며, 우리가 검색한 범위에서는 선행 연구를 찾지 못했다. 선행 연구 조사는 제한적이다(논문 1.2절, 7.2절).

---

## 📂 저장소 구조 (Repository Structure)

```
7KarnaughGroupClassification/
├─ README.md                               ← 저장소 안내 (본 문서)
├─ LICENSE                                 ← 이용 조건 (All rights reserved)
├─ index.html                              ← 대화형 웹 논문 포털 (KaTeX)
├─ paper/
│  ├─ KarnaughGroupClassification.md     ← 논문 전문
│  ├─ 01_KarnaughGroupClassification.pdf ← 논문 PDF (원고에서 생성)
│  └─ GeneralizationNote.md              ← (보충) n변수 일반화 노트. 원고와 별개이며 원고는 수정하지 않았다
├─ images/                                 ← 논문 그림 21장 (출처·검증: images/README.md)
└─ scripts/                                ← 본문 수치를 검증하는 Python 스크립트 (표준 라이브러리만 사용)
   ├─ verify_orbits.py                     ← S4 궤도 수 (열거 + Burnside)
   ├─ verify_tables.py                     ← Fix 표, 궤도 크기 분포, 안정화군 위수, 그림 비교
   ├─ verify_double_action.py              ← S4와 격자 대칭의 합성군 크기·궤도 수
   ├─ verify_b4_table.py                   ← B4 켤레류 표와 전수 열거 대조
   ├─ verify_pictures.py                   ← 세 배치의 카르노맵 그림 전수 비교
   ├─ verify_extras.py                     ← 패리티 체커보드, 단조 30궤도 목록, B4-궤도의 W-분할, L∩M, n=5 예비 결과
   ├─ verify_picture_criterion.py          ← 정리 5(그림 종류 수 = 안정화군의 S3 상의 궤도 수), 따름정리 6, 부호 순환의 점 순환 분포
   ├─ verify_monotone_fix.py               ← 단조 Fix 값 = 궤도 순서집합의 상집합 수 (168, 50, 28, 15, 8)
   ├─ verify_stabilizer_counts.py          ← 뫼비우스(단조 궤도 크기 분포)와 포함·배제(그림 종류별 함수 3,220 / 36,204 / 26,112)
   ├─ verify_figures.py                    ← images/ 그림의 격자 값이 본문의 함수·배치·축 순서와 일치하는지 대조
   ├─ verify_clone_generators.py           ← 아핀·단조·자기쌍대 함수의 생성 연산(XOR과 상수 1 / AND, OR와 상수 / NOT과 다수결) 확인
   └─ verify_general_n.py                  ← (보충) n=2~6 일반화: 격자군, 정리 5의 일반화, 궤도 수, 8×8 모델의 붕괴 (paper/GeneralizationNote.md의 수치)
```

각 스크립트는 `python scripts/<이름>.py`로 실행한다.

---

## 🌐 관련 저장소 (선택 사항, 읽지 않아도 됨)

이 논문은 독립적으로 읽을 수 있습니다. 아래는 같은 저자의 다른 저장소이며, 읽지 않아도 됩니다.

| 저장소 | 내용 |
|:---|:---|
| [Research-Portfolio](https://github.com/inha20/Research-Portfolio) | 전체 연구 프로그램 포털 |
| [8StructuralThinkingAndHumanAICollaboration](https://github.com/inha20/8StructuralThinkingAndHumanAICollaboration) | 구조적 사고와 인간-AI 연구 협력 (자매 논문. 이 논문의 작성 과정을 사례로 다룬다, 8번 논문 4.7절) |

---

## 📜 인용 정보 (Citation)

```bibtex
@misc{choi2026karnaughgroupclassification,
  author       = {Choi, Jonghun},
  title        = {Group-Theoretic Classification of 4-Variable Boolean Function Spaces on Karnaugh Maps},
  howpublished = {Independent Mathematics Research Program Preprint},
  year      = {2026},
  url       = {https://github.com/inha20/7KarnaughGroupClassification}
}
```

---
© 2026 Jonghun Choi (최종훈). All rights reserved. 이용 조건은 [LICENSE](LICENSE)를 참조하세요.
