import logging
import re
import time
from typing import Any
from urllib.parse import urljoin

from .base import BaseScraper
from config import DEVFORUM_BASE, DEVFORUM_SEARCH_QUERIES, DEVFORUM_CURATED_TOPIC_IDS, DEVFORUM_EXCLUDED_TOPIC_IDS

logger = logging.getLogger(__name__)

EXCLUDE_KEYWORDS = [
    "hiring", "looking for", "commission", "portfolio", "open to work",
    "showcase", "wanted", "recruitment", "job",
]

CATEGORY_MAP = {
    55: "scripting-support",
    54: "art-design-support",
    63: "tutorials",
    62: "resources",
    57: "community-resources",
    6: "general",
    4: "releases",
    5: "feedback",
}


class DevForumScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        seen_ids = set()
        results = []

        for tid in DEVFORUM_CURATED_TOPIC_IDS:
            if tid in DEVFORUM_EXCLUDED_TOPIC_IDS:
                continue
            if tid in seen_ids:
                continue
            seen_ids.add(tid)
            try:
                detail = self._fetch_topic(tid)
                if detail:
                    detail["curated"] = True
                    results.append(detail)
                    logger.info("Scraped curated topic %d: %s", tid, detail["title"][:50])
            except Exception as e:
                logger.debug("Failed curated topic %d: %s", tid, e)

        for query in DEVFORUM_SEARCH_QUERIES:
            try:
                topic_ids = self._search_topic_ids(query)
                for tid in topic_ids:
                    if tid in DEVFORUM_EXCLUDED_TOPIC_IDS:
                        continue
                    if tid not in seen_ids:
                        seen_ids.add(tid)
                        try:
                            detail = self._fetch_topic(tid)
                            if detail and self._is_quality_topic(detail):
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

    def _is_quality_topic(self, topic: dict) -> bool:
        title = topic.get("title", "").lower()
        for kw in EXCLUDE_KEYWORDS:
            if kw in title:
                return False
        if not topic.get("posts"):
            return False
        total_likes = sum(p.get("likes", 0) for p in topic["posts"])
        if total_likes < 2 and len(topic["posts"]) < 3:
            return False
        return True

    def _fetch_topic(self, topic_id: int) -> dict[str, Any] | None:
        url = urljoin(DEVFORUM_BASE, f"/t/{topic_id}.json")
        resp = self.session.get(url, timeout=15)
        if resp.status_code != 200:
            return None

        data = resp.json()
        title = data.get("title", "Untitled")

        posts = []
        for post in data.get("post_stream", {}).get("posts", []):
            cooked = post.get("cooked", "")
            posts.append({
                "author": post.get("username", "unknown"),
                "content": self._html_to_text(cooked),
                "likes": post.get("like_count", 0),
                "accepted": post.get("accepted_answer", False),
            })

        tags = data.get("tags", [])
        cat_id = data.get("category_id")
        category_name = CATEGORY_MAP.get(cat_id, f"category-{cat_id}")

        return {
            "title": title,
            "url": urljoin(DEVFORUM_BASE, f"/t/{data.get('slug', '')}/{topic_id}"),
            "slug": data.get("slug", ""),
            "topic_id": topic_id,
            "category": category_name,
            "posts": posts,
            "tags": tags,
            "source": "devforum",
        }

    def _html_to_text(self, html: str) -> str:
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"&[a-z]+;", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()[:3000]
