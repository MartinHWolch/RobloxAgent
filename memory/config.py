"""Memory module configuration."""

import os

MEMORY_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(MEMORY_DIR, "memory.db")

RULE_CATEGORIES = [
    "architecture",
    "naming",
    "dependencies",
    "practices",
    "patterns",
    "conventions",
]

CASE_OUTCOMES = ["success", "partial", "failure"]
