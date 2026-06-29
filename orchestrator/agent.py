"""Main agent: receives query, gathers context, calls LLM, returns response."""

from typing import Any

from .router import classify
from .context import gather_context
from .prompts import build_messages
from .llm import call_llm


def process_query(query: str) -> dict[str, Any]:
    intents = classify(query)
    context = gather_context(query)
    messages = build_messages(query, context)

    response = call_llm(messages)

    return {
        "query": query,
        "response": response,
        "intents": intents,
        "rag_count": len(context.get("rag_results", [])),
        "rules_count": len(context.get("memory_rules", [])),
        "cases_count": len(context.get("memory_cases", [])),
    }
