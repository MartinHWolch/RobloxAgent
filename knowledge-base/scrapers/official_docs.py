import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper
from config import CREATE_HUB_BASE, API_REF_BASE

logger = logging.getLogger(__name__)

ENGINE_ARTICLES = [
    "/docs/reference/engine/datastores/DataStore",
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
    "/docs/reference/engine/classes/GroupService",
    "/docs/reference/engine/classes/TeamsService",
    "/docs/reference/engine/classes/BadgeService",
    "/docs/reference/engine/classes/InsertService",
    "/docs/reference/engine/classes/CollectionService",
    "/docs/reference/engine/classes/ReplicatedStorage",
    "/docs/reference/engine/classes/ServerStorage",
    "/docs/reference/engine/classes/ServerScriptService",
    "/docs/reference/engine/classes/HttpClient",
    "/docs/reference/engine/classes/Plugin",
    "/docs/reference/engine/classes/Selection",
    "/docs/reference/engine/classes/DebuggerManager",
    "/docs/reference/engine/enums/Enum",
    "/docs/reference/engine/libraries/RobloxGlobals",
    "/docs/reference/engine/libraries/string",
    "/docs/reference/engine/libraries/table",
    "/docs/reference/engine/libraries/math",
    "/docs/reference/engine/libraries/debug",
    "/docs/reference/engine/libraries/task",
    "/docs/reference/engine/libraries/coroutine",
    "/docs/reference/engine/libraries/utf8",
    "/docs/reference/engine/libraries/script",
]

GUIDES = [
    "/docs/education/build-it-play-it-island-of-move",
    "/docs/scripting",
    "/docs/scripting/networking",
    "/docs/scripting/data-persistence",
    "/docs/scripting/ui",
    "/docs/scripting/animations",
    "/docs/scripting/physics",
    "/docs/scripting/terrain",
    "/docs/scripting/audio",
    "/docs/scripting/optimization",
    "/docs/projects",
    "/docs/projects/data-model",
]


class OfficialDocsScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for path in ENGINE_ARTICLES:
            try:
                result = self._scrape_article(path)
                if result:
                    results.append(result)
                    logger.info("Scraped: %s", path)
            except Exception as e:
                logger.warning("Failed %s: %s", path, e)
        return results

    def _scrape_article(self, path: str) -> dict[str, Any] | None:
        url = urljoin(CREATE_HUB_BASE, path)
        resp = self._get(url)
        soup = BeautifulSoup(resp.text, "lxml")

        title_el = soup.select_one("h1") or soup.select_one("title")
        if not title_el:
            return None
        title = self._clean_text(title_el.get_text())

        content_el = soup.select_one(
            "article, .article-content, .content, main, [role='main']"
        ) or soup
        text = self._clean_text(content_el.get_text())

        breadcrumbs = []
        for crumb in soup.select("[class*='breadcrumb'] a, nav a"):
            breadcrumbs.append(self._clean_text(crumb.get_text()))

        return {
            "title": title,
            "url": url,
            "path": path,
            "summary": text[:1000],
            "content": text,
            "breadcrumbs": breadcrumbs,
            "source": "official_docs",
        }


class CreatorHubScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for path in GUIDES:
            try:
                result = self._scrape_guide(path)
                if result:
                    results.append(result)
                    logger.info("Scraped guide: %s", path)
            except Exception as e:
                logger.warning("Failed guide %s: %s", path, e)
        return results

    def _scrape_guide(self, path: str) -> dict[str, Any] | None:
        url = urljoin(CREATE_HUB_BASE, path)
        resp = self._get(url)
        soup = BeautifulSoup(resp.text, "lxml")

        title_el = soup.select_one("h1") or soup.select_one("title")
        if not title_el:
            return None
        title = self._clean_text(title_el.get_text())

        content_el = soup.select_one(
            "article, .article-content, .content, main, [role='main']"
        ) or soup
        text = self._clean_text(content_el.get_text())

        categories = path.strip("/").split("/")

        return {
            "title": title,
            "url": url,
            "path": path,
            "content": text,
            "categories": categories,
            "source": "creator_hub",
        }
