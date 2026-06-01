# Experiment Plan

I am using this file to keep track of what the benchmark is actually testing.

## Main question

Can coding-agent repair tasks be arranged in a more cache-friendly way?

The current version only tests this on a small toy benchmark. It does not prove real LLM serving speedups yet. For now, it checks whether prompt layout and task order create more shared prefix structure.

## Current hypothesis

Coding agents repeat a lot of the same text: instructions, output format, repo context, and task setup.

If the repeated parts are placed at the front of the prompt, then the prompt should be more friendly to prefix caching / KV-cache reuse.

If similar tasks are placed next to each other, adjacent prompts should also share more context.

## Runs right now

The experiment runner compares:

1. normal prompt layout with mixed task order
2. cache-aware prompt layout with mixed task order
3. cache-aware prompt layout with grouped task order

The current task groups are:

- math utilities
- string utilities
- list utilities

## Metrics

The main metrics right now are:

- best prefix reuse
- recent prefix reuse
- prompt tokens
- repair pass rate
- fixer call time
- output size

`best_prefix_reuse` checks the best overlap with any earlier prompt.

`recent_prefix_reuse` checks overlap with the immediately previous prompt. This is useful because task ordering should mostly affect adjacent calls.

## Current result

The current run shows that cache-aware prompts create much higher prefix reuse than the normal prompt layout.

Grouping also improves recent prefix reuse because similar tasks are placed next to each other.

Repair pass rate stays the same under the rule-based baseline, so the prompt changes are not breaking the repair loop in this small setup.

## What this does not prove yet

This does not prove real latency gains yet.

The current fixer is rule-based, so its timing is not meaningful as model inference timing.

The task set is still small and toy-like.

The next serious step is to run the same setup with a real model-server backend, and later with vLLM / SGLang on a GPU machine.

## Next things to try

- add more tasks
- make the task groups more realistic
- run the model-server backend
- track retries and failed repair attempts
- compare pass rate and latency together
- run the same benchmark through vLLM and SGLang later