# News — 국제정세 데일리 브리핑

매일 한국시간 오전 7시에 GitHub Actions가 자동으로 직전 24시간 국제정세 뉴스를 수집·교차검증·시장영향 분석하여, 미국 주식 투자자 관점의 신뢰도 높은 마크다운 브리핑을 [reports/](reports/)에 push합니다.

## 디렉토리 구조

```
News/
├── CLAUDE.md                       # 하네스 포인터
├── .claude/
│   ├── agents/                     # 4개 전문 에이전트 정의
│   │   ├── news-collector.md
│   │   ├── cross-verifier.md
│   │   ├── market-analyst.md
│   │   └── report-writer.md
│   └── skills/daily-news-curate/   # 오케스트레이터 스킬
│       ├── SKILL.md
│       ├── references/             # 신뢰 매체 리스트, 신뢰도 루브릭
│       └── assets/                 # 보고서 템플릿
├── .github/workflows/
│   └── daily-news.yml              # cron 자동 실행 (KST 07:00)
├── reports/                        # 자동 생성 보고서 (commit됨)
│   └── YYYY-MM-DD.md
└── _workspace/                     # 중간 산출물 (gitignore)
    ├── 01_collected.json
    ├── 02_verified.json
    └── 03_analyzed.json
```

## 워크플로우

```
news-collector ─→ cross-verifier ─→ market-analyst ─→ report-writer
   (수집)            (교차검증)          (시장영향)        (보고서)
```

각 단계는 4명 에이전트 팀이 협업합니다. 신뢰도(HIGH/MEDIUM/LOW/DROP) 평가 기준은 [credibility-rubric.md](.claude/skills/daily-news-curate/references/credibility-rubric.md), 신뢰 매체는 [trusted-sources.md](.claude/skills/daily-news-curate/references/trusted-sources.md) 참조.

## 초기 설정 (1회)

### 1) GitHub repo 생성 + push

```bash
cd /home/chmax7213/workspace/News
git add .
git commit -m "init: news curation harness"
gh repo create News --private --source=. --remote=origin --push
```

또는 GitHub 웹에서 repo 생성 후 `git remote add origin <URL> && git push -u origin main`.

### 2) CLAUDE_CODE_OAUTH_TOKEN 등록 (Max 구독 사용)

**Max(또는 Pro) 구독자는 OAuth 토큰 방식을 사용하면 추가 API 결제 없이 구독 한도 내에서 GitHub Actions 실행이 차감됩니다.**

로컬 터미널에서:

```bash
claude setup-token
```

브라우저가 열리고 인증 후 발급된 토큰을 복사. GitHub repo의 **Settings → Secrets and variables → Actions → New repository secret** 에서:

- Name: `CLAUDE_CODE_OAUTH_TOKEN`
- Value: `<발급된 토큰>`

OAuth 토큰은 약 1년 후 만료되므로, 만료 시 재발급하여 secret을 업데이트하세요.

> **API key 방식을 쓰고 싶다면**: workflow 파일에서 `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`을 `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`로 바꾸고 secret 이름을 `ANTHROPIC_API_KEY`로 등록. 이 경우는 별도 API 사용량 결제가 발생합니다.

### 3) 첫 실행 (수동 트리거)

GitHub repo의 **Actions** 탭 → **Daily News Curation** 워크플로우 → **Run workflow** 클릭. 정상 작동하면 `reports/YYYY-MM-DD.md`가 새 commit으로 푸시됩니다.

### 4) cron 자동 실행 확인

수동 실행이 성공했다면 다음 날 오전 7시(KST)에 자동 실행됩니다. 처음 며칠은 Actions 탭에서 실행 결과를 확인하세요. (GitHub Actions cron은 5~15분 지연될 수 있습니다.)

## 로컬 수동 실행

Claude Code 세션에서:

```
/daily-news-curate
```

또는 자연어로 "오늘 뉴스 정리해줘" / "국제정세 브리핑 만들어줘".

부분 재실행:
- "검증부터 다시" → Phase 3부터
- "보고서만 다시" → Phase 5만

## GitHub Actions 자동화 — `claude-code-action` 파라미터 검증

`.github/workflows/daily-news.yml`의 step `Run daily-news-curate skill`은 `anthropics/claude-code-action@beta`를 사용합니다. 액션 버전에 따라 파라미터명(`prompt` vs `direct_prompt`)이 다를 수 있으므로 **첫 수동 실행 시** 다음을 확인하세요:

- 액션이 `Invalid input "prompt"` 같은 에러로 실패 → workflow 파일에서 `prompt:` 를 `direct_prompt:` 로 변경
- 액션 버전을 고정하고 싶으면 `@beta` → `@v1` 또는 release 태그
- 공식 사용법: https://github.com/anthropics/claude-code-action

## 비용

### Max 구독 사용 시 (권장)

`CLAUDE_CODE_OAUTH_TOKEN` 방식으로 등록했으면 GitHub Actions 실행분은 **Max 구독 한도 내에서 차감**되며 추가 결제는 없습니다. 단, 매일 1회 자동 실행 + 수동 실행 + 로컬 사용이 합산되므로, Max 구독 한도를 초과하면 일시적으로 rate limit이 걸릴 수 있습니다.

자동 실행 1회의 토큰 사용량 추정:
- 입력 ~50K + 출력 ~15K (4 에이전트 × 보고서 한 건)
- WebSearch/WebFetch: 30~80건

이 정도는 Max(20x) 구독 일일 한도에서 큰 비중은 아니지만, 한도가 빠듯할 때는 워크플로우 cron 빈도(매일 → 격일)나 모델(opus → sonnet)을 조정하세요.

### API key 방식 사용 시

`ANTHROPIC_API_KEY`로 등록한 경우 별도 결제. Opus 단가 기준 1회 실행당 $0.5~$2, 월 $15~$60 예상.

### 비용/한도 절감

- 모델 다운그레이드: 각 에이전트의 `model: "opus"` → `"sonnet"` (품질 약간 하락 vs. 토큰 ~3배 절감)
- 카테고리 축소: 4개 → 2~3개
- 매체 수 축소: collector의 `outlets_checked` 제한
- 빈도 조정: cron `0 22 * * *` → `0 22 * * 1-5` (평일만)

## 보고서 형식

[보고서 템플릿](.claude/skills/daily-news-curate/assets/report-template.md) 참조. 구조:

1. **TL;DR** — 가장 중요한 3건
2. **카테고리별 정리** — 통화정책 / 지정학 / 무역 / 원자재
3. **시장 영향 종합** — 매크로·섹터·티커
4. **주의** — LOW 등급 1줄 요약
5. **출처 부록** — 사건별 출처 링크

## 면책

본 보고서는 정보 정리 목적이며 매수·매도 추천이 아닙니다. 모든 투자 판단은 투자자 본인의 책임입니다.
