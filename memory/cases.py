"""Resolved cases: problems and solutions for continuous learning."""

import json
from typing import Any

from .store import get_conn, now
from .config import CASE_OUTCOMES


def add_case(title: str, problem_summary: str, solution_summary: str,
             files_changed: list[str] | None = None,
             patterns_used: list[str] | None = None,
             tags: list[str] | None = None,
             outcome: str = "success") -> dict[str, Any]:
    assert outcome in CASE_OUTCOMES, f"Invalid outcome: {outcome}, choose from {CASE_OUTCOMES}"

    conn = get_conn()
    ts = now()
    cur = conn.execute(
        """INSERT INTO resolved_cases
           (title, problem_summary, solution_summary, files_changed, patterns_used, tags, outcome, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            title,
            problem_summary,
            solution_summary,
            json.dumps(files_changed or [], ensure_ascii=False),
            json.dumps(patterns_used or [], ensure_ascii=False),
            json.dumps(tags or [], ensure_ascii=False),
            outcome,
            ts,
        ),
    )
    conn.execute(
        "INSERT INTO cases_fts (rowid, title, problem_summary, solution_summary) VALUES (?, ?, ?, ?)",
        (cur.lastrowid, title, problem_summary, solution_summary),
    )
    conn.commit()
    return get_case(cur.lastrowid)


def get_case(case_id: int) -> dict[str, Any] | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM resolved_cases WHERE id = ?", (case_id,)
    ).fetchone()
    return _row_to_dict(row) if row else None


def list_cases(tag: str | None = None, outcome: str | None = None,
               limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    conn = get_conn()
    where = []
    params = []

    if tag:
        where.append("tags LIKE ?")
        params.append(f'%"{tag}"%')
    if outcome:
        where.append("outcome = ?")
        params.append(outcome)

    sql = "SELECT * FROM resolved_cases"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(sql, params).fetchall()
    return [_row_to_dict(r) for r in rows]


def search_cases(query: str) -> list[dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        """SELECT resolved_cases.* FROM resolved_cases
           JOIN cases_fts ON resolved_cases.id = cases_fts.rowid
           WHERE cases_fts MATCH ?
           ORDER BY rank""",
        (query,),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def delete_case(case_id: int) -> bool:
    conn = get_conn()
    case = get_case(case_id)
    if not case:
        return False
    conn.execute("DELETE FROM resolved_cases WHERE id = ?", (case_id,))
    conn.execute("DELETE FROM cases_fts WHERE rowid = ?", (case_id,))
    conn.commit()
    return True


def count_cases(outcome: str | None = None) -> int:
    conn = get_conn()
    if outcome:
        return conn.execute(
            "SELECT COUNT(*) FROM resolved_cases WHERE outcome = ?", (outcome,)
        ).fetchone()[0]
    return conn.execute("SELECT COUNT(*) FROM resolved_cases").fetchone()[0]


def _row_to_dict(row) -> dict[str, Any]:
    d = dict(row)
    for field in ("files_changed", "patterns_used", "tags"):
        if isinstance(d.get(field), str):
            d[field] = json.loads(d[field])
    return d
