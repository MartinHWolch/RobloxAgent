"""File-system scanner: walks directories, identifies Roblox project structure."""

import os
from pathlib import Path

from ..config import EXCLUDED_DIRS, EXCLUDED_EXTENSIONS


SCRIPT_EXTENSIONS = {".lua", ".luau"}
MODEL_EXTENSIONS = {".rbxm", ".rbxmx"}
JSON_EXTENSIONS = {".json"}
CONFIG_FILES = {
    "wally.toml",
    "aftman.toml",
    "rojo.json",
    "rojo.project.json",
    "default.project.json",
    ".luaurc",
    ".editorconfig",
}


def scan_directory(root: str) -> dict:
    """Walk root dir and return a categorized file tree."""
    root = os.path.abspath(root)
    tree = {
        "root": root,
        "scripts": [],
        "models": [],
        "configs": [],
        "json_files": [],
        "directories": [],
        "unknown": [],
        "file_count": 0,
        "dir_count": 0,
    }

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]

        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
        tree["dir_count"] += 1
        tree["directories"].append({
            "path": rel_dir,
            "name": os.path.basename(dirpath) if rel_dir else "",
        })

        for fname in filenames:
            if fname in EXCLUDED_DIRS:
                continue

            ext = os.path.splitext(fname)[1].lower()
            rel_path = os.path.join(rel_dir, fname) if rel_dir else fname
            full_path = os.path.join(dirpath, fname)

            entry = {
                "path": rel_path,
                "name": fname,
                "size": os.path.getsize(full_path),
            }

            if ext in SCRIPT_EXTENSIONS:
                entry["script_type"] = _detect_script_type(fname)
                tree["scripts"].append(entry)
            elif ext in MODEL_EXTENSIONS:
                tree["models"].append(entry)
            elif ext in JSON_EXTENSIONS:
                tree["json_files"].append(entry)
            elif fname in CONFIG_FILES:
                tree["configs"].append(entry)
            elif ext not in EXCLUDED_EXTENSIONS:
                tree["unknown"].append(entry)

            tree["file_count"] += 1

    tree["scripts"].sort(key=lambda x: x["path"])
    tree["models"].sort(key=lambda x: x["path"])
    tree["configs"].sort(key=lambda x: x["path"])
    tree["directories"].sort(key=lambda x: x["path"])

    return tree


def detect_project_framework(tree: dict) -> str | None:
    """Detect framework type from config files and directory structure."""
    config_names = {c["name"] for c in tree["configs"]}

    if "wally.toml" in config_names:
        return "rojo_wally"
    if "rojo.json" in config_names or "default.project.json" in config_names:
        return "rojo"
    if _has_replicated_storage(tree):
        return "default"
    return None


def _detect_script_type(fname: str) -> str:
    """Guess script type from naming conventions."""
    lower = fname.lower()
    if "module" in lower or "service" in lower or "controller" in lower:
        return "ModuleScript"
    if "client" in lower or lower.startswith("gui") or "ui" in lower:
        return "LocalScript"
    if "server" in lower:
        return "Script"
    return "ModuleScript"


def _has_replicated_storage(tree: dict) -> bool:
    top_dirs = {d["name"] for d in tree["directories"] if d["path"] and "/" not in d["path"]}
    return bool(top_dirs & {"ReplicatedStorage", "ServerScriptService", "src"})
