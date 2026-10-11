"""Simple portfolio valuation for transparent stress-test calculations."""

import csv
from collections import defaultdict
from pathlib import Path

CRORE = 10_000_000
PORTFOLIO_PATH = Path(__file__).resolve().parents[2] / "data" / "portfolio.csv"
DEFAULT_ASSETS = {
    "loans": 40 * CRORE,
    "corp_bonds": 20 * CRORE,
    "govt_bonds": 20 * CRORE,
    "equities": 15 * CRORE,
    "derivatives": 5 * CRORE,
}


class Portfolio:
    """A INR 100 crore portfolio with fixed asset and sector exposures."""

    def __init__(self) -> None:
        self.assets = self._load_assets()
        self.sector_exposure = {
            "loans": "Banking",
            "corp_bonds": "Banking",
            "govt_bonds": "Fixed Income",
            "equities": "Mixed",
            "derivatives": "Mixed",
        }

    @staticmethod
    def _load_assets() -> dict[str, float]:
        """Load CSV portfolio totals, retaining fixed asset-class totals on fallback."""
        if not PORTFOLIO_PATH.is_file():
            return DEFAULT_ASSETS.copy()

        totals: dict[str, float] = defaultdict(float)
        try:
            with PORTFOLIO_PATH.open("r", encoding="utf-8", newline="") as source:
                for row in csv.DictReader(source):
                    totals[row["asset_class"]] += float(row["value_cr"]) * CRORE
        except (OSError, KeyError, TypeError, ValueError):
            return DEFAULT_ASSETS.copy()

        if set(totals) != set(DEFAULT_ASSETS):
            return DEFAULT_ASSETS.copy()
        if any(abs(totals[asset] - DEFAULT_ASSETS[asset]) > 1 for asset in DEFAULT_ASSETS):
            return DEFAULT_ASSETS.copy()
        return dict(totals)

    @property
    def total_value(self) -> float:
        return float(sum(self.assets.values()))

    def revalue(self, shocks: dict[str, float]) -> float:
        """Return the portfolio value after applying asset-type multipliers.

        Assets absent from ``shocks`` retain their current value.  The method is
        non-mutating, allowing the same portfolio to be evaluated repeatedly.
        """
        return float(sum(
            value * shocks.get(asset_type, 1.0)
            for asset_type, value in self.assets.items()
        ))
