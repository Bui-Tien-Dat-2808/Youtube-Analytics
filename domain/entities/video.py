from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class VideoRecord:
    video_id: str
    title: str
    description: str
    published_at: datetime
    channel_id: str
    channel_title: str
    views: Optional[int]
    likes: Optional[int]
    comments: Optional[int]
    keyword: Optional[str] = None

    @property
    def ingestion_date(self) -> str:
        return self.published_at.date().isoformat()
