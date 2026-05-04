from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List

from domain.entities import VideoRecord
from shared.logging.logger import get_logger

logger = get_logger(__name__)


class LocalStageRepository:
    def __init__(self, stage_file_path: Path) -> None:
        self._stage_file_path = stage_file_path
        self._stage_file_path.parent.mkdir(parents=True, exist_ok=True)

    def write_records(self, records: List[VideoRecord]) -> None:
        logger.info(
            "Writing %s records to local stage file %s",
            len(records),
            self._stage_file_path,
        )
        with self._stage_file_path.open("w", encoding="utf-8") as stage_file:
            for record in records:
                payload = asdict(record)
                payload["published_at"] = record.published_at.isoformat()
                stage_file.write(json.dumps(payload) + "\n")

    def read_records(self) -> List[VideoRecord]:
        if not self._stage_file_path.exists():
            logger.info("Stage file %s does not exist", self._stage_file_path)
            return []

        records: List[VideoRecord] = []
        with self._stage_file_path.open("r", encoding="utf-8") as stage_file:
            for line in stage_file:
                payload = json.loads(line)
                records.append(
                    VideoRecord(
                        video_id=payload["video_id"],
                        title=payload["title"],
                        description=payload["description"],
                        published_at=datetime.fromisoformat(payload["published_at"]),
                        channel_id=payload["channel_id"],
                        channel_title=payload["channel_title"],
                        views=payload["views"],
                        likes=payload["likes"],
                        comments=payload["comments"],
                        keyword=payload.get("keyword"),
                    )
                )
        logger.info("Loaded %s records from local stage file", len(records))
        return records

    def clear_stage_file(self) -> None:
        if self._stage_file_path.exists():
            self._stage_file_path.unlink()
            logger.info("Cleared stage file %s", self._stage_file_path)
