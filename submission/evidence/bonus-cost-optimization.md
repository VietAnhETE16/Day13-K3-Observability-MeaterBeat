# Bonus cost optimization evidence

## Setup

- Incident: `cost_spike`
- Mitigation: `/config/cost-optimization/enable?max_output_tokens=220`
- Implementation: `app/mock_llm.py` caps `output_tokens` through `app/cost_control.py` before cost is estimated.

## Before

Command:

```bash
python scripts/inject_incident.py --scenario cost_spike
python scripts/load_test.py --concurrency 5
curl http://127.0.0.1:8000/metrics
```

Metrics after the before run:

```json
{"traffic":10,"latency_p50":151.0,"latency_p95":3566.0,"latency_p99":3566.0,"avg_cost_usd":0.008,"total_cost_usd":0.0803,"tokens_in_total":330,"tokens_out_total":5288,"error_breakdown":{},"error_rate_pct":0.0,"quality_avg":0.88}
```

Representative log lines:

```text
req-f5302301 tokens_out=696 cost_usd=0.010545
req-84b080d6 tokens_out=720 cost_usd=0.010884
```

## After

Command:

```bash
curl -X POST 'http://127.0.0.1:8000/config/cost-optimization/enable?max_output_tokens=220'
python scripts/load_test.py --concurrency 5
curl http://127.0.0.1:8000/metrics
```

Metrics after the after run, cumulative since server reload:

```json
{"traffic":20,"latency_p50":151.0,"latency_p95":3566.0,"latency_p99":3566.0,"avg_cost_usd":0.0057,"total_cost_usd":0.1143,"tokens_in_total":660,"tokens_out_total":7488,"error_breakdown":{},"error_rate_pct":0.0,"quality_avg":0.88}
```

Marginal after run:

- `total_cost_usd`: `0.1143 - 0.0803 = 0.0340`
- `tokens_out_total`: `7488 - 5288 = 2200`
- all 10 after-run responses had `tokens_out=220`

Result:

- Cost per 10 requests dropped from about `$0.0803` to about `$0.0340`.
- Reduction: about `57.7%`.

