from pydantic import BaseModel, Field


class ArticleInput(BaseModel):
    source: str
    title: str
    text: str
    sectors: list[str] = []
    source_count: int = Field(default=1, ge=1)


class RiskSignal(BaseModel):
    source: str
    title: str
    sentiment_score: float
    event_type: str
    impact_score: int
    affected_sectors: list[str]
    stress_test_triggered: bool