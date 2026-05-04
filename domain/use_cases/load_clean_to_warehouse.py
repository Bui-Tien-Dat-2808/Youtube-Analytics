from __future__ import annotations

from dataclasses import dataclass

from application.services.warehouse_service import WarehouseService


@dataclass(slots=True)
class LoadCleanToWarehouseUseCase:
    warehouse_service: WarehouseService

    def execute(self) -> None:
        self.warehouse_service.load_clean_layer_to_postgres()
