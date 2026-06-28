import time
import logging
from abc import ABC, abstractmethod
from typing import Any

import requests

from config import REQUEST_DELAY, USER_AGENT

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    @abstractmethod
    def scrape(self) -> list[dict[str, Any]]:
        ...

    def _get(self, url: str, **kwargs) -> requests.Response:
        time.sleep(REQUEST_DELAY)
        logger.debug("GET %s", url)
        resp = self.session.get(url, **kwargs)
        resp.raise_for_status()
        return resp

    def _clean_text(self, text: str | None) -> str:
        if not text:
            return ""
        import re
        text = re.sub(r"\s+", " ", text)
        return text.strip()
