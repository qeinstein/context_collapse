import os
import time
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from src.config import (
    MAX_TOKENS,
    MODEL_NAME,
    OPENROUTER_APP_NAME,
    OPENROUTER_BASE_URL,
    OPENROUTER_SITE_URL,
    TEMPERATURE,
)
from src.task_defs import ModelResponse, Task

load_dotenv()

class DummyModel:
    def __init__(self, name: str = "dummy-model") -> None:
        self.name = name

    def generate(self, prompt: str, task: Task) -> ModelResponse:
        start = time.perf_counter()
        output = task.expected_answer
        latency_ms = (time.perf_counter() - start) * 1000

        return ModelResponse(
            raw_text=output,
            latency_ms=latency_ms,
            metadata={"backend": "dummy"},
        )


class OpenRouterModel:
    """
    OpenRouter adapter using the OpenAI Python SDK against OpenRouter's
    OpenAI-compatible chat completions endpoint.
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        api_key: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
    ) -> None:
        self.name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OPENROUTER_API_KEY is not set.")

        self.client = OpenAI(
            api_key=key,
            base_url=OPENROUTER_BASE_URL,
        )

        # Optional OpenRouter headers for app attribution.
        self.extra_headers = {
            "HTTP-Referer": OPENROUTER_SITE_URL,
            "X-Title": OPENROUTER_APP_NAME,
        }

    def generate(self, prompt: str, task: Task) -> ModelResponse:
        start = time.perf_counter()

        response = self.client.chat.completions.create(
            model=self.name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            extra_headers=self.extra_headers,
        )

        latency_ms = (time.perf_counter() - start) * 1000

        raw_text = ""
        if response.choices and response.choices[0].message:
            raw_text = response.choices[0].message.content or ""

        metadata = {
            "backend": "openrouter",
            "response_id": getattr(response, "id", None),
            "model": getattr(response, "model", None),
            "usage": response.usage.model_dump() if getattr(response, "usage", None) else None,
        }

        return ModelResponse(
            raw_text=raw_text,
            latency_ms=latency_ms,
            metadata=metadata,
        )
