"""LLM provider: handles API calls to OpenAI (or prints prompt as fallback)."""

import sys
from typing import Any

from .config import OPENAI_API_KEY, DEFAULT_MODEL


def call_llm(messages: list[dict]) -> str:
    if OPENAI_API_KEY:
        return _call_openai(messages)
    else:
        return _no_api_fallback(messages)


def _call_openai(messages: list[dict]) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=2048,
    )
    return response.choices[0].message.content or ""


def _no_api_fallback(messages: list[dict]) -> str:
    print("=" * 60, file=sys.stderr)
    print("  NO OPENAI_API_KEY SET", file=sys.stderr)
    print("  Set OPENAI_API_KEY env var or paste this prompt into ChatGPT:", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"]
        print(f"\n{'─' * 60}", file=sys.stderr)
        print(f"  {role}", file=sys.stderr)
        print(f"{'─' * 60}", file=sys.stderr)
        print(content[:3000], file=sys.stderr)

    return (
        "[LLM response not available - set OPENAI_API_KEY environment variable]\n"
        "The prompt has been printed to stderr. Copy it into ChatGPT or another LLM."
    )
