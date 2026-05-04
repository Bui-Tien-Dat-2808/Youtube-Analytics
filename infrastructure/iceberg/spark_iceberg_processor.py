from __future__ import annotations

from pyspark.sql.functions import col, lower, regexp_replace, to_date, to_timestamp, trim

from infrastructure.iceberg.spark_session_factory import build_spark_session
from shared.config.settings import Settings
from shared.logging.logger import get_logger

logger = get_logger(__name__)


class SparkIcebergProcessor:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._spark = build_spark_session(settings, app_name="youtube-clean-processing")

    def run_cleaning_job(self) -> None:
        if not self._spark.catalog.tableExists(self._settings.iceberg_raw_table):
            logger.info("Raw Iceberg table %s does not exist yet. Skipping cleaning job.", self._settings.iceberg_raw_table)
            return

        logger.info("Loading raw Iceberg table %s", self._settings.iceberg_raw_table)
        raw_df = self._spark.table(self._settings.iceberg_raw_table)

        clean_df = (
            raw_df.dropna(
                subset=[
                    "video_id",
                    "title",
                    "description",
                    "published_at",
                    "channel_id",
                    "channel_title",
                ]
            )
            .withColumn("title", trim(lower(regexp_replace(col("title"), r"[^a-zA-Z0-9\\s]", ""))))
            .withColumn(
                "description",
                trim(lower(regexp_replace(col("description"), r"[^a-zA-Z0-9\\s]", ""))),
            )
            .withColumn("published_at", to_timestamp(col("published_at")))
            .withColumn("views", col("views").cast("int"))
            .withColumn("likes", col("likes").cast("int"))
            .withColumn("comments", col("comments").cast("int"))
            .filter(col("views").isNull() | (col("views") >= 0))
            .filter(col("likes").isNull() | (col("likes") >= 0))
            .filter(col("comments").isNull() | (col("comments") >= 0))
            .dropDuplicates(["video_id", "keyword"])
            .withColumn("publish_date", to_date(col("published_at")))
        )

        logger.info("Writing clean records to Iceberg table %s", self._settings.iceberg_clean_table)
        self._spark.sql(
            f"""
            CREATE TABLE IF NOT EXISTS {self._settings.iceberg_clean_table} (
                video_id STRING,
                title STRING,
                description STRING,
                published_at TIMESTAMP,
                publish_date DATE,
                channel_id STRING,
                channel_title STRING,
                views INT,
                likes INT,
                comments INT,
                keyword STRING,
                ingestion_date STRING
            )
            USING iceberg
            PARTITIONED BY (publish_date, channel_id)
            """
        )

        (
            clean_df.writeTo(self._settings.iceberg_clean_table)
            .overwritePartitions()
        )
        logger.info("Clean Iceberg table write completed")
