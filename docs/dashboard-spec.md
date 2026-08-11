# Đặc tả dashboard

## Cấu hình chung

- Công cụ: dashboard dạng spec, contract tại `config/dashboard.yaml`.
- Nguồn chuẩn: `data/logs.jsonl`; endpoint `/metrics` dùng để kiểm tra nhanh giá trị hiện tại.
- Khoảng thời gian mặc định: 60 phút.
- Tần suất refresh: 30 giây.
- Mỗi panel hiển thị rõ tên, đơn vị và threshold/SLO line.

## Sáu nhóm chỉ số kỹ thuật

| # | Nhóm / tên panel | Nguồn dữ liệu và phép tổng hợp | Đơn vị | Threshold / SLO |
|---|---|---|---|---|
| 1 | Latency — `Latency percentiles` | Event `response_sent`, field `latency_ms`; P50/P95/P99 | ms | P95 ≤ 3000 ms |
| 2 | Traffic — `Request traffic` | Event `request_received`; count và rate theo phút | requests/minute | Rate ≥ 1 request/phút |
| 3 | Error — `Error rate and breakdown` | `request_failed / request_received × 100`; breakdown theo `error_type` | % | Error rate ≤ 2% |
| 4 | Cost — `Cost over time` | Event `response_sent`, tổng `cost_usd` theo phút và toàn cửa sổ | USD | Tổng chi phí ≤ 2.5 USD |
| 5 | Tokens — `Input and output tokens` | Event `response_sent`, tổng riêng `tokens_in` và `tokens_out` | tokens | Tổng theo field ≤ 50.000 tokens |
| 6 | Quality — `Quality proxy` | Event `response_sent`, trung bình `quality_score` | score 0–1 | Mean ≥ 0.75 |

## Kiểm tra và evidence

Kiểm tra snapshot hiện tại:

```bash
curl http://localhost:8000/metrics | python -m json.tool
```

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```

Kết quả hợp lệ phải có dòng `HỢP LỆ: 6/6 panel`. Evidence dashboard phải nhìn được sáu tên panel, time range 60 phút, đơn vị và threshold; lưu trong `submission/evidence/`.
