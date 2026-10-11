"""GDELT article ingestion with safe failure behavior."""

from datetime import datetime, timezone

import requests


GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


def _infer_sectors(text: str) -> list[str]:
    """Derive a small, transparent sector set from an event headline."""
    text = text.lower()
    sectors = []
    if any(term in text for term in ("bank", "credit", "loan", "bond")):
        sectors.append("Banking")
    if any(term in text for term in ("oil", "energy", "gas", "commodity")):
        sectors.append("Energy")
    if any(term in text for term in ("tech", "software", "semiconductor")):
        sectors.append("Technology")
    return sectors or ["Mixed"]


def fetch_gdelt_events(limit: int = 10) -> list[dict]:
    """Fetch recent financial-risk articles from GDELT, returning [] on failure."""
    try:
        response = requests.get(
            GDELT_URL,
            params={
                "query": "(economy OR markets OR finance OR geopolitical)",
                "mode": "ArtList",
                "format": "json",
                "maxrecords": limit,
                "sort": "DateDesc",
            },
            timeout=10,
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])
    except (requests.RequestException, ValueError, AttributeError):
        return []

    normalized = []
    for article in articles[:limit]:
        text = article.get("title") or article.get("seendate")
        if not text:
            continue
        normalized.append({
            "text": text,
            "source": article.get("domain") or "GDELT",
            "timestamp": article.get("seendate") or datetime.now(timezone.utc).isoformat(),
            "sectors": _infer_sectors(text),
        })
    return normalized
