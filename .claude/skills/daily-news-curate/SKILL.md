---
name: daily-news-curate
description: 매일 직전 24시간(KST 기준) 국제정세 뉴스를 다수 신뢰 매체에서 수집·교차검증·시장영향 분석·신뢰도 필터링하여 마크다운 보고서(reports/YYYY-MM-DD.md)로 작성. 사용자 트리거 표현 "오늘 뉴스 정리", "국제정세 브리핑", "데일리 뉴스", "daily news brief", "/daily-news-curate". GitHub Actions cron(매일 KST 07:00)에서도 자동 호출됨. 보고서 재실행/업데이트, 특정 날짜 보고서 재생성, 부분 갱신(예: "통화정책 부분만 다시"), 어제 보고서 갱신 요청도 이 스킬을 사용. 단순 "뉴스 어때?" 같은 잡담은 제외.
---

# daily-news-curate (오케스트레이터)

매일 직전 24시간의 국제정세 뉴스를 4명의 전문 에이전트 팀이 협업하여 수집·검증·분석·작성한다. 미국 주식 투자자 관점에서 시장 영향이 큰 사건만 골라 신뢰도 높은 정보로 정리한다.

## 실행 모드

**에이전트 팀** (Phase 0의 환경변수 활성 확인됨, `TeamCreate` 패턴). Phase 2~5에서 4명이 파이프라인으로 협업하며, 검증·분석 단계에서 필요시 `SendMessage`로 이전 에이전트에게 추가 정보 요청.

## 팀 구성

| 에이전트 | 역할 | 산출물 |
|---------|------|--------|
| `news-collector` | 24시간 뉴스 수집 (4 카테고리) | `_workspace/01_collected.json` |
| `cross-verifier` | 출처 교차검증 + 신뢰도 평가 | `_workspace/02_verified.json` |
| `market-analyst` | 미국 주식 시장 영향 분석 | `_workspace/03_analyzed.json` |
| `report-writer` | 마크다운 보고서 작성 | `reports/YYYY-MM-DD.md` |

## 데이터 흐름

```
[news-collector] ──01_collected──> [cross-verifier] ──02_verified──> [market-analyst] ──03_analyzed──> [report-writer] ──> reports/YYYY-MM-DD.md
                                          │ (옵션)                          │ (옵션)
                                          ▼ SendMessage                     ▼ SendMessage
                                     [news-collector]                  [cross-verifier]
                                     "evt_X 추가 출처"                 "evt_X 사실 명료화"
```

전송 방식:
- **태스크 기반:** 작업 흐름은 `TaskCreate`로 파이프라인 의존성 관리
- **파일 기반:** 모든 산출물은 `_workspace/`의 약속된 경로에 저장 (감사 추적)
- **메시지 기반:** 후행 에이전트가 선행에게 보완 요청 (`SendMessage`)

---

## 워크플로우

### Phase 0: 컨텍스트 확인

실행 전 다음을 확인:

1. **실행 시각 (UTC 및 KST 변환):** `date -u`로 UTC 시각 확인, KST(UTC+9)로 변환하여 시간창 결정. 보고서 파일명은 KST 기준 날짜.
2. **이전 산출물 확인:**
   - `reports/{오늘 KST 날짜}.md` 존재? → **재생성 모드** (사용자가 명시 요청한 경우만 덮어쓰기, 기본은 `_v2` 접미사)
   - `_workspace/01_collected.json` 등 잔여 산출물 → 이전 실행이 중간에 중단된 상태. 사용자에게 "기존 산출물 사용 vs 처음부터 재실행" 확인 (자동 실행이면 처음부터)
   - 사용자가 부분 작업 요청 (예: "검증만 다시"): 해당 단계부터 시작
3. **이전 보고서 참조 (있으면):** `reports/{어제 KST 날짜}.md`를 collector·writer에게 전달 — 후속 보도 식별용.
4. **watchlist 로드:** `watchlist.yaml`(repo 루트)을 읽어 collector·analyst·writer에게 전달. 파일 없으면 watchlist 섹션 비활성화하고 카테고리 뉴스만 처리.

### Phase 1: 팀 생성

`TeamCreate`로 4명 팀 구성:

```
TeamCreate(
  team_name: "daily-news-team-{YYYY-MM-DD}",
  members: [
    {name: "news-collector", subagent_type: "news-collector", model: "opus"},
    {name: "cross-verifier", subagent_type: "cross-verifier", model: "opus"},
    {name: "market-analyst", subagent_type: "market-analyst", model: "opus"},
    {name: "report-writer", subagent_type: "report-writer", model: "opus"}
  ]
)
```

> 모든 Agent/팀원 호출에 `model: "opus"` 명시. 환경변수 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 활성 시 IDE에 팀원별 메시지가 시각화됨.

### Phase 2: 수집 (raw_news.json 변환)

> **2026-05-08~ 변경:** WebSearch/WebFetch 비활성 환경 대응. 뉴스는 GitHub Actions의 Python step(`scripts/fetch_news.py`)이 Google News RSS로 미리 fetch하여 `_workspace/raw_news.json`에 저장. collector는 이 파일을 읽어 events[]로 변환만 수행.

`TaskCreate`로 collector에 작업 부여:

- 입력: `_workspace/raw_news.json`, **`watchlist.yaml`**, 어제 보고서 경로(있으면)
- 작업: raw_news.json의 카테고리·watchlist 항목을 읽어 의미적 중복 제거 후 events[] 생성. 같은 사건이 여러 카테고리/watchlist에 나오면 `event_id` 통합 + `affects_watchlist` 표시.
- 산출물: `_workspace/01_collected.json`
- 완료 신호: `TaskUpdate(status: "completed", message: "산출물 경로")`

### Phase 3: 검증

collector 완료 확인 후 verifier에 작업 부여:

- 입력: `_workspace/01_collected.json`
- 산출물: `_workspace/02_verified.json`
- **추가 요청 가능:** verifier가 `SendMessage(to: "news-collector")`로 특정 사건의 출처 보완 요청. 1회 한정 (무한 루프 방지). collector 회신 후 검증 재개.

### Phase 4: 시장 영향 분석

verifier 완료 후 analyst에 작업 부여:

- 입력: `_workspace/02_verified.json` (HIGH/MEDIUM 사건만 분석), **`watchlist.yaml`**
- 작업: 매크로/섹터/티커 영향 + watchlist 종목·지수에 대한 직접 영향(`watchlist_impact` 필드)
- 산출물: `_workspace/03_analyzed.json`
- 추가 요청 가능: `SendMessage(to: "cross-verifier")`로 사실 명료화 요청 (1회 한정)

### Phase 5: 보고서 작성

analyst 완료 후 writer에 작업 부여:

- 입력: `_workspace/02_verified.json`, `_workspace/03_analyzed.json`, **`watchlist.yaml`**, 어제 보고서(있으면), 템플릿(`assets/report-template.md`)
- 작업: 카테고리 섹션 + 시장 영향 종합 + **"관심 종목 뉴스" 섹션(0건이면 생략)** + LOW 주의 + 출처 부록
- 산출물: `reports/{오늘 KST 날짜}.md`
- 완료 신호: 파일 경로 + 분석 메타(HIGH/MEDIUM/LOW/DROP 건수, watchlist 종목별 게재 건수)

### Phase 6: 종료

1. 팀 정리: `TeamDelete`
2. 사용자 (또는 GitHub Actions 로그)에 결과 요약:
   - 보고서 경로
   - 사건 수: HIGH n / MEDIUM n / LOW n / DROP n
   - 검색 매체 수
3. **`_workspace/` 보존** — 감사 추적용. `.gitignore`에 포함되어 repo엔 푸시 안 됨.

---

## 에러 핸들링

| 에러 | 처리 |
|------|------|
| 에이전트 작업 실패 (1차) | 1회 재시도 |
| 재시도 후도 실패 | 해당 단계 산출물 없이 다음 단계 진행. 보고서에 "[단계명] 실패" 명시 |
| WebSearch/WebFetch 모두 실패 | collector가 빈 events 리스트 반환. 보고서에 "수집 실패 — 네트워크 문제 가능성" |
| 신뢰도 HIGH/MEDIUM 0건 | writer가 "오늘 신뢰도 높은 시장 영향 뉴스 없음" 보고서 작성 (LOW만으로 본문 채우지 않음) |
| 같은 날짜 보고서 이미 존재 | `_v2`, `_v3` 접미사로 새 파일 생성 (덮어쓰기는 명시 요청 시만) |
| 시각 정보 모호 | published_utc=null, 보고서엔 "시각 미상" |
| 매체 간 사실 불일치 | 삭제 금지, "출처 간 불일치" 표기로 병기 |
| 팀 통신 무한 루프 (재요청 2회 이상) | 더 이상 요청 받지 않고 진행. 보고서에 "검증 미완"으로 표기 |

---

## 테스트 시나리오

### 정상 흐름
- **Trigger:** 사용자가 "/daily-news-curate" 또는 "오늘 뉴스 정리해줘"
- **기대 결과:**
  1. `_workspace/01_collected.json` 생성 (events 5+건, 출처 매체 5+개)
  2. `_workspace/02_verified.json` 생성 (각 사건 credibility 부여)
  3. `_workspace/03_analyzed.json` 생성 (HIGH/MEDIUM 사건만 분석)
  4. `reports/{YYYY-MM-DD}.md` 생성 (마크다운 표준, GitHub 렌더링 가능)
  5. 보고서에 TL;DR, 4 카테고리, 시장 영향 종합, LOW 주의, 출처 부록 모두 존재

### 에러 흐름 1: 단일 출처 사건만 다수
- **시나리오:** 모든 사건이 1개 매체 단독 (LOW)
- **기대 결과:** 보고서 본문 비고 "오늘 신뢰도 높은 뉴스 없음", LOW 섹션에만 사건 나열

### 에러 흐름 2: GitHub Actions 자동 실행 시 push 권한 누락
- **시나리오:** workflow 파일의 `permissions: contents: write` 누락
- **기대 결과:** 보고서는 생성되지만 commit 실패. 이 경우 workflow가 에러로 종료. 다음 실행에서 자동 복구.

### 에러 흐름 3: 부분 재실행
- **시나리오:** 사용자가 "검증만 다시 해줘" 요청
- **기대 결과:** Phase 2 스킵, Phase 3부터 시작. 기존 `_workspace/01_collected.json` 그대로 사용.

---

## 자동 실행 (GitHub Actions)

이 스킬은 `.github/workflows/daily-news.yml`의 cron(`0 22 * * *` UTC = KST 07:00)에서 Claude Code Action을 통해 자동 호출된다. workflow는 다음을 수행:

1. repo checkout
2. Claude Code Action 실행 (prompt: 이 스킬 호출)
3. 생성된 보고서를 commit & push
4. 실패 시 issue 자동 생성 (workflow에 정의)

자동 실행 시 사용자 상호작용이 없으므로 **모든 결정을 합리적 기본값으로 처리**:
- 같은 날짜 보고서 존재 → `_v2` 접미사
- 부분 재실행 의도 없음 → 항상 전체 흐름 실행

상세 자동화 설정은 `.github/workflows/daily-news.yml` 참조.

---

## 참조

- 신뢰 매체 리스트: `references/trusted-sources.md`
- 신뢰도 평가 루브릭: `references/credibility-rubric.md`
- 보고서 템플릿: `assets/report-template.md`
- 에이전트 정의: `.claude/agents/{news-collector,cross-verifier,market-analyst,report-writer}.md`
