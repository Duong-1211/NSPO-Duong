from pathlib import Path


def test_render_chat_prompt_passes_verl_messages_without_nesting():
    # A VERL prompt is already a conversation and must reach Qwen unchanged.
    source_path = Path(__file__).resolve().parents[3] / "verl" / "utils" / "dataset" / "rl_dataset.py"

    source = source_path.read_text(encoding="utf-8")

    assert '[{"role": "user", "content": messages}]' not in source
