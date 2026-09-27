"""
STAGE iv — GENERATION

Calls an LLM with the augmented prompt from Stage iii and returns the
answer text. Three implementations behind one `LLMClient` interface:

  - StubLLMClient — no API key needed, no network call. Returns a
    templated answer built directly from the retrieved passages.

  - GroqLLMClient — FREE, no credit card required. Get a key at
    https://console.groq.com/keys. Uses an OpenAI-compatible REST
    endpoint via `requests`, no extra SDK dependency needed.

  - AnthropicLLMClient — paid, real calls to Claude via the Anthropic API.
    Requires ANTHROPIC_API_KEY in your .env.

Switch between them with LLM_PROVIDER in .env — nothing calling
`get_llm_client()` needs to know or care which one is active.
"""

import os
from abc import ABC, abstractmethod
from typing import List

from app.rag.prompt_builder import SYSTEM_PROMPT, SourceEntry


class LLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        ...


class StubLLMClient(LLMClient):
    """No API key required — used until a real provider is configured."""

    def __init__(self, sources: List[SourceEntry] = None):
        self.sources = sources or []

    async def generate(self, prompt: str) -> str:
        if not self.sources:
            return (
                "I couldn't find anything relevant to that question in this submission's "
                "indexed documents. (Note: this is the offline stub LLM — set "
                "LLM_PROVIDER=groq and GROQ_API_KEY in your .env for real generated answers, "
                "free of charge.)"
            )
        lines = [f"Based on the indexed documents, here's what's relevant:\n"]
        for s in self.sources[:3]:
            lines.append(f"[{s.index}] {s.snippet.strip()}")
        lines.append(
            "\n(Note: this is the offline stub LLM, showing raw retrieved passages rather "
            "than a generated answer. Set LLM_PROVIDER=groq and GROQ_API_KEY in your .env "
            "to get real LLM-generated responses grounded in this context — free, no credit "
            "card required.)"
        )
        return "\n".join(lines)


class GroqLLMClient(LLMClient):
    """
    Free — no credit card required. Get a key at https://console.groq.com/keys
    Uses an OpenAI-compatible REST endpoint, called directly with `requests`
    so no extra SDK dependency is needed.
    """

    def __init__(self, model: str = None):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in the environment.")
        self.api_key = api_key
        # Groq's model lineup changes fairly often — override via GROQ_MODEL in
        # .env if this default ever gets deprecated. Check current options at
        # https://console.groq.com/docs/models
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    async def generate(self, prompt: str) -> str:
        import requests  # deferred import — only needed if this client is used

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "max_tokens": 1000,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


class AnthropicLLMClient(LLMClient):
    def __init__(self, model: str = "claude-sonnet-5"):
        from anthropic import Anthropic  # deferred import — only needed if this client is used
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set in the environment.")
        self.client = Anthropic(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


def get_llm_client(sources: List[SourceEntry] = None) -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "stub").lower()
    if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicLLMClient()
    if provider == "groq" and os.getenv("GROQ_API_KEY"):
        return GroqLLMClient()
    return StubLLMClient(sources=sources)