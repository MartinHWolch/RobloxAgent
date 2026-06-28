import logging
import time
from typing import Any
from urllib.parse import urljoin

from .base import BaseScraper
from config import DEVFORUM_BASE, DEVFORUM_SEARCH_QUERIES

logger = logging.getLogger(__name__)


class DevForumScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        seen_ids = set()
        results = []

        for query in DEVFORUM_SEARCH_QUERIES:
            try:
                topic_ids = self._search_topic_ids(query)
                for tid in topic_ids:
                    if tid not in seen_ids:
                        seen_ids.add(tid)
                        try:
                            detail = self._fetch_topic(tid)
                            if detail:
                                results.append(detail)
                                logger.info("Scraped topic %d: %s", tid, detail["title"][:50])
                        except Exception as e:
                            logger.debug("Failed topic %d: %s", tid, e)
            except Exception as e:
                logger.warning("Search query failed '%s': %s", query, e)

        return results

    def _search_topic_ids(self, query: str) -> list[int]:
        url = urljoin(DEVFORUM_BASE, f"/search.json?q={query}")
        resp = self.session.get(url, timeout=15)
        if resp.status_code != 200:
            return []
        data = resp.json()
        return [t.get("id") for t in data.get("topics", []) if t.get("id")]

    def _fetch_topic(self, topic_id: int) -> dict[str, Any] | None:
        url = urljoin(DEVFORUM_BASE, f"/t/{topic_id}.json")
        resp = self.session.get(url, timeout=15)
        if resp.status_code != 200:
            return None

        data = resp.json()
        title = data.get("title", "Untitled")

        posts = []
        for post in data.get("post_stream", {}).get("posts", []):
            posts.append({
                "author": post.get("username", "unknown"),
                "content": self._clean_text(post.get("cooked", "")),
                "likes": post.get("like_count", 0),
                "accepted": post.get("accepted_answer", False),
            })

        tags = data.get("tags", [])
        category = data.get("category_id")

        return {
            "title": title,
            "url": urljoin(DEVFORUM_BASE, f"/t/{data.get('slug', '')}/{topic_id}"),
            "slug": data.get("slug", ""),
            "topic_id": topic_id,
            "category_id": category,
            "posts": posts,
            "tags": tags,
            "source": "devforum",
        }
