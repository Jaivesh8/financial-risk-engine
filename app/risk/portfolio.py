"""Simple portfolio valuation for transparent stress-test calculations."""

CRORE = 10_000_000


class Portfolio:
    """A INR 100 crore portfolio with fixed asset and sector exposures."""

    def __init__(self) -> None:
        self.assets = {
            "loans": 40 * CRORE,
            "corp_bonds": 20 * CRORE,
            "govt_bonds": 20 * CRORE,
            "equities": 15 * CRORE,
            "derivatives": 5 * CRORE,
        }
        self.sector_exposure = {
            "loans": "Banking",
            "corp_bonds": "Banking",
            "govt_bonds": "Fixed Income",
            "equities": "Mixed",
            "derivatives": "Mixed",
        }

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
