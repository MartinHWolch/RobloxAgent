import logging
from typing import Any

import requests

from .base import BaseScraper
from config import GITHUB_REPOS

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


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
        repo_data = self._github_api(f"/repos/{owner}/{repo}")
        if not repo_data:
            return None

        readme_text = self._get_readme(owner, repo)

        return {
            "title": repo_data.get("full_name", f"{owner}/{repo}"),
            "url": repo_data.get("html_url", f"https://github.com/{owner}/{repo}"),
            "owner": owner,
            "repo": repo,
            "description": repo_data.get("description") or "",
            "stars": repo_data.get("stargazers_count", 0),
            "language": repo_data.get("language") or "",
            "topics": repo_data.get("topics", []),
            "license": repo_data.get("license", {}).get("spdx_id") if repo_data.get("license") else "",
            "readme": readme_text,
            "source": "github",
        }

    def _github_api(self, path: str) -> dict | None:
        url = f"{GITHUB_API}{path}"
        resp = self.session.get(url, timeout=15)
        if resp.status_code != 200:
            logger.debug("GitHub API %s returned %d", path, resp.status_code)
            return None
        return resp.json()

    def _get_readme(self, owner: str, repo: str) -> str:
        for branch in ["main", "master"]:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            try:
                resp = self.session.get(readme_url, timeout=10)
                if resp.status_code == 200:
                    return resp.text[:5000]
            except Exception:
                pass
        return ""
