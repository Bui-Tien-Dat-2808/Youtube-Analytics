from __future__ import annotations

from dataclasses import dataclass

from application.services.dbt_service import DbtService


@dataclass(slots=True)
class RunDbtModelsUseCase:
    dbt_service: DbtService

    def execute(self) -> None:
        self.dbt_service.run()
