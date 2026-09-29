from script.safe_reward import load_reward_settings


def test_load_reward_settings_reads_compact_guard_policy_from_environment():
    # Reward model and request policy must be injected by the shared runtime config.
    settings = load_reward_settings(
        {
            "REWARD_API_BASE": "http://127.0.0.1:52001/v1",
            "REWARD_MODEL_NAME": "Llama-Guard-3-1B",
            "REWARD_MAX_WORKERS": "16",
            "REWARD_TEMPERATURE": "0.0",
            "REWARD_MAX_TOKENS": "16",
        }
    )

    assert settings == {
        "api_base": "http://127.0.0.1:52001/v1",
        "model_name": "Llama-Guard-3-1B",
        "max_workers": 16,
        "temperature": 0.0,
        "max_tokens": 16,
    }


import pytest
from script.safe_reward import build_guard_messages, get_scores, compute_score_batch


def test_guard_classifies_assistant_response_with_original_prompt():
    assert build_guard_messages("answer", "question") == [
        {"role": "user", "content": "question"},
        {"role": "assistant", "content": "answer"},
    ]


@pytest.mark.parametrize("result", [{"error": "offline"}, {"result": None}, {"result": "unknown"}])
def test_invalid_reward_never_silently_becomes_safe(result):
    with pytest.raises(RuntimeError):
        get_scores([result])


def test_batch_adapter_preserves_order_and_prompt_context(monkeypatch):
    def evaluate(responses, prompts):
        assert responses == ["first", "second"]
        assert prompts == ["question one", "question two"]
        return [{"result": "safe"}, {"result": "unsafe\nS1"}]
    monkeypatch.setattr("script.safe_reward.eval_batch_responses", evaluate)
    assert compute_score_batch(["pku"] * 2, ["first", "second"], ["", ""],
                               [{"question": "question one"}, {"question": "question two"}]) == [0.0, -1.0]
