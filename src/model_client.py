import os
import time
from dataclasses import dataclass
from typing import Optional

from src.env_loader import load_env


@dataclass
class ModelCallResult:
    text: str
    model: str
    backend_type: str
    base_url: str
    latency_seconds: float
    prompt_chars: int
    output_chars: int


def get_backend_type(base_url: Optional[str]) -> str:
    if not base_url:
        return "hosted"

    lowered = base_url.lower()

    if "localhost" in lowered or "127.0.0.1" in lowered or "0.0.0.0" in lowered:
        return os.getenv("MODEL_BACKEND", "local_openai_compatible")

    return os.getenv("MODEL_BACKEND", "remote_openai_compatible")


class OpenAICompatibleModelClient:
    """
    Small wrapper around OpenAI-compatible chat endpoints.

    Works with hosted APIs, vLLM, and SGLang as long as the backend exposes
    /v1/chat/completions.
    """

    def __init__(self) -> None:
        load_env()

        self.model = os.getenv("MODEL_NAME", "local-code-model")
        self.api_key = os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("MODEL_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None
        self.backend_type = get_backend_type(self.base_url)

        if not self.api_key:
            raise ValueError(
                "No model API key found. Set MODEL_API_KEY in your local .env file. "
                "For local vLLM/SGLang, MODEL_API_KEY can usually be EMPTY."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAICompatibleModelClient needs the openai package. "
                "Install requirements first."
            ) from exc

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def list_models(self) -> list[str]:
        models = self.client.models.list()
        return [item.id for item in models.data]

    def chat(self, prompt: str, temperature: float = 0) -> ModelCallResult:
        start = time.perf_counter()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )

        elapsed = time.perf_counter() - start
        text = response.choices[0].message.content or ""

        return ModelCallResult(
            text=text,
            model=self.model,
            backend_type=self.backend_type,
            base_url=self.base_url or "",
            latency_seconds=round(elapsed, 8),
            prompt_chars=len(prompt),
            output_chars=len(text),
        )
