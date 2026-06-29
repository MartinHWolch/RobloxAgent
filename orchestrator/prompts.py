"""Prompt builder: formats context into structured prompts for the LLM."""

import json
from typing import Any

from .config import MAX_CONTEXT_LENGTH, MAX_RAG_CHARS

SYSTEM_PROMPT = """You are a senior Roblox developer AI assistant. You help developers build better Roblox games by providing accurate, practical, and up-to-date advice.

You have access to:
1. A curated knowledge base of Roblox documentation, DevForum topics, GitHub libraries, and code examples
2. The project index (structure, scripts, dependencies) if the user provides a project path
3. Persistent memory (project rules, past decisions, resolved cases)

## Guidelines
- Always reference the knowledge base context when answering technical questions
- Cite your sources (engine_api, devforum, github, examples)
- When generating code, include clear Luau examples with proper type annotations
- Follow the project rules if they exist
- If you don't know something from the provided context, say so
- Be concise and practical, like a senior developer giving advice
- ALWAYS reply in Spanish unless the user asks otherwise
"""


def build_messages(query: str, context: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    rag_context = _format_rag(context.get("rag_results", []))
    project_context = _format_project(context.get("project_index"))
    memory_context = _format_memory(context.get("memory_rules", []), context.get("memory_cases", []))

    system = SYSTEM_PROMPT

    if rag_context:
        system += f"\n\n## Relevant Knowledge Base\n{rag_context}"

    if project_context:
        system += f"\n\n## Project Structure\n{project_context}"

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


def _format_project(index: dict | None) -> str:
    if not index:
        return ""
    if "error" in index:
        return f"(Index error: {index['error']})"

    lines = [f"Project: {index.get('name', '?')}"]
    lines.append(f"Framework: {index.get('framework', '?')}")
    lines.append(f"Scripts: {index.get('total_scripts', 0)} ({index.get('total_code_lines', 0)} lines)")
    services = index.get("services_used", [])
    if services:
        lines.append(f"Services used: {', '.join(services)}")
    lines.append("")

    for s in index.get("scripts", []):
        svcs = [sv["service"] for sv in s.get("services", [])]
        deps = s.get("requires", [])
        lines.append(f"  {s['name']} ({s['path']})")
        if svcs:
            lines.append(f"    Services: {', '.join(svcs)}")
        if deps:
            lines.append(f"    Requires: {', '.join(deps[:3])}")

    return "\n".join(lines)


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
