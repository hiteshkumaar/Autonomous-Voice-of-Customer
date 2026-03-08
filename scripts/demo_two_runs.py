import csv
from pathlib import Path

from voc_agent.pipeline import run_weekly_ingestion


def append_new_rows() -> None:
    rows_1 = [
        {
            "title": "ANC got worse after update",
            "text": "After firmware update, ANC now has hiss noise.",
            "rating": "2",
            "date": "2026-03-01",
            "author": "Samar",
        },
        {
            "title": "Superb fit improvement",
            "text": "New ear tips made the comfort much better.",
            "rating": "5",
            "date": "2026-03-02",
            "author": "Pooja",
        },
    ]
    rows_2 = [
        {
            "title": "Battery praise this week",
            "text": "Still getting great battery backup after one month.",
            "rating": "5",
            "date": "2026-03-01",
            "author": "Akash",
        },
        {
            "title": "Pairing became unstable",
            "text": "Bluetooth disconnects randomly after calls.",
            "rating": "2",
            "date": "2026-03-03",
            "author": "Isha",
        },
    ]

    for path, rows in [
        (Path("data/seed_master_buds_1.csv"), rows_1),
        (Path("data/seed_master_buds_max.csv"), rows_2),
    ]:
        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "text", "rating", "date", "author"])
            for r in rows:
                writer.writerow(r)


if __name__ == "__main__":
    first = run_weekly_ingestion(use_seed_csv=True)
    append_new_rows()
    second = run_weekly_ingestion(use_seed_csv=True)
    print(f"Initial run: {first}")
    print(f"Delta run: {second}")
    print("Check outputs/ for global_action_items.md, weekly_delta_action_items.md, and delta_sample_<run_id>.csv")
