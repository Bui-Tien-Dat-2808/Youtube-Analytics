from __future__ import annotations

from application.services import (
    DbtService,
    SparkProcessingService,
    WarehouseService,
    YouTubeIngestionService,
)
from domain.use_cases import (
    FetchRecentVideosUseCase,
    LoadCleanToWarehouseUseCase,
    LoadRawVideosUseCase,
    ProcessRawVideosUseCase,
    RunDbtModelsUseCase,
)
from infrastructure.database import PostgresWarehouseLoader
from infrastructure.iceberg import IcebergVideoRepository, SparkIcebergProcessor
from infrastructure.storage import LocalStageRepository
from infrastructure.youtube_api import YouTubeApiClient
from shared.config import get_settings
from shared.logging import configure_logging


def fetch_youtube_data() -> None:
    configure_logging()
    settings = get_settings()
    service = YouTubeIngestionService(
        settings=settings,
        youtube_client=YouTubeApiClient(settings),
        iceberg_repository=IcebergVideoRepository(settings),
        stage_repository=LocalStageRepository(settings.local_stage_file_path),
    )
    use_case = FetchRecentVideosUseCase(ingestion_service=service)
    use_case.execute()


def load_raw_iceberg() -> None:
    configure_logging()
    settings = get_settings()
    service = YouTubeIngestionService(
        settings=settings,
        youtube_client=YouTubeApiClient(settings),
        iceberg_repository=IcebergVideoRepository(settings),
        stage_repository=LocalStageRepository(settings.local_stage_file_path),
    )
    use_case = LoadRawVideosUseCase(ingestion_service=service)
    use_case.execute()


def process_clean_data() -> None:
    configure_logging()
    settings = get_settings()
    use_case = ProcessRawVideosUseCase(
        spark_processing_service=SparkProcessingService(
            processor=SparkIcebergProcessor(settings)
        )
    )
    use_case.execute()


def load_to_postgres() -> None:
    configure_logging()
    settings = get_settings()
    use_case = LoadCleanToWarehouseUseCase(
        warehouse_service=WarehouseService(
            loader=PostgresWarehouseLoader(settings)
        )
    )
    use_case.execute()


def run_dbt_models() -> None:
    configure_logging()
    settings = get_settings()
    use_case = RunDbtModelsUseCase(
        dbt_service=DbtService(
            project_dir=settings.dbt_project_dir,
            profiles_dir=settings.dbt_profiles_dir,
        )
    )
    use_case.execute()
