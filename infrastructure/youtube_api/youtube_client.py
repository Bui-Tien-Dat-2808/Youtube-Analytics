from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build

from domain.entities import VideoRecord
from shared.config.settings import Settings
from shared.logging.logger import get_logger

logger = get_logger(__name__)


class YouTubeApiClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = build(
            serviceName="youtube",
            version="v3",
            developerKey=settings.youtube_api_key,
            cache_discovery=False,
        )

    def fetch_recent_videos(
        self,
        keywords: List[str],
        published_after: Optional[datetime] = None,
    ) -> List[VideoRecord]:
        effective_published_after = published_after or (
            datetime.now(timezone.utc) - timedelta(days=self._settings.youtube_lookback_days)
        )
        logger.info(
            "Fetching YouTube videos published after %s",
            effective_published_after.isoformat(),
        )

        records: List[VideoRecord] = []
        for keyword in keywords:
            search_items = self._search_recent_videos(
                keyword=keyword,
                published_after=effective_published_after,
            )
            video_ids = [
                item["id"]["videoId"]
                for item in search_items
                if item["id"].get("videoId")
            ]
            if not video_ids:
                logger.info("No videos returned for keyword=%s", keyword)
                continue

            statistics_map = self._fetch_video_statistics(video_ids)
            for item in search_items:
                video_id = item["id"].get("videoId")
                snippet = item.get("snippet", {})
                statistics = statistics_map.get(video_id, {})
                if not video_id:
                    continue

                records.append(
                    VideoRecord(
                        video_id=video_id,
                        title=snippet.get("title", ""),
                        description=snippet.get("description", ""),
                        published_at=datetime.fromisoformat(
                            snippet["publishedAt"].replace("Z", "+00:00")
                        ).astimezone(timezone.utc),
                        channel_id=snippet.get("channelId", ""),
                        channel_title=snippet.get("channelTitle", ""),
                        views=self._safe_int(statistics.get("viewCount")),
                        likes=self._safe_int(statistics.get("likeCount")),
                        comments=self._safe_int(statistics.get("commentCount")),
                        keyword=keyword,
                    )
                )
        return records

    def _search_recent_videos(
        self,
        keyword: str,
        published_after: datetime,
    ) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        next_page_token: Optional[str] = None

        for _ in range(self._settings.youtube_max_pages):
            request = self._client.search().list(
                part="id,snippet",
                q=keyword,
                type="video",
                order=self._settings.youtube_search_order,
                maxResults=self._settings.youtube_page_size,
                publishedAfter=published_after.isoformat().replace("+00:00", "Z"),
                pageToken=next_page_token,
            )
            response = request.execute()
            page_items = response.get("items", [])
            items.extend(page_items)
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        logger.info(
            "Collected %s search items from YouTube API for keyword=%s",
            len(items),
            keyword,
        )
        return items

    def _fetch_video_statistics(self, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        statistics_map: Dict[str, Dict[str, Any]] = {}

        for offset in range(0, len(video_ids), 50):
            batch_ids = video_ids[offset : offset + 50]
            request = self._client.videos().list(
                part="statistics",
                id=",".join(batch_ids),
            )
            response = request.execute()
            for item in response.get("items", []):
                statistics_map[item["id"]] = item.get("statistics", {})

        logger.info("Collected statistics for %s videos", len(statistics_map))
        return statistics_map

    @staticmethod
    def _safe_int(value: Optional[str]) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
