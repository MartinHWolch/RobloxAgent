"""Config file parser: wally.toml, rojo.json, aftman.toml, .luaurc."""

import os
import json
import configparser


def parse_wally_toml(filepath: str) -> dict | None:
    """Parse wally.toml dependency manifest."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        result = {
            "package": {},
            "dependencies": {},
            "server_dependencies": {},
            "dev_dependencies": {},
        }

        section = None
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                continue
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if section == "package":
                    result["package"][key] = value
                elif section == "dependencies":
                    result["dependencies"][key] = value
                elif section == "server-dependencies":
                    result["server_dependencies"][key] = value
                elif section == "dev-dependencies":
                    result["dev_dependencies"][key] = value
                elif section is None and key == "name":
                    result["package"][key] = value

        return result
    except Exception as e:
        return {"error": str(e)}


def parse_rojo_json(filepath: str) -> dict | None:
    """Parse rojo.json or default.project.json."""
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return {
            "name": data.get("name", ""),
            "tree": data.get("tree", data.get("root", {})),
            "serve_port": data.get("servePort"),
            "glob_ignore": data.get("globIgnore", []),
        }
    except Exception as e:
        return {"error": str(e)}


def parse_aftman_toml(filepath: str) -> dict | None:
    """Parse aftman.toml tool manifest."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        tools = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                tools[key.strip()] = value.strip().strip('"').strip("'")

        return {"tools": tools}
    except Exception as e:
        return {"error": str(e)}


def parse_luaurc(filepath: str) -> dict | None:
    """Parse .luaurc configuration."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def parse_configs(config_files: list[dict], root: str) -> dict:
    """Parse all discovered config files."""
    configs = {}
    for entry in config_files:
        full_path = os.path.join(root, entry["path"])
        name = entry["name"]

        if name == "wally.toml":
            configs["wally"] = parse_wally_toml(full_path)
        elif name in ("rojo.json", "default.project.json", "rojo.project.json"):
            configs["rojo"] = parse_rojo_json(full_path)
        elif name == "aftman.toml":
            configs["aftman"] = parse_aftman_toml(full_path)
        elif name == ".luaurc":
            configs["luaurc"] = parse_luaurc(full_path)

    return configs
