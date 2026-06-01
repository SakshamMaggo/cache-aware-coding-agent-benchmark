# Latest Run

This is a quick summary from the latest local run.

## Prompt layout

| run | recent reuse | best reuse | pass rate | avg prompt tokens |
|---|---:|---:|---:|---:|
| cache_grouped | 0.353 | 0.354 | 66.7% | 124.2 |
| cache_no_repo_grouped | 0.360 | 0.360 | 66.7% | 100.8 |
| cache_original | 0.251 | 0.341 | 66.7% | 124.2 |
| normal_original | 0.015 | 0.015 | 66.7% | 196.9 |

## Backend comparison

| backend | tasks | pass rate | avg attempts | failed tests after |
|---|---:|---:|---:|---:|
| none | 9 | 0.0% | 2.00 | 16 |
| rule | 9 | 66.7% | 1.33 | 6 |

## Repair run

- fixed tasks: 6/9
- attempt rows logged: 12
- max attempts used by any task: 2

## Model prompt experiment sample

| run | tasks | pass rate | recent reuse | avg model call time |
|---|---:|---:|---:|---:|
| cache_grouped | 8 | 100.0% | 0.366 | 1.08s |
| cache_no_repo_grouped | 8 | 100.0% | 0.365 | 2.08s |
| cache_original | 8 | 100.0% | 0.255 | 1.10s |
| normal_original | 8 | 100.0% | 0.015 | 1.44s |

This sample is saved under `examples/sample_model_experiment_results.csv`. It is not run in CI because it needs a private API key.

## Model sample run

- model: gpt-4.1-mini
- fixed tasks: 9/9
- avg model call time: 1.85 seconds
- avg prompt chars: 350.2
- avg output chars: 151.4

This sample is saved under `examples/`. It is not run in CI because it needs a private API key.

## Notes

- The default local run still uses the rule baseline.
- The model sample run is saved separately, so CI does not need a private API key.
- The main useful result right now is that prompt layout and task order change prefix reuse a lot.
- The next serious step is to test the same setup on less toy-like repair tasks.
