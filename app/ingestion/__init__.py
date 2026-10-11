"""Unified article-ingestion interface."""

from concurrent.futures import ThreadPoolExecutor

from app.ingestion.gdelt import fetch_gdelt_events
from app.ingestion.newsapi import fetch_headlines
from app.ingestion.sample_data import get_sample_articles


def _clean_and_dedupe(articles: list[dict]) -> list[dict]:
    cleaned = []
    seen = set()
    for article in articles:
        text = str(article.get("text", "")).strip()
        if not text:
            continue
        key = " ".join(text.lower().split())
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({
            "text": text,
            "source": article.get("source") or "unknown",
            "timestamp": article.get("timestamp"),
            "company": article.get("company"),
            "sectors": article.get("sectors", []),
        })
    return cleaned


def ingest_articles(use_sample: bool = True, newsapi_key: str | None = None) -> list[dict]:
    """Use deterministic sample data or concurrently retrieve external sources."""
    if use_sample:
        return _clean_and_dedupe(get_sample_articles())

    with ThreadPoolExecutor(max_workers=2) as executor:
        gdelt_future = executor.submit(fetch_gdelt_events)
        newsapi_future = executor.submit(fetch_headlines, newsapi_key or "")
        return _clean_and_dedupe(gdelt_future.result() + newsapi_future.result())
