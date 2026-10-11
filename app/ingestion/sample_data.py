"""Reliable demo articles spanning the engine's primary event types."""

SAMPLE_ARTICLES = [
    {"text": "Escalating geopolitical tensions disrupt trade routes and lift oil prices.", "source": "sample", "timestamp": "2026-10-01T08:00:00Z", "company": None},
    {"text": "Central bank signals further interest rate cuts as inflation slows.", "source": "sample", "timestamp": "2026-10-01T09:00:00Z", "company": None},
    {"text": "Regional lender faces credit downgrade after rising loan defaults.", "source": "sample", "timestamp": "2026-10-01T10:00:00Z", "company": "Regional Lender"},
    {"text": "Atlas Bank agrees to acquire Meridian Capital in a major merger.", "source": "sample", "timestamp": "2026-10-01T11:00:00Z", "company": "Atlas Bank"},
    {"text": "Nova Technologies reports record earnings and beats analyst expectations.", "source": "sample", "timestamp": "2026-10-01T12:00:00Z", "company": "Nova Technologies"},
    {"text": "Regulator fines Harbor Securities for compliance failures.", "source": "sample", "timestamp": "2026-10-01T13:00:00Z", "company": "Harbor Securities"},
    {"text": "Energy markets retreat after ceasefire talks ease supply concerns.", "source": "sample", "timestamp": "2026-10-02T08:00:00Z", "company": None},
    {"text": "Government bond yields rise as markets price persistent inflation.", "source": "sample", "timestamp": "2026-10-02T09:00:00Z", "company": None},
    {"text": "Property developer misses debt payment, raising bankruptcy concerns.", "source": "sample", "timestamp": "2026-10-02T10:00:00Z", "company": "Crest Properties"},
    {"text": "Global Foods launches a new low-cost product range.", "source": "sample", "timestamp": "2026-10-02T11:00:00Z", "company": "Global Foods"},
    {"text": "Metro Motors raises annual guidance after strong quarterly profit.", "source": "sample", "timestamp": "2026-10-02T12:00:00Z", "company": "Metro Motors"},
    {"text": "Competition authority approves the proposed telecom acquisition.", "source": "sample", "timestamp": "2026-10-02T13:00:00Z", "company": None},
    {"text": "Sanctions announced against exporters amid widening regional conflict.", "source": "sample", "timestamp": "2026-10-03T08:00:00Z", "company": None},
    {"text": "Manufacturing recession deepens as orders contract for a third month.", "source": "sample", "timestamp": "2026-10-03T09:00:00Z", "company": None},
    {"text": "Corporate bond spreads widen following a surprise default.", "source": "sample", "timestamp": "2026-10-03T10:00:00Z", "company": None},
    {"text": "Pioneer Health unveils a new diagnostic platform.", "source": "sample", "timestamp": "2026-10-03T11:00:00Z", "company": "Pioneer Health"},
    {"text": "Financial watchdog proposes stricter capital rules for banks.", "source": "sample", "timestamp": "2026-10-03T12:00:00Z", "company": None},
    {"text": "Consumer spending recovery supports broad equity market growth.", "source": "sample", "timestamp": "2026-10-03T13:00:00Z", "company": None},
]


def get_sample_articles() -> list[dict]:
    """Return copies so callers cannot mutate the demo dataset."""
    return [article.copy() for article in SAMPLE_ARTICLES]
