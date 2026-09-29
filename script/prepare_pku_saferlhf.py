"""Prepare PKU-SafeRLHF prompts for VERL reinforcement learning."""

import argparse
import json
import random
from pathlib import Path

DATA_SOURCE = "PKU-Alignment/PKU-SafeRLHF"


def load_env_config(path: str | Path) -> dict[str, str]:
    """Read simple KEY=VALUE entries from the shared NSPO config."""
    config = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            raise ValueError(f"Invalid config line: {raw_line}")
        config[key.strip()] = value.strip().strip("'\"")
    return config


def build_rl_record(example: dict, split: str, source_index: int) -> dict:
    """Convert one PKU-SafeRLHF row to the schema consumed by VERL."""
    return {
        "data_source": DATA_SOURCE,
        "prompt": [{"role": "user", "content": example["prompt"]}],
        "ability": "safety",
        "reward_model": {"style": "rule", "ground_truth": ""},
        "extra_info": {
            "split": split,
            "source_index": source_index,
            "index": source_index,
            "question": example["prompt"],
            "prompt_source": example.get("prompt_source", ""),
        },
    }


def sample_source_indices(total_size: int, sample_size: int, seed: int) -> list[int]:
    """Choose source rows deterministically without replacement."""
    if sample_size > total_size:
        raise ValueError(f"sample_size={sample_size} exceeds total_size={total_size}")
    return random.Random(seed).sample(range(total_size), sample_size)


def build_sampled_records(rows, split: str, sample_size: int, seed: int, deduplicate=False, excluded_prompts=()) -> list[dict]:
    """Sample source rows and convert them to VERL records."""
    eligible = []
    seen = set(excluded_prompts)
    for index, row in enumerate(rows):
        prompt = row["prompt"].strip()
        if not prompt or (deduplicate and prompt in seen):
            continue
        eligible.append(index)
        seen.add(prompt)
    indices = sample_source_indices(len(eligible), sample_size, seed)
    return [build_rl_record(rows[eligible[index]], split=split, source_index=eligible[index]) for index in indices]


def write_records(records: list[dict], output_path: str | Path) -> None:
    """Write VERL records to a Parquet file."""
    from datasets import Dataset

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    Dataset.from_list(records).to_parquet(str(destination))


def prepare_artifacts(train_rows, validation_rows, config: dict[str, str], output_dir: str | Path) -> dict:
    """Create configured train/validation Parquet files and a reproducibility manifest."""
    destination = Path(output_dir)
    train_size = int(config["SAFETY_TRAIN_SIZE"])
    validation_size = int(config["SAFETY_VAL_SIZE"])
    seed = int(config["SAFETY_DATA_SEED"])

    deduplicate = config.get("SAFETY_DEDUPLICATE_PROMPTS", "false") == "true"
    train_records = build_sampled_records(train_rows, "train", train_size, seed, deduplicate)
    train_prompts = {record["prompt"][0]["content"].strip() for record in train_records}
    validation_records = build_sampled_records(validation_rows, "test", validation_size, seed,
                                               deduplicate, train_prompts)
    write_records(train_records, destination / config["SAFETY_TRAIN_FILE"])
    write_records(validation_records, destination / config["SAFETY_VAL_FILE"])

    manifest = {
        "dataset_id": config["PKU_DATASET_ID"],
        "dataset_config": config["PKU_DATASET_CONFIG"],
        "dataset_revision": config.get("PKU_DATASET_REVISION"),
        "train_source_split": "train",
        "validation_source_split": "test",
        "seed": seed,
        "deduplicate_prompts": deduplicate,
        "train_size": len(train_records),
        "validation_size": len(validation_records),
        "train_file": config["SAFETY_TRAIN_FILE"],
        "validation_file": config["SAFETY_VAL_FILE"],
        "train_source_indices": [record["extra_info"]["source_index"] for record in train_records],
        "validation_source_indices": [record["extra_info"]["source_index"] for record in validation_records],
    }
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def prepare_from_config(config_path: str | Path) -> dict:
    """Download PKU-SafeRLHF and prepare the configured local artifacts."""
    from datasets import load_dataset

    config = load_env_config(config_path)
    dataset = load_dataset(config["PKU_DATASET_ID"], config["PKU_DATASET_CONFIG"],
                           **({"revision": config["PKU_DATASET_REVISION"]} if "PKU_DATASET_REVISION" in config else {}))
    output_dir = Path(config["SAFETY_OUTPUT_DIR"])
    if not output_dir.is_absolute():
        output_dir = Path(__file__).resolve().parents[1] / output_dir
    return prepare_artifacts(dataset["train"], dataset["test"], config, output_dir)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=repo_root / "config" / "nspo.env")
    args = parser.parse_args()
    manifest = prepare_from_config(args.config)
    print(json.dumps({key: value for key, value in manifest.items() if not key.endswith("_indices")}, indent=2))


if __name__ == "__main__":
    main()
