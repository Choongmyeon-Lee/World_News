# News — 국제정세 데일리 브리핑 하네스

## 하네스: 국제정세 뉴스 큐레이션

**목표:** 매일 직전 24시간(KST)의 국제정세 뉴스를 다수 신뢰 매체에서 수집·교차검증·시장영향 분석하여, 미국 주식 투자자가 신뢰할 수 있는 정보만 정리한 마크다운 보고서를 자동 생성.

**트리거:** 국제정세 뉴스 정리/브리핑/분석 요청 시 `daily-news-curate` 스킬을 사용하라. 트리거 표현 예: "오늘 뉴스 정리", "국제정세 브리핑", "데일리 뉴스", "/daily-news-curate", "어제 보고서 갱신". 단순한 뉴스 잡담은 제외.

**자동 실행:** `.github/workflows/daily-news.yml`이 매일 KST 07:00(=UTC 22:00)에 cron 트리거되어 동일 스킬을 실행하고, 결과를 `reports/YYYY-MM-DD.md`로 commit & push.

## Team API
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 활성 (`~/.claude/settings.json`)
- `daily-news-curate`: `TeamCreate` 패턴 사용 → 시각화 활성

## Superpowers 설정
- TDD 강제: **OFF** (콘텐츠 큐레이션 도메인, 단위 테스트 부적합)
- brainstorming HARD-GATE: 수동 호출 시에만 (`/brainstorming`)
- writing-plans: 신규 카테고리 추가/대규모 워크플로우 변경 시에만
- systematic-debugging: 워크플로우 버그 보고 시 ON
- subagent-driven-development의 spec/quality 2단계 리뷰: 본 도메인엔 비활성 (코드 변경 도메인 아님)

## 변경 이력

| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-05-07 | 초기 구성 | 전체 | 미국 주식 투자 정보용 데일리 국제정세 브리핑 자동화 |
| 2026-05-07 | OAuth 토큰 방식으로 변경 | workflow + README | Max 구독 한도 내 사용 (별도 API 결제 회피) |
| 2026-05-07 | workflow 입력 schema 수정 | daily-news.yml | claude-code-action v1: prompt→direct_prompt, mode: agent 추가, id-token: write 권한 추가 |
