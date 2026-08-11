from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from statistics import mean
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.cli import configure_utf8_stdio

PII_DETECTORS = {
    "email": re.compile(r"[\w.-]+@[\w.-]+\.\w+"),
    "phone_vn": re.compile(r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)"),
    "cccd": re.compile(r"\b\d{12}\b"),
    "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
}


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    index = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[index])


def detect(records: list[dict[str, Any]], *, latency_slo_ms: int, cost_budget_usd: float) -> list[str]:
    findings: list[str] = []
    responses = [record for record in records if record.get("event") == "response_sent"]
    failures = [record for record in records if record.get("event") == "request_failed"]
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
    tokens_out = [
        int(record["tokens_out"])
        for record in responses
        if isinstance(record.get("tokens_out"), (int, float))
    ]

    latency_p95 = percentile(latencies, 95)
    if latency_p95 > latency_slo_ms:
        findings.append(f"LATENCY_SLO_BREACH p95={latency_p95:.0f}ms threshold={latency_slo_ms}ms")

    total_cost = sum(costs)
    if total_cost > cost_budget_usd:
        findings.append(f"COST_BUDGET_BREACH total_cost_usd={total_cost:.6f} threshold={cost_budget_usd:.6f}")

    if tokens_out and max(tokens_out) > max(300, mean(tokens_out) * 2):
        findings.append(f"TOKEN_SPIKE max_tokens_out={max(tokens_out)} avg_tokens_out={mean(tokens_out):.1f}")

    if failures:
        error_types = sorted({str(record.get("error_type") or "UnknownError") for record in failures})
        findings.append(f"REQUEST_FAILURES count={len(failures)} error_types={','.join(error_types)}")

    pii_hits: list[str] = []
    for record in records:
        raw = json.dumps(record, ensure_ascii=False)
        for name, detector in PII_DETECTORS.items():
            if detector.search(raw):
                pii_hits.append(f"{record.get('event', 'unknown')}:{name}")
    if pii_hits:
        findings.append(f"PII_LEAK count={len(pii_hits)} samples={';'.join(pii_hits[:5])}")

    return findings


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Detect simple anomalies from data/logs.jsonl")
    parser.add_argument("--log-path", type=Path, default=Path("data/logs.jsonl"))
    parser.add_argument("--latency-slo-ms", type=int, default=3000)
    parser.add_argument("--cost-budget-usd", type=float, default=2.5)
    args = parser.parse_args()

    records = load_records(args.log_path)
    findings = detect(records, latency_slo_ms=args.latency_slo_ms, cost_budget_usd=args.cost_budget_usd)
    if findings:
        print("ANOMALY DETECTED")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("OK: no anomaly detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
