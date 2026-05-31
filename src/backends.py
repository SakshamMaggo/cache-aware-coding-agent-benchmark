import time
import hashlib


class DummyBackend:
    """
    A fake model backend.

    This lets us build and test the benchmark pipeline before using real LLMs.
    It simulates latency based on prompt length and returns a deterministic response.
    """

    def __init__(self, name: str = "dummy-local"):
        self.name = name

    def generate(self, prompt: str) -> dict:
        start = time.perf_counter()

        # Simulated latency: longer prompts take slightly more time.
        simulated_delay = min(0.15, 0.00002 * len(prompt))
        time.sleep(simulated_delay)

        prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8]

        output = f"""Bug summary:
This is a dummy backend response for prompt {prompt_hash}.

Fix explanation:
A real backend will generate a patch or corrected code here.

Corrected code:
# dummy corrected code
"""

        end = time.perf_counter()

        return {
            "backend": self.name,
            "output": output,
            "latency_seconds": round(end - start, 4),
            "ttft_seconds": round((end - start) * 0.35, 4),
            "tokens_per_second": round(len(output.split()) / max(end - start, 0.001), 2),
        }