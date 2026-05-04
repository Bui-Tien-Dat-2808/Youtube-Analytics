from __future__ import annotations

from typing import List

from shared.logging.logger import get_logger

logger = get_logger(__name__)


class ManualKeywordProvider:
    def __init__(self, keyword_csv: str | None, limit: int) -> None:
        self._keyword_csv = keyword_csv or ""
        self._limit = limit

    def get_keywords(self) -> List[str]:
        keywords = [
            keyword.strip()
            for keyword in self._keyword_csv.split(",")
            if keyword.strip()
        ]
        unique_keywords = list(dict.fromkeys(keywords))
        limited_keywords = unique_keywords[: self._limit]
        logger.info("Loaded %s fallback keywords", len(limited_keywords))
        return limited_keywords
