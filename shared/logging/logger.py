from __future__ import annotations

import logging
from logging.config import dictConfig

from shared.config.settings import get_settings


def configure_logging() -> None:
    if logging.getLogger().hasHandlers():
        return

    settings = get_settings()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": settings.log_level,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": settings.log_level,
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
