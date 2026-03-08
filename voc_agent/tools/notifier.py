from __future__ import annotations

from pathlib import Path

import requests

from voc_agent.config import (
    MARKETING_TEAM_WEBHOOK_URL,
    PRODUCT_TEAM_WEBHOOK_URL,
    REQUEST_TIMEOUT_SEC,
    SUPPORT_TEAM_WEBHOOK_URL,
)


def _extract_section(report_text: str, heading: str) -> str:
    lines = report_text.splitlines()
    start = -1
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i + 1
            break
    if start == -1:
        return "No section found."

    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("## ") and line.strip() != heading:
            break
        out.append(line)
    return "\n".join(out).strip() or "No content."


def _post_webhook(url: str, title: str, body: str) -> None:
    if not url:
        return
    payload = {"text": f"{title}\n\n{body}"}
    resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT_SEC)
    resp.raise_for_status()


def push_action_items(global_report_path: Path, weekly_report_path: Path, run_id: str, delta_count: int) -> None:
    global_text = global_report_path.read_text(encoding="utf-8") if global_report_path.exists() else ""
    weekly_text = weekly_report_path.read_text(encoding="utf-8") if weekly_report_path.exists() else ""

    product_summary = _extract_section(weekly_text or global_text, "### Product")
    marketing_summary = _extract_section(weekly_text or global_text, "### Marketing")
    support_summary = _extract_section(weekly_text or global_text, "### Support")

    header = f"VoC Weekly Action Push | run_id={run_id} | new_reviews={delta_count}"

    _post_webhook(PRODUCT_TEAM_WEBHOOK_URL, header + " | Team=Product", product_summary)
    _post_webhook(MARKETING_TEAM_WEBHOOK_URL, header + " | Team=Marketing", marketing_summary)
    _post_webhook(SUPPORT_TEAM_WEBHOOK_URL, header + " | Team=Support", support_summary)
