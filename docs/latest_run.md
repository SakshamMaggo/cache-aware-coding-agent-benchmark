# Latest Run

This is a quick summary from the latest local run.

## Prompt layout

| run | recent reuse | best reuse | pass rate | avg prompt tokens |
|---|---:|---:|---:|---:|
| cache_grouped | 0.335 | 0.345 | 60.0% | 133.5 |
| cache_no_repo_grouped | 0.343 | 0.343 | 60.0% | 111.0 |
| cache_original | 0.252 | 0.333 | 60.0% | 133.5 |
| normal_original | 0.015 | 0.015 | 60.0% | 207.1 |

## Backend comparison

| backend | tasks | pass rate | avg attempts | failed tests after |
|---|---:|---:|---:|---:|
| none | 10 | 0.0% | 2.00 | 19 |
| rule | 10 | 60.0% | 1.40 | 9 |

## Repair run

- fixed tasks: 6/10
- attempt rows logged: 14
- max attempts used by any task: 2

## Model prompt experiment sample

| run | tasks | pass rate | recent reuse | avg model call time |
|---|---:|---:|---:|---:|
| cache_grouped | 9 | 100.0% | 0.353 | 1.21s |
| cache_no_repo_grouped | 9 | 100.0% | 0.360 | 1.57s |
| cache_original | 9 | 100.0% | 0.251 | 1.37s |
| normal_original | 9 | 100.0% | 0.015 | 1.32s |

This sample is saved under `examples/sample_model_experiment_results.csv`. It is not run in CI because it needs a private API key.

## Model sample run

- model: gpt-4.1-mini
- fixed tasks: 10/10
- avg model call time: 1.85 seconds
- avg prompt chars: 395.2
- avg output chars: 179.0

This sample is saved under `examples/`. It is not run in CI because it needs a private API key.

## Notes

- The default local run still uses the rule baseline.
- The model sample run is saved separately, so CI does not need a private API key.
- The main useful result right now is that prompt layout and task order change prefix reuse a lot.
- The next serious step is to test the same setup on less toy-like repair tasks.
