from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_root: Path = Field(default=Path(__file__).resolve().parents[2])
    log_level: str = Field(default="INFO")

    youtube_api_key: str
    youtube_keyword_source: str = Field(default="google_trends_rss")
    youtube_keyword_fallback: Optional[str] = Field(default=None)
    youtube_search_keyword: Optional[str] = Field(default=None)
    youtube_channel_id: Optional[str] = Field(default=None)
    youtube_trends_geo: str = Field(default="US")
    youtube_top_keywords_limit: int = Field(default=10)
    youtube_search_order: str = Field(default="viewCount")
    youtube_page_size: int = Field(default=25)
    youtube_max_pages: int = Field(default=4)
    youtube_lookback_days: int = Field(default=7)

    iceberg_catalog_name: str = Field(default="local")
    iceberg_catalog_type: str = Field(default="hadoop")
    iceberg_namespace: str = Field(default="youtube")
    iceberg_warehouse_path: str = Field(default="file:///opt/project/data/warehouse")
    iceberg_raw_table: str = Field(default="local.youtube.raw_videos")
    iceberg_clean_table: str = Field(default="local.youtube.clean_videos")

    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="youtube_analytics")
    postgres_user: str = Field(default="youtube")
    postgres_password: str = Field(default="youtube")
    postgres_schema: str = Field(default="analytics")

    airflow_executor: str = Field(default="LocalExecutor")
    airflow_webserver_port: int = Field(default=8080)

    dbt_project_dir: Path = Field(default=Path("/opt/project/dbt"))
    dbt_profiles_dir: Path = Field(default=Path("/opt/project/dbt"))

    spark_master_url: str = Field(default="local[*]")
    spark_jars_packages: Optional[str] = Field(
        default="org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2,org.postgresql:postgresql:42.7.4"
    )
    local_stage_file_path: Path = Field(default=Path("/opt/project/data/staging/youtube_raw_batch.jsonl"))

    @property
    def postgres_jdbc_url(self) -> str:
        return (
            f"jdbc:postgresql://{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
