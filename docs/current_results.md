# Current Results

This is a short note on the current 12-task run.

The benchmark currently compares four prompt-layout settings:

1. normal prompt layout with mixed task order
2. cache-aware prompt layout with mixed task order
3. cache-aware prompt layout with grouped task order
4. cache-aware prompt layout without repo context, using grouped task order

The default local run still uses the rule-based baseline. So the default CI-safe result is mainly useful for checking the benchmark pipeline, prompt structure, task ordering, traces, reports, and dashboard. It should not be read as a real model-quality result.

## Main observation

The normal prompt layout gives very low adjacent prefix reuse. In the current run, recent prefix reuse stays close to zero.

The cache-aware prompt layout improves this because shared instructions and repo context are placed earlier in the prompt.

The grouped cache-aware run improves recent prefix reuse further because tasks from similar utility groups are placed closer together.

The no-repo-context ablation is useful because it separates two effects:

- how much reuse comes from a stable prompt layout
- how much reuse comes from including shared repo context

## Why this matters

Prefix caching and KV-cache reuse depend on prompts sharing the same beginning tokens.

So if coding-agent workloads can be written so repeated parts appear earlier, and similar tasks are scheduled together, the workload should be more friendly to efficient serving systems.

This does not prove a serving-system speedup by itself. It shows that the workload can be made structurally more cache-friendly, and that the same experiment path can now run with a real model backend.

## Repair quality

The default rule baseline currently fixes 6/12 tasks.

This is a better signal than the earlier toy-only run because the newer medium tasks are not all solved by simple rules. The rule baseline is still useful as a cheap reproducible check, but it is no longer pretending to solve the full benchmark.

The no-fix baseline fixes 0/12 tasks.

## Model backend sample

I also ran the model-server backend on the current 12-task set using a hosted model endpoint.

This confirms that the --fixer model path is wired up and can produce real repair outputs.

In the saved model repair sample:

- all 12 tasks were attempted with model_server
- the model fixed 11/12 tasks
- the failed task is a prompt-block deduplication task that requires normalizing whitespace/casing for comparison while preserving the first readable block
- real model latency was logged
- prompt size and output size were saved
- attempt-level traces were written

The sample files are saved separately under examples/:

- sample_model_repair_results.csv
- sample_model_attempt_results.csv
- sample_model_repair_traces.jsonl

I am still treating the rule baseline as the default reproducible run because GitHub Actions should not depend on a private API key.

## Model prompt experiment sample

The latest saved model prompt-layout experiment is still from the 10-task version of the benchmark.

That sample was run with:

    python -m src.experiment_runner --fixer model --max-tasks 10

It produced a real model-backed experiment CSV with four prompt settings:

- normal prompt layout
- cache-aware prompt layout
- grouped cache-aware prompt layout
- grouped cache-aware prompt layout without repo context

The sample file is saved as:

- examples/sample_model_experiment_results.csv

In that 10-task run, all four prompt settings solved 10/10 tasks. The main difference was prefix reuse: normal prompting had very low recent prefix reuse, while cache-aware and grouped layouts had much higher recent prefix reuse.

The next update should rerun this model prompt experiment on the current 12-task set.

## Current limitations

The task set is still small. It is better than the first toy-only version, but it is not close to SWE-bench-style realism yet.

The saved model runs use one hosted model backend. This is enough to prove that the model path works, but not enough to make a general claim about coding-agent serving performance.

The current prefix-reuse metric is a proxy. The next stronger version should connect this to real serving metrics such as TTFT, total latency, throughput, and cache hit behavior on a local model-serving backend.

## Next result to aim for

The next meaningful result should compare:

- repair pass rate
- recent prefix reuse
- model call latency
- prompt size
- output size
- retries or failed attempts

across at least two backend types:

1. hosted model-server backend
2. local OpenAI-compatible backend, eventually vLLM or SGLang

The longer-term goal is to test whether cache-aware prompt layout and grouped scheduling improve serving-side behavior, not just whether they improve a toy prefix-reuse score.