"""Dependency graph: resolves require() calls to file paths and builds a graph."""

import os


def resolve_dependencies(scripts: list[dict], root: str) -> dict:
    """Build a dependency graph from parsed scripts."""
    nodes = {}
    edges = []
    unresolved = []
    cycles = []

    service_dir_map = _build_service_dir_map(root)

    for script in scripts:
        rel_path = script["path"]
        node_id = _node_id(rel_path)
        nodes[node_id] = {
            "id": node_id,
            "path": rel_path,
            "name": script["name"],
            "requires_count": len(script["requires"]),
        }

        script_full = os.path.join(root, rel_path)
        script_dir = os.path.dirname(script_full)

        for req in script["requires"]:
            raw_path = req["path"]
            target = _resolve_path(raw_path, script_dir, root, service_dir_map)
            if target:
                target_rel = os.path.relpath(target, root)
                edges.append({
                    "source": node_id,
                    "target": _node_id(target_rel),
                    "raw": req["raw"],
                })
            else:
                unresolved.append({
                    "source": node_id,
                    "raw": req["raw"],
                    "attempted_path": raw_path,
                })

    adj = _build_adjacency(edges)
    for node_id in nodes:
        visited = set()
        stack = []
        if _detect_cycle(node_id, adj, visited, stack):
            cycles.append(list(stack))

    in_degree = {}
    out_degree = {}
    for node_id in nodes:
        in_degree[node_id] = 0
        out_degree[node_id] = 0
    for e in edges:
        out_degree[e["source"]] = out_degree.get(e["source"], 0) + 1
        in_degree[e["target"]] = in_degree.get(e["target"], 0) + 1

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "unresolved": unresolved,
        "cycles": cycles,
        "roots": [nid for nid, d in in_degree.items() if d == 0],
        "leaves": [nid for nid, d in out_degree.items() if d == 0],
        "max_depth": _max_depth(edges, nodes),
    }


def _build_service_dir_map(root: str) -> dict[str, str]:
    """Map Roblox service names to their actual directory paths."""
    service_dirs = {}
    for dirpath, dirnames, _ in os.walk(root):
        for d in dirnames:
            service_dirs[d] = os.path.join(dirpath, d)
    return service_dirs


def _node_id(rel_path: str) -> str:
    return rel_path.replace("\\", "/")


def _resolve_path(req_path: str, script_dir: str, root: str, service_dir_map: dict) -> str | None:
    """Resolve a require() path to an actual file on disk.

    Handles:
      - script.Parent.X -> look in parent dir
      - X/Y/Z -> direct relative path
      - ReplicatedStorage.X -> look in ReplicatedStorage dir
      - plain names like 'DataService' -> scan nearby
    """
    candidates = _generate_candidates(req_path, script_dir, root, service_dir_map)
    for candidate in candidates:
        if os.path.isfile(candidate):
            candidate_lower = candidate.lower()
            if candidate_lower.endswith(".lua") or candidate_lower.endswith(".luau"):
                return candidate
        for ext in (".lua", ".luau", ".lua.luau"):
            with_ext = candidate + ext
            if os.path.isfile(with_ext):
                return with_ext
    return None


def _generate_candidates(req_path: str, script_dir: str, root: str, service_dir_map: dict) -> list[str]:
    """Generate possible file paths for a require target."""
    candidates = []
    parts = req_path.replace("\\", "/").split("/")
    name = parts[-1]

    rel_name = name
    if "." in name:
        rel_name = name.rsplit(".", 1)[-1]

    candidates.append(os.path.join(script_dir, rel_name))
    candidates.append(os.path.join(script_dir, name))

    if parts[0] in service_dir_map:
        base = service_dir_map[parts[0]]
        rest = parts[1:]
        if rest:
            candidates.append(os.path.join(base, *rest))
            candidates.append(os.path.join(base, *rest, rest[-1]))
        else:
            candidates.append(base)
    else:
        for svc_dir in service_dir_map.values():
            candidates.append(os.path.join(svc_dir, name))
            candidates.append(os.path.join(svc_dir, *parts))

    parent_count = req_path.count("Parent")
    base_dir = script_dir
    for _ in range(parent_count):
        base_dir = os.path.dirname(base_dir)

    if parent_count > 0:
        clean_parts = [p for p in parts if p != "Parent"]
        if clean_parts:
            candidates.append(os.path.join(base_dir, *clean_parts))

    candidates.append(os.path.join(root, name))
    candidates.append(os.path.join(root, *parts))

    return candidates


def _build_adjacency(edges: list[dict]) -> dict[str, list[str]]:
    adj = {}
    for e in edges:
        adj.setdefault(e["source"], []).append(e["target"])
    return adj


def _detect_cycle(node: str, adj: dict, visited: set, stack: list) -> bool:
    if node in stack:
        return True
    if node in visited:
        return False
    visited.add(node)
    stack.append(node)
    for neighbor in adj.get(node, []):
        if _detect_cycle(neighbor, adj, visited, stack):
            return True
    stack.pop()
    return False


def _max_depth(edges: list[dict], nodes: dict) -> int:
    if not edges:
        return 0
    from collections import defaultdict
    adj = defaultdict(list)
    for e in edges:
        adj[e["source"]].append(e["target"])
    memo = {}

    def dfs(nid):
        if nid in memo:
            return memo[nid]
        best = 0
        for nb in adj.get(nid, []):
            best = max(best, 1 + dfs(nb))
        memo[nid] = best
        return best

    depths = [dfs(nid) for nid in nodes]
    return max(depths) if depths else 0
