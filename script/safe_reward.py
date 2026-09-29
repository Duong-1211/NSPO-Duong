"""Batch safety reward backed by an OpenAI-compatible guard-model server."""

import concurrent.futures
import os

from openai import OpenAI


def load_reward_settings(environ) -> dict:
    """Load reward request policy exported from the shared NSPO config."""
    return {
        "api_base": environ["REWARD_API_BASE"],
        "model_name": environ["REWARD_MODEL_NAME"],
        "max_workers": int(environ["REWARD_MAX_WORKERS"]),
        "temperature": float(environ["REWARD_TEMPERATURE"]),
        "max_tokens": int(environ["REWARD_MAX_TOKENS"]),
    }


def build_guard_messages(model_answer: str, prompt: str) -> list[dict]:
    """Let the guard's native chat template classify the assistant turn."""
    return [{"role": "user", "content": prompt}, {"role": "assistant", "content": model_answer}]


def send_single_request(client: OpenAI, settings: dict, model_answer: str, prompt: str, request_id: int):
    try:
        response = client.chat.completions.create(
            model=settings["model_name"],
            messages=build_guard_messages(model_answer, prompt),
            temperature=settings["temperature"],
            max_tokens=settings["max_tokens"],
        )
        return {"result": response.choices[0].message.content}, request_id
    except Exception as error:
        return {"error": str(error)}, request_id


def eval_batch_responses(responses: list[str], prompts: list[str]) -> list[dict]:
    settings = load_reward_settings(os.environ)
    client = OpenAI(api_key=os.environ["REWARD_API_KEY"], base_url=settings["api_base"])
    results = [{} for _ in responses]
    with concurrent.futures.ThreadPoolExecutor(max_workers=settings["max_workers"]) as executor:
        futures = {
            executor.submit(send_single_request, client, settings, response, prompts[index], index)
            for index, response in enumerate(responses)
        }
        for future in concurrent.futures.as_completed(futures):
            result, index = future.result()
            results[index] = result
    return results


def get_scores(results: list[dict]) -> list[float]:
    scores = []
    for response in results:
        verdict = (response.get("result") or "").strip().lower().splitlines()
        label = verdict[0] if verdict else ""
        if label not in {"safe", "unsafe"}:
            raise RuntimeError(f"Guard returned no valid verdict: {response}")
        scores.append(-1.0 if label == "unsafe" else 0.0)
    return scores


def compute_score_batch(data_sources, solution_strs, ground_truths, extra_infos) -> list[float]:
    """VERL BatchRewardManager adapter: safe=0, unsafe=-1; failures abort scoring."""
    prompts = [extra["question"] for extra in extra_infos]
    return get_scores(eval_batch_responses(solution_strs, prompts))
