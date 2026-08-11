from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .pii import scrub_text

AUDIT_LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))


def write_audit_event(event: str, *, actor: str = "system", payload: dict[str, Any] | None = None) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": event,
        "actor": actor,
        "payload": _scrub(payload or {}),
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as audit_log:
        audit_log.write(json.dumps(record, ensure_ascii=False) + "\n")


def _scrub(value: Any) -> Any:
    if isinstance(value, str):
        return scrub_text(value)
    if isinstance(value, dict):
        return {key: _scrub(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_scrub(item) for item in value]
    return value
