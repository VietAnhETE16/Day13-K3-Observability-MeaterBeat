# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Meater Beat
- Repository URL: https://github.com/VietAnhETE16/Day13-K3-Observability-MeaterBeat
- Commit SHA cuối: `eef89987606c16863ff83fc7f8fc83851cf5897e`
- Thành viên và vai trò:
  - Mai Việt Anh — trưởng nhóm — mã học viên `2A202601083` — CP1: Logging và PII.
  - Lương Đăng Doanh — thành viên — mã học viên `2A202601209` — CP2: Metrics, traces và dashboard.
  - Trương Đình Khoa — thành viên — mã học viên `2A202601297` — CP3: Điều tra challenge.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: 124 trace có tag `lab` (xác minh qua Langfuse API ngày 2026-08-11)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `http://127.0.0.1:8000/dashboard`, `config/dashboard.yaml` và `docs/dashboard-spec.md`

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/log_sample.jsonl` (ví dụ `correlation_id: "req-dfffbcb8"` đồng bộ giữa `request_received` và `response_sent`)
- Evidence PII redaction: `submission/evidence/log_sample.jsonl` (`[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]`) và `submission/evidence/log_validator.png`
- Evidence danh sách trace: `submission/evidence/cp2-trace-list.png`.
- Evidence trace waterfall: `submission/evidence/cp2-trace-waterfall.png`; trace `23fdac4725e65af966debf76d8f9dce6`.
- Giải thích một span đáng chú ý: trace trên có `run` (GENERATION) bao hai span con `retrieve` và `generate`, cho phép tách thời gian retrieval khỏi thời gian sinh câu trả lời.

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Version/label baseline: version 1, labels `baseline` và `production` (trạng thái cuối sau rollback).
- Version/label candidate: version 2, labels `candidate` và `latest`.
- Trace ID của mỗi version: baseline v1 `9d94ef9507a308f99eb4db0bac40e626`; candidate v2 `e012eb73cc1c300971287b3ab7766a39`.
- Bằng chứng đổi label hoặc rollback: production trên v2 `8712e45d8f16ec5f981e02e05aa366e2`; production sau rollback về v1 `c724dd6021022bc5e7058ac323246190`. Xác minh API tại `submission/evidence/cp2-prompt-verification.md`; cần bổ sung ảnh giao diện Langfuse trước/sau rollback.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: `submission/evidence/cp2-dashboard-runtime.png`; kết quả validator tại `submission/evidence/cp2-dashboard-validator.png`.
- SLO đã chọn và lý do: giữ bộ giá trị mặc định của checkpoint tại `config/slo.yaml` (P95 ≤ 3000 ms, error rate ≤ 2%, chi phí ngày ≤ 2.5 USD, quality trung bình ≥ 0.75).
- Alert rules và runbook: `config/alert_rules.yaml` và `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`; incident chính thức `rag_slow`; affected feature `refund`.
- Triệu chứng từ metrics: sau khi chạy `python scripts/load_test.py --challenge --concurrency 5`, `/metrics` ghi `latency_p95=4092ms`, vượt SLO `3000ms`; `error_rate_pct=0.0`, `total_cost_usd=0.0206`, `quality_avg=0.86`. Load test trả HTTP 200 nhưng các request `refund` mất khoảng `13.27s` từ phía client.
- Trace ID liên quan: mở Langfuse trong khoảng `2026-08-11T05:06Z` đến `2026-08-11T05:08Z`, lọc tag `lab` và feature/session `refund`; trace chậm cần xác nhận span `retrieve` chiếm phần lớn latency.
- Log line/correlation ID liên quan: `submission/evidence/cp3-log-evidence.jsonl`, ví dụ `req-245ec5b9` có `feature="refund"` và `latency_ms=4092`; `req-ee27ba38` có `feature="refund"` và `latency_ms=2651`.
- Root cause: incident `rag_slow` bật làm RAG retrieval path chậm. Trong `app/mock_rag.py`, khi `STATE["rag_slow"]` là true, span/function `retrieve()` sleep `2.5s` trước khi trả docs; điều này làm latency tăng nhưng không tạo lỗi hay cost spike.
- Fix action: tắt incident bằng `python scripts/inject_incident.py --disable`; trong hệ thống thật, mitigation tương ứng là dùng retrieval timeout/cache/fallback hoặc tạm chuyển feature `refund` sang fallback không chờ vector retrieval khi P95 vượt SLO.
- Preventive measure: thêm alert `high_latency_p95`, theo dõi P95 theo feature, mở trace chậm để kiểm tra span `retrieve`, và đặt timeout/circuit breaker cho RAG dependency để một retrieval chậm không kéo toàn bộ request vượt SLO.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Mai Việt Anh (`2A202601083`) | Trưởng nhóm; CP1 Logging và PII: correlation ID, JSON log enrichment, user hash và PII redaction. | `eef89987606c16863ff83fc7f8fc83851cf5897e` | Correlation ID nối request/response log; PII phải được scrub trước khi ghi log; validator chỉ kiểm tra kỹ thuật nhanh chứ không thay thế evidence. |
| Lương Đăng Doanh (`2A202601209`) | CP2 Metrics, traces và dashboard: Langfuse traces/prompt metadata, prompt version evidence, dashboard 6 panel, SLO/threshold và alert/runbook. | `eef89987606c16863ff83fc7f8fc83851cf5897e` | Metrics dùng để phát hiện triệu chứng, trace khoanh vùng span, dashboard cần thể hiện latency/traffic/error/token-cost/quality cùng threshold rõ ràng. |
| Trương Đình Khoa (`2A202601297`) | CP3 Challenge: chạy incident `rag_slow`, load test challenge, nối metrics → logs → root cause, đề xuất fix và preventive measure. | `eef89987606c16863ff83fc7f8fc83851cf5897e` | P95 latency tăng nhưng error rate bằng 0 là tín hiệu performance incident; cần dùng trace/log để chứng minh root cause thay vì chỉ nhìn metric. |

## 8. Bonus

- Cost optimization: triển khai giới hạn `output_tokens` bằng `app/cost_control.py` và endpoint `/config/cost-optimization/enable?max_output_tokens=220`. Khi bật `cost_spike`, cost 10 request giảm từ khoảng `$0.0803` xuống `$0.0340` sau mitigation; evidence tại `submission/evidence/bonus-cost-optimization.md`.
- Audit log: `app/audit.py` ghi các sự kiện quan trọng như incident enable/disable và config change vào `data/audit.jsonl` theo `AUDIT_LOG_PATH`; evidence tại `submission/evidence/bonus-audit-and-automation.md`.
- Custom automation: `scripts/detect_anomalies.py` tự động phát hiện latency SLO breach, cost budget breach, token spike, request failure và PII leak từ `data/logs.jsonl`; output mẫu tại `submission/evidence/bonus-audit-and-automation.md`.
