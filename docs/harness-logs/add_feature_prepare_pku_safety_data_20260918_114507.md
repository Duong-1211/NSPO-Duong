# Execution Log: Prepare PKU safety data and compact reward model

## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — test schema dữ liệu thất bại như kỳ vọng vì module chuẩn bị dữ liệu chưa tồn tại
- **Nhiệm vụ**: Định nghĩa record PKU-SafeRLHF tương thích VERL.
- **Đầu vào nhận được**: `verl/examples/data_preprocess/full_hh_rlhf.py`, schema `RLHFDataset`, yêu cầu 8.000 mẫu.
- **Files đã sửa**: Không có
- **Files đã tạo**: `verl/tests/data_preprocess/test_prepare_pku_saferlhf.py`
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — lệnh `python -m pytest verl/tests/data_preprocess/test_prepare_pku_saferlhf.py -q` thất bại với `ModuleNotFoundError: No module named 'script.prepare_pku_saferlhf'`, đúng Red dự kiến.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement; cần tạo `script/prepare_pku_saferlhf.py` với `build_rl_record`.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — thêm chuyển đổi một record PKU sang schema VERL; Refactor — no-change-needed
- **Nhiệm vụ**: Làm test schema dữ liệu vượt qua.
- **Đầu vào nhận được**: Test Red `test_build_rl_record_converts_pku_prompt_to_verl_schema`.
- **Files đã sửa**: Không có
- **Files đã tạo**: `script/prepare_pku_saferlhf.py`
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `python -m pytest verl/tests/data_preprocess/test_prepare_pku_saferlhf.py -q`: `1 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed. Tiếp tục vòng Red cho sampling xác định và xuất artifact.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — test sampling xác định thất bại như kỳ vọng vì hàm chưa tồn tại
- **Nhiệm vụ**: Định nghĩa sampling không lặp, tái lập được theo seed.
- **Đầu vào nhận được**: `script/prepare_pku_saferlhf.py` sau Green đầu tiên.
- **Files đã sửa**: `verl/tests/data_preprocess/test_prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — test thất bại với `ImportError: cannot import name 'sample_source_indices'` đúng Red dự kiến.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement để thêm sampling bằng seed.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — thêm sampling theo seed; Refactor — no-change-needed
- **Nhiệm vụ**: Sampling đúng kích thước, không lặp và tái lập được.
- **Đầu vào nhận được**: Test Red `test_sample_source_indices_is_deterministic_and_without_replacement`.
- **Files đã sửa**: `script/prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `2 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed. Tiếp tục vòng Red cho cấu hình và ghi Parquet.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — test cấu hình chung thất bại như kỳ vọng vì loader chưa tồn tại
- **Nhiệm vụ**: Định nghĩa cách đọc runtime policy từ file `.env` dùng chung.
- **Đầu vào nhận được**: Yêu cầu AGENTS.md không hardcode runtime/workflow policy.
- **Files đã sửa**: `verl/tests/data_preprocess/test_prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — test thất bại với `ImportError: cannot import name 'load_env_config'` đúng Red dự kiến.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement để thêm parser `.env` tối thiểu.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — thêm parser `.env`; Refactor — no-change-needed
- **Nhiệm vụ**: Đọc dataset/reward runtime policy từ file cấu hình dùng chung.
- **Đầu vào nhận được**: Test Red `test_load_env_config_reads_dataset_and_reward_runtime_policy`.
- **Files đã sửa**: `script/prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `3 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — test dựng tập sample thất bại như kỳ vọng vì hàm chưa tồn tại
- **Nhiệm vụ**: Bảo toàn source index và đúng số record sau sampling.
- **Đầu vào nhận được**: Hàm record conversion và sampling đã Green.
- **Files đã sửa**: `verl/tests/data_preprocess/test_prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — test thất bại với `ImportError: cannot import name 'build_sampled_records'` đúng Red dự kiến.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — dựng record từ các source index đã sample; Refactor — no-change-needed
- **Nhiệm vụ**: Tạo đúng số record và giữ truy vết source index.
- **Đầu vào nhận được**: Test Red `test_build_sampled_records_preserves_selected_source_indices`.
- **Files đã sửa**: `script/prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `4 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — test ghi/đọc Parquet thất bại như kỳ vọng vì writer chưa tồn tại
- **Nhiệm vụ**: Đảm bảo artifact Parquet round-trip đúng schema chat.
- **Đầu vào nhận được**: `datasets` và `pyarrow` đã được cài trong môi trường kiểm thử.
- **Files đã sửa**: `verl/tests/data_preprocess/test_prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — test thất bại với `ImportError: cannot import name 'write_records'` đúng Red dự kiến.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — thêm Parquet writer; Refactor — no-change-needed
- **Nhiệm vụ**: Ghi artifact đọc lại được bằng Hugging Face Datasets.
- **Đầu vào nhận được**: Test Red `test_write_records_creates_readable_parquet`.
- **Files đã sửa**: `script/prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `5 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — test tạo hai split và manifest thất bại vì orchestrator artifact chưa tồn tại
- **Nhiệm vụ**: Đảm bảo kích thước/file output hoàn toàn lấy từ config.
- **Đầu vào nhận được**: Converter, sampler và Parquet writer đã Green.
- **Files đã sửa**: `verl/tests/data_preprocess/test_prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — test thất bại với `ImportError: cannot import name 'prepare_artifacts'` đúng Red dự kiến.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — tạo train/validation artifacts và manifest; Refactor — no-change-needed
- **Nhiệm vụ**: Xuất các split và metadata tái lập theo config.
- **Đầu vào nhận được**: Test Red `test_prepare_artifacts_writes_configured_splits_and_manifest`.
- **Files đã sửa**: `script/prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `6 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — entry point theo config thất bại vì chưa tồn tại
- **Nhiệm vụ**: Tải đúng dataset/config và ghi vào output dir từ config.
- **Đầu vào nhận được**: Artifact builder đã Green.
- **Files đã sửa**: `verl/tests/data_preprocess/test_prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — test thất bại với `ImportError: cannot import name 'prepare_from_config'` đúng Red dự kiến.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — thêm entry point download/prepare theo config; Refactor — no-change-needed
- **Nhiệm vụ**: Chạy chuẩn bị dữ liệu bằng một lệnh với policy từ config.
- **Đầu vào nhận được**: Test Red `test_prepare_from_config_loads_pku_splits_and_writes_output`.
- **Files đã sửa**: `script/prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `7 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — import reward module thất bại đúng ở lỗi cấu hình credentials hiện hữu
- **Nhiệm vụ**: Đọc reward runtime policy từ environment và không tạo client lỗi tại import.
- **Đầu vào nhận được**: `script/safe_reward.py`, yêu cầu đổi sang Llama Guard 3 1B.
- **Files đã sửa**: Không có
- **Files đã tạo**: `verl/tests/reward_score/test_safe_reward.py`
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — Red quan sát `openai.OpenAIError: Missing credentials` từ client global hiện tại.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement; cần lazy client và `load_reward_settings`.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — reward settings từ environment và lazy OpenAI client; Refactor — no-change-needed
- **Nhiệm vụ**: Loại hardcode model/API và lỗi credentials tại import.
- **Đầu vào nhận được**: Test Red `test_load_reward_settings_reads_compact_guard_policy_from_environment`.
- **Files đã sửa**: `script/safe_reward.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `1 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — config được check-in chưa tồn tại
- **Nhiệm vụ**: Khóa policy 8.000 train samples và Llama Guard 3 1B/Tensor Parallel 1.
- **Đầu vào nhận được**: Config loader đã Green.
- **Files đã sửa**: `verl/tests/data_preprocess/test_prepare_pku_saferlhf.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — test thất bại với `FileNotFoundError: config/nspo.env` đúng Red dự kiến.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement để thêm config chung.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — thêm config runtime chung; Refactor — no-change-needed
- **Nhiệm vụ**: Cấu hình 8K train, 1K validation, Qwen 0.5B và Llama Guard 3 1B.
- **Đầu vào nhận được**: Test Red `test_checked_in_config_selects_8k_train_and_compact_guard`.
- **Files đã sửa**: Không có
- **Files đã tạo**: `config/nspo.env`
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `8 passed` ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — hai launcher vẫn hardcode model/GPU/path và chưa source config
- **Nhiệm vụ**: Đồng bộ reward server và trainer với `config/nspo.env`.
- **Đầu vào nhận được**: Config chung đã Green.
- **Files đã sửa**: Không có
- **Files đã tạo**: `verl/tests/script/test_nspo_shell_config.py`
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `2 failed` đúng Red; thiếu `config/nspo.env` trong cả hai launcher.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — hai launcher source config chung; Refactor — no-change-needed
- **Nhiệm vụ**: Dùng Llama Guard 3 1B trên một GPU và dataset được tạo trong repo.
- **Đầu vào nhận được**: Hai test Red trong `test_nspo_shell_config.py`.
- **Files đã sửa**: `script/start_vllm_llama_guard.sh`, `script/nspo_verl_rule_base.sh`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — `2 passed`; `bash -n` vượt qua cho cả hai script.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed. WSL in cảnh báo `.wslconfig` không liên quan nhưng command trả exit code 0.
## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red — regression xác nhận conversation bị bọc lồng trong `RLHFDataset`
- **Nhiệm vụ**: Bảo toàn schema chat VERL khi render prompt cho Qwen.
- **Đầu vào nhận được**: `verl/verl/utils/dataset/rl_dataset.py` và schema Parquet mới.
- **Files đã sửa**: Không có
- **Files đã tạo**: `verl/tests/utils/dataset/test_rl_dataset_chat_template.py`
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — assertion bắt được chuỗi lỗi `[{"role": "user", "content": messages}]` trong source.
- **Số lần tự sửa lỗi**: 1 — test import trực tiếp bị chặn vì môi trường thiếu `ray`; chuyển sang regression tĩnh tập trung đúng biểu hiện nesting.
- **Trạng thái**: COMPLETED
- **Ghi chú**: Handoff sang 03-implement để truyền `messages` trực tiếp vào chat template.
## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green — truyền conversation trực tiếp vào tokenizer; Refactor — no-change-needed
- **Nhiệm vụ**: Sửa prompt nesting để Parquet VERL hoạt động đúng với Qwen.
- **Đầu vào nhận được**: Regression Red trong `test_rl_dataset_chat_template.py`.
- **Files đã sửa**: `verl/verl/utils/dataset/rl_dataset.py`
- **Files đã tạo**: Không có
- **Files đã xóa**: Không có
- **Kết quả kiểm tra**: PASS — regression `1 passed`; `py_compile` thành công ở Green và sau Refactor.
- **Số lần tự sửa lỗi**: 0
- **Trạng thái**: COMPLETED
- **Ghi chú**: Refactor outcome: no-change-needed.

## Skill Execution Log: 06-test

- **Skill**: 06-test
- **TDD phase**: Red
- **Nhi?m v?**: Ki?m th? native assistant moderation, l?i verdict v? batch adapter.
- **??u v?o nh?n ???c**: Y?u c?u 8K PKU-SafeRLHF v? reward model nh? h?n.
- **Files ?? s?a**: verl/tests/reward_score/test_safe_reward.py
- **Files ?? t?o**: data/safety/pku_saferlhf_8k/ ch?a hai Parquet v? manifest.
- **Files ?? x?a**: Kh?ng c?
- **K?t qu? ki?m tra**: PASS ? Red: ImportError compute_score_batch ch?a t?n t?i.
- **S? l?n t? s?a l?i**: 1 ? ph?t hi?n v? lo?i prompt overlap t? split g?c.
- **Tr?ng th?i**: COMPLETED
- **Ghi ch?**: Kh?ng c? context-engine tool kh? d?ng; d?ng t?m ki?m c?c b?. M?y c? Quadro T1000 4GB; thi?u torch/transformers/ray, ch?a ch?y guard inference hay training. Regression chat hi?n l? ki?m tra source, ch?a ph?i tokenizer runtime.

## Skill Execution Log: 03-implement

- **Skill**: 03-implement
- **TDD phase**: Green
- **Nhi?m v?**: D?ng native chat template; batch manager chu?n; l?i reward d?ng scoring. Pin dataset revision v? lo?i tr?ng prompt, lo?i giao nhau train/validation.
- **??u v?o nh?n ???c**: Y?u c?u 8K PKU-SafeRLHF v? reward model nh? h?n.
- **Files ?? s?a**: script/safe_reward.py; script/prepare_pku_saferlhf.py; script/nspo_verl_rule_base.sh; config/nspo.env; .gitattributes; .gitignore
- **Files ?? t?o**: data/safety/pku_saferlhf_8k/ ch?a hai Parquet v? manifest.
- **Files ?? x?a**: Kh?ng c?
- **K?t qu? ki?m tra**: PASS ? 18 tests passed; Parquet 8000/1000 unique prompts, zero overlap. Refactor: no-change-needed.
- **S? l?n t? s?a l?i**: 1 ? ph?t hi?n v? lo?i prompt overlap t? split g?c.
- **Tr?ng th?i**: COMPLETED
- **Ghi ch?**: Kh?ng c? context-engine tool kh? d?ng; d?ng t?m ki?m c?c b?. M?y c? Quadro T1000 4GB; thi?u torch/transformers/ray, ch?a ch?y guard inference hay training. Regression chat hi?n l? ki?m tra source, ch?a ph?i tokenizer runtime.

## Skill Execution Log: 08-readme-management

- **Skill**: 08-readme-management
- **TDD phase**: N/A
- **Nhi?m v?**: C?p nh?t h??ng d?n c?i ??t, t?i t?o dataset, guard 1B v? training.
- **??u v?o nh?n ???c**: Y?u c?u 8K PKU-SafeRLHF v? reward model nh? h?n.
- **Files ?? s?a**: README.md
- **Files ?? t?o**: data/safety/pku_saferlhf_8k/ ch?a hai Parquet v? manifest.
- **Files ?? x?a**: Kh?ng c?
- **K?t qu? ki?m tra**: PASS ? l?nh/path kh?p c?u h?nh; kh?ng kh?ng ??nh ?? ch?y GPU.
- **S? l?n t? s?a l?i**: 1 ? ph?t hi?n v? lo?i prompt overlap t? split g?c.
- **Tr?ng th?i**: COMPLETED
- **Ghi ch?**: Kh?ng c? context-engine tool kh? d?ng; d?ng t?m ki?m c?c b?. M?y c? Quadro T1000 4GB; thi?u torch/transformers/ray, ch?a ch?y guard inference hay training. Regression chat hi?n l? ki?m tra source, ch?a ph?i tokenizer runtime.

## Skill Execution Log: 07-review

- **Skill**: 07-review
- **TDD phase**: N/A
- **Nhi?m v?**: R? so?t dataset, reward integration, launcher v? gi?i h?n ki?m ch?ng.
- **??u v?o nh?n ???c**: Y?u c?u 8K PKU-SafeRLHF v? reward model nh? h?n.
- **Files ?? s?a**: Kh?ng c?
- **Files ?? t?o**: data/safety/pku_saferlhf_8k/ ch?a hai Parquet v? manifest.
- **Files ?? x?a**: Kh?ng c?
- **K?t qu? ki?m tra**: PASS ? ki?m tra t?nh v? d? li?u ho?n t?t; GPU inference/training ch?a ???c ki?m ch?ng.
- **S? l?n t? s?a l?i**: 1 ? ph?t hi?n v? lo?i prompt overlap t? split g?c.
- **Tr?ng th?i**: COMPLETED
- **Ghi ch?**: Kh?ng c? context-engine tool kh? d?ng; d?ng t?m ki?m c?c b?. M?y c? Quadro T1000 4GB; thi?u torch/transformers/ray, ch?a ch?y guard inference hay training. Regression chat hi?n l? ki?m tra source, ch?a ph?i tokenizer runtime.

## T?ng k?t Pipeline

- **Pattern**: Small implementation
- **TDD**: yes (Red ? Green ? Refactor); ki?m tra dedup b? sung sau khi ph?t hi?n overlap ? artifact th?t.
- **T?ng s? skills**: 4
- **Ho?n th?nh**: 4
- **Th?t b?i**: 0
- **T?ng files ?? s?a**: script/prepare_pku_saferlhf.py, script/safe_reward.py, script/nspo_verl_rule_base.sh, script/start_vllm_llama_guard.sh, config/nspo.env, verl/verl/utils/dataset/rl_dataset.py, README.md, .gitattributes, .gitignore, tests v? data/safety/pku_saferlhf_8k/.
- **K?t qu? ki?m tra t?ng th?**: PARTIAL ? unit/data/shell PASS; GPU inference/training ch?a ch?y.
- **Timeline**:
  1. 06-test: COMPLETED ? Red v? 18 tests Green.
  2. 03-implement: COMPLETED ? artifacts v? reward model integration.
  3. 08-readme-management: COMPLETED ? h??ng d?n c?p nh?t.
  4. 07-review: COMPLETED ? kh?ng c?n blocker t?nh; gi?i h?n runtime ghi r?.
- **V?n ?? g?p ph?i**: PKU split c? prompt overlap; ?? lo?i theo n?i dung. Guard 1B c?n quy?n truy c?p Hugging Face. Ch?a ??nh gi? ch?t l??ng reward so v?i 12B.
- **B??c ti?p theo ???c ?? xu?t**: Ch?y guard v? smoke training tr?n Linux/CUDA v?i ph?n c?ng ?? b? nh? theo README.
