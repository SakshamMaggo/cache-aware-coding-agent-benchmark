# Current Results

This is a short note on the current 6-task run.

The benchmark compares three settings:

1. normal prompt layout with mixed task order
2. cache-aware prompt layout with mixed task order
3. cache-aware prompt layout with grouped task order

The repair backend is still the rule-based baseline, so the main thing to look at here is prompt structure, not model quality.

## Main observation

The normal prompt layout gives very low adjacent prefix reuse. In the current run, recent prefix reuse stays around 0.02 after the first task.

The cache-aware prompt layout improves this because shared instructions and repo context are placed earlier in the prompt.

The grouped cache-aware run improves recent prefix reuse further for similar tasks. This happens because tasks from the same group, such as math utilities, string utilities, or list utilities, are placed next to each other.

## Why this matters

Prefix caching and KV-cache reuse depend on prompts sharing the same beginning tokens.

So if coding-agent workloads can be arranged so repeated parts appear earlier, and similar tasks are scheduled together, the workload should be more friendly to efficient serving systems.

This does not prove a real speedup yet. It only shows that the workload can be made structurally more cache-friendly.

## Repair quality

The repair pass rate stays unchanged in the current rule-based run. All tasks fail before repair and pass after repair across the tested settings.

This is useful because it means the prompt-layout experiment is not breaking the repair loop in the current setup.

## Current limitation

The current fixer is rule-based, so the fixer latency is not meaningful as model inference latency.

The task set is also small and toy-like. The next useful step is to run the same experiment through a real model-server backend, and later through vLLM or SGLang.

## Model backend check

I also ran the model-server backend once on the current 6-task set using a hosted model endpoint.

This is not a full benchmark result yet, but it confirms that the `--fixer model` path is actually wired up and can produce real repair outputs.

In the sample run:

- all 6 tasks were attempted with `model_server`
- the run logged real model latency
- prompt size and output size were saved
- attempt-level traces were written

The sample files are saved separately under `examples/`:

- `sample_model_repair_results.csv`
- `sample_model_attempt_results.csv`
- `sample_model_repair_traces.jsonl`

I am still treating the rule baseline as the default reproducible run because GitHub Actions should not depend on a private API key.

## Next result to aim for

The next meaningful result should compare:

- repair pass rate
- recent prefix reuse
- model call latency
- prompt size
- output size
- retries or failed attempts

across at least two backends:

1. rule baseline
2. model-server backend

Later, the model-server backend can point to local vLLM or SGLang endpoints.