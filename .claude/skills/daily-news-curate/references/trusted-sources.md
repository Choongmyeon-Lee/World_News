# Trusted Sources Reference

매체별 신뢰도 Tier와 검색 우선순위. news-collector / cross-verifier가 참조.

## 목차
1. Tier 1 — 1차 통신사
2. Tier 2 — 주요 영자지
3. Tier 3 — 경제·전문 매체
4. Tier 4 — 방송
5. 공식 소스 (정부·중앙은행·기관)
6. 카테고리별 권장 매체 매핑
7. 한국어 매체 사용 원칙

---

## 1. Tier 1 — 1차 통신사 (가장 높은 신뢰도)

자체 취재망 보유, 다른 매체가 받아쓰는 원 출처. 단독 보도라도 통상 신뢰 가능.

| 매체 | 도메인 | 강점 영역 |
|------|--------|----------|
| Reuters | reuters.com | 종합, 정책, 시장, 지정학 |
| Associated Press (AP) | apnews.com | 종합, 정치, 외교 |
| Bloomberg | bloomberg.com | 시장, 기업, 통화정책 (페이월 多) |
| Agence France-Presse (AFP) | afp.com | 유럽·중동·아프리카 외교 |

## 2. Tier 2 — 주요 영자지 (자체 취재 + 분석)

| 매체 | 도메인 | 강점 영역 |
|------|--------|----------|
| Wall Street Journal (WSJ) | wsj.com | 시장, 기업, 미국 정책 (페이월) |
| Financial Times (FT) | ft.com | 글로벌 시장, 정책 (페이월) |
| New York Times (NYT) | nytimes.com | 종합, 외교, 분석 |
| Washington Post | washingtonpost.com | 미국 정책, 외교 |
| Nikkei Asia | asia.nikkei.com | 아시아 시장, 일본 정책 |
| The Economist | economist.com | 분석 (페이월) |

## 3. Tier 3 — 경제·전문 매체

| 매체 | 도메인 | 강점 영역 |
|------|--------|----------|
| CNBC | cnbc.com | 미국 시장, 실시간 |
| MarketWatch | marketwatch.com | 미국 시장 |
| Barron's | barrons.com | 분석 (페이월) |
| Politico | politico.com | 미국·EU 정책 |
| Foreign Policy | foreignpolicy.com | 외교·지정학 분석 |
| Foreign Affairs | foreignaffairs.com | 장기 지정학 분석 |
| Axios | axios.com | 미국 정책 속보 |
| Semafor | semafor.com | 정책·외교 |

## 4. Tier 4 — 방송 (헤드라인 보조 확인용)

| 매체 | 도메인 |
|------|--------|
| BBC | bbc.com |
| Al Jazeera English | aljazeera.com |
| CNN | cnn.com |
| Deutsche Welle | dw.com |

## 5. 공식 소스 (가능하면 직접 확인 — 자동 HIGH 등급 후보)

### 미국 정부·중앙은행
- **Federal Reserve:** federalreserve.gov (FOMC 성명, 의장 연설, 의사록)
- **Treasury:** home.treasury.gov, ofac.treasury.gov (제재)
- **USTR (무역대표부):** ustr.gov (관세, 무역협정)
- **Bureau of Labor Statistics (BLS):** bls.gov (CPI, 고용)
- **Bureau of Economic Analysis (BEA):** bea.gov (GDP, PCE)
- **White House:** whitehouse.gov (행정명령, 보도자료)
- **State Department:** state.gov (외교 발표)
- **Department of Commerce / BIS:** commerce.gov, bis.gov (수출통제)

### 국제기관·중앙은행
- **ECB:** ecb.europa.eu
- **Bank of Japan:** boj.or.jp
- **Bank of England:** bankofengland.co.uk
- **People's Bank of China:** pbc.gov.cn
- **IMF:** imf.org
- **World Bank:** worldbank.org
- **OECD:** oecd.org
- **OPEC:** opec.org
- **WTO:** wto.org

### 시장 인프라
- **NYSE/NASDAQ:** nyse.com, nasdaq.com (상장폐지·거래정지)
- **SEC:** sec.gov (8-K, 10-K filings)

## 6. 카테고리별 권장 매체 매핑

### 통화정책·금리·인플레이션
- 1차: Federal Reserve / ECB / BOJ 공식 사이트
- 보도: Reuters, Bloomberg, WSJ, FT
- 보조: CNBC, MarketWatch

### 지정학·전쟁·외교
- 1차: 정부 공식 발표 (State, White House, EU)
- 보도: Reuters, AP, AFP, NYT, Washington Post
- 분석: Foreign Policy, Foreign Affairs, BBC

### 무역·관세·공급망
- 1차: USTR, Commerce, EU Commission, WTO
- 보도: Reuters, FT, WSJ, Politico, Nikkei Asia
- 보조: Semafor, Bloomberg

### 원자재·에너지·환율
- 1차: OPEC 공식, EIA(eia.gov), CFTC(cftc.gov)
- 보도: Reuters, Bloomberg, FT
- 보조: Argus Media, S&P Global Platts (전문지)

## 7. 한국어 매체 사용 원칙

한국 매체(연합뉴스, 매일경제, 한국경제, 조선일보 등)는 **국제뉴스 1차 출처로 사용 금지**. 영문 1차 매체에서 확인되지 않은 국제뉴스는 신뢰 어려움.

**예외:** 한국 정부·기업·통화 관련 뉴스(원화, 한은, 한국 기업의 미국 시장 진출 등)는 한국 매체가 1차 출처가 될 수 있음. 이 경우에도 영문 매체 교차확인 시도.

## 검색 안티패턴

다음은 **검색에 사용해서는 안 되는** 출처:
- SNS (X, Reddit, Truth Social) — 1차 정보원이 아닌 한 인용 금지
- 익명 블로그 / 뉴스 어그리게이터 (Yahoo News 헤드라인은 OK이지만 원 출처 추적 필수)
- 의견 매체 단독 (Breitbart, Daily Wire, Common Dreams 등 강한 정파성)
- AI 생성 뉴스 사이트 (도메인이 의심스럽고 저자 불명)
