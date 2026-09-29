set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NSPO_PATH="${NSPO_PATH:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
NSPO_CONFIG_PATH="${NSPO_CONFIG_PATH:-${NSPO_PATH}/config/nspo.env}"

set -a
source "${NSPO_CONFIG_PATH}"
set +a

echo "Start vLLM safety reward service"
echo "Model: ${REWARD_MODEL_PATH}"
echo "Endpoint: http://${REWARD_HOST}:${REWARD_PORT}/v1"
echo "CUDA devices: ${REWARD_CUDA_VISIBLE_DEVICES}"

CUDA_VISIBLE_DEVICES="${REWARD_CUDA_VISIBLE_DEVICES}" python -m vllm.entrypoints.openai.api_server \
    --model "${REWARD_MODEL_PATH}" \
    --host "${REWARD_HOST}" \
    --port "${REWARD_PORT}" \
    --gpu-memory-utilization "${REWARD_GPU_MEMORY_UTILIZATION}" \
    --tensor-parallel-size "${REWARD_TENSOR_PARALLEL_SIZE}" \
    --max-model-len "${REWARD_MAX_MODEL_LEN}" \
    --served-model-name "${REWARD_MODEL_NAME}" \
    --trust-remote-code \
    --disable-log-requests
