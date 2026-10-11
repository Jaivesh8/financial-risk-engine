from pydantic import BaseModel, Field


class TextIn(BaseModel):
    text: str
    source: str
    company: str | None = None
    n_sources: int = Field(default=1, ge=1)


class ArticleInput(BaseModel):
    text: str
    source: str
    company: str | None = None
    n_sources: int = Field(default=1, ge=1)


class StressRequest(BaseModel):
    signal_id: int | None = None
    force: bool = False


class AssetClassStressResult(BaseModel):
    asset_class: str
    pre_value: float
    post_value: float
    loss: float
    loss_pct: float


class StressResponse(BaseModel):
    pre_value: float
    post_value: float
    loss: float
    loss_pct: float
    event: str
    impact_score: float
    affected_sectors: list[str]
    by_asset_class: list[AssetClassStressResult]


class RiskSignal(BaseModel):
    source: str
    title: str
    sentiment_score: float
    event_type: str
    impact_score: int
    affected_sectors: list[str]
    stress_test_triggered: bool
