# Methodology

This project is a small benchmark prototype for studying cache-aware prompt layout and task ordering in coding-agent workloads.

The main question is not only whether a repair backend can fix code. The larger question is whether coding-agent prompts can be structured and scheduled in a way that makes them more friendly to model-serving systems that use prefix caching or KV-cache reuse.

## What is measured

The benchmark currently tracks:

- whether each task fails before repair
- whether each task passes after repair
- number of repair attempts used
- prompt size
- output size
- model call latency when a model backend is used
- recent prefix reuse between adjacent prompts
- best prefix reuse against earlier prompts in the same run

The prompt-layout experiments compare:

1. normal prompt layout
2. cache-aware prompt layout
3. cache-aware prompt layout with grouped task ordering
4. cache-aware prompt layout without repo context

## Prefix reuse metric

The prefix-reuse score is a proxy metric.

It checks how much of the beginning of one prompt is shared with earlier prompts. This matters because many serving systems can benefit when prompts share the same prefix.

The metric is useful for comparing prompt layouts because it can show whether repeated instructions, repo context, and task metadata are placed in stable positions.

It does not directly prove a speedup. A real speedup depends on the serving backend, cache implementation, batching behavior, model size, hardware, and request scheduling.

## Why the rule baseline exists

The rule baseline is not meant to be a serious coding agent.

It exists because it gives a cheap and reproducible local check. It makes sure that the benchmark pipeline, task runner, trace logging, reports, and dashboard work without requiring a private API key.

GitHub Actions uses this path because CI should stay free and reproducible.

## Why model samples are saved separately

The hosted model backend is used for saved sample runs.

These runs show that the same repair and prompt-layout scripts can work with a real model backend. They also record real model latency, prompt size, output size, and pass/fail behavior.

The model samples are not rerun in CI because they require a private API key and would create paid usage.

## Current task design

The task set includes a mix of simple utility repair tasks and benchmark-system tasks.

The later tasks are more relevant to this project because they involve cache-key normalization, retry trace aggregation, prompt block deduplication, and stable task grouping.

This is still a small benchmark. It should be treated as a prototype task set, not as a replacement for larger benchmarks like SWE-bench or SWE-bench Lite.

## What this benchmark does not claim yet

This project does not yet claim that cache-aware prompting improves real serving throughput.

It also does not claim general coding-agent quality across real repositories.

The current results only show that:

- prompt layout and task ordering can strongly change prefix reuse
- the model backend path works
- saved model samples can be produced with real latency and pass/fail data
- the benchmark can separate a cheap CI-safe baseline from paid model-backed samples

## Next methodology step

The next stronger version should connect the prefix-reuse proxy to real serving metrics.

Useful future measurements would include:

- TTFT
- total latency
- tokens per second
- throughput under batched requests
- prefix cache hit behavior
- cost per successful repair
- performance across multiple model backends

A local OpenAI-compatible backend such as vLLM or SGLang would make this comparison much stronger.