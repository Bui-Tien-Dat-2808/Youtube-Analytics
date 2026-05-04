from __future__ import annotations

import xml.etree.ElementTree as element_tree
from typing import List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from shared.logging.logger import get_logger

logger = get_logger(__name__)


class GoogleTrendsKeywordProvider:
    def __init__(self, geo: str, limit: int) -> None:
        self._geo = geo
        self._limit = limit
        self._feed_url = (
            "https://trends.google.com/trending/rss?"
            + urlencode({"geo": self._geo})
        )

    def get_keywords(self) -> List[str]:
        logger.info(
            "Fetching trending keywords from Google Trends RSS for geo=%s",
            self._geo,
        )
        request = Request(
            self._feed_url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urlopen(request, timeout=30) as response:
            payload = response.read()

        root = element_tree.fromstring(payload)
        titles = [
            item.findtext("title", default="").strip()
            for item in root.findall(".//item")
        ]
        keywords = [title for title in titles if title]
        unique_keywords = list(dict.fromkeys(keywords))
        limited_keywords = unique_keywords[: self._limit]
        logger.info("Resolved %s trending keywords", len(limited_keywords))
        return limited_keywords
