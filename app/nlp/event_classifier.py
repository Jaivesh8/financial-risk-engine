"""Event classification with BART zero-shot classification and keyword fallback."""

try:
    from transformers import pipeline
except ImportError:
    pipeline = None


CANDIDATE_LABELS = [
    "Geopolitical",
    "Macroeconomic",
    "Credit Event",
    "Merger/Acquisition",
    "Earnings",
    "Regulatory",
    "Product Launch",
    "Other",
]


def classify_keyword_event(text: str) -> str:
    """Return the original rule-based classification when BART is unavailable."""
    text = text.lower()

    if any(word in text for word in ("war", "sanctions", "invasion", "geopolitical")):
        return "Geopolitical"
    if any(word in text for word in (
        "interest rate", "inflation", "recession", "central bank", "monetary policy"
    )):
        return "Macroeconomic"
    if any(word in text for word in (
        "default", "bankruptcy", "credit downgrade", "debt crisis"
    )):
        return "Credit Event"
    if any(word in text for word in ("merger", "acquisition", "acquires")):
        return "Merger/Acquisition"
    if any(word in text for word in ("earnings", "revenue", "profit", "guidance")):
        return "Earnings"
    if any(word in text for word in ("regulator", "regulatory", "fine", "approval")):
        return "Regulatory"
    if any(word in text for word in ("launch", "released", "unveiled", "new product")):
        return "Product Launch"
    return "Other"


class ZeroShotEventClassifier:
    """Classify financial-news text into the engine's fixed event categories."""

    def __init__(self) -> None:
        self._classifier = None
        if pipeline is not None:
            self._classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
            )

    def classify(self, text: str) -> tuple[str, float]:
        """Return the highest-confidence event label and its probability."""
        if self._classifier is None:
            return classify_keyword_event(text), 0.0

        result = self._classifier(text, candidate_labels=CANDIDATE_LABELS)
        labels = result.get("labels", [])
        scores = result.get("scores", [])
        if not labels or not scores:
            raise RuntimeError("Zero-shot classifier returned no labels or scores.")

        return str(labels[0]), float(scores[0])
