from __future__ import annotations

from dataclasses import dataclass

from infrastructure.database.postgres_loader import PostgresWarehouseLoader
from shared.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class WarehouseService:
    loader: PostgresWarehouseLoader

    def load_clean_layer_to_postgres(self) -> None:
        logger.info("Starting PostgreSQL warehouse load")
        self.loader.load_dimensions_and_facts()
        logger.info("PostgreSQL warehouse load completed")
