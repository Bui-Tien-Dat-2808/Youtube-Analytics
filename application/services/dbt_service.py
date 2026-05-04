from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from shared.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class DbtService:
    project_dir: Path
    profiles_dir: Path

    def run(self) -> None:
        logger.info("Running dbt models")
        subprocess.run(
            ["dbt", "run", "--project-dir", str(self.project_dir), "--profiles-dir", str(self.profiles_dir)],
            check=True,
        )
        logger.info("dbt run completed successfully")
