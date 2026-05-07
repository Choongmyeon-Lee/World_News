# Credibility Rubric

cross-verifier가 사건별 신뢰도(HIGH/MEDIUM/LOW/DROP)를 부여할 때 사용하는 루브릭.

## 목차
1. 4-등급 정의
2. 등급 결정 트리 (Decision Tree)
3. 다중 출처 vs 받아쓰기 구분
4. 단독 보도 처리 규칙
5. 공식 발표 처리 규칙
6. 자주 발생하는 함정
7. 등급별 보고서 처리

---

## 1. 4-등급 정의

| 등급 | 의미 | 보고서 처리 |
|------|------|------------|
| **HIGH** | 사실 확정성이 매우 높음. 시장 의사결정에 활용 가능. | 본문 게재, "[HIGH]" 태그 |
| **MEDIUM** | 사실 가능성 높지만 출처가 단일이거나 부분 확인. | 본문 게재, "[MEDIUM]" 태그 + 영향 강도 한 단계 디스카운트 |
| **LOW** | 단독 보도 + 검증 미완 / 매체 간 사실 불일치. | 본문 제외, "주의" 섹션에 1줄 |
| **DROP** | 사실 오류·정정·SNS 단독·부인됨. | 보고서 제외, drop_log에만 기록 |

## 2. 등급 결정 트리

```
[1] 공식 발표(정부·중앙은행·SEC 등) URL이 확인되는가?
├─ YES → 1차 통신사(Tier 1) 보도가 함께 있는가?
│        ├─ YES → HIGH
│        └─ NO  → MEDIUM (공식 발표만 있고 매체 보도가 없는 건 드물지만, 발표 시점 기준 5분 내라면 MEDIUM, 1시간 후에도 매체가 받지 않으면 비주류 발표)
└─ NO  → [2]로

[2] Tier 1-2 매체가 몇 개 사실을 일치 보도?
├─ 3개 이상 일치 → HIGH (단, 모두가 동일한 1개 출처를 받아쓴 게 아니어야)
├─ 2개 일치 → MEDIUM
├─ 1개 단독 → [3]으로
└─ 0개 (Tier 3-4만) → LOW

[3] 1개 단독 보도의 성격은?
├─ Tier 1 통신사의 자체 취재 + 익명 아닌 공식 소식통 인용 → MEDIUM
├─ Tier 1 통신사의 자체 취재이지만 익명 소식통만 → LOW
├─ Tier 2-3 매체 단독 → LOW
└─ Tier 4 단독 / SNS 발 → DROP

[4] 다음 중 하나라도 해당하면 즉시 강등
├─ 같은 사건에 사실 오류 정정 보도가 등장 → DROP (is_corrected_or_retracted: true)
├─ 정부·기업·당사자가 공식 부인 → DROP
├─ 매체 간 핵심 수치(사망자, 금액, 시점) 불일치 → 한 단계 강등 (HIGH→MEDIUM, MEDIUM→LOW)
└─ 사건의 정의 자체가 매체마다 다름 → MEDIUM 이하
```

## 3. 다중 출처 vs 받아쓰기 구분

**진짜 다중 확인:**
- 매체 A의 기사 본문에 매체 A 자체 기자 바이라인 + 자체 취재 인용
- 매체 B도 마찬가지로 자체 바이라인 + 매체 B의 별도 소식통
- → 2개 1차 확인

**가짜 다중 확인 (받아쓰기):**
- 매체 A의 기사 본문에 "Reuters에 따르면", "according to Bloomberg"
- 매체 B, C, D도 모두 동일 출처 인용
- → 1개 1차 확인 (Reuters/Bloomberg)이며, A/B/C/D는 "추가 출처"로만 인정

**식별 방법:**
1. 본문에 "according to" / "as reported by" / "Reuters에 따르면" 같은 표현이 있는지
2. 바이라인(저자명)이 자체 기자인지, "AP" / "Reuters" 같은 통신사 표기인지
3. 인용된 소식통이 매체별로 다른지, 동일한지

`primary_sources_count`에는 **자체 취재한 1차 매체 수만** 카운트. 받아쓴 매체는 `secondary_sources_count`로.

## 4. 단독 보도 처리 규칙

**MEDIUM 자격 단독:**
- Reuters/AP/Bloomberg 단독 + 자체 취재 표시 + 익명이 아닌 공식 소식통
- 예: "Treasury Secretary tells Reuters in interview..."

**LOW 자격 단독:**
- Tier 1 단독이지만 익명 소식통만 ("sources familiar with the matter")
- Tier 2-3 단독 보도

**예외 — 단독이라도 HIGH:**
- 발표 직후 5분 이내 (다른 매체가 받기 전이라 단독으로 보임) + 공식 발표 URL 확인
- 1차 통신사가 자체 데이터 분석으로 보도 (예: Reuters가 위성 이미지 분석)

## 5. 공식 발표 처리 규칙

**정부·중앙은행 공식 보도자료 + 1차 매체 보도 = HIGH**

다음은 자동 HIGH:
- Federal Reserve FOMC statement (federalreserve.gov)
- BLS 데이터 발표 (bls.gov, 예정 시각 정확)
- USTR 관세 공시 (ustr.gov)
- OFAC 제재 공시 (ofac.treasury.gov)
- SEC 8-K (sec.gov)
- ECB monetary policy decision

**다만:**
- 공식 발표가 "보도자료(press release)"가 아니라 "정상 또는 고위 인사의 발언" 인용이면 MEDIUM (말은 번복될 수 있음)
- 정부 공식 X(트위터) 계정 발언은 사실로 확정되기 전까지 MEDIUM

## 6. 자주 발생하는 함정

### 함정 1: 같은 통신사 기사를 여러 사이트에 게재
Reuters 기사가 Yahoo News, MSN, 한국 매체에 동시 게재되는 경우. 1개 1차 확인이지 다중 확인이 아님.

### 함정 2: "분석" / "전망" / "expected" 보도
"전문가들은 X가 일어날 것으로 본다" 류 보도는 **사건이 아닌 의견**. 이런 보도는 사건으로 다루지 않거나, 의견임을 명시하고 LOW로 강등.

### 함정 3: 헤드라인과 본문 불일치
헤드라인은 강하게 단정하지만 본문은 조건부("if confirmed", "could lead to"). 본문 기준으로 평가.

### 함정 4: 시각 차이로 인한 중복
같은 사건이 발표 시점·현지 시간 차이로 다르게 보도. 같은 사건이면 1개로 묶어야.

### 함정 5: 정정 보도 누락
1시간 전 보도가 정정·철회됐는데도 캐시에 남은 경우. `WebFetch`로 원문 URL 직접 확인하여 정정·삭제 여부 체크.

### 함정 6: "Anonymous Sources" 체인
"sources told CNN, who confirmed to Reuters" 같은 표현은 출처가 1개일 가능성이 높음. 익명 소식통이 매체 간 공유되는지 추적.

### 함정 7: 의도적 리크(leak)
정책 발표 전 의도적으로 흘린 정보가 정식 발표와 약간 다른 경우. 정식 발표 후 사실이 변경됐다면 사건 정보를 갱신.

## 7. 등급별 보고서 처리

| 등급 | 본문 게재 | 영향 분석 디스카운트 | TL;DR 후보 | 출처 부록 게재 |
|------|----------|---------------------|-----------|---------------|
| HIGH | YES | 없음 | YES | YES |
| MEDIUM | YES | 한 단계 (high→medium) | 영향이 클 때만 | YES |
| LOW | NO (주의 섹션 1줄) | N/A | NO | YES (간략히) |
| DROP | NO | N/A | NO | NO (drop_log에만) |

## credibility_reason 작성 가이드

verifier 출력 JSON의 `credibility_reason`은 한 줄로 다음 정보를 포함:
- 1차 매체 수와 매체 이름
- 공식 발표 확인 여부
- 강등 사유 (있으면)

**예시:**
- HIGH: "Treasury 공식 발표 + Reuters/Bloomberg/AP 일치 보도"
- MEDIUM: "FT 단독 + 공식 소식통 인용 (FT bylined reporter)"
- LOW: "WSJ 단독, 익명 소식통, 다른 매체 미보도"
- DROP: "X(트위터) 단독, Reuters의 부인 보도 확인됨"
