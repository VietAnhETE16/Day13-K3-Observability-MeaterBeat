from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app


def test_chat_response_log_exposes_quality_for_dashboard(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "Explain observability",
            },
        )

    assert response.status_code == 200
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    response_event = next(event for event in events if event["event"] == "response_sent")
    assert response_event["quality_score"] == response.json()["quality_score"]


def test_correlation_id_generated_and_propagated(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "student-02",
                "session_id": "session-02",
                "feature": "qa",
                "message": "Hello observability",
            },
        )

    assert response.status_code == 200
    cid = response.headers.get("x-request-id")
    assert cid is not None
    assert cid.startswith("req-")
    assert len(cid) == 12  # "req-" (4) + 8 hex chars = 12
    assert response.json()["correlation_id"] == cid
    assert "x-response-time-ms" in response.headers

    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    for ev in events:
        if ev.get("service") == "api":
            assert ev["correlation_id"] == cid


def test_custom_correlation_id_preserved(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    custom_id = "req-aabb1122"
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": custom_id},
            json={
                "user_id": "student-03",
                "session_id": "session-03",
                "feature": "summary",
                "message": "Summarize logs",
            },
        )

    assert response.status_code == 200
    assert response.headers.get("x-request-id") == custom_id
    assert response.json()["correlation_id"] == custom_id

    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    for ev in events:
        if ev.get("service") == "api":
            assert ev["correlation_id"] == custom_id


def test_log_enrichment_fields(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "user-vip-99",
                "session_id": "sess-vip-88",
                "feature": "summary",
                "message": "Enrich my logs",
            },
        )

    assert response.status_code == 200
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    api_events = [ev for ev in events if ev.get("service") == "api"]
    assert len(api_events) >= 2  # request_received & response_sent

    for ev in api_events:
        assert ev["session_id"] == "sess-vip-88"
        assert ev["feature"] == "summary"
        assert "model" in ev and ev["model"] is not None
        assert "env" in ev and ev["env"] is not None
        assert "user_id_hash" in ev
        assert ev["user_id_hash"] != "user-vip-99"  # Hashed, not raw
        assert len(ev["user_id_hash"]) == 12
