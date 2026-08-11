from __future__ import annotations

import json
from pathlib import Path

from app import audit, cost_control
from app.mock_llm import FakeLLM
from app.incidents import STATE


def test_audit_event_writes_scrubbed_jsonl(monkeypatch, tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "AUDIT_LOG_PATH", audit_path)

    audit.write_audit_event(
        "incident_enabled",
        actor="test",
        payload={"name": "cost_spike", "note": "owner student@example.com"},
    )

    record = json.loads(audit_path.read_text(encoding="utf-8"))
    assert record["event"] == "incident_enabled"
    assert record["actor"] == "test"
    assert record["payload"]["name"] == "cost_spike"
    assert "student@example.com" not in json.dumps(record)
    assert "REDACTED_EMAIL" in record["payload"]["note"]


def test_cost_optimization_caps_cost_spike_tokens(monkeypatch) -> None:
    monkeypatch.setattr(cost_control.STATE, "enabled", True)
    monkeypatch.setattr(cost_control.STATE, "max_output_tokens", 120)
    monkeypatch.setitem(STATE, "cost_spike", True)
    monkeypatch.setattr("app.mock_llm.random.randint", lambda _start, _end: 180)

    response = FakeLLM().generate.__wrapped__(FakeLLM(), "Feature=qa\nQuestion=hello")

    assert response.usage.output_tokens == 120
