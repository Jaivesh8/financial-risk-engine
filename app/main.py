from fastapi import FastAPI
from app.schemas import ArticleInput, RiskSignal

app = FastAPI(title="Financial AI Risk Engine")

EVENT_SEVERITY = {
    "Geopolitical": 8,
    "Macroeconomic": 7,
    "Credit Event": 8,
    "Merger/Acquisition": 6,
    "Corporate": 4,
}

NEGATIVE_WORDS = {
    "crisis", "default", "war", "sanctions",
    "loss", "collapse", "fraud", "downgrade",
    "bankruptcy", "recession", "disruption",
}

POSITIVE_WORDS = {
    "growth", "profit", "surge", "recovery",
    "upgrade", "expansion", "record", "approval",
}


def classify_event(text: str) -> str:
    text = text.lower()

    if any(w in text for w in [
        "war", "sanctions", "invasion", "geopolitical"
    ]):
        return "Geopolitical"

    if any(w in text for w in [
        "interest rate", "inflation", "recession",
        "central bank", "monetary policy"
    ]):
        return "Macroeconomic"

    if any(w in text for w in [
        "default", "bankruptcy", "credit downgrade",
        "debt crisis"
    ]):
        return "Credit Event"

    if any(w in text for w in [
        "merger", "acquisition", "acquires"
    ]):
        return "Merger/Acquisition"

    return "Corporate"


def score_sentiment(text: str) -> float:
    words = text.lower().split()
    negative = sum(w.strip(".,:;!?") in NEGATIVE_WORDS for w in words)
    positive = sum(w.strip(".,:;!?") in POSITIVE_WORDS for w in words)

    if positive + negative == 0:
        return 0.0

    return round(
        (positive - negative) / (positive + negative), 2
    )


def score_impact(
    event_type: str,
    sentiment: float,
    source_count: int,
    sectors: list[str],
) -> int:
    score = EVENT_SEVERITY[event_type]

    # Corroboration by multiple sources
    if source_count >= 3:
        score += 1

    # Broad sector exposure
    if len(set(sectors)) >= 3:
        score += 1

    # Sentiment is deliberately a small component
    if sentiment <= -0.7:
        score += 1

    return max(1, min(10, score))


@app.get("/")
def health():
    return {"status": "running", "service": "Financial AI Risk Engine"}


@app.post("/analyze", response_model=RiskSignal)
def analyze_article(article: ArticleInput):
    text = f"{article.title} {article.text}"

    event_type = classify_event(text)
    sentiment = score_sentiment(text)

    impact = score_impact(
        event_type,
        sentiment,
        article.source_count,
        article.sectors,
    )

    return RiskSignal(
        source=article.source,
        title=article.title,
        sentiment_score=sentiment,
        event_type=event_type,
        impact_score=impact,
        affected_sectors=article.sectors,
        stress_test_triggered=impact > 7,
    )