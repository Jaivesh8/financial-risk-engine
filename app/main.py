from fastapi import FastAPI, HTTPException
from app.database.db import get_signal, insert_stress_test, list_stress_tests
from app.nlp.event_classifier import ZeroShotEventClassifier
from app.nlp.sentiment import get_sentiment_model
from app.risk.calculator import run_stress_test, should_trigger
from app.risk.portfolio import Portfolio
from app.schemas import ArticleInput, RiskSignal, StressRequest, StressResponse

app = FastAPI(title="Financial AI Risk Engine")

EVENT_SEVERITY = {
    "Geopolitical": 8,
    "Macroeconomic": 7,
    "Credit Event": 8,
    "Merger/Acquisition": 6,
    "Earnings": 4,
    "Regulatory": 5,
    "Product Launch": 4,
    "Other": 4,
    "Corporate": 4,
}

event_classifier = ZeroShotEventClassifier()


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
    text = article.text

    event_type, _confidence = event_classifier.classify(text)
    sentiment = get_sentiment_model().score(text)

    impact = score_impact(
        event_type,
        sentiment,
        article.n_sources,
        [],
    )

    return RiskSignal(
        source=article.source,
        title=article.text,
        sentiment_score=sentiment,
        event_type=event_type,
        impact_score=impact,
        affected_sectors=[],
        stress_test_triggered=impact > 7,
    )


def _test_signal(signal_id: int | None) -> dict:
    """Provide a deterministic signal until the signal persistence module exists."""
    return {
        "signal_id": signal_id,
        "event": "Geopolitical",
        "impact_score": 8.0,
        "affected_sectors": ["Banking", "Fixed Income", "Mixed"],
    }


@app.post("/stress-test", response_model=StressResponse)
def stress_test(request: StressRequest):
    # Signal persistence is not part of this milestone, so use a deterministic
    # test signal when no stored signal can be retrieved.
    signal = (
        get_signal(request.signal_id)
        if request.signal_id is not None
        else None
    ) or _test_signal(request.signal_id)
    if not request.force and not should_trigger(signal["event"], signal["impact_score"]):
        raise HTTPException(status_code=400, detail="Signal does not meet stress-test trigger.")

    result = run_stress_test(
        Portfolio(),
        signal["event"],
        signal["impact_score"],
        signal["affected_sectors"],
    )
    result["signal_id"] = signal["signal_id"]
    insert_stress_test(result)
    return StressResponse(**result)


@app.get("/stress-tests")
def get_stress_tests():
    return list_stress_tests(limit=10)
