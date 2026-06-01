# Latest Run

This is a quick summary from the latest local run.

## Prompt layout

| run | recent reuse | best reuse | pass rate | avg prompt tokens |
|---|---:|---:|---:|---:|
| cache_grouped | 0.402 | 0.402 | 100.0% | 113.5 |
| cache_no_repo_grouped | 0.373 | 0.373 | 100.0% | 88.5 |
| cache_original | 0.260 | 0.394 | 100.0% | 113.5 |
| normal_original | 0.015 | 0.015 | 100.0% | 184.7 |

## Backend comparison

| backend | tasks | pass rate | avg attempts | failed tests after |
|---|---:|---:|---:|---:|
| none | 6 | 0.0% | 2.00 | 10 |
| rule | 6 | 100.0% | 1.00 | 0 |

## Repair run

- fixed tasks: 6/6
- attempt rows logged: 6
- max attempts used by any task: 1

## Model sample run

- model: gpt-4.1-mini
- fixed tasks: 6/6
- avg model call time: 1.59 seconds
- avg prompt chars: 285.0
- avg output chars: 81.7

This sample is saved under `examples/`. It is not run in CI because it needs a private API key.

## Notes

- The default local run still uses the rule baseline.
- The model sample run is saved separately, so CI does not need a private API key.
- The main useful result right now is that prompt layout and task order change prefix reuse a lot.
- The next serious step is to test the same setup on less toy-like repair tasks.
