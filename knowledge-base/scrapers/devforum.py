import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper
from config import DEVFORUM_BASE, DEVFORUM_TOPICS

logger = logging.getLogger(__name__)


class DevForumScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for topic_slug in DEVFORUM_TOPICS:
            try:
                result = self._scrape_topic(topic_slug)
                if result:
                    results.append(result)
                    logger.info("Scraped topic: %s", topic_slug)
            except Exception as e:
                logger.warning("Failed topic %s: %s", topic_slug, e)
        return results

    def _scrape_topic(self, slug: str) -> dict[str, Any] | None:
        url = urljoin(DEVFORUM_BASE, f"/t/{slug}")
        resp = self._get(url)
        soup = BeautifulSoup(resp.text, "lxml")

        title_el = soup.select_one("h1") or soup.select_one(".topic-title")
        if not title_el:
            return None
        title = self._clean_text(title_el.get_text())

        posts = []
        for post_el in soup.select("[class*='post'], article"):
            author_el = post_el.select_one("[class*='username'], [class*='creator']")
            body_el = post_el.select_one("[class*='post-body'], [class*='cooked']")

            if body_el:
                posts.append({
                    "author": self._clean_text(author_el.get_text()) if author_el else "unknown",
                    "content": self._clean_text(body_el.get_text()),
                    "likes": self._extract_likes(post_el),
                    "accepted": self._is_accepted(post_el),
                })

        tags = []
        for tag_el in soup.select("[class*='tag']"):
            tags.append(self._clean_text(tag_el.get_text()))

        return {
            "title": title,
            "url": url,
            "slug": slug,
            "posts": posts,
            "tags": tags,
            "source": "devforum",
        }

    def _extract_likes(self, post_el) -> int:
        like_el = post_el.select_one("[class*='like-count'], .likes")
        if like_el:
            try:
                return int(self._clean_text(like_el.get_text()))
            except ValueError:
                pass
        return 0

    def _is_accepted(self, post_el) -> bool:
        return bool(post_el.select_one("[class*='accepted'], .solved"))
