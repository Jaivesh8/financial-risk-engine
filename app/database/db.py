"""SQLite storage for completed stress tests."""

import sqlite3
import json
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "risk_engine.db"


def _connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _initialize(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS stress_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER,
            event TEXT NOT NULL,
            impact_score REAL NOT NULL,
            pre_value REAL NOT NULL,
            post_value REAL NOT NULL,
            loss REAL NOT NULL,
            loss_pct REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def insert_stress_test(result: dict) -> int:
    """Persist a stress-test result and return its database identifier."""
    with _connect() as connection:
        _initialize(connection)
        cursor = connection.execute(
            """
            INSERT INTO stress_tests (
                signal_id, event, impact_score, pre_value, post_value, loss, loss_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.get("signal_id"), result["event"], result["impact_score"],
                result["pre_value"], result["post_value"], result["loss"], result["loss_pct"],
            ),
        )
        return int(cursor.lastrowid)


def list_stress_tests(limit: int = 10) -> list[dict]:
    """Return the most recent persisted stress tests, newest first."""
    with _connect() as connection:
        _initialize(connection)
        rows = connection.execute(
            "SELECT * FROM stress_tests ORDER BY id DESC LIMIT ?",
            (max(1, min(int(limit), 100)),),
        ).fetchall()
    return [dict(row) for row in rows]


def get_signal(signal_id: int) -> dict | None:
    """Fetch an optional stored signal, returning None when signal storage is absent."""
    try:
        with _connect() as connection:
            row = connection.execute(
                """
                SELECT id, event, impact_score, affected_sectors
                FROM signals WHERE id = ?
                """,
                (signal_id,),
            ).fetchone()
    except sqlite3.OperationalError:
        return None

    if row is None:
        return None

    sectors = row["affected_sectors"]
    return {
        "signal_id": row["id"],
        "event": row["event"],
        "impact_score": row["impact_score"],
        "affected_sectors": json.loads(sectors) if sectors else [],
    }
