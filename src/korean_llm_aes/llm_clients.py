from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class LLMConfig:
    provider: str
    model: str
    temperature: float = 0.0
    max_retries: int = 5
    sleep_seconds: float = 0.5


def extract_json_object(text: str) -> Dict[str, object]:
    """Parse a JSON object from a model response."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def call_openai(prompt: str, cfg: LLMConfig) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=cfg.model,
        temperature=cfg.temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


def call_anthropic(prompt: str, cfg: LLMConfig) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=cfg.model,
        max_tokens=2048,
        temperature=cfg.temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if getattr(block, "type", None) == "text")


def call_google(prompt: str, cfg: LLMConfig) -> str:
    import google.generativeai as genai

    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(cfg.model)
    response = model.generate_content(
        prompt,
        generation_config={"temperature": cfg.temperature},
    )
    return response.text or ""


def call_llm(prompt: str, cfg: LLMConfig) -> Dict[str, object]:
    callers = {
        "openai": call_openai,
        "anthropic": call_anthropic,
        "google": call_google,
    }
    if cfg.provider not in callers:
        raise ValueError(f"Unknown provider: {cfg.provider}")
    last_error: Optional[Exception] = None
    for attempt in range(1, cfg.max_retries + 1):
        try:
            text = callers[cfg.provider](prompt, cfg)
            return extract_json_object(text)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < cfg.max_retries:
                time.sleep(cfg.sleep_seconds * attempt)
    raise RuntimeError(f"LLM call failed after {cfg.max_retries} attempts: {last_error}")
