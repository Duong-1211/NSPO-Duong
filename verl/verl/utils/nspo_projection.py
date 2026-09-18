# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path


def load_preservation_prompts(
    dataset_path: str | Path,
    prompt_key: str,
    expected_size: int | None = None,
) -> list[str]:
    """Load and validate the prompt-only JSONL artifact used to build NSPO projectors."""
    path = Path(dataset_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"NSPO preservation dataset does not exist: {path}")
    if path.suffix.lower() != ".jsonl":
        raise ValueError(f"NSPO preservation dataset must be JSONL, got: {path}")

    prompts = []
    with path.open("r", encoding="utf-8") as dataset_file:
        for line_number, line in enumerate(dataset_file, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_number}") from exc

            if prompt_key not in record:
                raise ValueError(f"Missing prompt key '{prompt_key}' at {path}:{line_number}")
            prompt = record[prompt_key]
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError(f"Empty or non-string prompt at {path}:{line_number}")
            prompts.append(prompt)

    if expected_size is not None and len(prompts) != expected_size:
        raise ValueError(f"Expected {expected_size} preservation prompts, found {len(prompts)} in {path}")
    if not prompts:
        raise ValueError(f"NSPO preservation dataset is empty: {path}")
    return prompts
