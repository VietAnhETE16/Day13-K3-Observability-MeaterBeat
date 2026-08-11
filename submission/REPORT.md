# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

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
