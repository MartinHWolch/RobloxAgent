"""Script parser: extracts requires, services, exports, and metadata from Lua/Luau."""

import re
import os


_REQUIRE_PATTERN = re.compile(
    r"(?:local\s+(\w+)\s*=\s*)?"  # optional local binding
    r"require\([^)]*?(?:game|script|ReplicatedStorage|ServerStorage|ServerScriptService|StarterPlayer|StarterGui|StarterPack|ReplicatedFirst|Players)"
    r'\[?"([^"]+)"\]?|\.([^)]+)[^)]*\)',
)

_REQUIRE_SIMPLE = re.compile(r"require\([^)]+\)")

_GET_SERVICE = re.compile(r'game:\s*GetService\s*\(\s*"(\w+)"\s*\)')

_LOCAL_BIND = re.compile(r"local\s+(\w+)\s*=\s*(.+)")

_EXPORT_RETURN = re.compile(
    r"return\s*\{",
    re.MULTILINE,
)

_ATTRIBUTE_DECL = re.compile(
    r'(?:Instance|script|obj)\s*:\s*SetAttribute\s*\(\s*"(\w+)"\s*,\s*(.+?)\s*\)',
)

_TAG_COMMENT = re.compile(r"--\s*@(\w[\w.]*)\s*(.*)")

_FUNCTION_DECL = re.compile(
    r"(?:export\s+)?(?:function\s+(\w+)\.?(\w*))\s*\(",
)

_CLASS_METHOD = re.compile(
    r"function\s+(\w+):(\w+)\s*\(",
)

_STRICT_MARKER = re.compile(r"--!strict")
_OPTIMIZE_MARKER = re.compile(r"--!optimize")


def parse_script(filepath: str) -> dict:
    """Parse a Lua/Luau script and extract structured metadata."""
    with open(filepath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.splitlines()
    rel_path = filepath  # caller should normalize

    result = {
        "path": rel_path,
        "name": os.path.basename(filepath),
        "total_lines": len(lines),
        "code_lines": sum(1 for l in lines if l.strip() and not l.strip().startswith("--")),
        "comment_lines": sum(1 for l in lines if l.strip().startswith("--")),
        "blank_lines": sum(1 for l in lines if not l.strip()),
        "requires": _extract_requires(content),
        "services": _extract_services(content),
        "exports": _extract_exports(content),
        "functions": _extract_functions(content),
        "attributes": _extract_attributes(content),
        "tags": _extract_tags(content),
        "has_strict": bool(_STRICT_MARKER.search(content)),
        "has_optimize": bool(_OPTIMIZE_MARKER.search(content)),
        "is_module": module_like(content),
    }

    return result


def _extract_requires(content: str) -> list[dict]:
    """Extract all require() calls with their bindings."""
    requires = []
    for match in _REQUIRE_SIMPLE.finditer(content):
        full = match.group(0)
        requires.append({
            "raw": full,
            "path": _resolve_require_path(full),
        })
    return requires


_SCRIPT_DOT = re.compile(r"(?:script|game)\..+?([\w.]+)\s*\)")


def _resolve_require_path(raw: str) -> str:
    """Extract required module identifier from a require() call.

    Handles:
      require(ReplicatedStorage.X.Y)
      require(script.Parent.X)
      require(script.Parent.Parent.X.Y)
      require(game:GetService("X").Y)
    """
    inner = raw[len("require("):-len(")")].strip()

    string_m = re.search(r'"([^"]+)"', inner)
    if string_m:
        return string_m.group(1)

    path_parts = re.split(r'[.](?=[A-Z])', inner)
    path_parts = [p for p in path_parts if re.match(r'^[A-Z]', p)]

    if not path_parts:
        path_parts = re.findall(r'[\w.]+', inner)
        path_parts = [p for p in path_parts if p not in ("game", "script", "Parent")]

    if path_parts:
        return "/".join(path_parts)

    return inner


_REQUIRE_BINDING = re.compile(
    r"local\s+(\w+)\s*=\s*require\s*\(\s*([^)]+?)\s*\)",
)


def _extract_services(content: str) -> list[dict]:
    """Extract game:GetService calls with their variable bindings."""
    services = []
    for match in _GET_SERVICE.finditer(content):
        service_name = match.group(1)
        line_start = content.rfind("\n", 0, match.start()) + 1
        line_end = content.find("\n", match.end())
        line = content[line_start:line_end if line_end != -1 else len(content)].strip()
        services.append({
            "service": service_name,
            "line": line,
        })
    return services


def _extract_exports(content: str) -> dict:
    """Extract module export patterns."""
    exports = {
        "returns_table": bool(_EXPORT_RETURN.search(content)),
        "export_types": [],
        "export_functions": [],
    }

    for m in re.finditer(r"export\s+type\s+(\w+)", content):
        exports["export_types"].append(m.group(1))

    for m in re.finditer(r"export\s+function\s+(\w+)", content):
        exports["export_functions"].append(m.group(1))

    return exports


def _extract_functions(content: str) -> list[dict]:
    """Extract function declarations (both local and global)."""
    functions = []

    for m in _CLASS_METHOD.finditer(content):
        functions.append({
            "name": f"{m.group(1)}:{m.group(2)}",
            "type": "method",
        })

    for m in _FUNCTION_DECL.finditer(content):
        if m.group(2):
            name = f"{m.group(1)}.{m.group(2)}"
        else:
            name = m.group(1)
        functions.append({
            "name": name,
            "type": "function",
        })

    return functions


def _extract_attributes(content: str) -> list[dict]:
    """Extract Instance:SetAttribute(...) calls."""
    attributes = []
    for m in _ATTRIBUTE_DECL.finditer(content):
        attributes.append({
            "name": m.group(1),
            "value_raw": m.group(2).strip(),
        })
    return attributes


def _extract_tags(content: str) -> list[dict]:
    """Extract -- @tag comments (used for CollectionService tags)."""
    tags = []
    for m in _TAG_COMMENT.finditer(content):
        tag_type = m.group(1)
        tag_value = m.group(2).strip()
        if tag_type == "tag":
            tags.append(tag_value)  # CollectionService tag
        else:
            tags.append(f"{tag_type}:{tag_value}" if tag_value else tag_type)
    return tags


def module_like(content: str) -> bool:
    """Heuristic: does this look like a ModuleScript?"""
    markers = 0
    if _EXPORT_RETURN.search(content):
        markers += 1
    if re.search(r"local module\s*=", content):
        markers += 1
    if "require(" in content:
        markers += 1
    if "module.exports" in content:
        markers += 1
    if re.search(r"local \w+ = \{\}", content) and "return" in content:
        markers += 1
    return markers >= 2
