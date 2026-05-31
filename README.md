# Cache-Aware Coding Agent Benchmark

This is an early benchmark project around coding-agent inference.

The basic idea is that coding agents usually send a lot of repeated text across calls: system instructions, output rules, repo context, tool format, and task setup. If the repeated part of the prompt is kept at the front, the workload should be more friendly to prefix caching / KV-cache reuse.

Right now, this repo is not trying to claim a final result. It is a working prototype to test the pipeline.

## What works right now

- Builds normal and cache-aware prompts for small code-repair tasks.
- Measures prompt tokens and prefix reuse.
- Runs a small set of buggy Python tasks with pytest.
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

text benchmark task -> build prompt -> measure prefix reuse -> run tests -> apply baseline fix -> run tests again -> save results -> show dashboard 

The repair runner uses a temporary workspace under runs/current_run, so the original buggy tasks stay unchanged.

## Project structure

text benchmark_tasks/     original buggy tasks src/                 benchmark and repair code runs/                temporary working copies, ignored by git results/             generated outputs, ignored by git app.py               Streamlit dashboard requirements.txt     Python dependencies 

## Running it locally

## Running it locally

Create the environment:

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

Run the prompt/cache benchmark:

```bash
python -m src.runner
```

Run the test evaluator:

```bash
python -m src.test_runner
```

Run the repair pipeline:

```bash
python -m src.repair_runner
```

Start the dashboard:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Metrics shown

Current metrics include:

- prefix reuse score
- prompt tokens
- simulated latency
- simulated TTFT
- unit-test pass/fail
- repair success rate
- before/after code traces

TTFT means time to first token. In the current version, latency and TTFT are still simulated because the model backend is not real yet.

## Next steps

- Add a real OpenAI-compatible backend.
- Add support for local vLLM / SGLang endpoints.
- Add more realistic code-repair tasks.
- Track pass rate, retries, TTFT, latency, and throughput together.
- Compare normal prompting, cache-aware prompting, and grouped scheduling.