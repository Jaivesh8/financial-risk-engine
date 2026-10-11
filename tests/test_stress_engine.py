from app.risk.calculator import run_stress_test, should_trigger
from app.risk.portfolio import CRORE, Portfolio


def test_portfolio_initial_value_is_100_crore():
    assert Portfolio().total_value == 100 * CRORE


def test_revalue_with_equity_shock_loses_1_5_crore():
    portfolio = Portfolio()

    post_value = portfolio.revalue({"equities": 0.90})

    assert portfolio.total_value - post_value == 1.5 * CRORE


def test_geopolitical_stress_test_has_loss():
    result = run_stress_test(Portfolio(), "Geopolitical", 9, ["Banking"])

    assert result["loss"] > 0
    assert len(result["by_asset_class"]) == 5
    assert result["by_asset_class"][0]["asset_class"] == "loans"


def test_geopolitical_event_at_eight_triggers():
    assert should_trigger("Geopolitical", 8.0) is True


def test_low_impact_other_event_does_not_trigger():
    assert should_trigger("Other", 6.0) is False
