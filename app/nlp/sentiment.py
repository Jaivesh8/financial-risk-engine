"""Sentiment scoring with FinBERT and a dependency-free fallback."""

from functools import lru_cache

try:
    from transformers import pipeline
except ImportError:
    pipeline = None


NEGATIVE_WORDS = {
    "crisis", "default", "war", "sanctions",
    "loss", "collapse", "fraud", "downgrade",
    "bankruptcy", "recession", "disruption",
}

POSITIVE_WORDS = {
    "growth", "profit", "surge", "recovery",
    "upgrade", "expansion", "record", "approval",
}


def score_lexicon_sentiment(text: str) -> float:
    """Return the original lexicon score when FinBERT is unavailable."""
    words = text.lower().split()
    negative = sum(word.strip(".,:;!?") in NEGATIVE_WORDS for word in words)
    positive = sum(word.strip(".,:;!?") in POSITIVE_WORDS for word in words)

    if positive + negative == 0:
        return 0.0

    return round((positive - negative) / (positive + negative), 2)


class FinBertSentiment:
    """Score financial text as P(positive) minus P(negative)."""

    def __init__(self) -> None:
        self._classifier = None
        if pipeline is not None:
            self._classifier = pipeline(
                "text-classification",
                model="ProsusAI/finbert",
                top_k=None,
            )

    def score(self, text: str) -> float:
        """Return a score in the inclusive range [-1, 1]."""
        if self._classifier is None:
            return score_lexicon_sentiment(text)

        predictions = self._classifier(text)
        if predictions and isinstance(predictions[0], list):
            predictions = predictions[0]

        probabilities = {
            prediction["label"].lower(): float(prediction["score"])
            for prediction in predictions
        }
        score = probabilities.get("positive", 0.0) - probabilities.get("negative", 0.0)
        return max(-1.0, min(1.0, score))


@lru_cache(maxsize=1)
def get_sentiment_model() -> FinBertSentiment:
    """Return the singleton model so the FinBERT weights load only once."""
    return FinBertSentiment()
