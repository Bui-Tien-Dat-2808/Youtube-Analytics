from __future__ import annotations

from dataclasses import dataclass

from application.services.youtube_ingestion_service import YouTubeIngestionService


@dataclass(slots=True)
class LoadRawVideosUseCase:
    ingestion_service: YouTubeIngestionService

    def execute(self) -> None:
        self.ingestion_service.load_staged_videos_to_raw()
