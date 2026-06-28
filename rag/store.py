"""Vector store using ChromaDB with local persistence."""

import os
import shutil
from typing import Any

import chromadb
from chromadb.config import Settings

from .config import CHROMA_DB_DIR, DEFAULT_TOP_K
from .embeddings import embed_texts, embed_query


_COLLECTION_NAME = "robux_kb"

_client = None
_collection = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DB_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = _get_client()
        existing = [c.name for c in client.list_collections()]
        if _COLLECTION_NAME in existing:
            _collection = client.get_collection(_COLLECTION_NAME)
        else:
            _collection = client.create_collection(
                _COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
    return _collection


def insert_chunks(chunks: list[dict], batch_size: int = 100):
    col = get_collection()

    ids = []
    texts = []
    metadatas = []

    for chunk in chunks:
        chunk_id = chunk.get("id") or chunk["metadata"].get("id", "")
        if not chunk_id:
            import hashlib
            chunk_id = hashlib.md5((str(id(chunk)) + chunk["text"][:50]).encode()).hexdigest()[:16]

        ids.append(chunk_id)
        texts.append(chunk["text"])
        metadatas.append(chunk["metadata"])

    for i in range(0, len(ids), batch_size):
        batch_end = min(i + batch_size, len(ids))
        batch_ids = ids[i:batch_end]
        batch_texts = texts[i:batch_end]
        batch_metas = metadatas[i:batch_end]

        embeddings = embed_texts(batch_texts)

        col.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_texts,
            metadatas=batch_metas,
        )


def search(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    filter_source: str | None = None,
    filter_category: str | None = None,
) -> list[dict[str, Any]]:
    col = get_collection()
    query_emb = embed_query(query)

    where_clause = {}
    if filter_source:
        where_clause["source"] = filter_source
    if filter_category:
        where_clause["category"] = filter_category

    results = col.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        where=where_clause or None,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    if results["ids"]:
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1.0 - results["distances"][0][i],
            })

    return output


def count() -> int:
    col = get_collection()
    return col.count()


def reset():
    global _collection
    client = _get_client()
    try:
        client.delete_collection(_COLLECTION_NAME)
    except Exception:
        pass
    _collection = None
    if os.path.isdir(CHROMA_DB_DIR):
        shutil.rmtree(CHROMA_DB_DIR)
