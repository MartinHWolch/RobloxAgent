"""Core SQLite store: schema, connection, and base operations."""

import os
import sqlite3
import json
from datetime import datetime, timezone

from .config import DB_PATH


_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
        _init_schema(_conn)
    return _conn


def _init_schema(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS project_rules (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            key         TEXT    NOT NULL UNIQUE,
            value       TEXT    NOT NULL,
            category    TEXT    NOT NULL DEFAULT 'practices',
            description TEXT    NOT NULL DEFAULT '',
            priority    INTEGER NOT NULL DEFAULT 5,
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_rules_category ON project_rules(category);
        CREATE INDEX IF NOT EXISTS idx_rules_key    ON project_rules(key);

        CREATE VIRTUAL TABLE IF NOT EXISTS rules_fts USING fts5(
            key, value, description
        );

        CREATE TABLE IF NOT EXISTS resolved_cases (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            title             TEXT    NOT NULL,
            problem_summary   TEXT    NOT NULL,
            solution_summary  TEXT    NOT NULL,
            files_changed     TEXT    NOT NULL DEFAULT '[]',
            patterns_used     TEXT    NOT NULL DEFAULT '[]',
            tags              TEXT    NOT NULL DEFAULT '[]',
            outcome           TEXT    NOT NULL DEFAULT 'success',
            created_at        TEXT    NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_cases_tags    ON resolved_cases(tags);
        CREATE INDEX IF NOT EXISTS idx_cases_outcome ON resolved_cases(outcome);

        CREATE VIRTUAL TABLE IF NOT EXISTS cases_fts USING fts5(
            title, problem_summary, solution_summary
        );

        CREATE TABLE IF NOT EXISTS session_context (
            id                  INTEGER PRIMARY KEY CHECK (id = 1),
            active_task         TEXT    NOT NULL DEFAULT '',
            active_files        TEXT    NOT NULL DEFAULT '[]',
            recent_queries      TEXT    NOT NULL DEFAULT '[]',
            conversation_summary TEXT   NOT NULL DEFAULT '',
            current_goal        TEXT   NOT NULL DEFAULT '',
            updated_at          TEXT   NOT NULL
        );

        INSERT OR IGNORE INTO session_context (id, updated_at)
        VALUES (1, '');
    """)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def close():
    global _conn
    if _conn:
        _conn.close()
        _conn = None
