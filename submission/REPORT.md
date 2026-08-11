# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: 60 trace có tag `lab` (xác minh qua Langfuse API ngày 2026-08-11)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `config/dashboard.yaml` và `docs/dashboard-spec.md`

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/log_sample.jsonl` (ví dụ `correlation_id: "req-dfffbcb8"` đồng bộ giữa `request_received` và `response_sent`)
- Evidence PII redaction: `submission/evidence/log_sample.jsonl` (`[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]`) và `submission/evidence/log_validator.png`
- Evidence trace waterfall: cần bổ sung ảnh giao diện Langfuse vào `submission/evidence/`; trace đã xác minh: `393b6a3e3ab66838f0deeac3420e4248`.
- Giải thích một span đáng chú ý: trace trên có `run` (GENERATION) bao hai span con `retrieve` và `generate`, cho phép tách thời gian retrieval khỏi thời gian sinh câu trả lời.

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: đặc tả đủ sáu nhóm tại `docs/dashboard-spec.md`; cần bổ sung ảnh theo hình thức dashboard được nhóm chọn.
- SLO đã chọn và lý do: giữ bộ giá trị mặc định của checkpoint tại `config/slo.yaml` (P95 ≤ 3000 ms, error rate ≤ 2%, chi phí ngày ≤ 2.5 USD, quality trung bình ≥ 0.75).
- Alert rules và runbook: `config/alert_rules.yaml` và `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
