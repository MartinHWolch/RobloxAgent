"""Context builder: gathers relevant context from RAG and memory."""

import os
import sys
from typing import Any

from .config import PROJECT_ROOT, RAG_TOP_K, MEMORY_RULES_LIMIT
from .router import classify, needs_rag, needs_memory


def gather_context(query: str) -> dict[str, Any]:
    intents = classify(query)

    context = {
        "query": query,
        "intents": intents,
        "rag_results": [],
        "memory_rules": [],
        "memory_cases": [],
    }

    if needs_rag(intents):
        context["rag_results"] = _query_rag(query)

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
        search_queries = _rag_search_queries(query)
        results = []
        seen_ids = set()
        per_query = max(3, RAG_TOP_K // max(len(search_queries), 1))

        for search_query in search_queries:
            for r in retrieve(search_query, top_k=per_query):
                rid = r.get("id")
                if rid in seen_ids:
                    continue
                seen_ids.add(rid)
                results.append(r)

        results = results[:RAG_TOP_K]
        for r in results:
            if isinstance(r.get("text"), str):
                r["text"] = r["text"][:2000]
        return results
    except Exception as e:
        return [{"error": f"RAG error: {e}"}]


def _rag_search_queries(query: str) -> list[str]:
    lower = query.lower()
    queries = []

    if any(term in lower for term in ["guardar", "guardado", "datos", "persistencia", "datastore", "profilestore"]):
        queries.append("DataStore ProfileStore ProfileService session locking autosave UpdateAsync player data persistence")

    if any(term in lower for term in ["remoteevent", "remote", "validaci", "seguridad", "exploit", "server authoritative", "autoridad"]):
        queries.append("RemoteEvent OnServerEvent server authoritative sanity checks exploit prevention remote validation")

    if any(term in lower for term in ["arquitectura", "estructura", "proyecto"]):
        queries.append("Roblox server services modules controllers structure architecture")

    if any(term in lower for term in ["memorystore", "matchmaking", "cola", "queue"]):
        queries.append("MemoryStoreService MemoryStoreQueue MemoryStoreSortedMap matchmaking cross server")

    if any(term in lower for term in ["npc", "pathfinding", "camino", "path"]):
        queries.append("PathfindingService NPC optimization humanoid performance A star")

    if any(term in lower for term in ["ui", "interfaz", "gui", "startergui", "playergui", "hud", "menu", "boton", "botón"]):
        queries.append("Roblox UI ScreenGui StarterGui PlayerGui safe area UIScale UITextSizeConstraint mobile touch targets")

    if any(term in lower for term in ["playtest", "test", "prueba", "validar", "logs", "errores"]):
        queries.append("Roblox Studio testing modes playtest output logs server client validation")

    if any(term in lower for term in ["spawn", "colision", "colisión", "collision", "raycast", "terreno", "terrain", "suelo", "placement", "posicion", "posición"]):
        queries.append("Roblox raycast overlap bounds collision spawn placement terrain walkability Workspace GetPartBoundsInBox")

    if any(term in lower for term in ["seguridad", "security", "exploit", "anti cheat", "anticheat", "remoteevent", "remotefunction", "onserverevent", "onserverinvoke"]):
        queries.append("Roblox RemoteEvent RemoteFunction server authoritative validation rate limiting exploit prevention client trust")

    if any(term in lower for term in ["performance", "rendimiento", "lag", "fps", "memoria", "memory", "optimiz", "mobile", "móvil"]):
        queries.append("Roblox performance optimization mobile memory leaks Heartbeat RenderStepped StreamingEnabled RemoteEvent bandwidth")

    if any(term in lower for term in ["monetiz", "gamepass", "developer product", "devproduct", "processreceipt", "premium", "marketplaceservice", "tienda"]):
        queries.append("Roblox monetization MarketplaceService GamePass Developer Product ProcessReceipt Premium payouts PolicyService")

    if any(term in lower for term in ["publicar", "publish", "release", "lanzamiento", "checklist", "producción", "production"]):
        queries.append("Roblox publish checklist DataStore security performance mobile metadata analytics release readiness")

    if any(term in lower for term in ["debug", "debuggear", "error", "stack trace", "traza", "bug", "fallo"]):
        queries.append("Roblox debugging console output stack trace playtest nil reference type mismatch script errors")

    if any(term in lower for term in ["obby", "tycoon", "simulator", "simulador", "rpg", "horror", "terror", "battle royale", "backrooms"]):
        queries.append("Roblox game genre patterns obby tycoon simulator RPG horror battle royale scope checklist")

    expanded = _expand_query_for_rag(query, queries)
    return list(dict.fromkeys(queries + [expanded]))


def _expand_query_for_rag(query: str, additions: list[str]) -> str:
    if not additions:
        return query

    return f"{query}\n\nSearch keywords: {' '.join(additions)}"


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
