# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

import importlib.util
import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "verl" / "verl" / "utils" / "nspo_projection.py"
DATASET_PATH = REPO_ROOT / "data" / "preservation" / "nspo_mix" / "prompts.jsonl"


def _load_projection_module():
    spec = importlib.util.spec_from_file_location("nspo_projection", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_load_preservation_prompts_returns_verified_pool():
    # The checked-in artifact must expose exactly the configured prompt pool.
    projection = _load_projection_module()

    prompts = projection.load_preservation_prompts(
        dataset_path=DATASET_PATH,
        prompt_key="prompt",
        expected_size=1000,
    )

    assert len(prompts) == 1000
    assert all(prompt.strip() for prompt in prompts)


def test_load_preservation_prompts_rejects_schema_mismatch(tmp_path):
    # A malformed artifact must fail before projector construction starts.
    invalid_dataset = tmp_path / "invalid.jsonl"
    invalid_dataset.write_text(json.dumps({"text": "missing configured key"}) + "\n", encoding="utf-8")
    projection = _load_projection_module()

    try:
        projection.load_preservation_prompts(invalid_dataset, prompt_key="prompt", expected_size=1)
    except ValueError as exc:
        assert "Missing prompt key 'prompt'" in str(exc)
    else:
        raise AssertionError("Schema mismatch was not rejected")


def test_load_preservation_prompts_rejects_unexpected_count(tmp_path):
    # Dataset membership changes must be explicit rather than silently accepted.
    short_dataset = tmp_path / "short.jsonl"
    short_dataset.write_text(json.dumps({"prompt": "one prompt"}) + "\n", encoding="utf-8")
    projection = _load_projection_module()

    try:
        projection.load_preservation_prompts(short_dataset, prompt_key="prompt", expected_size=2)
    except ValueError as exc:
        assert "Expected 2 preservation prompts, found 1" in str(exc)
    else:
        raise AssertionError("Unexpected dataset count was not rejected")


def test_nspo_launch_uses_checked_in_pool_and_qwen_half_billion_model():
    # Runtime policy must be explicit in config and enabled by the NSPO launch script.
    trainer_config = yaml.safe_load((REPO_ROOT / "verl" / "verl" / "trainer" / "config" / "ppo_trainer.yaml").read_text())
    launch_script = (REPO_ROOT / "script" / "nspo_verl_rule_base.sh").read_text(encoding="utf-8")

    preservation = trainer_config["actor_rollout_ref"]["preservation"]
    assert preservation == {
        "enabled": False,
        "dataset_path": None,
        "prompt_key": "prompt",
        "expected_size": 1000,
        "batch_size": 16,
        "max_prompt_length": 2048,
        "max_new_tokens": 256,
        "apply_chat_template": True,
        "module_name_pattern": "mlp",
        "projection_threshold": 0.0005,
        "apply_interval": 5,
    }
    assert "MODEL_PATH=${MODEL_PATH:-Qwen/Qwen2.5-0.5B-Instruct}" in launch_script
    assert "actor_rollout_ref.preservation.enabled=True" in launch_script
    assert "data/preservation/nspo_mix/prompts.jsonl" in launch_script


def test_nspo_worker_and_trainer_use_preservation_configuration():
    # Projector construction and its schedule must be driven by the declared config.
    worker_source = (REPO_ROOT / "verl" / "verl" / "workers" / "fsdp_workers.py").read_text(encoding="utf-8")
    trainer_source = (REPO_ROOT / "verl" / "verl" / "trainer" / "ppo" / "ray_trainer.py").read_text(
        encoding="utf-8"
    )

    assert "load_preservation_prompts(" in worker_source
    assert 'self.config.preservation.get("projection_threshold")' in worker_source
    assert "store_embedding(attention_mask)" in worker_source
    assert 'preservation_config.get("enabled", False)' in worker_source
    assert 'preservation_config.get("apply_interval")' in trainer_source
    assert "store_embedding(prompt_length)" not in worker_source
    assert '"/Your training model path"' not in worker_source
    assert '"/Directory path of your general capability training dataset' not in worker_source
