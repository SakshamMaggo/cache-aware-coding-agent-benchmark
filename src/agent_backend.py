import time
from pathlib import Path

from src.fixer import generate_rule_based_fix
from src.model_client import OpenAICompatibleModelClient


class BaseFixer:
    name = "base"

    def __init__(self) -> None:
        self.last_call = {}

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        raise NotImplementedError("fix() is not implemented for this fixer")

class NoFixer(BaseFixer):
    name = "no_fix"

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        self.last_call = {
            "model": "none",
            "latency_seconds": 0,
            "prompt_chars": len(task_text) + len(buggy_code),
            "output_chars": len(buggy_code),
        }
        return buggy_code
    
class RuleFixer(BaseFixer):
    """
    Small baseline fixer for the toy tasks.

    Not smart, but useful: it lets the rest of the benchmark run end-to-end
    before plugging in a real model server.
    """

    name = "rule_baseline"

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        start = time.perf_counter()
        fixed_code = generate_rule_based_fix(task_id, buggy_code)
        elapsed = time.perf_counter() - start

        self.last_call = {
             "model": "rule_based",
             "latency_seconds": round(elapsed, 8),
             "prompt_chars": len(task_text) + len(buggy_code),
             "output_chars": len(fixed_code),
}

        return fixed_code


class ModelServerFixer(BaseFixer):
    """
    Generic backend for chat-style model servers.

    This can point to a hosted API or a local vLLM/SGLang server if the server
    exposes an OpenAI-style chat endpoint.
    """

    name = "model_server"

    def __init__(self) -> None:
        super().__init__()
        self.client = OpenAICompatibleModelClient()
        self.model = self.client.model

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        prompt = (
            "Fix the Python bug below.\n\n"
            f"Task:\n{task_text}\n\n"
            f"Buggy code:\n{buggy_code}\n\n"
            "Return only the corrected Python code. "
            "Do not include markdown. Do not include explanation."
        )

        result = self.client.chat(prompt=prompt, temperature=0)

        fixed_code = strip_code_fence(result.text)

        self.last_call = {
            "model": result.model,
            "backend_type": result.backend_type,
            "base_url": result.base_url,
            "latency_seconds": result.latency_seconds,
            "prompt_chars": result.prompt_chars,
            "output_chars": len(fixed_code),
        }

        return fixed_code


def strip_code_fence(text: str) -> str:
    text = text.strip()

    if text.startswith("```python"):
        text = text.removeprefix("```python").strip()

    if text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text + "\n"


def read_task_text(task_dir: Path) -> str:
    task_file = task_dir / "task.md"

    if not task_file.exists():
        return ""

    return task_file.read_text().strip()