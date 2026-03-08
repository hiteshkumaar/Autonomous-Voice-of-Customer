from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dt_parser

from voc_agent.config import MAX_REVIEWS_PER_PRODUCT, REQUEST_TIMEOUT_SEC
from voc_agent.utils import stable_hash


def _parse_date(value: str) -> str:
    if not value:
        return ""
    try:
        return dt_parser.parse(value, fuzzy=True).date().isoformat()
    except Exception:
        return value.strip()


def _safe_rating(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"(\d+(?:\.\d+)?)", str(value))
    return float(m.group(1)) if m else None


def _extract_jsonld_reviews(soup: BeautifulSoup) -> list[dict]:
    reviews: list[dict] = []
    for node in soup.select("script[type='application/ld+json']"):
        text = node.get_text(strip=True)
        if not text:
            continue
        try:
            payload = json.loads(text)
        except Exception:
            continue

        chunks = payload if isinstance(payload, list) else [payload]
        for chunk in chunks:
            items = []
            if isinstance(chunk, dict) and "review" in chunk:
                maybe = chunk.get("review")
                items = maybe if isinstance(maybe, list) else [maybe]
            elif isinstance(chunk, dict) and chunk.get("@type") == "Review":
                items = [chunk]

            for item in items:
                if not isinstance(item, dict):
                    continue
                title = item.get("name") or ""
                text = item.get("reviewBody") or ""
                rating = _safe_rating((item.get("reviewRating") or {}).get("ratingValue"))
                date = _parse_date(item.get("datePublished") or "")
                author_obj = item.get("author") or {}
                author = author_obj.get("name") if isinstance(author_obj, dict) else str(author_obj)
                if title or text:
                    reviews.append({
                        "title": title.strip(),
                        "text": text.strip(),
                        "rating": rating,
                        "date": date,
                        "author": (author or "anonymous").strip(),
                    })
    return reviews


def _extract_common_dom_reviews(soup: BeautifulSoup) -> list[dict]:
    candidates = soup.select("[data-hook='review'], .review, ._27M-vq")
    out = []
    for c in candidates:
        title = ""
        text = ""
        rating = None
        date = ""
        author = ""

        title_node = c.select_one("[data-hook='review-title'], .review-title, ._2-N8zT")
        text_node = c.select_one("[data-hook='review-body'], .review-text, .t-ZTKy")
        rating_node = c.select_one("[data-hook='review-star-rating'], .review-rating, ._3LWZlK")
        date_node = c.select_one("[data-hook='review-date'], .review-date, ._2sc7ZR")
        author_node = c.select_one(".a-profile-name, .review-author, ._2sc7ZR")

        if title_node:
            title = title_node.get_text(" ", strip=True)
        if text_node:
            text = text_node.get_text(" ", strip=True)
        if rating_node:
            rating = _safe_rating(rating_node.get_text(" ", strip=True))
        if date_node:
            date = _parse_date(date_node.get_text(" ", strip=True))
        if author_node:
            author = author_node.get_text(" ", strip=True)

        if title or text:
            out.append({
                "title": title,
                "text": text,
                "rating": rating,
                "date": date,
                "author": author or "anonymous",
            })
    return out


def fetch_reviews_from_url(url: str) -> list[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SEC)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    reviews = _extract_jsonld_reviews(soup)
    if len(reviews) < 5:
        reviews.extend(_extract_common_dom_reviews(soup))

    dedup = {}
    for r in reviews:
        key = stable_hash(r.get("title", ""), r.get("text", ""), str(r.get("rating", "")), r.get("date", ""))
        dedup[key] = r
    return list(dedup.values())[:MAX_REVIEWS_PER_PRODUCT]


def load_reviews_from_csv(csv_path: str | Path) -> list[dict]:
    import csv

    rows = []
    with Path(csv_path).open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "title": (r.get("title") or "").strip(),
                "text": (r.get("text") or "").strip(),
                "rating": _safe_rating(r.get("rating")),
                "date": _parse_date(r.get("date") or ""),
                "author": (r.get("author") or "anonymous").strip(),
            })
    return rows
