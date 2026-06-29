"""Session context: short-term working memory for the current session."""

import json
from typing import Any

from .store import get_conn, now


def get_session() -> dict[str, Any]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM session_context WHERE id = 1").fetchone()
    d = dict(row)
    for field in ("active_files", "recent_queries"):
        if isinstance(d.get(field), str):
            d[field] = json.loads(d[field])
    return d


def set_task(task: str):
    conn = get_conn()
    conn.execute(
        "UPDATE session_context SET active_task = ?, updated_at = ? WHERE id = 1",
        (task, now()),
    )
    conn.commit()


def add_active_file(filepath: str):
    session = get_session()
    files = session["active_files"]
    if filepath not in files:
        files.append(filepath)
    conn = get_conn()
    conn.execute(
        "UPDATE session_context SET active_files = ?, updated_at = ? WHERE id = 1",
        (json.dumps(files, ensure_ascii=False), now()),
    )
    conn.commit()


def remove_active_file(filepath: str):
    session = get_session()
    files = [f for f in session["active_files"] if f != filepath]
    conn = get_conn()
    conn.execute(
        "UPDATE session_context SET active_files = ?, updated_at = ? WHERE id = 1",
        (json.dumps(files, ensure_ascii=False), now()),
    )
    conn.commit()


def add_query(query: str, max_queries: int = 20):
    session = get_session()
    queries = session["recent_queries"]
    queries.append(query)
    if len(queries) > max_queries:
        queries = queries[-max_queries:]
    conn = get_conn()
    conn.execute(
        "UPDATE session_context SET recent_queries = ?, updated_at = ? WHERE id = 1",
        (json.dumps(queries, ensure_ascii=False), now()),
    )
    conn.commit()


def set_summary(summary: str):
    conn = get_conn()
    conn.execute(
        "UPDATE session_context SET conversation_summary = ?, updated_at = ? WHERE id = 1",
        (summary, now()),
    )
    conn.commit()


def set_goal(goal: str):
    conn = get_conn()
    conn.execute(
        "UPDATE session_context SET current_goal = ?, updated_at = ? WHERE id = 1",
        (goal, now()),
    )
    conn.commit()


def clear_session():
    conn = get_conn()
    conn.execute(
        """UPDATE session_context SET
           active_task = '', active_files = '[]', recent_queries = '[]',
           conversation_summary = '', current_goal = '', updated_at = ?
           WHERE id = 1""",
        (now(),),
    )
    conn.commit()
