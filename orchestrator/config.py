"""Orchestrator configuration."""

import os

ORCHESTRATOR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(ORCHESTRATOR_DIR, "..")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEFAULT_MODEL = "gpt-4o-mini"
FALLBACK_MODEL = "gpt-4o-mini"

RAG_TOP_K = 8
MEMORY_RULES_LIMIT = 20

MAX_CONTEXT_LENGTH = 8000
MAX_RAG_CHARS = 6000
