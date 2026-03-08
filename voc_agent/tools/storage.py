from __future__ import annotations

from typing import Any

from voc_agent.db import execute, execute_many, fetch_all


def begin_run(run_id: str, started_at: str) -> None:
    execute(
        "INSERT OR REPLACE INTO ingestion_runs(run_id, started_at, status) VALUES (?, ?, ?)",
        (run_id, started_at, "running"),
    )


def end_run(run_id: str, completed_at: str, status: str, notes: str = "") -> None:
    execute(
        "UPDATE ingestion_runs SET completed_at = ?, status = ?, notes = ? WHERE run_id = ?",
        (completed_at, status, notes, run_id),
    )


def insert_reviews(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    inserted: list[dict[str, Any]] = []
    for row in rows:
        before = fetch_all(
            "SELECT 1 FROM reviews WHERE product_id = ? AND review_id = ?",
            (row["product_id"], row["review_id"]),
        )
        if before:
            continue
        execute_many(
            """
            INSERT INTO reviews(
                run_id, source, product_id, product_name, review_id,
                review_title, review_text, rating, review_date, author, sentiment, themes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(
                row["run_id"], row["source"], row["product_id"], row["product_name"], row["review_id"],
                row.get("review_title", ""), row.get("review_text", ""), row.get("rating"),
                row.get("review_date", ""), row.get("author", "anonymous"), row.get("sentiment", "Neutral"), row.get("themes", "")
            )],
        )
        execute(
            "INSERT OR IGNORE INTO run_reviews(run_id, product_id, review_id) VALUES (?, ?, ?)",
            (row["run_id"], row["product_id"], row["review_id"]),
        )
        inserted.append(row)
    return inserted


def get_run_delta(run_id: str) -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT r.*
        FROM reviews r
        JOIN run_reviews rr
          ON rr.review_id = r.review_id
         AND rr.product_id = r.product_id
        WHERE rr.run_id = ?
        """,
        (run_id,),
    )
    return [dict(r) for r in rows]


def get_all_reviews() -> list[dict[str, Any]]:
    return [dict(r) for r in fetch_all("SELECT * FROM reviews")]
