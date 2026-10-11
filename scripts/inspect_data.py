"""Print a compact, dependency-free profile for every CSV in data/raw/."""

from __future__ import annotations

import csv
import math
import statistics
from collections import Counter
from pathlib import Path


RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
SAMPLE_SIZE = 5
TOP_VALUES = 10


def is_null(value: str | None) -> bool:
    return value is None or value.strip().lower() in {"", "null", "none", "nan", "na", "n/a"}


def as_number(value: str | None) -> float | None:
    """Parse common CSV number formats, or return None for non-numeric data."""
    if is_null(value):
        return None
    try:
        return float(value.strip().replace(",", "").replace("₹", "").replace("$", ""))
    except ValueError:
        return None


def infer_type(values: list[str | None]) -> str:
    populated = [value for value in values if not is_null(value)]
    if not populated:
        return "unknown (all null)"
    numeric = [as_number(value) for value in populated]
    if all(value is not None for value in numeric):
        return "int" if all(value.is_integer() for value in numeric) else "float"
    return "string"


def is_amount_column(name: str, column_type: str) -> bool:
    name = name.lower()
    return column_type in {"int", "float"} and any(
        marker in name for marker in ("amount", "amt", "value", "balance", "price", "payment")
    )


def profile_csv(path: Path) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        columns = reader.fieldnames or []
        rows = list(reader)

    values_by_column = {column: [row.get(column) for row in rows] for column in columns}
    types = {column: infer_type(values) for column, values in values_by_column.items()}

    print(f"\n{'=' * 80}\nFile: {path.name}")
    print(f"Row count: {len(rows)}")
    print("Columns and inferred types:")
    for column in columns:
        print(f"  - {column}: {types[column]}")

    print(f"Sample rows (up to {SAMPLE_SIZE}):")
    for row in rows[:SAMPLE_SIZE]:
        print(f"  {row}")

    print("Null counts:")
    for column in columns:
        print(f"  - {column}: {sum(is_null(value) for value in values_by_column[column])}")

    for column in columns:
        values = values_by_column[column]
        non_null = [value for value in values if not is_null(value)]
        # String columns with a manageable number of distinct values are categorical.
        if types[column] == "string" and non_null and len(set(non_null)) <= 100:
            print(f"Top {TOP_VALUES} values for categorical column '{column}':")
            for value, count in Counter(non_null).most_common(TOP_VALUES):
                print(f"  - {value}: {count}")

        if is_amount_column(column, types[column]):
            numbers = [as_number(value) for value in non_null]
            numbers = [value for value in numbers if value is not None and math.isfinite(value)]
            if numbers:
                print(
                    f"Amount statistics for '{column}': "
                    f"min={min(numbers)}, median={statistics.median(numbers)}, max={max(numbers)}"
                )


def main() -> None:
    if not RAW_DATA_DIR.is_dir():
        print(f"No raw-data directory found: {RAW_DATA_DIR}")
        return

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in: {RAW_DATA_DIR}")
        return

    for csv_file in csv_files:
        profile_csv(csv_file)


if __name__ == "__main__":
    main()
