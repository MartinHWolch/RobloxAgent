"""High-level retriever with optional re-ranking and formatting."""

from typing import Any

from .store import search, count, reset as reset_store
from .chunker import index_all
from .store import insert_chunks


def build_index(force_rebuild: bool = False) -> int:
    if force_rebuild:
        reset_store()

    existing = count()
    if existing > 0 and not force_rebuild:
        return existing

    chunks = index_all()
    insert_chunks(chunks)
    return len(chunks)


def retrieve(
    query: str,
    top_k: int = 10,
    filter_source: str | None = None,
    filter_category: str | None = None,
) -> list[dict[str, Any]]:
    results = search(
        query=query,
        top_k=top_k,
        filter_source=filter_source,
        filter_category=filter_category,
    )
    return results


def _sanitize(text: str) -> str:
    try:
        text.encode("cp1252")
        return text
    except UnicodeEncodeError:
        return text.encode("cp1252", errors="replace").decode("cp1252")


def format_retrieval(results: list[dict], include_score: bool = False) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        meta = r["metadata"]
        header = f"[{i}] {meta.get('source', '?')}: {meta.get('name', meta.get('category', '?'))}"
        if include_score:
            header += f" (score: {r['score']:.3f})"
        lines.append(_sanitize(header))
        lines.append("-" * 60)
        lines.append(_sanitize(r["text"][:2000]))
        lines.append("")
    return "\n".join(lines)
