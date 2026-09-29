from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_reward_server_uses_shared_compact_model_config():
    # The server launcher must source policy instead of embedding a model or GPU layout.
    script = (REPO_ROOT / "script" / "start_vllm_llama_guard.sh").read_text(encoding="utf-8")

    assert "config/nspo.env" in script
    assert 'REWARD_MODEL_PATH' in script
    assert 'REWARD_TENSOR_PARALLEL_SIZE' in script
    assert "Llama-Guard-4-12B" not in script
    assert "CUDA_VISIBLE_DEVICES=4,5" not in script
    assert "\\." not in script


def test_training_launcher_uses_shared_dataset_and_gpu_config():
    # Trainer paths and GPU count must resolve from the same checked-in runtime policy.
    script = (REPO_ROOT / "script" / "nspo_verl_rule_base.sh").read_text(encoding="utf-8")

    assert "config/nspo.env" in script
    assert 'SAFETY_OUTPUT_DIR' in script
    assert 'TRAIN_CUDA_VISIBLE_DEVICES' in script
    assert 'TRAIN_N_GPUS_PER_NODE' in script
    assert 'TRAIN_LOGGER' in script
    assert '${DATA_PATH:?' not in script
