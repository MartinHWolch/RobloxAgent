"""Document chunker: splits knowledge base items into searchable chunks."""

import re
import json
import os
from typing import Any

from .config import KB_SOURCES, CHUNK_MAX_SIZE, CHUNK_OVERLAP


def load_all_kb_items() -> list[dict]:
    items = []
    for source_name, filepath in KB_SOURCES.items():
        if not os.path.isfile(filepath):
            continue
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        items_list = data.get("items", data if isinstance(data, list) else [])
        for item in items_list:
            item["_source"] = source_name
            items.append(item)
    return items


def chunk_document(item: dict) -> list[dict]:
    source = item.get("_source", "unknown")
    source_name = source

    if source == "engine_api":
        return _chunk_engine_api(item)
    elif source == "creator_hub":
        return _chunk_creator_hub(item)
    elif source == "devforum":
        return _chunk_devforum(item)
    elif source == "github":
        return _chunk_github(item)
    elif source == "examples":
        return _chunk_examples(item)
    else:
        return _generic_chunk(item, source_name)


def _chunk_engine_api(item: dict) -> list[dict]:
    chunks = []
    name = item.get("name", item.get("title", "Unknown"))
    item_type = item.get("type", "class")
    description = item.get("description", "")
    category_name = item.get("category", name)

    intro_ns = f"{item_type}: {name}"
    parts = [intro_ns]
    if description:
        parts.append(description)

    props = item.get("properties", [])
    if props:
        prop_texts = []
        for p in props:
            pname = p.get("name", "")
            ptype = p.get("meta", {}).get("type", "any")
            pdesc = p.get("description", "").strip()
            parts.append(f"Property {name}.{pname}: {ptype} — {pdesc or 'No description'}")

    methods = item.get("methods", [])
    if methods:
        for m in methods:
            mname = m.get("name", "")
            msig = m.get("signature", mname)
            mdesc = m.get("description", "").strip()
            parts.append(f"Method {name}:{mname} — signature: {msig} — {mdesc or 'No description'}")

    events = item.get("events", [])
    if events:
        for e in events:
            ename = e.get("name", "")
            edesc = e.get("description", "").strip()
            parts.append(f"Event {name}.{ename} — {edesc or 'No description'}")

    text = "\n".join(parts)
    return _split_chunks(text, {
        "source": "engine_api",
        "category": category_name,
        "name": name,
        "type": item_type,
    })


def _chunk_creator_hub(item: dict) -> list[dict]:
    title = item.get("title", item.get("name", "Unknown"))
    description = item.get("description", "")
    content = item.get("content", "")
    category_name = item.get("category", title)

    parts = [f"Title: {title}"]
    if description:
        parts.append(f"Description: {description}")
    parts.append(content)

    text = "\n".join(parts)
    return _split_chunks(text, {
        "source": "creator_hub",
        "category": category_name,
        "name": title,
        "type": "guide",
    })


def _chunk_devforum(item: dict) -> list[dict]:
    title = item.get("title", "Untitled")
    content = item.get("content", "")
    raw = item.get("raw", "")
    category_raw = item.get("category_raw", item.get("category", "General"))
    likes = item.get("likes", 0)
    posts = item.get("posts", 0)

    header = f"Title: {title}\nCategory: {category_raw}\nLikes: {likes} | Replies: {posts}"
    body = content or raw

    text = f"{header}\n\n{body}"
    return _split_chunks(text, {
        "source": "devforum",
        "category": category_raw,
        "name": title,
        "type": "topic",
    })


def _chunk_github(item: dict) -> list[dict]:
    full_name = item.get("full_name", item.get("name", "Unknown"))
    description = item.get("description", "")
    readme = item.get("readme", "")
    stars = item.get("stars", 0)
    language = item.get("language", "Unknown")

    parts = [
        f"Repository: {full_name}",
        f"Stars: {stars} | Language: {language}",
    ]
    if description:
        parts.append(f"Description: {description}")
    if readme:
        parts.append(readme)

    text = "\n\n".join(parts)
    return _split_chunks(text, {
        "source": "github",
        "category": "code",
        "name": full_name,
        "type": "repository",
    })


def _chunk_examples(item: dict) -> list[dict]:
    category_name = item.get("category", "Example")
    description = item.get("description", "")
    architecture = item.get("architecture", "")
    code = item.get("code_example", "")
    best_practices = item.get("best_practices", "")

    parts = [f"Category: {category_name}"]
    if description:
        parts.append(f"Description: {description}")
    if architecture:
        parts.append(f"Architecture: {architecture}")
    if code:
        parts.append(f"Code:\n{code}")
    if best_practices:
        parts.append(f"Best Practices: {best_practices}")

    text = "\n\n".join(parts)
    return _split_chunks(text, {
        "source": "examples",
        "category": category_name,
        "name": f"Example: {category_name}",
        "type": "example",
    })


def _generic_chunk(item: dict, source_name: str) -> list[dict]:
    text = json.dumps(item, ensure_ascii=False)
    name = item.get("name", item.get("title", "Unknown"))
    return _split_chunks(text, {
        "source": source_name,
        "category": source_name,
        "name": name,
        "type": "generic",
    })


def _split_chunks(text: str, metadata: dict) -> list[dict]:
    if not text.strip():
        return [{"text": "", "metadata": metadata}]

    if len(text) <= CHUNK_MAX_SIZE:
        return [{"text": text, "metadata": metadata}]

    chunks = []
    sections = re.split(r"(?=^#{1,3}\s|\n#{1,3}\s|\n---\n)", text, flags=re.MULTILINE)

    if len(sections) <= 1:
        sections = re.split(r"\n\n+", text)

    current = ""
    for section in sections:
        if not section.strip():
            continue
        if len(current) + len(section) > CHUNK_MAX_SIZE and current:
            chunks.append(current.strip())
            current = section
        else:
            if current:
                current += "\n\n"
            current += section

    if current:
        chunks.append(current.strip())

    if len(chunks) <= 1:
        words = text.split()
        chunks = []
        for i in range(0, len(words), 250):
            chunk = " ".join(words[i:i + 250 + CHUNK_OVERLAP // 4])
            chunks.append(chunk)

    return [{"text": c, "metadata": {**metadata}} for c in chunks if c.strip()]


def index_all() -> list[dict]:
    chunks = []
    items = load_all_kb_items()
    print(f"Loading {len(items)} items from knowledge base...")

    counter = 0
    for item in items:
        item_chunks = chunk_document(item)
        for c in item_chunks:
            c["metadata"]["id"] = _make_id(c["text"], c["metadata"], counter)
            counter += 1
        chunks.extend(item_chunks)

    print(f"Generated {len(chunks)} chunks total")
    return chunks


def _make_id(text: str, metadata: dict, counter: int) -> str:
    import hashlib
    raw = f"{metadata.get('source', '')}:{metadata.get('name', '')}:{counter}:{text[:30]}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]
