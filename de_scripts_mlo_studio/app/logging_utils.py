from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Optional


class LogBus:
    def __init__(self) -> None:
        self._subscribers: list[Callable[[str], None]] = []

    def subscribe(self, callback: Callable[[str], None]) -> None:
        self._subscribers.append(callback)

    def publish(self, message: str) -> None:
        for callback in self._subscribers:
            callback(message)


class UILogHandler(logging.Handler):
    def __init__(self, bus: LogBus) -> None:
        super().__init__()
        self.bus = bus

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self.bus.publish(message)


def configure_logging(log_bus: Optional[LogBus], log_dir: Path) -> logging.Logger:
    logger = logging.getLogger("de_scripts_mlo_studio")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "studio.log"

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if log_bus is not None:
        ui_handler = UILogHandler(log_bus)
        ui_handler.setFormatter(formatter)
        logger.addHandler(ui_handler)

    return logger
