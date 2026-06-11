#!/usr/bin/env bash
set -euo pipefail

BACKEND="${1:-vllm}"
MAX_TASKS="${MAX_TASKS:-3}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-1}"
MODEL_PATH="${MODEL_PATH:-Qwen/Qwen2.5-Coder-1.5B-Instruct}"

if [ "$BACKEND" = "vllm" ]; then
  export MODEL_BACKEND="vllm"
  export MODEL_BASE_URL="${MODEL_BASE_URL:-http://localhost:8000/v1}"
  export MODEL_API_KEY="${MODEL_API_KEY:-EMPTY}"
elif [ "$BACKEND" = "sglang" ]; then
  export MODEL_BACKEND="sglang"
  export MODEL_BASE_URL="${MODEL_BASE_URL:-http://127.0.0.1:30000/v1}"
  export MODEL_API_KEY="${MODEL_API_KEY:-EMPTY}"
else
  echo "Unknown backend: $BACKEND"
  echo "Use: vllm or sglang"
  exit 1
fi

export MODEL_NAME="${MODEL_NAME:-$MODEL_PATH}"

echo "Running local backend experiment"
echo "BACKEND=${MODEL_BACKEND}"
echo "MODEL_NAME=${MODEL_NAME}"
echo "MODEL_BASE_URL=${MODEL_BASE_URL}"
echo "MAX_TASKS=${MAX_TASKS}"
echo "MAX_ATTEMPTS=${MAX_ATTEMPTS}"

python -m src.check_model_backend
python -m src.streaming_probe
python -m src.repair_runner --fixer model --max-tasks "$MAX_TASKS" --max-attempts "$MAX_ATTEMPTS"
