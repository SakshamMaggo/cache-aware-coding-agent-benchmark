# v1.2 Local Backend Support

This version adds support for OpenAI-compatible model backends such as hosted APIs, vLLM, and SGLang.

The benchmark now has a shared model client layer in `src/model_client.py`. The same repair runner, backend checker, and streaming probe can point to different model servers by changing environment variables.

## What changed

- Added `OpenAICompatibleModelClient`
- Added real backend health checks through `src/check_model_backend.py`
- Added backend metadata to repair results:
  - `backend_type`
  - `base_url`
- Updated streaming probe to log backend information
- Added scripts for vLLM and SGLang server startup
- Added one script to run the local backend experiment end-to-end

## Environment variables

For hosted API use:

    export MODEL_NAME=gpt-4.1-mini
    export MODEL_API_KEY=your_key_here
    unset MODEL_BASE_URL
    export MODEL_BACKEND=hosted

For vLLM use:

    export MODEL_BACKEND=vllm
    export MODEL_BASE_URL=http://localhost:8000/v1
    export MODEL_API_KEY=EMPTY
    export MODEL_NAME=Qwen/Qwen2.5-Coder-1.5B-Instruct

For SGLang use:

    export MODEL_BACKEND=sglang
    export MODEL_BASE_URL=http://127.0.0.1:30000/v1
    export MODEL_API_KEY=EMPTY
    export MODEL_NAME=Qwen/Qwen2.5-Coder-1.5B-Instruct

## Start a local server

vLLM:

    MODEL_PATH=Qwen/Qwen2.5-Coder-1.5B-Instruct ./scripts/run_vllm_server.sh

SGLang:

    MODEL_PATH=Qwen/Qwen2.5-Coder-1.5B-Instruct ./scripts/run_sglang_server.sh

## Run the benchmark against a local backend

In another terminal, after the server is running:

    ./scripts/run_local_backend_experiment.sh vllm

or:

    ./scripts/run_local_backend_experiment.sh sglang

By default this runs:

    python -m src.check_model_backend
    python -m src.streaming_probe
    python -m src.repair_runner --fixer model --max-tasks 3 --max-attempts 1

You can change the number of tasks:

    MAX_TASKS=12 ./scripts/run_local_backend_experiment.sh vllm

## Notes

This is not yet a full serving benchmark. It is the first local-backend integration layer. The goal is to make the existing cache-aware coding-agent benchmark runnable against local OpenAI-compatible model servers.

A future version can add repeated trials, prefix-cache-specific measurements, batching experiments, and context reliability metrics.
