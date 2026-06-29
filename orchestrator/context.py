"""Context builder: gathers relevant context from RAG, memory, and project indexer."""

import os
import json
import sys
from typing import Any

from .config import PROJECT_ROOT, RAG_TOP_K, MEMORY_RULES_LIMIT
from .router import classify, needs_rag, needs_project, needs_memory


def gather_context(query: str, project_path: str | None = None) -> dict[str, Any]:
    intents = classify(query)

    context = {
        "query": query,
        "intents": intents,
        "rag_results": [],
        "project_index": None,
        "memory_rules": [],
        "memory_cases": [],
    }

    if needs_rag(intents):
        context["rag_results"] = _query_rag(query)

    if needs_project(intents) and project_path:
        context["project_index"] = _index_project(project_path)

    if needs_memory(intents):
        rules, cases = _query_memory(query)
        context["memory_rules"] = rules
        context["memory_cases"] = cases
    else:
        context["memory_rules"] = _get_all_rules()

    return context


def _query_rag(query: str) -> list[dict]:
    try:
        sys.path.insert(0, os.path.join(PROJECT_ROOT))
        from rag.retriever import retrieve
        results = retrieve(query, top_k=RAG_TOP_K)
        for r in results:
            if isinstance(r.get("text"), str):
                r["text"] = r["text"][:2000]
        return results
    except Exception as e:
        return [{"error": f"RAG error: {e}"}]


def _index_project(project_path: str) -> dict | None:
    try:
        sys.path.insert(0, os.path.join(PROJECT_ROOT))
        from project_indexer import index_project as run_index
        result = run_index(project_path)
        summary = result.get("summary", {})
        return {
            "name": result.get("project", {}).get("name", ""),
            "framework": result.get("project", {}).get("framework", ""),
            "total_scripts": summary.get("total_scripts", 0),
            "total_code_lines": summary.get("total_code_lines", 0),
            "services_used": summary.get("services_used", []),
            "scripts": [
                {"name": s.get("name", ""), "path": s.get("path", ""),
                 "services": s.get("services", []),
                 "requires": [r["path"] for r in s.get("requires", [])]}
                for s in result.get("scripts", [])
            ],
        }
    except Exception as e:
        return {"error": f"Project index error: {e}"}


def _query_memory(query: str) -> tuple[list, list]:
    rules = []
    cases = []
    try:
        sys.path.insert(0, os.path.join(PROJECT_ROOT))
        from memory.rules import search_rules, list_rules
        from memory.cases import search_cases
        rules = search_rules(query)
        if not rules:
            rules = list_rules()
        cases = search_cases(query)
    except Exception as e:
        rules = [{"error": f"Memory error: {e}"}]
    return rules, cases


def _get_all_rules() -> list:
    try:
        sys.path.insert(0, os.path.join(PROJECT_ROOT))
        from memory.rules import list_rules
        rules = list_rules()
        return rules[:MEMORY_RULES_LIMIT]
    except Exception as e:
        return [{"error": f"Memory error: {e}"}]
