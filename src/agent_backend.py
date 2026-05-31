import os
from pathlib import Path

from src.fixer import generate_rule_based_fix


class BaseFixer:
    name = "base"

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
        return generate_rule_based_fix(task_id, buggy_code)


class ModelServerFixer(BaseFixer):
    """
    Generic backend for chat-style model servers.

    This can point to a hosted API or a local vLLM/SGLang server if the server
    exposes an OpenAI-style chat endpoint.
    """

    name = "model_server"

    def __init__(self) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "ModelServerFixer needs the openai package. "
                "Install requirements first."
            ) from exc

        self.model = os.getenv("MODEL_NAME", "gpt-4.1-mini")
        self.client = OpenAI(
            api_key=os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("MODEL_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None,
        )

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        prompt = (
            "Fix the Python bug below.\n\n"
            f"Task:\n{task_text}\n\n"
            f"Buggy code:\n{buggy_code}\n\n"
            "Return only the corrected Python code. "
            "Do not include markdown. Do not include explanation."
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        raw_code = response.choices[0].message.content or ""
        return strip_code_fence(raw_code)


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