"""Transparent, tunable shock scenarios for the stress-testing engine."""

from app.risk.portfolio import Portfolio


# Values are percentage changes before impact scaling, not price multipliers.
SCENARIO_SHOCKS = {
    "Geopolitical": {"equities": -0.10, "corp_bonds": -0.05, "loans": -0.02},
    "Macroeconomic": {"govt_bonds": -0.04, "equities": -0.08, "loans": -0.03},
    "Credit Event": {"corp_bonds": -0.08, "loans": -0.05, "govt_bonds": -0.02},
    "Regulatory": {"equities": -0.03, "corp_bonds": -0.02},
    "Other": {asset: -0.01 for asset in Portfolio().assets},
}


def get_shocks(event: str, impact_score: float) -> dict[str, float]:
    """Return asset multipliers with shocks scaled by impact_score / 10."""
    changes = SCENARIO_SHOCKS.get(event, SCENARIO_SHOCKS["Other"])
    scale = max(0.0, min(1.0, float(impact_score) / 10.0))
    return {asset: 1.0 + change * scale for asset, change in changes.items()}
