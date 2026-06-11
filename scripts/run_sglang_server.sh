#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH="${MODEL_PATH:-Qwen/Qwen2.5-Coder-1.5B-Instruct}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-30000}"

echo "Starting SGLang server"
echo "MODEL_PATH=${MODEL_PATH}"
echo "HOST=${HOST}"
echo "PORT=${PORT}"

python -m sglang.launch_server \
  --model-path "$MODEL_PATH" \
  --host "$HOST" \
  --port "$PORT"
