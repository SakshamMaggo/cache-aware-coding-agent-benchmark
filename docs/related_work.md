# Related Work Notes

This project is not trying to replace coding-agent benchmarks like SWE-bench.

SWE-bench evaluates whether language models can fix real GitHub issues by generating patches for existing repositories. SWE-bench Lite is a smaller 300-task version that makes evaluation cheaper and easier to iterate on.

My current benchmark is much smaller. It only has toy repair tasks right now, so the pass-rate numbers should not be read as model-quality results.

The part I am trying to study is different: whether coding-agent workloads can be written and ordered in a way that is more friendly to prefix caching / KV-cache reuse.

So the current comparison is more about prompt structure than about final repair ability.

The rough positioning is:

- SWE-bench / SWE-bench Lite: realistic software repair benchmark
- this project right now: small systems prototype for prompt layout, grouping, traces, and backend comparison
- intended next step: run the same pipeline with a real model-server backend, then later with vLLM / SGLang

The main missing piece is still a real model run. Until that is added, the project should be treated as an early benchmark prototype, not a full coding-agent evaluation.