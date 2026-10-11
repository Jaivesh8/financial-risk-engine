"""Derive the loan-book sector mix from positive transaction spend."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TRANSACTIONS_PATH = ROOT / "data" / "raw" / "transactions_data.csv"
MCC_CODES_PATH = ROOT / "data" / "raw" / "mcc_codes.json"
PORTFOLIO_PATH = ROOT / "data" / "portfolio.csv"
CHUNK_SIZE = 500_000
LOAN_BOOK_VALUE_CR = Decimal("40")

SECTOR_KEYWORDS = {
    "Banking": ("bank", "financial", "credit", "loan", "insurance", "investment"),
    "Energy": ("fuel", "petroleum", "gas", "electric", "utility", "service station"),
    "Technology": ("computer", "software", "electronics", "telecommunication", "data processing"),
    "Logistics": ("airline", "transport", "freight", "shipping", "railroad", "toll", "parking"),
    "Healthcare": ("medical", "hospital", "dental", "pharmacy", "drug", "health"),
    "Real Estate": ("real estate", "property", "rental", "lease", "hotel", "lodging"),
    "Automotive": ("automotive", "automobile", "motor vehicle", "car rental", "vehicle"),
    "Commodities": ("metal", "agricultur", "lumber", "coal", "chemical", "raw material"),
}


def sector_for_description(description: str) -> str:
    """Map an MCC description to one transparent, keyword-based sector."""
    description = description.lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(keyword in description for keyword in keywords):
            return sector
    return "Consumer"


def positive_spend_by_sector() -> dict[str, Decimal]:
    """Read only amount and MCC columns, in chunks, and aggregate positive spend."""
    with MCC_CODES_PATH.open("r", encoding="utf-8") as source:
        descriptions = json.load(source)

    spend_by_mcc: dict[str, Decimal] = defaultdict(Decimal)
    for chunk in pd.read_csv(
        TRANSACTIONS_PATH,
        usecols=["amount", "mcc"],
        dtype={"amount": "string", "mcc": "string"},
        chunksize=CHUNK_SIZE,
    ):
        amounts = pd.to_numeric(
            chunk["amount"].str.replace("$", "", regex=False).str.replace(",", "", regex=False),
            errors="coerce",
        )
        positive = chunk.loc[amounts.gt(0), ["mcc"]].copy()
        positive["amount"] = amounts[amounts.gt(0)]
        for mcc, amount in positive.groupby("mcc", dropna=True)["amount"].sum().items():
            spend_by_mcc[str(mcc)] += Decimal(str(amount))

    sector_totals: dict[str, Decimal] = defaultdict(Decimal)
    for mcc, amount in spend_by_mcc.items():
        sector_totals[sector_for_description(descriptions.get(mcc, ""))] += amount
    return dict(sector_totals)


def build_portfolio() -> list[dict[str, str]]:
    """Write loan exposure plus synthetic non-loan rows to data/portfolio.csv."""
    sector_totals = positive_spend_by_sector()
    total_spend = sum(sector_totals.values(), Decimal())
    if total_spend <= 0:
        raise ValueError("No positive transaction amounts were found.")

    ordered_sectors = sorted(sector_totals)
    rows: list[dict[str, str]] = []
    allocated = Decimal()
    for sector in ordered_sectors[:-1]:
        value_cr = (LOAN_BOOK_VALUE_CR * sector_totals[sector] / total_spend).quantize(
            Decimal("0.000001")
        )
        allocated += value_cr
        rows.append({
            "asset_class": "loans",
            "sector": sector,
            "value_cr": str(value_cr),
            "source": "derived from transactions_data.csv",
        })
    final_sector = ordered_sectors[-1]
    rows.append({
        "asset_class": "loans",
        "sector": final_sector,
        "value_cr": str(LOAN_BOOK_VALUE_CR - allocated),
        "source": "derived from transactions_data.csv",
    })
    rows.extend([
        {"asset_class": "corp_bonds", "sector": "Banking", "value_cr": "20", "source": "synthetic assumption"},
        {"asset_class": "govt_bonds", "sector": "Fixed Income", "value_cr": "20", "source": "synthetic assumption"},
        {"asset_class": "equities", "sector": "Mixed", "value_cr": "15", "source": "synthetic assumption"},
        {"asset_class": "derivatives", "sector": "Mixed", "value_cr": "5", "source": "synthetic assumption"},
    ])

    if sum(Decimal(row["value_cr"]) for row in rows) != Decimal("100"):
        raise AssertionError("Portfolio rows must total exactly 100 crore.")

    PORTFOLIO_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PORTFOLIO_PATH.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["asset_class", "sector", "value_cr", "source"])
        writer.writeheader()
        writer.writerows(rows)

    print("Derived loan-book sector weights:")
    for row in rows:
        if row["asset_class"] == "loans":
            weight = Decimal(row["value_cr"]) / LOAN_BOOK_VALUE_CR * 100
            print(f"  {row['sector']}: {weight:.4f}% ({row['value_cr']} cr)")
    print("Portfolio total: 100 crore")
    print(f"Wrote: {PORTFOLIO_PATH}")
    return rows


if __name__ == "__main__":
    build_portfolio()
