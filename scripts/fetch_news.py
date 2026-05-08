#!/usr/bin/env python3
"""
Google News RSS로 직전 24시간 뉴스를 카테고리별 + watchlist 종목별로 수집.

- claude-code-action(@beta) agent 모드는 WebSearch/WebFetch를 자동 disallow하므로,
  Claude가 직접 검색하지 못한다. 대신 이 스크립트가 RSS로 미리 fetch해서
  _workspace/raw_news.json에 저장하면 Claude는 Read 도구로 읽기만 한다.
- Google News는 다양한 매체(Reuters, AP, FT, WSJ, Bloomberg, BBC 등)를 한 번에 묶어
  검색 결과로 반환하므로 "여러 매체 공통 보도" 식별이 쉽다.
- when:1d 연산자로 24시간 내 결과만 가져옴.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.parse
from pathlib import Path

import feedparser  # type: ignore
import yaml  # type: ignore


CATEGORY_QUERIES = {
    "monetary_policy": [
        "Federal Reserve interest rate",
        "FOMC statement",
        "Powell speech",
        "ECB rate decision",
        "Bank of Japan policy",
        "CPI inflation US",
        "PCE inflation",
        "PPI producer price",
    ],
    "geopolitics": [
        "Ukraine Russia war",
        "Middle East conflict Israel",
        "China Taiwan tension",
        "North Korea missile",
        "sanctions Iran",
        "summit diplomacy",
        "NATO",
    ],
    "trade": [
        "US tariff China",
        "trade war",
        "export controls semiconductor",
        "supply chain disruption",
        "USTR trade",
    ],
    "commodities": [
        "oil price OPEC",
        "WTI Brent crude",
        "natural gas price",
        "gold price",
        "USD index dollar",
    ],
}

# Google News RSS 검색 URL 템플릿
GN_RSS_URL = (
    "https://news.google.com/rss/search?"
    "q={query}&hl=en-US&gl=US&ceid=US:en"
)

# 매체 신뢰도 Tier — RSS source.title 매칭용 (소문자 부분 일치)
TIER_1 = {"reuters", "associated press", "ap news", "bloomberg", "agence france-presse", "afp"}
TIER_2 = {"wall street journal", "wsj", "financial times", "ft", "new york times",
          "nyt", "washington post", "nikkei asia", "the economist"}
TIER_3 = {"cnbc", "marketwatch", "barron", "politico", "foreign policy",
          "foreign affairs", "axios", "semafor"}
TIER_4 = {"bbc", "al jazeera", "cnn", "deutsche welle", "dw"}


def classify_tier(source_title: str) -> int:
    s = (source_title or "").lower()
    for keyword in TIER_1:
        if keyword in s:
            return 1
    for keyword in TIER_2:
        if keyword in s:
            return 2
    for keyword in TIER_3:
        if keyword in s:
            return 3
    for keyword in TIER_4:
        if keyword in s:
            return 4
    return 5  # unknown / Tier 5 (보조 출처)


def fetch_rss(query: str, when: str = "1d", limit: int = 20) -> list[dict]:
    full_query = f"{query} when:{when}"
    url = GN_RSS_URL.format(query=urllib.parse.quote(full_query))
    try:
        feed = feedparser.parse(url)
    except Exception as ex:
        print(f"  [WARN] feedparser failed for '{query}': {ex}", file=sys.stderr)
        return []

    items: list[dict] = []
    for e in feed.entries[:limit]:
        # Google News RSS의 source 필드는 entry.source 객체 (title, href)
        source_title = ""
        if hasattr(e, "source"):
            src = e.source
            source_title = getattr(src, "title", "") or src.get("title", "") if isinstance(src, dict) else getattr(src, "title", "")

        items.append({
            "title": getattr(e, "title", ""),
            "link": getattr(e, "link", ""),
            "published": getattr(e, "published", ""),
            "published_parsed": _to_iso(getattr(e, "published_parsed", None)),
            "source": source_title,
            "tier": classify_tier(source_title),
            "summary": (getattr(e, "summary", "") or "")[:600],
        })
    return items


def _to_iso(parsed: object) -> str | None:
    if parsed is None:
        return None
    try:
        return dt.datetime(*parsed[:6], tzinfo=dt.timezone.utc).isoformat()
    except Exception:
        return None


def dedupe(items: list[dict]) -> list[dict]:
    """제목 기준으로 중복 제거. 같은 제목이 여러 매체에서 오면 다양한 매체 정보 보존."""
    seen: dict[str, dict] = {}
    for it in items:
        # 제목을 정규화 (소문자, 공백 정리, 매체명 suffix 제거)
        key = (it["title"] or "").split(" - ")[0].strip().lower()
        if not key:
            continue
        if key in seen:
            # 같은 사건의 추가 출처로 처리
            existing = seen[key]
            existing.setdefault("additional_sources", [])
            existing["additional_sources"].append({
                "source": it["source"],
                "tier": it["tier"],
                "link": it["link"],
            })
        else:
            seen[key] = it
    return list(seen.values())


def fetch_categories() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for cat, queries in CATEGORY_QUERIES.items():
        all_items: list[dict] = []
        for q in queries:
            print(f"  [{cat}] querying: {q}")
            all_items.extend(fetch_rss(q))
        deduped = dedupe(all_items)
        # Tier 1-2 우선 정렬
        deduped.sort(key=lambda x: (x["tier"], x["title"]))
        out[cat] = deduped
        print(f"  → {cat}: {len(deduped)} unique items")
    return out


def fetch_watchlist(watchlist_path: Path) -> dict[str, dict]:
    if not watchlist_path.exists():
        print(f"  [INFO] {watchlist_path} not found, skipping watchlist")
        return {}

    with open(watchlist_path, encoding="utf-8") as f:
        wl = yaml.safe_load(f) or {}

    out: dict[str, dict] = {}
    for entry in wl.get("watchlist", []):
        name = entry.get("name", "")
        ticker = entry.get("ticker", "")
        aliases = entry.get("aliases", []) or []

        # 검색 쿼리 — name + ticker (영문/국제 표준명 위주)
        search_terms = [name]
        if ticker:
            search_terms.append(ticker)
        # aliases 중 영문만 (한글은 Google News에서 결과 적음)
        for a in aliases[:2]:
            if a and not any(0xAC00 <= ord(c) <= 0xD7A3 for c in str(a)):
                search_terms.append(a)

        all_items: list[dict] = []
        for term in search_terms:
            # 종목 뉴스는 stock/earnings/upgrade 같은 시장성 단어 결합
            for suffix in ["stock", "earnings"]:
                q = f'"{term}" {suffix}'
                print(f"  [watchlist:{ticker or name}] querying: {q}")
                all_items.extend(fetch_rss(q, limit=10))

        deduped = dedupe(all_items)
        deduped.sort(key=lambda x: (x["tier"], x["title"]))

        out[ticker or name] = {
            "name": name,
            "ticker": ticker,
            "aliases": aliases,
            "items": deduped,
        }
        print(f"  → {name} ({ticker}): {len(deduped)} unique items")

    return out


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    workspace = repo_root / "_workspace"
    workspace.mkdir(exist_ok=True)

    now_utc = dt.datetime.now(dt.timezone.utc)
    now_kst = now_utc.astimezone(dt.timezone(dt.timedelta(hours=9)))
    window_start_kst = now_kst - dt.timedelta(hours=24)

    print(f"수집 시점 (KST): {now_kst.isoformat()}")
    print(f"시간창: {window_start_kst.isoformat()} ~ {now_kst.isoformat()}\n")

    print("=== 카테고리 뉴스 수집 ===")
    categories = fetch_categories()

    print("\n=== Watchlist 종목 뉴스 수집 ===")
    watchlist = fetch_watchlist(repo_root / "watchlist.yaml")

    out = {
        "collected_at_utc": now_utc.isoformat(),
        "collected_at_kst": now_kst.isoformat(),
        "window_start_kst": window_start_kst.isoformat(),
        "window_end_kst": now_kst.isoformat(),
        "categories": categories,
        "watchlist": watchlist,
        "tier_legend": {
            "1": "1차 통신사 (Reuters, AP, Bloomberg, AFP)",
            "2": "주요 영자지 (WSJ, FT, NYT, WaPo, Nikkei Asia)",
            "3": "경제·전문 (CNBC, MarketWatch, Politico, Foreign Policy)",
            "4": "방송 (BBC, Al Jazeera, CNN, DW)",
            "5": "기타 (보조 출처)",
        },
    }

    out_path = workspace / "raw_news.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    total_cat = sum(len(v) for v in categories.values())
    total_wl = sum(len(v["items"]) for v in watchlist.values())
    print(f"\n=== 저장 완료: {out_path} ===")
    print(f"카테고리 사건: {total_cat}건 / Watchlist 사건: {total_wl}건")
    print(f"파일 크기: {out_path.stat().st_size / 1024:.1f} KB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
