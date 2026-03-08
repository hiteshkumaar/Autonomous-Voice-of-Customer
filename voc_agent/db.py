import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

from voc_agent.config import DB_PATH


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    review_id TEXT NOT NULL,
    review_title TEXT,
    review_text TEXT,
    rating REAL,
    review_date TEXT,
    author TEXT,
    sentiment TEXT,
    themes TEXT,
    inserted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, review_id)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS run_reviews (
    run_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    review_id TEXT NOT NULL,
    PRIMARY KEY (run_id, product_id, review_id)
);
"""


@contextmanager
def get_conn(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA_SQL)


def execute_many(query: str, rows: Iterable[tuple]) -> None:
    with get_conn() as conn:
        conn.executemany(query, rows)


def fetch_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute(query, params)
        return cur.fetchall()


def execute(query: str, params: tuple = ()) -> None:
    with get_conn() as conn:
        conn.execute(query, params)
