from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def _theme_sentiment_stats(rows: Iterable[dict]) -> dict[tuple[str, str], Counter]:
    stats: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for r in rows:
        product = r.get("product_name", r.get("product_id", "unknown"))
        sentiment = r.get("sentiment", "Neutral")
        themes = [x.strip() for x in (r.get("themes") or "").split("|") if x.strip()]
        for t in themes:
            stats[(product, t)][sentiment] += 1
    return stats


def _top_quotes(rows: Iterable[dict], sentiment: str, limit: int = 3) -> list[str]:
    picks = []
    for r in rows:
        if r.get("sentiment") != sentiment:
            continue
        text = (r.get("review_text") or "").strip()
        if text:
            picks.append(text[:180])
        if len(picks) >= limit:
            break
    return picks


def _department_actions(rows: list[dict]) -> dict[str, list[str]]:
    neg = [r for r in rows if r.get("sentiment") == "Negative"]
    pos = [r for r in rows if r.get("sentiment") == "Positive"]

    actions = {
        "Product": [],
        "Marketing": [],
        "Support": [],
    }

    theme_counts = Counter()
    for r in neg:
        for t in (r.get("themes") or "").split("|"):
            if t:
                theme_counts[t] += 1

    for theme, cnt in theme_counts.most_common(4):
        actions["Product"].append(f"Investigate recurring {theme} complaints ({cnt} negative mentions).")

    pos_themes = Counter()
    for r in pos:
        for t in (r.get("themes") or "").split("|"):
            if t:
                pos_themes[t] += 1
    for theme, cnt in pos_themes.most_common(3):
        actions["Marketing"].append(f"Emphasize {theme} in campaigns ({cnt} positive mentions).")

    for theme, cnt in theme_counts.most_common(3):
        actions["Support"].append(f"Publish troubleshooting macros for {theme} issues ({cnt} recent tickets expected).")

    for team in actions:
        if not actions[team]:
            actions[team].append("No major issues detected in this period.")

    return actions


def write_action_report(rows: list[dict], output_path: Path, title: str) -> None:
    stats = _theme_sentiment_stats(rows)
    actions = _department_actions(rows)

    lines = [f"# {title}", "", f"Total reviews analyzed: {len(rows)}", "", "## Theme Snapshot"]
    for (product, theme), counter in sorted(stats.items()):
        lines.append(
            f"- {product} | {theme}: +{counter['Positive']} / -{counter['Negative']} / ={counter['Neutral']}"
        )

    lines.extend(["", "## Department Action Items"])
    for dept, items in actions.items():
        lines.append(f"### {dept}")
        for item in items:
            lines.append(f"- {item}")

    lines.extend(["", "## Evidence Snippets (Negative)"])
    for q in _top_quotes(rows, "Negative"):
        lines.append(f"- \"{q}\"")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
