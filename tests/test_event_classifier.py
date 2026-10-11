from unittest.mock import Mock

from app.nlp import event_classifier


def _model_with_result(label: str, confidence: float) -> Mock:
    classifier = Mock(return_value={
        "labels": [label, "Other"],
        "scores": [confidence, 1 - confidence],
    })
    return Mock(return_value=classifier)


def test_zero_shot_classifies_geopolitical_headline(monkeypatch):
    monkeypatch.setattr(
        event_classifier,
        "pipeline",
        _model_with_result("Geopolitical", 0.93),
    )

    label, confidence = event_classifier.ZeroShotEventClassifier().classify(
        "Escalating geopolitical tensions"
    )

    assert label == "Geopolitical"
    assert confidence > 0.7


def test_zero_shot_classifies_earnings_headline(monkeypatch):
    monkeypatch.setattr(
        event_classifier,
        "pipeline",
        _model_with_result("Earnings", 0.91),
    )

    label, confidence = event_classifier.ZeroShotEventClassifier().classify(
        "Record earnings beat"
    )

    assert label == "Earnings"
    assert confidence > 0.7
