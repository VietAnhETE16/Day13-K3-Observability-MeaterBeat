from app import metrics
from app.metrics import percentile, record_error, record_request, snapshot


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_error_rate_pct(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 0)
    monkeypatch.setattr(metrics, "ERRORS", metrics.Counter())
    monkeypatch.setattr(metrics, "REQUEST_LATENCIES", [])
    monkeypatch.setattr(metrics, "REQUEST_COSTS", [])
    monkeypatch.setattr(metrics, "REQUEST_TOKENS_IN", [])
    monkeypatch.setattr(metrics, "REQUEST_TOKENS_OUT", [])
    monkeypatch.setattr(metrics, "QUALITY_SCORES", [])

    assert snapshot()["error_rate_pct"] == 0.0

    record_request(latency_ms=100, cost_usd=0.001, tokens_in=10, tokens_out=20, quality_score=0.9)
    assert snapshot()["error_rate_pct"] == 0.0

    record_error("TimeoutError")
    # 1 success + 1 error = 50.0%
    assert snapshot()["error_rate_pct"] == 50.0
