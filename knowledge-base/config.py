import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

REQUEST_DELAY = 1.0
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEVFORUM_BASE = "https://devforum.roblox.com"
CREATE_HUB_BASE = "https://create.roblox.com"
API_REF_BASE = "https://create.roblox.com/docs/reference/engine"

DEVFORUM_TOPICS = [
    "how-should-i-structure-a-large-robux-game",
    "what-is-the-best-way-to-store-data",
    "networking-best-practices",
    "optimization-guide-for-large-games",
]

GITHUB_REPOS = [
    ("Sleitnick", "Knit"),
    ("Sleitnick", "Cmdr"),
    ("Roblox", "react-lua"),
    ("phuebner", "matter"),
    ("elihutton", "fusion"),
    ("littensy", "ProfileStore"),
    ("evaera", "Promise"),
    ("evaera", "Maid"),
    ("Howmanysmall", "Janitor"),
    ("Campycodes", "Trove"),
]
