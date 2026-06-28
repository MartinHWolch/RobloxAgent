import logging
import re
from typing import Any
from urllib.parse import urljoin

from .base import BaseScraper
from .api_parser import parse_api_markdown
from config import CREATE_HUB_BASE

logger = logging.getLogger(__name__)

ENGINE_ARTICLES = [
    "/docs/reference/engine/classes/Instance",
    "/docs/reference/engine/classes/Player",
    "/docs/reference/engine/classes/Part",
    "/docs/reference/engine/classes/Model",
    "/docs/reference/engine/classes/Script",
    "/docs/reference/engine/classes/ModuleScript",
    "/docs/reference/engine/classes/LocalScript",
    "/docs/reference/engine/classes/RemoteEvent",
    "/docs/reference/engine/classes/RemoteFunction",
    "/docs/reference/engine/classes/BindableEvent",
    "/docs/reference/engine/classes/BindableFunction",
    "/docs/reference/engine/classes/Animation",
    "/docs/reference/engine/classes/AnimationController",
    "/docs/reference/engine/classes/AnimationTrack",
    "/docs/reference/engine/classes/Humanoid",
    "/docs/reference/engine/classes/HumanoidDescription",
    "/docs/reference/engine/classes/PathfindingService",
    "/docs/reference/engine/classes/Terrain",
    "/docs/reference/engine/classes/Sound",
    "/docs/reference/engine/classes/DataStoreService",
    "/docs/reference/engine/classes/MemoryStoreService",
    "/docs/reference/engine/classes/MessagingService",
    "/docs/reference/engine/classes/HttpService",
    "/docs/reference/engine/classes/TweenService",
    "/docs/reference/engine/classes/UserInputService",
    "/docs/reference/engine/classes/ContextActionService",
    "/docs/reference/engine/classes/TouchInputService",
    "/docs/reference/engine/classes/MarketplaceService",
    "/docs/reference/engine/classes/BadgeService",
    "/docs/reference/engine/classes/InsertService",
    "/docs/reference/engine/classes/CollectionService",
    "/docs/reference/engine/classes/ReplicatedStorage",
    "/docs/reference/engine/classes/ServerStorage",
    "/docs/reference/engine/classes/ServerScriptService",
    "/docs/reference/engine/classes/Plugin",
    "/docs/reference/engine/classes/Selection",
    "/docs/reference/engine/libraries/string",
    "/docs/reference/engine/libraries/table",
    "/docs/reference/engine/libraries/math",
    "/docs/reference/engine/libraries/debug",
    "/docs/reference/engine/libraries/task",
    "/docs/reference/engine/libraries/coroutine",
    "/docs/reference/engine/libraries/utf8",
]

GUIDES = [
    "/docs/scripting",
    "/docs/projects",
    "/docs/projects/data-model",
    "/docs/ui",
    "/docs/avatar",
    "/docs/animation",
    "/docs/physics",
    "/docs/audio",
    "/docs/environment",
    "/docs/production",
    "/docs/players",
    "/docs/studio",
    "/docs/tutorials",
]


class OfficialDocsScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for path in ENGINE_ARTICLES:
            try:
                result = self._scrape_markdown(path)
                if result:
                    results.append(result)
                    logger.info("Scraped: %s", path)
            except Exception as e:
                logger.warning("Failed %s: %s", path, e)
        return results

    def _scrape_markdown(self, path: str) -> dict[str, Any] | None:
        base = path.replace("/docs/", "", 1)
        md_url = f"https://create.roblox.com/docs/en-us/{base}.md"
        resp = self.session.get(md_url, timeout=15)
        if resp.status_code != 200:
            return None

        text = resp.text
        parsed = parse_api_markdown(text)
        fm = parsed["frontmatter"]
        sections = parsed["sections"]

        title = fm.get("name") or path.split("/")[-1]
        summary = fm.get("summary", "")
        class_type = fm.get("type", "")
        tags = fm.get("tags", [])
        inherits = fm.get("inherits", [])

        return {
            "title": title,
            "url": urljoin(CREATE_HUB_BASE, path),
            "path": path,
            "summary": summary,
            "type": class_type,
            "tags": tags,
            "inherits": inherits,
            "properties": sections["properties"],
            "methods": sections["methods"],
            "events": sections["events"],
            "callbacks": sections["callbacks"],
            "enums": sections["enums"],
            "source": "official_docs",
        }

    def _extract_frontmatter(self, text: str, key: str) -> str | None:
        match = re.search(rf"^{key}: (.+)$", text, re.MULTILINE)
        if match:
            return match.group(1).strip().strip("\"'")
        return None

    def _extract_frontmatter_list(self, text: str, key: str) -> list[str]:
        match = re.search(rf"^{key}:$", text, re.MULTILINE)
        if not match:
            return []
        start = match.end()
        items = []
        for line in text[start:].split("\n"):
            line = line.strip()
            if line.startswith("- "):
                items.append(line[2:].strip())
            elif not line.startswith("  ") and line != "":
                break
        return items

    def _strip_frontmatter(self, text: str) -> str:
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                return text[end + 3:].strip()
        return text


class CreatorHubScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for path in GUIDES:
            try:
                result = self._scrape_markdown(path)
                if result:
                    results.append(result)
                    logger.info("Scraped guide: %s", path)
            except Exception as e:
                logger.warning("Failed guide %s: %s", path, e)
        return results

    def _scrape_markdown(self, path: str) -> dict[str, Any] | None:
        base = path.replace("/docs/", "", 1)
        md_url = f"https://create.roblox.com/docs/en-us/{base}.md"
        resp = self.session.get(md_url, timeout=15)
        if resp.status_code != 200:
            return None

        text = resp.text
        parsed = _parse_guide_frontmatter(text)

        title = parsed.get("title") or path.split("/")[-1].replace("-", " ").title()
        description = parsed.get("description", "")

        content_body = _strip_fm(text)

        categories = path.strip("/").split("/")

        guide_type = self._classify_guide(path)

        return {
            "title": title,
            "url": urljoin(CREATE_HUB_BASE, path),
            "path": path,
            "summary": description,
            "type": guide_type,
            "content": content_body[:8000],
            "tags": parsed.get("tags", []),
            "categories": categories,
            "source": "creator_hub",
        }

    def _classify_guide(self, path: str) -> str:
        if "/tutorials" in path:
            return "tutorial"
        if "/reference/" in path:
            return "reference"
        return "guide"


def _parse_guide_frontmatter(text: str) -> dict[str, Any]:
    """Parse frontmatter from guide markdown (uses title:/description: keys)."""
    fm = {}
    if not text.startswith("---"):
        return fm
    end = text.find("---", 3)
    if end == -1:
        return fm
    block = text[3:end]
    for line in block.strip().split("\n"):
        if ": " in line:
            key, val = line.split(": ", 1)
            fm[key.strip()] = val.strip().strip("\"'")
    return fm


def _strip_fm(text: str) -> str:
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text
