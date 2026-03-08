from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from voc_agent.config import NOTIFY_ON_ZERO_DELTA, OUTPUT_DIR, PRODUCT_CONFIG_PATH
from voc_agent.db import init_db
from voc_agent.tools.nlp import classify_review
from voc_agent.tools.notifier import push_action_items
from voc_agent.tools.reports import write_action_report
from voc_agent.tools.scraper import fetch_reviews_from_url, load_reviews_from_csv
from voc_agent.tools.storage import begin_run, end_run, get_all_reviews, get_run_delta, insert_reviews
from voc_agent.utils import load_json, stable_hash, utc_now_iso


def _source_from_url(url: str) -> str:
    if "amazon" in url.lower():
        return "amazon"
    if "flipkart" in url.lower():
        return "flipkart"
    return "web"


def _build_rows(run_id: str, product: dict[str, Any], source: str, reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for r in reviews:
        review_id = stable_hash(
            product["product_id"],
            r.get("title", ""),
            r.get("text", ""),
            str(r.get("rating", "")),
            r.get("date", ""),
            r.get("author", ""),
        )
        sentiment, themes = classify_review(r.get("title", ""), r.get("text", ""), r.get("rating"))
        rows.append(
            {
                "run_id": run_id,
                "source": source,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "review_id": review_id,
                "review_title": r.get("title", ""),
                "review_text": r.get("text", ""),
                "rating": r.get("rating"),
                "review_date": r.get("date", ""),
                "author": r.get("author", "anonymous"),
                "sentiment": sentiment,
                "themes": "|".join(themes),
            }
        )
    return rows


def _write_delta_sample(delta_rows: list[dict[str, Any]], run_id: str) -> None:
    path = OUTPUT_DIR / f"delta_sample_{run_id}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["product_id", "review_id", "rating", "review_date", "sentiment", "themes", "review_title", "review_text"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in delta_rows[:30]:
            w.writerow({k: r.get(k, "") for k in cols})


def run_weekly_ingestion(use_seed_csv: bool = False) -> str:
    init_db()
    config = load_json(PRODUCT_CONFIG_PATH)

    run_id = utc_now_iso().replace(":", "-")
    begin_run(run_id, utc_now_iso())

    try:
        all_inserted = []
        for product in config.get("products", []):
            urls = product.get("urls", [])
            for url in urls:
                source = _source_from_url(url)
                if use_seed_csv:
                    seed_file = Path("data") / f"seed_{product['product_id']}.csv"
                    reviews = load_reviews_from_csv(seed_file)
                else:
                    reviews = fetch_reviews_from_url(url)

                rows = _build_rows(run_id, product, source, reviews)
                inserted = insert_reviews(rows)
                all_inserted.extend(inserted)

        all_rows = get_all_reviews()
        delta_rows = get_run_delta(run_id)

        global_report = OUTPUT_DIR / "global_action_items.md"
        weekly_report = OUTPUT_DIR / "weekly_delta_action_items.md"
        write_action_report(all_rows, global_report, "Global Action Item Report")
        write_action_report(delta_rows, weekly_report, "Weekly Delta Action Item Report")
        _write_delta_sample(delta_rows, run_id)

        if delta_rows or NOTIFY_ON_ZERO_DELTA:
            push_action_items(global_report, weekly_report, run_id, len(delta_rows))

        end_run(run_id, utc_now_iso(), "success", notes=f"Inserted {len(all_inserted)} new reviews")
        return run_id
    except Exception as exc:
        end_run(run_id, utc_now_iso(), "failed", notes=str(exc))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run weekly VoC ingestion pipeline")
    parser.add_argument("--seed", action="store_true", help="Use local seed CSV data instead of live scraping")
    args = parser.parse_args()

    run = run_weekly_ingestion(use_seed_csv=args.seed)
    print(f"Ingestion complete. run_id={run}")
