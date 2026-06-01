# Cache-Aware Coding Agent Benchmark

This is an early benchmark project around coding-agent inference.

The basic idea is that coding agents usually send a lot of repeated text across calls: system instructions, output rules, repo context, tool format, and task setup. If the repeated part of the prompt is kept at the front, the workload should be more friendly to prefix caching / KV-cache reuse.

Right now, this repo is not trying to claim a final result. It is a working prototype to test the pipeline.

## Current status in one line

The current version runs a 6-task toy repair benchmark, measures prefix reuse, evaluates failing tests, applies a rule-based baseline fixer, saves before/after traces, and shows everything in a Streamlit dashboard.

## What works right now

- Builds normal and cache-aware prompts for small code-repair tasks.
- Measures prompt tokens and prefix reuse.
- Runs a small set of buggy Python tasks with `pytest`.
- Applies a simple baseline fixer.
- Re-runs tests after repair.
- Saves before/after repair traces.
- Shows the results in a Streamlit dashboard.

The current fixer is rule-based. It is only there to test the full repair loop before adding actual model backends.

## Why I am building this

Most coding-agent benchmarks focus only on whether the final code passes tests. That is obviously important, but I also want to look at the serving side.

For example:

- Can we structure coding-agent prompts so more of the prefix is reused?
- Does grouping similar repair tasks help expose more shared context?
- Can this be done without hurting pass rate?
- What happens to TTFT, latency, throughput, and retries when we move from a dummy/backend baseline to real model serving?

The current version is just the first step toward that.

## Current pipeline

    benchmark task
    -> build prompt
    -> measure prefix reuse
    -> run tests
    -> apply baseline fix
    -> run tests again
    -> save results
    -> show dashboard

The repair runner uses a temporary workspace under `runs/current_run`, so the original buggy tasks stay unchanged.

## Project structure

    benchmark_tasks/     original buggy tasks
    src/                 benchmark and repair code
    runs/                temporary working copies, ignored by git
    results/             generated outputs, ignored by git
    app.py               Streamlit dashboard
    requirements.txt     Python dependencies

## Running it locally

Create the environment:

    uv venv --python 3.11
    source .venv/bin/activate
    uv pip install -r requirements.txt

Run the prompt/cache benchmark:

    python -m src.runner

Run the test evaluator:

    python -m src.test_runner

Run the repair pipeline with the rule-based baseline:

    python -m src.repair_runner --fixer rule

The runner also has a `--fixer model` option for future model-server experiments.

Run the prompt-layout experiment:

    python -m src.experiment_runner

This compares normal prompting, cache-aware prompting, and grouped cache-aware prompting on the same repair task set.

Start the dashboard:

    streamlit run app.py

Then open:

    http://localhost:8501

## Prompt-layout experiment

The experiment runner compares three settings:

- normal prompt layout;
- cache-aware prompt layout;
- cache-aware prompt layout with grouped task order.

The early result is simple but useful: cache-aware prompts create much higher prefix reuse while keeping the repair pass rate unchanged under the rule-based baseline. This does not prove real serving speedups yet, but it gives the project a clear systems question to test later with model-server, vLLM, or SGLang backends.

## Sample outputs

The `examples/` folder contains a few sample outputs from the current prototype:

    examples/sample_task_test_results.csv
    examples/sample_repair_results.csv
    examples/sample_repair_traces.jsonl

The actual `results/` folder is ignored by git because it gets regenerated every time the benchmark is run locally.

## Metrics shown

Current metrics include:

- prefix reuse score
- prompt tokens
- simulated latency
- simulated TTFT
- unit-test pass/fail
- repair success rate
- before/after code traces
- fixer backend used
- model/backend name
- fixer call latency
- prompt/output character counts

TTFT means time to first token. In the current prompt/cache benchmark, latency and TTFT are still simulated. In the repair pipeline, the fixer call time is now logged separately so real model-server runs can be compared later.

## Backend plan

The benchmark currently runs with a rule-based baseline:

    python -m src.repair_runner --fixer rule

The code also has a generic model-server mode:

    python -m src.repair_runner --fixer model

The model-server path is intentionally provider-neutral. The goal is to later compare the same repair tasks across:

- rule-based baseline;
- hosted model-server endpoint;
- local vLLM endpoint;
- local SGLang endpoint.

The main comparison I want to run later is the tradeoff between repair quality and serving efficiency: latency, prompt size, output size, retries, and eventually TTFT / throughput.

## Next steps

- Add a real model-server backend.
- Add support for local vLLM / SGLang endpoints.
- Add more realistic code-repair tasks.
- Track pass rate, retries, TTFT, latency, and throughput together.
- Compare normal prompting, cache-aware prompting, and grouped scheduling.