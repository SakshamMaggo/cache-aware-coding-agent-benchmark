import os
import time
from pathlib import Path

from src.fixer import generate_rule_based_fix


class BaseFixer:
    name = "base"

    def __init__(self) -> None:
        self.last_call = {}

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        raise NotImplementedError("fix() is not implemented for this fixer")


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
            "latency_seconds": round(elapsed, 4),
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

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "ModelServerFixer needs the openai package. "
                "Install requirements first."
            ) from exc

        self.model = os.getenv("MODEL_NAME", "gpt-4.1-mini")
        api_key = os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("MODEL_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None

        if not api_key:
         raise ValueError(
        "No model API key found. Set MODEL_API_KEY in your local .env file first."
    )

        self.client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        prompt = (
            "Fix the Python bug below.\n\n"
            f"Task:\n{task_text}\n\n"
            f"Buggy code:\n{buggy_code}\n\n"
            "Return only the corrected Python code. "
            "Do not include markdown. Do not include explanation."
        )

        start = time.perf_counter()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        elapsed = time.perf_counter() - start

        raw_code = response.choices[0].message.content or ""
        fixed_code = strip_code_fence(raw_code)

        self.last_call = {
            "model": self.model,
            "latency_seconds": round(elapsed, 4),
            "prompt_chars": len(prompt),
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