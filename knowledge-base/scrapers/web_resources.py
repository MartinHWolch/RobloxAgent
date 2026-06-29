import logging
import re
from typing import Any

from .base import BaseScraper
from config import WEB_RESOURCES

logger = logging.getLogger(__name__)


class WebResourcesScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for url, title, topic in WEB_RESOURCES:
            try:
                result = self._scrape_url(url, title, topic)
                if result:
                    results.append(result)
                    logger.info("Scraped web resource: %s", title)
            except Exception as e:
                logger.warning("Failed web resource %s: %s", url, e)
        return results

    def _scrape_url(self, url: str, title: str, topic: str) -> dict[str, Any] | None:
        fetch_url = _github_blob_to_raw(url)
        resp = self.session.get(fetch_url, timeout=20)
        if resp.status_code != 200:
            return None

        content_type = resp.headers.get("content-type", "").lower()
        text = resp.text
        if "html" in content_type or "<html" in text[:1000].lower():
            text = _html_to_text(text)

        return {
            "title": title,
            "url": url,
            "topic": topic,
            "content": text[:12000],
            "source": "web_resource",
        }


def _html_to_text(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"&nbsp;", " ", html)
    html = re.sub(r"&amp;", "&", html)
    html = re.sub(r"&lt;", "<", html)
    html = re.sub(r"&gt;", ">", html)
    html = re.sub(r"&quot;", '"', html)
    html = re.sub(r"&#39;", "'", html)
    return re.sub(r"\s+", " ", html).strip()


def _github_blob_to_raw(url: str) -> str:
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.*)", url)
    if not match:
        return url
    owner, repo, branch, path = match.groups()
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
