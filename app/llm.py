import json
import os
from typing import Any, Dict


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if len(lines) >= 3:
            t = "\n".join(lines[1:-1]).strip()
    return t


def safe_json_loads(text: str) -> Dict[str, Any]:
    cleaned = _strip_code_fence(text)
    return json.loads(cleaned)


def call_llm(prompt: str, temperature: float = 0.0) -> str:
    """
    Unified LLM call interface.
    If OPENAI_API_KEY is unavailable, returns a deterministic fallback stub.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        # Deterministic fallback keeps MVP runnable without cloud dependency.
        return "{}"

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        resp = client.responses.create(
            model=model,
            input=prompt,
            temperature=temperature,
        )
        return resp.output_text.strip()
    except Exception:
        return "{}"
