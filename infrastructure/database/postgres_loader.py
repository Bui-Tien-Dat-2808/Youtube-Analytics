from __future__ import annotations

import psycopg2

from infrastructure.iceberg.spark_session_factory import build_spark_session
from shared.config.settings import Settings
from shared.logging.logger import get_logger

logger = get_logger(__name__)


class PostgresWarehouseLoader:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._spark = build_spark_session(settings, app_name="youtube-warehouse-loader")

    def load_dimensions_and_facts(self) -> None:
        logger.info("Reading clean layer from Iceberg table %s", self._settings.iceberg_clean_table)
        clean_df = self._spark.table(self._settings.iceberg_clean_table)

        dim_channel_df = clean_df.selectExpr(
            "channel_id",
            "channel_title as channel_name",
        ).dropDuplicates(["channel_id"])
        dim_keyword_df = clean_df.selectExpr(
            "keyword as keyword_name"
        ).where("keyword is not null").dropDuplicates(["keyword_name"])
        fact_video_df = clean_df.select(
            "video_id",
            "channel_id",
            "publish_date",
            "views",
            "likes",
            "comments",
        ).dropDuplicates(["video_id"])
        bridge_video_keyword_df = clean_df.selectExpr(
            "video_id",
            "keyword as keyword_name",
        ).where("keyword is not null").dropDuplicates(["video_id", "keyword_name"])

        jdbc_url = self._settings.postgres_jdbc_url
        jdbc_properties = {
            "driver": "org.postgresql.Driver",
            "user": self._settings.postgres_user,
            "password": self._settings.postgres_password,
        }

        self._truncate_target_tables()

        logger.info("Writing dimension table dim_channel to PostgreSQL")
        (
            dim_channel_df.write.mode("append")
            .jdbc(
                url=jdbc_url,
                table="analytics.dim_channel",
                properties=jdbc_properties,
            )
        )

        logger.info("Writing dimension table dim_keyword to PostgreSQL")
        (
            dim_keyword_df.write.mode("append")
            .jdbc(
                url=jdbc_url,
                table="analytics.dim_keyword",
                properties=jdbc_properties,
            )
        )

        logger.info("Writing fact table fact_video to PostgreSQL")
        (
            fact_video_df.write.mode("append")
            .jdbc(
                url=jdbc_url,
                table="analytics.fact_video",
                properties=jdbc_properties,
            )
        )

        logger.info("Writing bridge table bridge_video_keyword to PostgreSQL")
        (
            bridge_video_keyword_df.write.mode("append")
            .jdbc(
                url=jdbc_url,
                table="analytics.bridge_video_keyword",
                properties=jdbc_properties,
            )
        )
        logger.info("Warehouse tables loaded to PostgreSQL")

    def _truncate_target_tables(self) -> None:
        logger.info("Truncating PostgreSQL warehouse tables before reload")
        with psycopg2.connect(
            host=self._settings.postgres_host,
            port=self._settings.postgres_port,
            dbname=self._settings.postgres_db,
            user=self._settings.postgres_user,
            password=self._settings.postgres_password,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE analytics.bridge_video_keyword")
                cursor.execute("TRUNCATE TABLE analytics.fact_video")
                cursor.execute("TRUNCATE TABLE analytics.dim_keyword")
                cursor.execute("TRUNCATE TABLE analytics.dim_channel")
            connection.commit()
