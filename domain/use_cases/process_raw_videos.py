from __future__ import annotations

from dataclasses import dataclass

from application.services.spark_processing_service import SparkProcessingService


@dataclass(slots=True)
class ProcessRawVideosUseCase:
    spark_processing_service: SparkProcessingService

    def execute(self) -> None:
        self.spark_processing_service.process_raw_to_clean()
