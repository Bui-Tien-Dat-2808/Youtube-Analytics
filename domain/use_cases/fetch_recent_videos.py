from __future__ import annotations

from dataclasses import dataclass

from application.services.youtube_ingestion_service import YouTubeIngestionService


@dataclass(slots=True)
class FetchRecentVideosUseCase:
    ingestion_service: YouTubeIngestionService

    def execute(self) -> None:
        self.ingestion_service.fetch_recent_videos_to_stage()
