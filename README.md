# NSPO: Null-Space constrained Policy Optimization for Safety Alignment


This is the **official implementation** of the [**paper**](https://arxiv.org/abs/2512.11391):  
**"Mitigating the Safety Alignment Tax with Null-Space Constrained Policy Optimization"** (ICLR 2026)

---

## 💡 Overview

Null-Space constrained Policy Optimization (NSPO) is a RL framework for LLM safety alignment while preserving their core abilities.  Notably, NSPO is data-efficient and only requires 40\% of public human-annotated safety data from PKU-SafeRLHF to achieve promising performance.

---

## 📂 Project Structure

```
NSPO/
├── evaluation/
│   ├── eval_sorrybench.py
│   ├── evaluation.py
│   ├── evaluator_configs/
│   │   ├── configs.yaml
│   │   └── template_base.txt
│   └── generate_alpaca.py
├── script/
│   ├── alpaca_eval.sh
│   ├── livecodebench_eval.sh
│   ├── math_eval.sh
│   ├── merge_verl_ckpt.py
│   ├── mmlu_bench.sh
│   ├── safe_reward.py
│   ├── safe_rl_verl_rule_base.sh
│   ├── safety_eval.sh
│   ├── start_vllm_llama_guard.sh
│   └── superGPQA_eval.sh
└── verl/
```
---

## 🚀 Quick Start

Run on Linux with CUDA. The default configuration uses GPU 0 for
`Qwen/Qwen2.5-0.5B-Instruct` and GPU 1 for `meta-llama/Llama-Guard-3-1B`.
Set device IDs, model paths, dataset paths and reward request settings in
[`config/nspo.env`](config/nspo.env). These defaults require two GPUs with sufficient VRAM;
a single 4 GB GPU is not a validated training setup.

### Install

From the repository root, in your CUDA/PyTorch environment (Python 3.10+):

```bash
pip install -r verl/requirements.txt
pip install -e ./verl
```

### Data

The prepared files are included in `data/safety/pku_saferlhf_8k/`:

- `SafeRLHFfull_safety.parquet`: 8,000 unique prompts sampled without replacement from the official train split.
- `SafeRLHFfull_test_safety.parquet`: 1,000 unique prompts sampled from the official test split, excluding training prompts, used for validation.
- `manifest.json`: dataset revision, seed (42), counts and source row indices.

To regenerate them:

```bash
python script/prepare_pku_saferlhf.py --config config/nspo.env
```

Source: [PKU-SafeRLHF](https://huggingface.co/datasets/PKU-Alignment/PKU-SafeRLHF)
(CC-BY-NC-4.0). This is a random 8K subset, not a reproduction of the paper's
exact safety-data selection. Prompt length filtering during training may reduce
the effective row count. The separate 1,000-prompt preservation pool remains in
`data/preservation/nspo_mix/prompts.jsonl`.

### Start the guard and train

Obtain access to [Llama-Guard-3-1B](https://huggingface.co/meta-llama/Llama-Guard-3-1B)
and authenticate with Hugging Face (`hf auth login`). The server downloads the
model on first launch; alternatively set `REWARD_MODEL_PATH` to a local checkpoint.

Terminal 1, from the repository root:

```bash
bash script/start_vllm_llama_guard.sh
```

Terminal 2, using the same environment:

```bash
curl http://127.0.0.1:52001/v1/models
bash script/nspo_verl_rule_base.sh
```

For an initial one-step smoke run:

```bash
bash script/nspo_verl_rule_base.sh trainer.total_training_steps=1 trainer.save_freq=-1 trainer.test_freq=-1
```

The guard classifies the original user prompt and generated assistant response
with its native chat template. Rewards remain `safe = 0`, `unsafe = -1`.
Request failures or invalid verdicts stop scoring rather than silently assigning
safe rewards. This smaller classifier changes the reward signal compared with
Llama Guard 4 12B; comparable safety quality has not been established.

Use `NSPO_CONFIG_PATH=/absolute/path/to/custom.env` for another configuration.
Checkpoints default to
`checkpoints/verl_grpo_safety_align_Qwen_NSPO/verl_grpo_safety_align_Qwen_NSPO/`.
The smoke run still constructs the preservation projector; one step does not
exercise every periodic NSPO projection update.

---


## 📊 Evaluation

The `script/` and `evaluation/` directories contain benchmark evaluation scripts.  
**Note:** You need to manually configure the dataset paths and API keys in these scripts before running them.

---

## 🤗 Models & Checkpoints

We have released our trained checkpoint on Hugging Face:

* [Qwen2.5-7B-Instruct-NSPO](https://huggingface.co/ICLR2026NSPO/Qwen2.5-7B-Instruct-NSPO): The policy model fine-tuned using NSPO on the Qwen2.5-7B-Instruct.

---

## ✍️ Citation

If you find this work helpful for your research, please cite our paper:
```
@article{niu2025mitigating,
  title={Mitigating the Safety Alignment Tax with Null-Space Constrained Policy Optimization},
  author={Niu, Yifan and Xiao, Han and Liu, Dongyi and Chen, Nuo and Li, Jia},
  journal={arXiv preprint arXiv:2512.11391},
  year={2025}
}
```
