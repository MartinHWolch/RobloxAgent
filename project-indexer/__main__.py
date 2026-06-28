"""Project Indexer CLI — indexes a Roblox project into structured JSON."""

import os
import sys
import json
import argparse
from datetime import datetime

from .config import ROBLOX_SERVICES
from .scanners.filesystem import scan_directory, detect_project_framework
from .scanners.scripts import parse_script
from .scanners.configs import parse_configs
from .scanners.deps import resolve_dependencies


def index_project(root: str) -> dict:
    """Index a Roblox project and return the full index."""
    root = os.path.abspath(root)

    tree = scan_directory(root)
    framework = detect_project_framework(tree)

    scripts = []
    for entry in tree["scripts"]:
        full_path = os.path.join(root, entry["path"])
        try:
            parsed = parse_script(full_path)
            parsed["path"] = entry["path"]
            parsed["size"] = entry["size"]
            scripts.append(parsed)
        except Exception as e:
            scripts.append({
                "path": entry["path"],
                "name": entry["name"],
                "error": str(e),
            })

    configs = parse_configs(tree["configs"], root)

    graph = resolve_dependencies(scripts, root)

    all_services = set()
    for s in scripts:
        for svc in s.get("services", []):
            all_services.add(svc["service"])

    code_lines = sum(s.get("code_lines", 0) for s in scripts if "code_lines" in s)
    comment_lines = sum(s.get("comment_lines", 0) for s in scripts if "comment_lines" in s)

    index = {
        "project": {
            "name": os.path.basename(root),
            "root": root,
            "framework": framework,
            "indexed_at": datetime.utcnow().isoformat() + "Z",
        },
        "structure": tree,
        "scripts": scripts,
        "configs": configs,
        "graph": graph,
        "summary": {
            "total_files": tree["file_count"],
            "total_dirs": tree["dir_count"],
            "total_scripts": len(tree["scripts"]),
            "total_models": len(tree["models"]),
            "scripts_with_errors": sum(1 for s in scripts if "error" in s),
            "total_code_lines": code_lines,
            "total_comment_lines": comment_lines,
            "total_requires": sum(len(s.get("requires", [])) for s in scripts),
            "total_service_refs": len(all_services),
            "services_used": sorted(all_services),
            "unresolved_requires": len(graph["unresolved"]),
            "dependency_cycles": len(graph["cycles"]),
        },
    }

    return index


def main_cli():
    parser = argparse.ArgumentParser(
        description="Index a Roblox project for the AI agent.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the Roblox project root (default: current dir)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (default: <project_name>_index.json in current dir)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: true)",
    )

    args = parser.parse_args()
    root = os.path.abspath(args.path)

    if not os.path.isdir(root):
        print(f"Error: path does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    print(f"Indexing Roblox project: {root}")
    result = index_project(root)

    output_path = args.output
    if not output_path:
        project_name = os.path.basename(root)
        output_path = os.path.join(os.getcwd(), f"{project_name}_index.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2 if args.pretty else None, ensure_ascii=False)

    s = result["summary"]
    print(f"Done. Output: {output_path}")
    print(f"  {s['total_scripts']} scripts ({s['total_code_lines']} code lines, "
          f"{s['total_comment_lines']} comment lines)")
    print(f"  {s['total_requires']} require() calls, {s['unresolved_requires']} unresolved")
    print(f"  {s['dependency_cycles']} dependency cycles")
    print(f"  {s['total_service_refs']} unique services referenced")
    print(f"  Framework: {result['project']['framework']}")


if __name__ == "__main__":
    main_cli()
