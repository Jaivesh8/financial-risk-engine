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
    post_value = portfolio.revalue(get_shocks(event, impact_score))
    loss = pre_value - post_value
    loss_pct = (loss / pre_value * 100.0) if pre_value else 0.0

    return {
        "pre_value": pre_value,
        "post_value": post_value,
        "loss": loss,
        "loss_pct": loss_pct,
        "event": event,
        "impact_score": float(impact_score),
        "affected_sectors": affected_sectors,
    }
