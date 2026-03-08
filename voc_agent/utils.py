import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def stable_hash(*parts: str) -> str:
    payload = "||".join((p or "").strip().lower() for p in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    # Support UTF-8 files with or without BOM.
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)
