"""Prompt builder: formats context into structured prompts for the LLM."""

import json
from typing import Any

from .config import MAX_CONTEXT_LENGTH, MAX_RAG_CHARS

SYSTEM_PROMPT = """You are a senior Roblox developer AI assistant. You help developers build better Roblox games by providing accurate, practical, and up-to-date advice.

You have access to:
1. A curated knowledge base of Roblox documentation, DevForum topics, GitHub libraries, and code examples
2. Persistent memory (project rules, past decisions, resolved cases)

## Guidelines
- Always reference the knowledge base context when answering technical questions
- Cite your sources (engine_api, devforum, github, examples)
- When generating code, include clear Luau examples with proper type annotations
- Follow the project rules if they exist
- If you don't know something from the provided context, say so
- Do not invent extra features, systems, assets, screens, effects, or refactors the user did not ask for
- If the request is ambiguous or missing a necessary decision, ask one concise clarifying question before proposing changes
- For Roblox Studio work, prefer a before/after verification mindset: inspect first, make the minimal requested change, then verify with readback, logs, screenshot, or playtest when applicable
- For UI, playtest, spawn, placement, collision, terrain, or walkability work, use explicit QA steps instead of assuming the result is correct
- For security, performance, debugging, publishing, monetization, and code review requests, answer with structured findings ordered by severity before suggesting fixes
- For genre requests such as obby, tycoon, simulator, RPG, horror, or battle royale, use genre patterns as optional context only; implement or propose only the features explicitly requested
- Never invent Roblox asset IDs; use only user-provided IDs or explicit accepted search results
- Never invent GamePass IDs, Developer Product IDs, prices, odds, or revenue claims
- Be concise and practical, like a senior developer giving advice
- ALWAYS reply in Spanish unless the user asks otherwise
"""


def build_messages(query: str, context: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    rag_context = _format_rag(context.get("rag_results", []))
    memory_context = _format_memory(context.get("memory_rules", []), context.get("memory_cases", []))

    system = SYSTEM_PROMPT

    if rag_context:
        system += f"\n\n## Relevant Knowledge Base\n{rag_context}"

    if memory_context:
        system += f"\n\n## Project Memory\n{memory_context}"

    if len(system) > MAX_CONTEXT_LENGTH:
        system = system[:MAX_CONTEXT_LENGTH] + "\n\n[Context truncated...]"

    user_msg = _build_user_message(query, context.get("intents", []))

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]


def _format_rag(results: list[dict]) -> str:
    if not results:
        return ""
    lines = []
    total_chars = 0
    for i, r in enumerate(results[:8], 1):
        if "error" in r:
            continue
        source = r.get("metadata", {}).get("source", "?")
        name = r.get("metadata", {}).get("name", r.get("metadata", {}).get("category", "?"))
        text = r.get("text", "")
        entry = f"\n### [{i}] Source: {source} | {name}\n{text}\n"
        if total_chars + len(entry) > MAX_RAG_CHARS:
            break
        lines.append(entry)
        total_chars += len(entry)
    return "".join(lines)


def _format_memory(rules: list, cases: list) -> str:
    lines = []

    if rules and "error" not in rules[0]:
        lines.append("### Project Rules")
        for r in rules:
            desc = r.get("description", "") or ""
            desc_part = f" ({desc})" if desc else ""
            lines.append(f"- [{r['category']}] {r['key']}: {r['value']}{desc_part}")

    if cases and "error" not in cases[0]:
        lines.append("\n### Past Resolved Cases")
        for c in cases[:5]:
            lines.append(f"- {c['title']} [{c['outcome']}]: {c['problem_summary'][:100]}")

    return "\n".join(lines)


def _build_user_message(query: str, intents: list[dict]) -> str:
    intent_str = ", ".join(f"{i['intent']} ({i['confidence']:.0%})" for i in intents[:3])
    return f"Query: {query}\n\nClassified as: {intent_str}\n\nPlease respond in Spanish with practical Roblox development advice."
