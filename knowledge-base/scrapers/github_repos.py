import logging
from typing import Any

from bs4 import BeautifulSoup

from .base import BaseScraper
from config import GITHUB_REPOS

logger = logging.getLogger(__name__)


class GitHubScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for owner, repo in GITHUB_REPOS:
            try:
                result = self._scrape_repo(owner, repo)
                if result:
                    results.append(result)
                    logger.info("Scraped repo: %s/%s", owner, repo)
            except Exception as e:
                logger.warning("Failed repo %s/%s: %s", owner, repo, e)
        return results

    def _scrape_repo(self, owner: str, repo: str) -> dict[str, Any] | None:
        url = f"https://github.com/{owner}/{repo}"
        resp = self._get(url)
        soup = BeautifulSoup(resp.text, "lxml")

        title = self._clean_text(soup.select_one("h1") or soup.select_one("title"))
        description_el = soup.select_one("p[class*='description'], [class*='repo-description']")
        description = self._clean_text(
            description_el.get_text()) if description_el else ""

        stars = 0
        star_el = soup.select_one("[class*='star-count'], [id*='star-count']")
        if star_el:
            try:
                stars = int(star_el.get("title", "0").replace(",", ""))
            except (ValueError, AttributeError):
                pass

        topics = []
        for topic_el in soup.select("[class*='topic-tag']"):
            topics.append(self._clean_text(topic_el.get_text()))

        readme_text = self._scrape_readme(owner, repo)

        return {
            "title": self._clean_text(title.get_text()) if title else repo,
            "url": url,
            "owner": owner,
            "repo": repo,
            "description": description,
            "stars": stars,
            "topics": topics,
            "readme": readme_text,
            "source": "github",
        }

    def _scrape_readme(self, owner: str, repo: str) -> str:
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
        try:
            resp = self.session.get(readme_url, timeout=10)
            if resp.status_code == 200:
                return resp.text[:5000]
        except Exception:
            pass

        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
        try:
            resp = self.session.get(readme_url, timeout=10)
            if resp.status_code == 200:
                return resp.text[:5000]
        except Exception:
            pass

        return ""
