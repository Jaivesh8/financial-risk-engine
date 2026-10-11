from app.ingestion import ingest_articles
from app.ingestion.sample_data import get_sample_articles


def test_sample_articles_has_at_least_ten_articles():
    assert len(get_sample_articles()) >= 10


def test_sample_articles_have_required_fields():
    for article in get_sample_articles():
        assert {"text", "source", "timestamp"} <= article.keys()


def test_sample_ingestion_returns_sample_articles():
    articles = ingest_articles(use_sample=True)

    assert len(articles) == len(get_sample_articles())
    assert all(article["source"] == "sample" for article in articles)


def test_live_ingestion_combines_mocked_sources(monkeypatch):
    monkeypatch.setattr(
        "app.ingestion.fetch_gdelt_events",
        lambda: [{"text": "GDELT article", "source": "GDELT", "timestamp": "now", "sectors": []}],
    )
    monkeypatch.setattr(
        "app.ingestion.fetch_headlines",
        lambda key: [{"text": "NewsAPI article", "source": "NewsAPI", "timestamp": "now", "company": None}],
    )

    assert len(ingest_articles(use_sample=False, newsapi_key="test-key")) == 2
