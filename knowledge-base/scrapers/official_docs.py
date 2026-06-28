import logging
import re
from typing import Any
from urllib.parse import urljoin

from .base import BaseScraper
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

        title = self._extract_frontmatter(text, "name") or path.split("/")[-1]
        summary = self._extract_frontmatter(text, "summary") or ""
        class_type = self._extract_frontmatter(text, "type") or ""
        tags = self._extract_frontmatter_list(text, "tags")
        inherits = self._extract_frontmatter_list(text, "inherits")

        content_body = self._strip_frontmatter(text)

        return {
            "title": title,
            "url": urljoin(CREATE_HUB_BASE, path),
            "path": path,
            "summary": summary,
            "type": class_type,
            "tags": tags,
            "inherits": inherits,
            "content": content_body[:8000],
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

        title = self._extract_frontmatter(text, "name") or path.split("/")[-1]
        summary = self._extract_frontmatter(text, "summary") or ""

        content_body = self._strip_frontmatter(text)

        categories = path.strip("/").split("/")

        return {
            "title": title,
            "url": urljoin(CREATE_HUB_BASE, path),
            "path": path,
            "summary": summary,
            "content": content_body[:8000],
            "categories": categories,
            "source": "creator_hub",
        }

    def _extract_frontmatter(self, text: str, key: str) -> str | None:
        match = re.search(rf"^{key}: (.+)$", text, re.MULTILINE)
        if match:
            return match.group(1).strip().strip("\"'")
        return None

    def _strip_frontmatter(self, text: str) -> str:
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                return text[end + 3:].strip()
        return text
