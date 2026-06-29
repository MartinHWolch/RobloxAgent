"""Project rules: persistent decisions that survive between sessions."""

import json
from typing import Any

from .store import get_conn, now
from .config import RULE_CATEGORIES


def add_rule(key: str, value: str, category: str = "practices",
             description: str = "", priority: int = 5) -> dict[str, Any]:
    assert category in RULE_CATEGORIES, f"Invalid category: {category}, choose from {RULE_CATEGORIES}"
    conn = get_conn()
    ts = now()
    cur = conn.execute(
        """INSERT INTO project_rules (key, value, category, description, priority, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (key, value, category, description, priority, ts, ts),
    )
    conn.execute(
        "INSERT INTO rules_fts (rowid, key, value, description) VALUES (?, ?, ?, ?)",
        (cur.lastrowid, key, value, description),
    )
    conn.commit()
    return get_rule(key)


def get_rule(key: str) -> dict[str, Any] | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM project_rules WHERE key = ?", (key,)
    ).fetchone()
    return _row_to_dict(row) if row else None


def list_rules(category: str | None = None) -> list[dict[str, Any]]:
    conn = get_conn()
    if category:
        rows = conn.execute(
            "SELECT * FROM project_rules WHERE category = ? ORDER BY priority DESC, key",
            (category,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM project_rules ORDER BY category, priority DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def search_rules(query: str) -> list[dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        """SELECT project_rules.* FROM project_rules
           JOIN rules_fts ON project_rules.id = rules_fts.rowid
           WHERE rules_fts MATCH ?
           ORDER BY rank""",
        (query,),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def update_rule(key: str, value: str | None = None,
                description: str | None = None, priority: int | None = None) -> dict[str, Any] | None:
    conn = get_conn()
    existing = get_rule(key)
    if not existing:
        return None

    new_value = value if value is not None else existing["value"]
    new_desc = description if description is not None else existing["description"]
    new_prio = priority if priority is not None else existing["priority"]
    ts = now()

    conn.execute(
        "UPDATE project_rules SET value=?, description=?, priority=?, updated_at=? WHERE key=?",
        (new_value, new_desc, new_prio, ts, key),
    )
    conn.execute("DELETE FROM rules_fts WHERE rowid = ?", (existing["id"],))
    conn.execute(
        "INSERT INTO rules_fts (rowid, key, value, description) VALUES (?, ?, ?, ?)",
        (existing["id"], new_value, new_desc, new_value),
    )
    conn.commit()
    return get_rule(key)


def delete_rule(key: str) -> bool:
    conn = get_conn()
    rule = get_rule(key)
    if not rule:
        return False
    conn.execute("DELETE FROM project_rules WHERE key = ?", (key,))
    conn.execute("DELETE FROM rules_fts WHERE rowid = ?", (rule["id"],))
    conn.commit()
    return True


def count_rules() -> int:
    conn = get_conn()
    return conn.execute("SELECT COUNT(*) FROM project_rules").fetchone()[0]


def _row_to_dict(row) -> dict[str, Any]:
    d = dict(row)
    return d
