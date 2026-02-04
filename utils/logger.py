"""Логирование."""
import logging
import sys
from pathlib import Path

from config import LOG_PATH

LOG_PATH = Path(LOG_PATH)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Настройка логов в файл и консоль."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        fh.setFormatter(formatter)
        root.addHandler(fh)
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        root.addHandler(ch)
    return logging.getLogger("bot")
