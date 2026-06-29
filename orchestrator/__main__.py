"""Orchestrator CLI: interactive REPL and single-query mode."""

import sys
import argparse

try:
    import readline
except ImportError:
    pass

from .agent import process_query


def main_cli():
    parser = argparse.ArgumentParser(description="RobloxAgent Orchestrator")
    parser.add_argument("query", nargs="*", help="Query to process (omit for interactive REPL)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show query debug info")

    args = parser.parse_args()

    if args.query:
        query = " ".join(args.query)
        result = process_query(query)
        _print_result(result, args.verbose)
    else:
        _repl(args.verbose)


def _repl(verbose: bool):
    print("RobloxAgent Orchestrator")
    print("=" * 50)
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

        result = process_query(query)
        _print_result(result, verbose)


def _print_result(result: dict, verbose: bool):
    if verbose:
        intents_str = " | ".join(f"{i['intent']} ({i['confidence']:.0%})" for i in result["intents"][:3])
        print(f"[Intents: {intents_str}]")
        rc = result["rag_count"]
        rls = result["rules_count"]
        cc = result["cases_count"]
        print(f"[RAG: {rc} items | Rules: {rls} | Cases: {cc}]")
        print()

    print(result["response"])
    print()


def _print_help():
    print("Commands:")
    print("  /help, /h       Show this help")
    print("  exit, quit      Exit")
    print()


if __name__ == "__main__":
    main_cli()
