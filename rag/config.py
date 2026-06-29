"""RAG configuration."""

import os

RAG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(RAG_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "knowledge-base", "data")

CHROMA_DB_DIR = os.path.join(RAG_DIR, "chroma_db")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
EMBEDDING_DEVICE = "cpu"

CHUNK_MAX_SIZE = 1000
CHUNK_OVERLAP = 200

KB_SOURCES = {
    "engine_api": os.path.join(DATA_DIR, "documentation", "engine_api.json"),
    "creator_hub": os.path.join(DATA_DIR, "documentation", "creator_hub.json"),
    "devforum": os.path.join(DATA_DIR, "community", "devforum.json"),
    "github": os.path.join(DATA_DIR, "code", "github_repos.json"),
    "examples": os.path.join(DATA_DIR, "examples", "categorized.json"),
    "web_resources": os.path.join(DATA_DIR, "external", "web_resources.json"),
}

DEFAULT_TOP_K = 10
