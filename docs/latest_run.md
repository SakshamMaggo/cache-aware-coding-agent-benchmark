# Latest Run

This is a quick summary from the latest local run.

## Prompt layout

| run | recent reuse | best reuse | pass rate | avg prompt tokens |
|---|---:|---:|---:|---:|
| cache_grouped | 0.419 | 0.419 | 100.0% | 115.5 |
| cache_original | 0.282 | 0.410 | 100.0% | 115.5 |
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

## Notes

- The current repair backend is still the rule baseline.
- The timing numbers are not real LLM inference timings yet.
- The main useful result right now is that prompt layout and task order change prefix reuse a lot, even before using a real model backend.
- A model-server run can use the same scripts later.
