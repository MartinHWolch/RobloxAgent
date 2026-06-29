"""Orchestrator CLI: interactive REPL and single-query mode."""

import sys
import argparse
from pathlib import Path

try:
    import readline
except ImportError:
    pass

from .agent import process_query
from .config import PROJECT_ROOT


def main_cli():
    parser = argparse.ArgumentParser(description="RobloxAgent Orchestrator")
    parser.add_argument("query", nargs="*", help="Query to process (omit for interactive REPL)")
    parser.add_argument("-p", "--project", help="Path to Roblox project to index")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show query debug info")

    args = parser.parse_args()

    project_path = _resolve_project(args.project)

    if args.query:
        query = " ".join(args.query)
        result = process_query(query, project_path)
        _print_result(result, args.verbose)
    else:
        _repl(project_path, args.verbose)


def _repl(project_path: str | None, verbose: bool):
    print("RobloxAgent Orchestrator")
    print("=" * 50)
    if project_path:
        print(f"Project: {project_path}")
    print("Type 'exit' or 'quit' to quit, '/help' for commands")
    print()

    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            break
        if query.lower() in ("/help", "/h"):
            _print_help()
            continue
        if query.lower() == "/project":
            print(f"Project path: {project_path or '(none set)'}")
            continue

        if query.startswith("/project "):
            project_path = _resolve_project(query[9:])
            print(f"Project set to: {project_path}")
            continue

        result = process_query(query, project_path)
        _print_result(result, verbose)


def _print_result(result: dict, verbose: bool):
    if verbose:
        intents_str = " | ".join(f"{i['intent']} ({i['confidence']:.0%})" for i in result["intents"][:3])
        print(f"[Intents: {intents_str}]")
        rc = result["rag_count"]
        rls = result["rules_count"]
        cc = result["cases_count"]
        hp = result["has_project"]
        print(f"[RAG: {rc} items | Rules: {rls} | Cases: {cc} | Project: {hp}]")
        print()

    print(result["response"])
    print()


def _print_help():
    print("Commands:")
    print("  /help, /h       Show this help")
    print("  /project <path> Set project path for context")
    print("  /project        Show current project path")
    print("  exit, quit      Exit")
    print()


def _resolve_project(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if p.is_absolute():
        return str(p)
    return str(Path.cwd() / p)


if __name__ == "__main__":
    main_cli()
