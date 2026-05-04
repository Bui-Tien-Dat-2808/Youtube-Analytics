from __future__ import annotations

from dataclasses import dataclass

from infrastructure.iceberg.spark_iceberg_processor import SparkIcebergProcessor
from shared.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class SparkProcessingService:
    processor: SparkIcebergProcessor

    def process_raw_to_clean(self) -> None:
        logger.info("Starting raw to clean processing with Spark")
        self.processor.run_cleaning_job()
        logger.info("Clean layer processing completed")
