# Backend Notes

Right now, the project uses a small rule-based fixer. That is intentional. I wanted the full loop to work first before adding a paid API or a local GPU server.

The loop is:

    task
    -> fixer backend
    -> proposed code
    -> pytest
    -> repair result

The backend is kept generic because I eventually want the same benchmark to run with different serving setups:

- rule-based baseline
- hosted model server
- local vLLM endpoint
- local SGLang endpoint

The main thing I want to compare later is not just whether the code passes tests. For coding agents, the model may be called many times, so serving cost and latency also matter.

Metrics I want to track:

- pass rate
- tests failed before and after repair
- fixer call time
- prompt size
- output size
- retries
- TTFT
- throughput
- effect of cache-aware prompt layout
- effect of grouping similar tasks together

The current version only logs the simpler parts of this. The point is to keep the runner stable first, then plug in model servers and compare them using the same task set.