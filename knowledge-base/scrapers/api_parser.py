import re
import json
from typing import Any


def parse_api_markdown(text: str) -> dict[str, Any]:
    sections = {
        "properties": [],
        "methods": [],
        "events": [],
        "callbacks": [],
        "enums": [],
    }

    frontmatter = _parse_frontmatter(text)
    body = _strip_frontmatter(text)

    current_section = None
    current_item_buffer = []
    current_item_heading = None

    lines = body.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()

        if line.startswith("## "):
            _flush_item(current_section, current_item_heading, current_item_buffer, sections)
            current_item_buffer = []
            current_item_heading = None
            section_name = line[3:].strip().lower()
            if section_name.startswith("propert"):
                current_section = "properties"
            elif section_name.startswith("method"):
                current_section = "methods"
            elif section_name.startswith("event"):
                current_section = "events"
            elif section_name.startswith("callback"):
                current_section = "callbacks"
            elif section_name.startswith("enum"):
                current_section = "enums"
            else:
                current_section = None
            continue

        if line.startswith("### ") and current_section:
            _flush_item(current_section, current_item_heading, current_item_buffer, sections)
            current_item_heading = line
            current_item_buffer = []
            continue

        if current_item_heading is not None:
            current_item_buffer.append(line)

    _flush_item(current_section, current_item_heading, current_item_buffer, sections)

    return {
        "frontmatter": frontmatter,
        "sections": sections,
    }


def _flush_item(section: str | None, heading: str | None, buffer: list[str], sections: dict):
    if not section or not heading:
        return
    item = _parse_item(heading, buffer)
    if item:
        sections[section].append(item)


def _parse_frontmatter(text: str) -> dict[str, Any]:
    fm = {}
    if not text.startswith("---"):
        return fm
    end = text.find("---", 3)
    if end == -1:
        return fm
    block = text[3:end]
    for line in block.strip().split("\n"):
        if ": " in line:
            key, val = line.split(": ", 1)
            key = key.strip()
            val = val.strip().strip("\"'")
            if val.startswith("[") or val.startswith("-"):
                fm[key] = _parse_yaml_list(block, key)
            else:
                fm[key] = val
    return fm


def _parse_yaml_list(block: str, key: str) -> list[str]:
    items = []
    lines = block.split("\n")
    in_list = False
    for line in lines:
        if line.strip() == f"{key}:":
            in_list = True
            continue
        if in_list:
            stripped = line.strip()
            if stripped.startswith("- "):
                items.append(stripped[2:].strip())
            elif stripped and not stripped.startswith(" "):
                break
    return items


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text


def _parse_item(heading: str, buffer: list[str]) -> dict[str, Any] | None:
    name_match = re.match(
        r"^### (Property|Method|Event|Callback|Enum):\s*([^(]+)(?:\(([^)]*)\))?",
        heading,
    )
    if not name_match:
        name_match = re.match(r"^### (Deprecated )?(Property|Method|Event|Callback|Enum):\s*(.+)", heading)
        if not name_match:
            return None
        item_type = name_match.group(2).lower()
        name = name_match.group(3).strip()
        signature = ""
    else:
        item_type = name_match.group(1).lower()
        name = name_match.group(2).strip()
        signature = name_match.group(3) or ""

    buffer_text = "\n".join(buffer)

    json_meta = {}
    json_match = re.search(r"```json\n(.+?)\n```", buffer_text, re.DOTALL)
    if json_match:
        try:
            json_meta = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
        desc_text = buffer_text[:json_match.start()] + buffer_text[json_match.end():]
    else:
        desc_text = buffer_text

    desc_text = re.sub(r"^```[\w]*\n", "", desc_text.strip())
    desc_text = re.sub(r"\n```", "", desc_text)
    desc_text = re.sub(r"\n+", "\n", desc_text).strip()

    return {
        "name": name,
        "type": item_type,
        "signature": signature,
        "meta": json_meta,
        "description": desc_text[:2000],
    }
