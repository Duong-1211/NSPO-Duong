from pathlib import Path

from script.prepare_pku_saferlhf import (
    build_rl_record,
    build_sampled_records,
    load_env_config,
    prepare_artifacts,
    prepare_from_config,
    sample_source_indices,
    write_records,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_build_rl_record_converts_pku_prompt_to_verl_schema():
    # A PKU prompt must become a single-turn VERL RL record.
    source = {"prompt": "How can I keep my account secure?", "prompt_source": "safe_rlhf"}

    record = build_rl_record(source, split="train", source_index=17)

    assert record == {
        "data_source": "PKU-Alignment/PKU-SafeRLHF",
        "prompt": [{"role": "user", "content": "How can I keep my account secure?"}],
        "ability": "safety",
        "reward_model": {"style": "rule", "ground_truth": ""},
        "extra_info": {
            "split": "train",
            "source_index": 17,
            "index": 17,
            "question": "How can I keep my account secure?",
            "prompt_source": "safe_rlhf",
        },
    }


def test_sample_source_indices_is_deterministic_and_without_replacement():
    # Sampling must be reproducible and contain exactly the requested number of rows.
    first = sample_source_indices(total_size=100, sample_size=8, seed=42)
    second = sample_source_indices(total_size=100, sample_size=8, seed=42)

    assert first == second
    assert len(first) == 8
    assert len(set(first)) == 8


def test_load_env_config_reads_dataset_and_reward_runtime_policy(tmp_path):
    # Runtime policy must come from the shared config file.
    config_path = tmp_path / "nspo.env"
    config_path.write_text(
        "PKU_DATASET_ID=PKU-Alignment/PKU-SafeRLHF\n"
        "SAFETY_TRAIN_SIZE=8000\n"
        "REWARD_MODEL_PATH=meta-llama/Llama-Guard-3-1B\n",
        encoding="utf-8",
    )

    config = load_env_config(config_path)

    assert config == {
        "PKU_DATASET_ID": "PKU-Alignment/PKU-SafeRLHF",
        "SAFETY_TRAIN_SIZE": "8000",
        "REWARD_MODEL_PATH": "meta-llama/Llama-Guard-3-1B",
    }


def test_build_sampled_records_preserves_selected_source_indices():
    # Generated metadata must trace every sampled row back to the source split.
    rows = [{"prompt": f"prompt-{index}", "prompt_source": "pku"} for index in range(20)]

    records = build_sampled_records(rows, split="train", sample_size=8, seed=7)

    assert len(records) == 8
    assert len({record["extra_info"]["source_index"] for record in records}) == 8
    for record in records:
        source_index = record["extra_info"]["source_index"]
        assert record["prompt"][0]["content"] == rows[source_index]["prompt"]


def test_write_records_creates_readable_parquet(tmp_path):
    # The generated artifact must round-trip through Hugging Face Datasets.
    from datasets import Dataset

    records = [build_rl_record({"prompt": "hello", "prompt_source": "pku"}, "train", 0)]
    output_path = tmp_path / "train.parquet"

    write_records(records, output_path)

    restored = Dataset.from_parquet(str(output_path))
    assert len(restored) == 1
    assert restored[0]["prompt"] == [{"role": "user", "content": "hello"}]


def test_prepare_artifacts_writes_configured_splits_and_manifest(tmp_path):
    # Train and validation sizes and filenames must be controlled by config.
    rows = [{"prompt": f"prompt-{index}", "prompt_source": "pku"} for index in range(20)]
    config = {
        "PKU_DATASET_ID": "PKU-Alignment/PKU-SafeRLHF",
        "PKU_DATASET_CONFIG": "default",
        "SAFETY_TRAIN_SIZE": "8",
        "SAFETY_VAL_SIZE": "2",
        "SAFETY_DATA_SEED": "42",
        "SAFETY_TRAIN_FILE": "train.parquet",
        "SAFETY_VAL_FILE": "validation.parquet",
    }

    manifest = prepare_artifacts(rows, rows, config, tmp_path)

    assert (tmp_path / "train.parquet").is_file()
    assert (tmp_path / "validation.parquet").is_file()
    assert (tmp_path / "manifest.json").is_file()
    assert manifest["train_size"] == 8
    assert manifest["validation_size"] == 2
    assert manifest["seed"] == 42


def test_prepare_from_config_loads_pku_splits_and_writes_output(tmp_path, monkeypatch):
    # The command entry point must use only paths and sampling policy from config.
    rows = [{"prompt": f"prompt-{index}", "prompt_source": "pku"} for index in range(20)]
    output_dir = tmp_path / "output"
    config_path = tmp_path / "nspo.env"
    config_path.write_text(
        "PKU_DATASET_ID=PKU-Alignment/PKU-SafeRLHF\n"
        "PKU_DATASET_CONFIG=default\n"
        "SAFETY_TRAIN_SIZE=8\n"
        "SAFETY_VAL_SIZE=2\n"
        "SAFETY_DATA_SEED=42\n"
        "SAFETY_OUTPUT_DIR=" + output_dir.as_posix() + "\n"
        "SAFETY_TRAIN_FILE=train.parquet\n"
        "SAFETY_VAL_FILE=validation.parquet\n",
        encoding="utf-8",
    )
    calls = []

    def fake_load_dataset(dataset_id, dataset_config):
        calls.append((dataset_id, dataset_config))
        return {"train": rows, "test": rows}

    monkeypatch.setattr("datasets.load_dataset", fake_load_dataset)

    manifest = prepare_from_config(config_path)

    assert calls == [("PKU-Alignment/PKU-SafeRLHF", "default")]
    assert manifest["train_size"] == 8
    assert (output_dir / "train.parquet").is_file()


def test_checked_in_config_selects_8k_train_and_compact_guard():
    # The checked-in runtime policy must match the requested dataset and reward model.
    config = load_env_config(REPO_ROOT / "config" / "nspo.env")

    assert config["SAFETY_TRAIN_SIZE"] == "8000"
    assert config["PKU_DATASET_ID"] == "PKU-Alignment/PKU-SafeRLHF"
    assert config["REWARD_MODEL_PATH"] == "meta-llama/Llama-Guard-3-1B"
    assert config["REWARD_TENSOR_PARALLEL_SIZE"] == "1"


def test_sampling_excludes_duplicate_and_training_prompts():
    rows = [{"prompt": text} for text in ["train prompt", "one", "one", "two"]]
    records = build_sampled_records(rows, "test", 2, 42, True, {"train prompt"})
    assert {row["prompt"][0]["content"] for row in records} == {"one", "two"}
