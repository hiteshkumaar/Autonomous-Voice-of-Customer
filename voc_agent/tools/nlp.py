from __future__ import annotations

import json
from typing import Any
import requests

from voc_agent.config import CLAWDBOT_API_KEY, CLAWDBOT_BASE_URL, CLAWDBOT_MODEL, REQUEST_TIMEOUT_SEC

THEMES = {
    "Sound Quality": ["sound", "bass", "treble", "audio", "volume", "mic"],
    "Battery Life": ["battery", "charging", "charge", "backup", "drain"],
    "Comfort/Fit": ["fit", "comfort", "ear", "wear", "lightweight", "pain"],
    "App Experience": ["app", "pair", "bluetooth", "firmware", "connect"],
    "Price/Value": ["price", "value", "cost", "expensive", "worth"],
    "Delivery": ["delivery", "shipping", "packaging", "courier"],
    "Build Quality": ["build", "quality", "material", "durable", "case", "hinge"],
    "ANC": ["anc", "noise cancellation", "noise cancel", "transparency"],
}

POSITIVE_HINTS = {"great", "excellent", "love", "good", "awesome", "best", "amazing", "impressed"}
NEGATIVE_HINTS = {"bad", "poor", "worst", "hate", "issue", "problem", "broken", "defect", "refund"}


def _rule_sentiment(text: str, rating: float | None) -> str:
    t = (text or "").lower()
    pos = sum(w in t for w in POSITIVE_HINTS)
    neg = sum(w in t for w in NEGATIVE_HINTS)
    if rating is not None:
        if rating >= 4 and pos >= neg:
            return "Positive"
        if rating <= 2 and neg >= pos:
            return "Negative"
    if pos > neg:
        return "Positive"
    if neg > pos:
        return "Negative"
    return "Neutral"


def _rule_themes(text: str, title: str) -> list[str]:
    body = f"{title} {text}".lower()
    tags = [theme for theme, words in THEMES.items() if any(w in body for w in words)]
    return tags or ["Build Quality"]


def _llm_available() -> bool:
    return bool(CLAWDBOT_API_KEY and CLAWDBOT_BASE_URL and CLAWDBOT_MODEL)


def _llm_classify(text: str, title: str, rating: float | None) -> tuple[str, list[str]]:
    prompt = (
        "Classify one review. Return strict JSON: "
        "{\"sentiment\":\"Positive|Negative|Neutral\",\"themes\":[...]} . "
        f"Allowed themes: {list(THEMES.keys())}. "
        f"Title: {title}\nText: {text}\nRating: {rating}"
    )
    payload: dict[str, Any] = {
        "model": CLAWDBOT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {CLAWDBOT_API_KEY}", "Content-Type": "application/json"}
    base = CLAWDBOT_BASE_URL.rstrip("/")
    if base.endswith("/chat/completions"):
        endpoint = base
    elif base.endswith("/v1"):
        endpoint = base + "/chat/completions"
    else:
        endpoint = base + "/v1/chat/completions"
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SEC)
    resp.raise_for_status()
    msg = resp.json()["choices"][0]["message"]["content"]
    parsed = json.loads(msg)
    sentiment = parsed.get("sentiment", "Neutral")
    themes = [t for t in parsed.get("themes", []) if t in THEMES]
    return sentiment, themes or _rule_themes(text, title)


def classify_review(title: str, text: str, rating: float | None) -> tuple[str, list[str]]:
    if _llm_available():
        try:
            return _llm_classify(text, title, rating)
        except Exception:
            pass
    sentiment = _rule_sentiment(f"{title} {text}", rating)
    themes = _rule_themes(text, title)
    return sentiment, themes
