from __future__ import annotations

import html
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from . import logging_config
from .metrics import percentile


TIME_RANGE_MINUTES = 60
REFRESH_SECONDS = 30


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_recent_records(
    path: Path | None = None,
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    log_path = path or logging_config.LOG_PATH
    if not log_path.exists():
        return []

    current_time = now or datetime.now(timezone.utc)
    cutoff = current_time - timedelta(minutes=TIME_RANGE_MINUTES)
    records: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        timestamp = _parse_timestamp(record.get("ts"))
        if timestamp is not None and cutoff <= timestamp <= current_time:
            records.append(record)
    return records


def calculate_dashboard_values(records: list[dict[str, Any]]) -> dict[str, Any]:
    responses = [record for record in records if record.get("event") == "response_sent"]
    requests = [record for record in records if record.get("event") == "request_received"]
    errors = [record for record in records if record.get("event") == "request_failed"]

    latencies = [
        int(record["latency_ms"])
        for record in responses
        if isinstance(record.get("latency_ms"), (int, float))
    ]
    costs = [
        float(record["cost_usd"])
        for record in responses
        if isinstance(record.get("cost_usd"), (int, float))
    ]
    qualities = [
        float(record["quality_score"])
        for record in responses
        if isinstance(record.get("quality_score"), (int, float))
    ]
    error_breakdown = Counter(
        str(record.get("error_type") or "UnknownError") for record in errors
    )
    traffic_by_minute: Counter[str] = Counter()
    cost_by_minute: Counter[str] = Counter()
    for record in requests:
        timestamp = _parse_timestamp(record.get("ts"))
        if timestamp is not None:
            traffic_by_minute[timestamp.strftime("%H:%M")] += 1
    for record in responses:
        timestamp = _parse_timestamp(record.get("ts"))
        cost = record.get("cost_usd")
        if timestamp is not None and isinstance(cost, (int, float)):
            cost_by_minute[timestamp.strftime("%H:%M")] += float(cost)

    return {
        "latency_p50": percentile(latencies, 50),
        "latency_p95": percentile(latencies, 95),
        "latency_p99": percentile(latencies, 99),
        "request_count": len(requests),
        "request_rate": round(len(requests) / TIME_RANGE_MINUTES, 2),
        "traffic_by_minute": dict(traffic_by_minute),
        "error_rate": round((len(errors) / len(requests)) * 100, 2) if requests else 0.0,
        "error_breakdown": dict(error_breakdown),
        "total_cost": round(sum(costs), 6),
        "cost_by_minute": {
            minute: round(cost, 6) for minute, cost in cost_by_minute.items()
        },
        "tokens_in": sum(
            int(record.get("tokens_in", 0))
            for record in responses
            if isinstance(record.get("tokens_in"), (int, float))
        ),
        "tokens_out": sum(
            int(record.get("tokens_out", 0))
            for record in responses
            if isinstance(record.get("tokens_out"), (int, float))
        ),
        "quality_avg": round(mean(qualities), 2) if qualities else 0.0,
    }


def _status(value: float, operator: str, threshold: float) -> str:
    passed = value <= threshold if operator == "lte" else value >= threshold
    return "ok" if passed else "alert"


def _render_series(
    series: dict[str, int | float],
    *,
    prefix: str = "",
    suffix: str = "",
    precision: int = 0,
) -> str:
    points = sorted(series.items())[-6:]
    if not points:
        return '<div class="empty-series">No samples in this window</div>'
    max_value = max(float(value) for _, value in points) or 1.0
    rows: list[str] = []
    for label, raw_value in points:
        value = float(raw_value)
        width = max(4.0, min(100.0, (value / max_value) * 100))
        formatted = f"{prefix}{value:.{precision}f}{suffix}"
        rows.append(
            '<div class="series-row">'
            f'<span>{html.escape(label)}</span>'
            f'<div class="bar-track"><div class="bar" style="width:{width:.1f}%"></div></div>'
            f"<strong>{formatted}</strong>"
            "</div>"
        )
    return '<div class="series">' + "".join(rows) + "</div>"


def render_dashboard(records: list[dict[str, Any]] | None = None) -> str:
    values = calculate_dashboard_values(records if records is not None else load_recent_records())
    breakdown = values["error_breakdown"]
    breakdown_html = (
        "".join(
            f"<li><span>{html.escape(error_type)}</span><strong>{count}</strong></li>"
            for error_type, count in sorted(breakdown.items())
        )
        or "<li><span>No errors</span><strong>0</strong></li>"
    )
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    traffic_series = _render_series(values["traffic_by_minute"], suffix=" req")
    cost_series = _render_series(values["cost_by_minute"], prefix="$", precision=4)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="{REFRESH_SECONDS}">
  <title>Day 13 AI Observability</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, system-ui, sans-serif; }}
    body {{ margin: 0; background: #07111f; color: #e5eefb; }}
    main {{ max-width: 1320px; margin: auto; padding: 28px; }}
    header {{ display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 22px; }}
    h1 {{ margin: 0 0 6px; font-size: 28px; }}
    .subtitle, .updated {{ color: #93a4bb; font-size: 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }}
    .panel {{ background: #101d2e; border: 1px solid #263851; border-radius: 14px; padding: 20px; min-height: 190px; }}
    .panel h2 {{ margin: 0; font-size: 17px; }}
    .unit {{ color: #93a4bb; font-size: 12px; margin-top: 4px; }}
    .metrics {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 25px 0 20px; }}
    .metric strong {{ display: block; font-size: 28px; color: #f8fbff; }}
    .metric span {{ color: #9eb0c8; font-size: 12px; }}
    .threshold {{ border-radius: 999px; display: inline-block; font-size: 12px; font-weight: 700; padding: 6px 10px; }}
    .ok {{ color: #72e6a6; background: #103a2c; }}
    .alert {{ color: #ff9f9f; background: #492129; }}
    ul {{ list-style: none; padding: 0; margin: 16px 0; }}
    li {{ display: flex; justify-content: space-between; border-bottom: 1px solid #263851; padding: 6px 0; }}
    .series {{ display: grid; gap: 5px; margin: 12px 0 16px; }}
    .series-row {{ align-items: center; display: grid; font-size: 11px; gap: 8px; grid-template-columns: 38px 1fr 70px; }}
    .series-row span, .empty-series {{ color: #93a4bb; }}
    .series-row strong {{ text-align: right; }}
    .bar-track {{ background: #23344a; border-radius: 999px; height: 6px; overflow: hidden; }}
    .bar {{ background: #5ea5ff; border-radius: inherit; height: 100%; }}
    footer {{ color: #71849e; font-size: 12px; margin-top: 20px; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} header {{ align-items: start; flex-direction: column; }} }}
  </style>
</head>
<body>
<main>
  <header>
    <div><h1>Day 13 AI Observability</h1><div class="subtitle">Last {TIME_RANGE_MINUTES} minutes · refresh {REFRESH_SECONDS}s · source: data/logs.jsonl</div></div>
    <div class="updated">Updated {updated_at}</div>
  </header>
  <div class="grid">
    <section class="panel" id="latency">
      <h2>Latency percentiles</h2><div class="unit">milliseconds (ms)</div>
      <div class="metrics">
        <div class="metric"><strong>{values['latency_p50']:.0f}</strong><span>P50</span></div>
        <div class="metric"><strong>{values['latency_p95']:.0f}</strong><span>P95</span></div>
        <div class="metric"><strong>{values['latency_p99']:.0f}</strong><span>P99</span></div>
      </div>
      <div class="threshold {_status(values['latency_p95'], 'lte', 3000)}">SLO: P95 ≤ 3000 ms</div>
    </section>
    <section class="panel" id="traffic">
      <h2>Request traffic</h2><div class="unit">requests / requests per minute</div>
      <div class="metrics">
        <div class="metric"><strong>{values['request_count']}</strong><span>requests</span></div>
        <div class="metric"><strong>{values['request_rate']:.2f}</strong><span>requests/min</span></div>
      </div>
      {traffic_series}
      <div class="threshold {_status(values['request_rate'], 'gte', 1)}">Threshold: rate ≥ 1 request/min</div>
    </section>
    <section class="panel" id="errors">
      <h2>Error rate and breakdown</h2><div class="unit">percent (%) / count by error type</div>
      <div class="metrics"><div class="metric"><strong>{values['error_rate']:.2f}%</strong><span>error rate</span></div></div>
      <ul>{breakdown_html}</ul>
      <div class="threshold {_status(values['error_rate'], 'lte', 2)}">SLO: error rate ≤ 2%</div>
    </section>
    <section class="panel" id="cost">
      <h2>Cost over time</h2><div class="unit">US dollars (USD)</div>
      <div class="metrics"><div class="metric"><strong>${values['total_cost']:.6f}</strong><span>total cost</span></div></div>
      {cost_series}
      <div class="threshold {_status(values['total_cost'], 'lte', 2.5)}">Budget: total ≤ $2.50</div>
    </section>
    <section class="panel" id="tokens">
      <h2>Input and output tokens</h2><div class="unit">tokens</div>
      <div class="metrics">
        <div class="metric"><strong>{values['tokens_in']}</strong><span>input</span></div>
        <div class="metric"><strong>{values['tokens_out']}</strong><span>output</span></div>
      </div>
      <div class="threshold {_status(max(values['tokens_in'], values['tokens_out']), 'lte', 50000)}">Threshold: each total ≤ 50,000 tokens</div>
    </section>
    <section class="panel" id="quality">
      <h2>Quality proxy</h2><div class="unit">score (0–1)</div>
      <div class="metrics"><div class="metric"><strong>{values['quality_avg']:.2f}</strong><span>mean quality</span></div></div>
      <div class="threshold {_status(values['quality_avg'], 'gte', 0.75)}">SLO: mean ≥ 0.75</div>
    </section>
  </div>
  <footer>Contract: config/dashboard.yaml · Runtime evidence for Checkpoint 2</footer>
</main>
</body>
</html>"""
