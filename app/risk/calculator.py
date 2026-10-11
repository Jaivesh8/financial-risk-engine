"""Stress-test trigger and calculation functions."""

from app.risk.portfolio import Portfolio
from app.risk.scenarios import SCENARIO_SHOCKS, get_shocks


def should_trigger(event: str, impact_score: float) -> bool:
    """Return whether a recognized event clears the automatic trigger level."""
    return event in SCENARIO_SHOCKS and float(impact_score) > 7.0


def run_stress_test(
    portfolio: Portfolio,
    event: str,
    impact_score: float,
    affected_sectors: list,
) -> dict:
    """Revalue a portfolio under the requested event scenario."""
    pre_value = portfolio.total_value
    shocks = get_shocks(event, impact_score)
    post_value = portfolio.revalue(shocks)
    loss = pre_value - post_value
    loss_pct = (loss / pre_value * 100.0) if pre_value else 0.0
    by_asset_class = []
    for asset_class, asset_pre_value in portfolio.assets.items():
        asset_post_value = asset_pre_value * shocks.get(asset_class, 1.0)
        asset_loss = asset_pre_value - asset_post_value
        by_asset_class.append({
            "asset_class": asset_class,
            "pre_value": float(asset_pre_value),
            "post_value": float(asset_post_value),
            "loss": float(asset_loss),
            "loss_pct": (
                asset_loss / asset_pre_value * 100.0 if asset_pre_value else 0.0
            ),
        })

    return {
        "pre_value": pre_value,
        "post_value": post_value,
        "loss": loss,
        "loss_pct": loss_pct,
        "event": event,
        "impact_score": float(impact_score),
        "affected_sectors": affected_sectors,
        "by_asset_class": by_asset_class,
    }
