# Streaming Probe

The streaming probe is a small v1.1 addition to the benchmark.

It sends one streamed chat-completion request to the configured model backend and logs a few serving-side measurements.

## What it logs

The probe saves:

- model name
- prompt size
- time to first streamed chunk
- total streamed latency
- output size
- characters per second after the first chunk

The output is written to:

    results/streaming_probe.csv

A saved sample is kept at:

    examples/sample_streaming_probe.csv

## Why this matters

Earlier versions of the project used prefix reuse as a proxy for cache-friendliness.

The streaming probe is a first step toward measuring real serving behavior. It does not prove a full serving-speedup result yet, but it starts moving the benchmark from prompt-structure metrics toward real inference measurements.

## Current limitation

The current sample uses a hosted model backend. That means it can measure client-observed streaming latency, but it cannot directly inspect server-side prefix-cache hits.

The stronger next step is to run the same probe against a local OpenAI-compatible backend such as vLLM or SGLang.