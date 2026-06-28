"""RAG CLI: index knowledge base and run queries."""

import sys
import json
import argparse

from .retriever import build_index, retrieve, format_retrieval
from .store import count, reset as reset_store


def main_cli():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="RAG pipeline for Roblox knowledge base")
    sub = parser.add_subparsers(dest="command", required=True)

    index_parser = sub.add_parser("index", help="Build/rebuild vector index")
    index_parser.add_argument("--force", action="store_true", help="Rebuild from scratch")
    index_parser.add_argument("--stats", action="store_true", help="Show stats after indexing")

    query_parser = sub.add_parser("query", help="Search the knowledge base")
    query_parser.add_argument("query", nargs="+", help="Search query")
    query_parser.add_argument("-k", "--top-k", type=int, default=10, help="Number of results")
    query_parser.add_argument("--source", help="Filter by source (engine_api, devforum, etc.)")
    query_parser.add_argument("--category", help="Filter by category")
    query_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    query_parser.add_argument("--score", action="store_true", help="Show relevance scores")

    stats_parser = sub.add_parser("stats", help="Show index statistics")

    reset_parser = sub.add_parser("reset", help="Delete all indexed data")

    args = parser.parse_args()

    if args.command == "index":
        total = build_index(force_rebuild=args.force)
        print(f"Indexed {total} chunks")
        if args.stats:
            print(f"Total vectors in DB: {count()}")

    elif args.command == "query":
        query = " ".join(args.query)
        results = retrieve(
            query,
            top_k=args.top_k,
            filter_source=args.source,
            filter_category=args.category,
        )
        if args.json:
            json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
        else:
            print(format_retrieval(results, include_score=args.score))

    elif args.command == "stats":
        total = count()
        print(f"Total indexed chunks: {total}")

    elif args.command == "reset":
        reset_store()
        print("Index reset complete")


if __name__ == "__main__":
    main_cli()
