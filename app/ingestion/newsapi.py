"""NewsAPI headline ingestion with safe failure behavior."""

from datetime import datetime, timezone

import requests


NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"


def fetch_headlines(api_key: str, limit: int = 10) -> list[dict]:
    """Fetch and normalize NewsAPI headlines, returning [] on any failure."""
    if not api_key:
        return []

    try:
        response = requests.get(
            NEWSAPI_URL,
            params={"apiKey": api_key, "category": "business", "pageSize": limit},
            timeout=10,
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])
    except (requests.RequestException, ValueError, AttributeError):
        return []

    normalized = []
    for article in articles[:limit]:
        text = article.get("title") or article.get("description")
        if not text:
            continue
        source = article.get("source", {}).get("name") or "NewsAPI"
        normalized.append({
            "text": text,
            "source": source,
            "timestamp": article.get("publishedAt") or datetime.now(timezone.utc).isoformat(),
            "company": None,
        })
    return normalized
