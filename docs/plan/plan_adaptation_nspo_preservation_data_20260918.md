# NSPO - Kế hoạch tích hợp preservation data

## Phase 0: Input Clarification

- Codebase hiện có: Python, PyTorch, verl/FSDP.
- Phạm vi: tích hợp bộ 1.000 prompt đã chuẩn bị trong GRIT vào NSPO.
- Model đích: `Qwen/Qwen2.5-0.5B-Instruct`.
- Ràng buộc: chỉ dùng null-space projection của NSPO; không thêm preservation KL.

## Phase 1: Requirements Analysis (EARS)

- WHEN actor NSPO được khởi tạo, THE SYSTEM SHALL đọc preservation dataset từ đường dẫn cấu hình.
- WHEN dataset được nạp, THE SYSTEM SHALL xác nhận cột prompt tồn tại, dữ liệu không rỗng và đủ số mẫu yêu cầu.
- WHEN tạo preservation contexts, THE SYSTEM SHALL dùng tokenizer/chat template và frozen checkpoint trùng với actor base model.
- WHEN tính projector, THE SYSTEM SHALL loại padding khỏi thống kê activation và dùng threshold từ cấu hình.
- WHEN training chạy, THE SYSTEM SHALL áp dụng projection theo chu kỳ cấu hình.
- WHEN script mẫu được chạy, THE SYSTEM SHALL dùng `Qwen/Qwen2.5-0.5B-Instruct` và dataset đã copy trong repo.

## Phase 2: Specification

### Thiết kế

Preservation config nằm dưới `actor_rollout_ref.model.preservation`. Worker nạp JSONL cục bộ, dùng toàn bộ 1.000 prompt, sinh continuation bằng frozen base model, tích lũy non-central covariance của activation MLP rồi tạo null-space projector. Trainer tiếp tục GRPO trên safety data và gọi phép chiếu theo chu kỳ cấu hình.

### Phân tích trade-off

| Approach | Ưu điểm | Nhược điểm | Độ phức tạp | Khuyến nghị |
|---|---|---|---|---|
| Sửa trực tiếp path trong Python | Ít dòng | Không tái lập, vi phạm chính sách config | Thấp | Không |
| Cấu hình hóa loader/projector hiện có | Tái lập, fail-fast, giữ kiến trúc NSPO | Thêm một nhóm config | Trung bình | Có |
| Thêm pipeline KL của GRIT | Nhiều ràng buộc bảo toàn hơn | Khác mục tiêu người dùng | Cao | Không |

### Edge cases

| Edge case | Điều kiện | Hành vi mong đợi | Tác động nếu bỏ qua |
|---|---|---|---|
| Sai path | File không tồn tại | Dừng với lỗi rõ ràng | Training thất bại muộn |
| Sai schema | Không có cột `prompt` | Dừng với lỗi rõ ràng | Tokenization lỗi khó hiểu |
| Dataset thiếu mẫu | Ít hơn `sample_size` | Dừng, không sampling lặp | Thí nghiệm lệch cấu hình |
| Prompt rỗng | Chuỗi rỗng/whitespace | Dừng và báo record | Projector nhận context vô nghĩa |
| Padding | Batch có độ dài khác nhau | Không đưa padding vào covariance | Projector bị nhiễu |

### Exception handling

| Exception | Nguồn | Xử lý | Khôi phục |
|---|---|---|---|
| `FileNotFoundError` | Dataset path | Báo path đã resolve | Sửa config và chạy lại |
| `ValueError` | Schema/count/prompt | Báo invariant vi phạm | Sửa artifact/config |
| CUDA/OOM | Generation/SVD | Giữ batch size trong config | Giảm batch size rồi chạy lại |

### Race conditions

| Shared resource | Kịch bản | Rủi ro | Giảm thiểu |
|---|---|---|---|
| Projection matrices | Nhiều distributed ranks | Projector khác nhau | Deterministic input/order và broadcast từ rank 0 theo flow hiện có |
| Dataset files | Nhiều rank chỉ đọc | Không có write race | Artifact bất biến, kiểm tra checksum ngoài training |

## Phase 3: Implementation Planning

### ROOT TASK: Adaptation - NSPO preservation data

1. Copy dataset và manifest vào repo.
2. Thêm preservation fields vào model config/YAML.
3. Viết test Red cho config, loader invariants và script model/path.
4. Cập nhật `_get_proj_weight()` để dùng config, Qwen chat template, attention mask và toàn bộ pool.
5. Cấu hình chu kỳ projection trong trainer và script.
6. Chạy test, compile check và review diff.

### Execution-ready tasks

Task: Copy preservation artifact  
Goal: Repo tự chứa đúng pool 1.000 prompt.  
Files: `data/preservation/nspo_mix/*`  
Minimal change: copy JSONL, Parquet và manifest không biến đổi.  
Verify command: `Get-FileHash` và đếm dòng JSONL.  
Expected output: checksum/count khớp nguồn GRIT.

Task: Configure and load projector data  
Goal: Loại bỏ runtime policy hardcode.  
Files: `verl/verl/trainer/config/ppo_trainer.yaml`, `verl/verl/workers/fsdp_workers.py`, `verl/verl/trainer/ppo/ray_trainer.py`  
Minimal change: đọc các giá trị hiện có từ config và fail-fast.  
Verify command: focused pytest.  
Expected output: tests pass.

Task: Provide runnable launch defaults  
Goal: Script dùng Qwen2.5-0.5B và artifact trong repo.  
Files: `script/nspo_verl_rule_base.sh`  
Minimal change: đặt default qua biến môi trường có thể override.  
Verify command: shell syntax check khi shell khả dụng, cùng static assertions.  
Expected output: model và preservation path resolve đúng.
