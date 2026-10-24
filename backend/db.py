"""
db.py — SQLite connection handling.

The database file defaults to jac_predictor.db next to this file. Point
somewhere else with an environment variable:
    DB_PATH=/path/to/jac_predictor.db

The API only reads data, so the file is opened read-only. Rows come back
as plain dicts (column name -> value), same shape the old MySQL DictCursor gave.
"""
import os
import sqlite3
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", str(Path(__file__).resolve().parent / "jac_predictor.db"))


def _dict_factory(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


def get_connection():
    path = Path(DB_PATH)
    if not path.is_file():
        raise FileNotFoundError(
            f"SQLite database not found at {path}. Build it with: "
            f"python data-pipeline/build_db.py (see the root README), or set DB_PATH."
        )
    conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    conn.row_factory = _dict_factory
    return conn


def fetch_all(sql, params=None):
    """Run one query and return all rows as a list of dicts."""
    conn = get_connection()
    try:
        return conn.execute(sql, params or {}).fetchall()
    finally:
        conn.close()
