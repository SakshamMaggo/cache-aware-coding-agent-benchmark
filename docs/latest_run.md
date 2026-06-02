# Latest Run

This is a quick summary from the latest local run.

## Prompt layout

| run | recent reuse | best reuse | pass rate | avg prompt tokens |
|---|---:|---:|---:|---:|
| cache_grouped | 0.331 | 0.350 | 50.0% | 134.8 |
| cache_no_repo_grouped | 0.332 | 0.332 | 50.0% | 113.8 |
| cache_original | 0.273 | 0.340 | 50.0% | 134.8 |
| normal_original | 0.015 | 0.015 | 50.0% | 209.8 |

## Backend comparison

| backend | tasks | pass rate | avg attempts | failed tests after |
|---|---:|---:|---:|---:|
| none | 12 | 0.0% | 2.00 | 22 |
| rule | 12 | 50.0% | 1.50 | 12 |

## Repair run

- fixed tasks: 6/12
- attempt rows logged: 18
- max attempts used by any task: 2

## Model prompt experiment sample

| run | tasks | pass rate | recent reuse | avg model call time |
|---|---:|---:|---:|---:|
| cache_grouped | 12 | 91.7% | 0.331 | 1.22s |
| cache_no_repo_grouped | 12 | 91.7% | 0.332 | 2.12s |
| cache_original | 12 | 91.7% | 0.273 | 1.23s |
| normal_original | 12 | 91.7% | 0.015 | 2.46s |

This sample is saved under `examples/sample_model_experiment_results.csv`. It is not run in CI because it needs a private API key.

## Model sample run

- model: gpt-4.1-mini
- fixed tasks: 11/12
- avg model call time: 1.57 seconds
- avg prompt chars: 412.9
- avg output chars: 183.6

This sample is saved under `examples/`. It is not run in CI because it needs a private API key.

## Notes

- The default local run still uses the rule baseline.
- The model sample run is saved separately, so CI does not need a private API key.
- The main useful result right now is that prompt layout and task order change prefix reuse a lot.
- The next serious step is to test the same setup on less toy-like repair tasks.
