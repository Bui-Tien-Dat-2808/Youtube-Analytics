from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from pyspark.sql import Row
from pyspark.sql.functions import col, max as spark_max
from pyspark.sql.types import IntegerType, StringType, StructField, StructType, TimestampType

from domain.entities import VideoRecord
from infrastructure.iceberg.spark_session_factory import build_spark_session
from shared.config.settings import Settings
from shared.logging.logger import get_logger

logger = get_logger(__name__)


class IcebergVideoRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._spark = build_spark_session(settings, app_name="youtube-raw-ingestion")

    def write_raw_records(self, records: List[VideoRecord]) -> None:
        logger.info("Writing %s raw records to Iceberg table %s", len(records), self._settings.iceberg_raw_table)
        schema = StructType(
            [
                StructField("video_id", StringType(), nullable=False),
                StructField("title", StringType(), nullable=False),
                StructField("description", StringType(), nullable=False),
                StructField("published_at", TimestampType(), nullable=False),
                StructField("channel_id", StringType(), nullable=False),
                StructField("channel_title", StringType(), nullable=False),
                StructField("views", IntegerType(), nullable=True),
                StructField("likes", IntegerType(), nullable=True),
                StructField("comments", IntegerType(), nullable=True),
                StructField("keyword", StringType(), nullable=True),
                StructField("ingestion_date", StringType(), nullable=False),
            ]
        )
        rows = [
            Row(
                video_id=record.video_id,
                title=record.title,
                description=record.description,
                published_at=record.published_at,
                channel_id=record.channel_id,
                channel_title=record.channel_title,
                views=record.views,
                likes=record.likes,
                comments=record.comments,
                keyword=record.keyword,
                ingestion_date=record.ingestion_date,
            )
            for record in records
        ]
        dataframe = self._spark.createDataFrame(rows, schema=schema)
        self._ensure_namespace()
        self._spark.sql(
            f"""
            CREATE TABLE IF NOT EXISTS {self._settings.iceberg_raw_table} (
                video_id STRING,
                title STRING,
                description STRING,
                published_at TIMESTAMP,
                channel_id STRING,
                channel_title STRING,
                views INT,
                likes INT,
                comments INT,
                keyword STRING,
                ingestion_date STRING
            )
            USING iceberg
            PARTITIONED BY (days(published_at), channel_id)
            """
        )

        (
            dataframe.writeTo(self._settings.iceberg_raw_table)
            .append()
        )
        logger.info("Raw records written to Iceberg successfully")

    def get_latest_published_at(self) -> datetime:
        self._ensure_namespace()
        if not self._table_exists(self._settings.iceberg_raw_table):
            logger.info("Raw Iceberg table does not exist yet, using 7-day lookback")
            return datetime.now(timezone.utc) - timedelta(days=self._settings.youtube_lookback_days)

        dataframe = self._spark.table(self._settings.iceberg_raw_table)
        latest_row = dataframe.select(spark_max(col("published_at")).alias("latest_published_at")).collect()[0]
        latest_published_at: Optional[datetime] = latest_row["latest_published_at"]
        if latest_published_at is None:
            return datetime.now(timezone.utc) - timedelta(days=self._settings.youtube_lookback_days)

        if latest_published_at.tzinfo is None:
            return latest_published_at.replace(tzinfo=timezone.utc)
        return latest_published_at.astimezone(timezone.utc)

    def _table_exists(self, table_name: str) -> bool:
        return self._spark.catalog.tableExists(table_name)

    def _ensure_namespace(self) -> None:
        self._spark.sql(
            f"CREATE NAMESPACE IF NOT EXISTS {self._settings.iceberg_namespace}"
        )
