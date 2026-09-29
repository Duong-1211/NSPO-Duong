set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NSPO_PATH="${NSPO_PATH:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
NSPO_CONFIG_PATH="${NSPO_CONFIG_PATH:-${NSPO_PATH}/config/nspo.env}"

set -a
source "${NSPO_CONFIG_PATH}"
set +a

SAFETY_DATA_PATH="${SAFETY_OUTPUT_DIR}"
[[ "${SAFETY_DATA_PATH}" = /* ]] || SAFETY_DATA_PATH="${NSPO_PATH}/${SAFETY_DATA_PATH}"
[[ "${PRESERVATION_DATA_PATH}" = /* ]] || PRESERVATION_DATA_PATH="${NSPO_PATH}/${PRESERVATION_DATA_PATH}"

test -f "${SAFETY_DATA_PATH}/${SAFETY_TRAIN_FILE}"
test -f "${SAFETY_DATA_PATH}/${SAFETY_VAL_FILE}"
test -f "${PRESERVATION_DATA_PATH}"
test -f "${NSPO_PATH}/script/safe_reward.py"

set -x
CUDA_VISIBLE_DEVICES="${TRAIN_CUDA_VISIBLE_DEVICES}" RAY_DEBUG=legacy python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    data.train_files=${SAFETY_DATA_PATH}/${SAFETY_TRAIN_FILE} \
    data.val_files=${SAFETY_DATA_PATH}/${SAFETY_VAL_FILE} \
    data.train_batch_size=320 \
    data.max_prompt_length=512 \
    data.max_response_length=512 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    actor_rollout_ref.model.path=${MODEL_PATH} \
    actor_rollout_ref.preservation.enabled=True \
    actor_rollout_ref.preservation.dataset_path=${PRESERVATION_DATA_PATH} \
    actor_rollout_ref.nccl_timeout=7200 \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=160 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=20 \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.kl_loss_coef=0.001 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=20 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
    actor_rollout_ref.rollout.n=5 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=20 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.use_kl_in_reward=False \
    reward_model.reward_manager=batch \
    custom_reward_function.name=compute_score_batch \
    custom_reward_function.path=${NSPO_PATH}/script/safe_reward.py \
    trainer.critic_warmup=0 \
    trainer.logger=${TRAIN_LOGGER} \
    trainer.project_name='verl_grpo_safety_align_Qwen_NSPO' \
    trainer.experiment_name='verl_grpo_safety_align_Qwen_NSPO' \
    trainer.n_gpus_per_node=${TRAIN_N_GPUS_PER_NODE} \
    trainer.nnodes=1 \
    trainer.save_freq=5 \
    trainer.test_freq=5 \
    trainer.val_before_train=False \
    trainer.total_epochs=1 "$@"
