from unittest.mock import Mock

from app.nlp import sentiment


def _model_with_predictions(predictions: list[dict[str, float | str]]):
    classifier = Mock(return_value=[predictions])
    return Mock(return_value=classifier)


def test_finbert_scores_positive_headline(monkeypatch):
    monkeypatch.setattr(
        sentiment,
        "pipeline",
        _model_with_predictions([
            {"label": "positive", "score": 0.90},
            {"label": "negative", "score": 0.05},
            {"label": "neutral", "score": 0.05},
        ]),
    )

    score = sentiment.FinBertSentiment().score("Record earnings beat expectations")

    assert score > 0.5


def test_finbert_scores_negative_headline(monkeypatch):
    monkeypatch.setattr(
        sentiment,
        "pipeline",
        _model_with_predictions([
            {"label": "positive", "score": 0.03},
            {"label": "negative", "score": 0.92},
            {"label": "neutral", "score": 0.05},
        ]),
    )

    score = sentiment.FinBertSentiment().score(
        "Escalating geopolitical tensions disrupt trade"
    )

    assert score < -0.5
