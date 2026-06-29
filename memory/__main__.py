"""Memory CLI: manage project rules, resolved cases, and session context."""

import sys
import json
import argparse

from .store import close
from .rules import add_rule, get_rule, list_rules, search_rules, update_rule, delete_rule, count_rules
from .cases import add_case, get_case, list_cases, search_cases, delete_case, count_cases
from .session import get_session, set_task, add_query, add_active_file, set_summary, set_goal, clear_session


def main_cli():
    parser = argparse.ArgumentParser(description="Memory module for RobloxAgent")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- rules ---
    r = sub.add_parser("rules", help="Manage project rules")
    r.add_argument("action", choices=["add", "get", "list", "search", "update", "delete", "count"])
    r.add_argument("--key", help="Rule key")
    r.add_argument("--value", help="Rule value")
    r.add_argument("--category", default="practices", help="Rule category")
    r.add_argument("--desc", default="", help="Rule description")
    r.add_argument("--priority", type=int, default=5, help="Priority (0-10)")
    r.add_argument("--query", help="Search query (for search action)")
    r.add_argument("--json", action="store_true", help="Output raw JSON")

    # --- cases ---
    c = sub.add_parser("cases", help="Manage resolved cases")
    c.add_argument("action", choices=["add", "get", "list", "search", "delete", "count"])
    c.add_argument("--id", type=int, help="Case ID")
    c.add_argument("--title", help="Case title")
    c.add_argument("--problem", help="Problem summary")
    c.add_argument("--solution", help="Solution summary")
    c.add_argument("--files", help="Files changed (comma-separated)")
    c.add_argument("--patterns", help="Patterns used (comma-separated)")
    c.add_argument("--tags", help="Tags (comma-separated)")
    c.add_argument("--outcome", default="success", help="Outcome: success/partial/failure")
    c.add_argument("--tag", help="Filter by tag")
    c.add_argument("--query", help="Search query")
    c.add_argument("--limit", type=int, default=50)
    c.add_argument("--offset", type=int, default=0)
    c.add_argument("--json", action="store_true", help="Output raw JSON")

    # --- session ---
    s = sub.add_parser("session", help="Manage session context")
    s.add_argument("action", choices=["get", "task", "query", "file", "summary", "goal", "clear"])
    s.add_argument("--value", help="Value to set")
    s.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    try:
        if args.command == "rules":
            _handle_rules(args)
        elif args.command == "cases":
            _handle_cases(args)
        elif args.command == "session":
            _handle_session(args)
    finally:
        close()


def _handle_rules(args):
    if args.action == "add":
        r = add_rule(args.key, args.value, args.category, args.desc, args.priority)
        print(f"Rule added: {r['key']} = {r['value']}")

    elif args.action == "get":
        r = get_rule(args.key)
        if not r:
            print(f"Rule not found: {args.key}")
            return
        _print_rule(r, args.json)

    elif args.action == "list":
        rules = list_rules(args.category if args.category != "practices" else None)
        if args.json:
            json.dump(rules, sys.stdout, indent=2, ensure_ascii=False)
        else:
            for r in rules:
                print(f"  [{r['category']:15s}] {r['key']:40s} = {r['value']}")

    elif args.action == "search":
        rules = search_rules(args.query)
        if args.json:
            json.dump(rules, sys.stdout, indent=2, ensure_ascii=False)
        else:
            print(f"Found {len(rules)} rules:")
            for r in rules:
                _print_rule(r, False)

    elif args.action == "update":
        r = update_rule(args.key, args.value, args.desc, args.priority)
        if not r:
            print(f"Rule not found: {args.key}")
            return
        print(f"Rule updated: {r['key']} = {r['value']}")

    elif args.action == "delete":
        if delete_rule(args.key):
            print(f"Rule deleted: {args.key}")
        else:
            print(f"Rule not found: {args.key}")

    elif args.action == "count":
        print(f"Total rules: {count_rules()}")


def _handle_cases(args):
    if args.action == "add":
        files = args.files.split(",") if args.files else []
        patterns = args.patterns.split(",") if args.patterns else []
        tags = args.tags.split(",") if args.tags else []
        c = add_case(args.title, args.problem, args.solution, files, patterns, tags, args.outcome)
        print(f"Case added: #{c['id']} - {c['title']}")

    elif args.action == "get":
        c = get_case(args.id)
        if not c:
            print(f"Case not found: #{args.id}")
            return
        _print_case(c, args.json)

    elif args.action == "list":
        cases = list_cases(tag=args.tag, outcome=args.outcome if args.outcome != "success" else None,
                           limit=args.limit, offset=args.offset)
        if args.json:
            json.dump(cases, sys.stdout, indent=2, ensure_ascii=False)
        else:
            for c in cases:
                print(f"  #{c['id']:4d} [{c['outcome']:7s}] {c['title']}")

    elif args.action == "search":
        cases = search_cases(args.query)
        if args.json:
            json.dump(cases, sys.stdout, indent=2, ensure_ascii=False)
        else:
            print(f"Found {len(cases)} cases:")
            for c in cases:
                _print_case(c, False)

    elif args.action == "delete":
        if delete_case(args.id):
            print(f"Case deleted: #{args.id}")
        else:
            print(f"Case not found: #{args.id}")

    elif args.action == "count":
        total = count_cases()
        by_outcome = {o: count_cases(o) for o in ["success", "partial", "failure"]}
        print(f"Total cases: {total} ({', '.join(f'{k}: {v}' for k, v in by_outcome.items())})")


def _handle_session(args):
    if args.action == "get":
        s = get_session()
        if args.json:
            json.dump(s, sys.stdout, indent=2, ensure_ascii=False)
        else:
            print(f"Task:   {s['active_task']}")
            print(f"Files:  {', '.join(s['active_files']) if s['active_files'] else '(none)'}")
            print(f"Goal:   {s['current_goal']}")
            print(f"Queries ({len(s['recent_queries'])}):")
            for q in s['recent_queries'][-5:]:
                print(f"  - {q[:100]}")
            print(f"Summary: {s['conversation_summary'][:200] if s['conversation_summary'] else '(none)'}")

    elif args.action == "task":
        set_task(args.value)
        print(f"Task set: {args.value}")

    elif args.action == "query":
        add_query(args.value)
        print("Query recorded")

    elif args.action == "file":
        add_active_file(args.value)
        print(f"File added: {args.value}")

    elif args.action == "summary":
        set_summary(args.value)
        print("Summary updated")

    elif args.action == "goal":
        set_goal(args.value)
        print(f"Goal set: {args.value}")

    elif args.action == "clear":
        clear_session()
        print("Session cleared")


def _print_rule(r: dict, raw_json: bool):
    if raw_json:
        json.dump(r, sys.stdout, indent=2, ensure_ascii=False)
    else:
        print(f"  Key:    {r['key']}")
        print(f"  Value:  {r['value']}")
        print(f"  Cat:    {r['category']}  Prio: {r['priority']}")
        if r['description']:
            print(f"  Desc:   {r['description']}")
        print()


def _print_case(c: dict, raw_json: bool):
    if raw_json:
        json.dump(c, sys.stdout, indent=2, ensure_ascii=False)
    else:
        print(f"  #{c['id']} - {c['title']} [{c['outcome']}]")
        print(f"  Problem:  {c['problem_summary'][:150]}")
        print(f"  Solution: {c['solution_summary'][:150]}")
        if c['tags']:
            print(f"  Tags:     {', '.join(c['tags'])}")
        if c['files_changed']:
            print(f"  Files:    {', '.join(c['files_changed'])}")
        print()


if __name__ == "__main__":
    main_cli()
