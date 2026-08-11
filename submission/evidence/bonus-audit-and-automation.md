# Bonus audit log and automation evidence

## Audit log

Audit events are written to `data/audit.jsonl` using `AUDIT_LOG_PATH`.

Relevant records:

```json
{"ts": "2026-08-11T05:24:02.922103Z", "event": "config_changed", "actor": "api", "payload": {"config": "cost_optimization", "state": {"enabled": false, "max_output_tokens": 220}}}
{"ts": "2026-08-11T05:24:13.133239Z", "event": "incident_enabled", "actor": "api", "payload": {"name": "cost_spike", "incidents": {"rag_slow": false, "tool_fail": false, "cost_spike": true}}}
{"ts": "2026-08-11T05:24:45.535036Z", "event": "config_changed", "actor": "api", "payload": {"config": "cost_optimization", "state": {"enabled": true, "max_output_tokens": 220}}}
```

## Automation

Script:

```bash
python scripts/detect_anomalies.py
```

Output on current logs:

```text
ANOMALY DETECTED
- TOKEN_SPIKE max_tokens_out=720 avg_tokens_out=253.0
```

The script detects:

- P95 latency over SLO.
- Cost budget breach.
- Output token spike.
- Request failures by `error_type`.
- Raw PII leaks in log records.
