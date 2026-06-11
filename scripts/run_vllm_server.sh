#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH="${MODEL_PATH:-Qwen/Qwen2.5-Coder-1.5B-Instruct}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
API_KEY="${MODEL_API_KEY:-EMPTY}"

echo "Starting vLLM server"
echo "MODEL_PATH=${MODEL_PATH}"
echo "HOST=${HOST}"
echo "PORT=${PORT}"

vllm serve "$MODEL_PATH" \
  --host "$HOST" \
  --port "$PORT" \
  --api-key "$API_KEY"
