from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.dashboard import calculate_dashboard_values, render_dashboard
from app.main import app


def test_dashboard_calculates_all_six_groups() -> None:
    now = datetime.now(timezone.utc).isoformat()
    records = [
        {"ts": now, "event": "request_received"},
        {"ts": now, "event": "request_received"},
        {
            "ts": now,
            "event": "response_sent",
            "latency_ms": 100,
            "cost_usd": 0.01,
            "tokens_in": 10,
            "tokens_out": 20,
            "quality_score": 0.8,
        },
        {"ts": now, "event": "request_failed", "error_type": "TimeoutError"},
    ]

    values = calculate_dashboard_values(records)

    assert values["latency_p95"] == 100
    assert values["request_count"] == 2
    assert sum(values["traffic_by_minute"].values()) == 2
    assert values["error_rate"] == 50
    assert values["error_breakdown"] == {"TimeoutError": 1}
    assert values["total_cost"] == 0.01
    assert sum(values["cost_by_minute"].values()) == 0.01
    assert values["tokens_in"] == 10
    assert values["tokens_out"] == 20
    assert values["quality_avg"] == 0.8


def test_dashboard_html_contains_contract_and_six_panels() -> None:
    page = render_dashboard([])

    for panel_id in ("latency", "traffic", "errors", "cost", "tokens", "quality"):
        assert f'id="{panel_id}"' in page
    assert "Last 60 minutes" in page
    assert "refresh 30s" in page
    assert "SLO: P95 ≤ 3000 ms" in page


def test_dashboard_route_is_available() -> None:
    with TestClient(app) as client:
        response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Day 13 AI Observability" in response.text
