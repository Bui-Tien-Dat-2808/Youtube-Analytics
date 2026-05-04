from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from domain.entities import VideoRecord
from infrastructure.iceberg.video_repository import IcebergVideoRepository
from infrastructure.keyword_sources import (
    GoogleTrendsKeywordProvider,
    ManualKeywordProvider,
)
from infrastructure.storage.local_stage_repository import LocalStageRepository
from infrastructure.youtube_api.youtube_client import YouTubeApiClient
from shared.config.settings import Settings
from shared.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class YouTubeIngestionService:
    settings: Settings
    youtube_client: YouTubeApiClient
    iceberg_repository: IcebergVideoRepository
    stage_repository: LocalStageRepository

    def fetch_recent_videos_to_stage(self) -> None:
        last_published_at = self.iceberg_repository.get_latest_published_at()
        logger.info(
            "Starting YouTube ingestion with last published_at watermark: %s",
            last_published_at,
        )

        keywords = self._resolve_keywords()
        if not keywords:
            logger.info("No keywords resolved for YouTube ingestion")
            self.stage_repository.clear_stage_file()
            return

        videos = self.youtube_client.fetch_recent_videos(
            keywords=keywords,
            published_after=last_published_at,
        )
        logger.info("Fetched %s videos from YouTube API", len(videos))

        if not videos:
            logger.info("No new videos found for ingestion")
            self.stage_repository.clear_stage_file()
            return

        records = self._deduplicate_records(videos)
        self.stage_repository.write_records(records)
        logger.info("Fetched YouTube videos staged locally")

    def load_staged_videos_to_raw(self) -> None:
        records = self.stage_repository.read_records()
        if not records:
            logger.info("No staged records available for raw Iceberg load")
            return

        self.iceberg_repository.write_raw_records(records)
        self.stage_repository.clear_stage_file()
        logger.info("Raw YouTube videos persisted to Iceberg")

    @staticmethod
    def _deduplicate_records(records: Iterable[VideoRecord]) -> List[VideoRecord]:
        unique_records = {
            f"{record.video_id}::{record.keyword or ''}": record
            for record in records
        }
        return list(unique_records.values())

    def _resolve_keywords(self) -> List[str]:
        logger.info(
            "Resolving keyword source using provider=%s",
            self.settings.youtube_keyword_source,
        )

        if self.settings.youtube_keyword_source == "google_trends_rss":
            try:
                provider = GoogleTrendsKeywordProvider(
                    geo=self.settings.youtube_trends_geo,
                    limit=self.settings.youtube_top_keywords_limit,
                )
                keywords = provider.get_keywords()
                if keywords:
                    return keywords
            except Exception as exc:
                logger.warning(
                    "Google Trends keyword fetch failed. Falling back to manual keywords: %s",
                    exc,
                )

        provider = ManualKeywordProvider(
            keyword_csv=self.settings.youtube_keyword_fallback
            or self.settings.youtube_search_keyword,
            limit=self.settings.youtube_top_keywords_limit,
        )
        return provider.get_keywords()
