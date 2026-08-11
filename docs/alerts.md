# Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `high_latency_p95`
- Severity: `warning`
- SLI/SLO liên quan: `latency_p95_ms`; P95 ≤ 3000 ms.
- Điều kiện và thời gian duy trì: `latency_p95 > 3000ms for 5 minutes`.
- Ảnh hưởng tới người dùng: phần lớn request chậm rõ rệt; người dùng phải chờ quá 3 giây để nhận phản hồi.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận P50/P95/P99 và thời điểm P95 vượt 3000 ms trên panel Latency.
  2. Mở các trace chậm trong cùng cửa sổ thời gian, so sánh waterfall `run`, `retrieve` và `generate` để khoanh vùng span chiếm thời gian.
  3. Dùng correlation ID của trace chậm để tìm log `response_sent` hoặc `request_failed`, rồi kiểm tra `latency_ms`, `error_type` và incident đang bật.
- Mitigation tạm thời: giảm concurrency hoặc lưu lượng vào hệ thống; nếu waterfall xác nhận retrieval chậm, tạm chuyển sang fallback không dùng retrieval trong khi owner xử lý nguyên nhân.
- Owner: `on-call-engineer`.

## Alert 2

- Tên: `elevated_error_rate`
- Severity: `critical`
- SLI/SLO liên quan: `error_rate_pct`; error rate ≤ 2%.
- Điều kiện và thời gian duy trì: `error_rate_pct > 5 for 3 minutes`.
- Ảnh hưởng tới người dùng: hơn 5% request không trả được câu trả lời thành công trong ít nhất 3 phút.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận error rate và breakdown theo `error_type` trên panel Error trong đúng cửa sổ cảnh báo.
  2. Mở các trace lỗi trong cửa sổ đó, kiểm tra span cuối cùng thành công và span bắt đầu lỗi.
  3. Tra correlation ID trong `data/logs.jsonl`, đối chiếu event `request_failed`, `error_type` và payload đã được redaction.
- Mitigation tạm thời: vô hiệu hóa đường xử lý hoặc dependency đang gây lỗi khi đã được trace/log chứng minh; điều hướng sang fallback và giảm concurrency cho đến khi tỷ lệ lỗi phục hồi.
- Owner: `on-call-engineer`.

## Alert 3

- Tên: `cost_budget_exceeded`
- Severity: `warning`
- SLI/SLO liên quan: `daily_cost_usd`; chi phí ≤ 2.5 USD/ngày.
- Điều kiện và thời gian duy trì: `daily_cost_usd > 2.5`.
- Ảnh hưởng tới người dùng: ngân sách vận hành trong ngày đã bị vượt; nếu tiếp tục tăng, dịch vụ có thể phải giới hạn lưu lượng hoặc giảm khả năng phục vụ.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận tổng `cost_usd` trong cửa sổ 24 giờ và kiểm tra xu hướng chi phí trên panel Cost.
  2. Mở các trace có cost hoặc token cao, so sánh `prompt_tokens`, `completion_tokens`, model và feature.
  3. Dùng correlation ID để đối chiếu log `response_sent`, đặc biệt `tokens_in`, `tokens_out` và `cost_usd`; kiểm tra đồng thời panel Traffic để phân biệt tăng chi phí do lưu lượng hay do chi phí mỗi request.
- Mitigation tạm thời: áp dụng giới hạn token/output hoặc rate limit cho feature đã được dữ liệu xác nhận gây tăng chi phí; không tắt toàn bộ dịch vụ nếu chưa cần thiết.
- Owner: `team-lead`.

## Vì sao cảnh báo phải symptom-based?

Cảnh báo symptom-based đo trực tiếp điều người dùng cảm nhận: phản hồi chậm, request thất bại hoặc dịch vụ vượt ngân sách có nguy cơ bị giới hạn. Vì vậy cảnh báo vẫn đúng khi code được refactor, đổi tên hàm hay thay dependency. Ngược lại, lỗi của một hàm nội bộ có thể được retry/fallback thành công và người dùng không bị ảnh hưởng; alert theo tên hàm khi đó tạo nhiễu. Tín hiệu triệu chứng phù hợp với SLI/SLO, giúp on-call ưu tiên theo mức ảnh hưởng, sau đó dùng trace và log để tìm nguyên nhân triển khai cụ thể.
