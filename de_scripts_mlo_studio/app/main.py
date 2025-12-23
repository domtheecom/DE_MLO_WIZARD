from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .logging_utils import LogBus, configure_logging
from .ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    base_dir = Path(__file__).resolve().parents[1]

    log_bus = LogBus()
    logger = configure_logging(log_bus, base_dir / "user_data")

    window = MainWindow(base_dir=base_dir, log_bus=log_bus, logger=logger)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
