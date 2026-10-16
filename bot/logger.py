import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os



BASE_DIR = Path(__file__).resolve().parent.parent
logs_dir = BASE_DIR / "logs"
os.makedirs(logs_dir, exist_ok=True)


logger = logging.getLogger("VideoNoteBot")
logger.setLevel(logging.DEBUG)


formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)



file_handler = RotatingFileHandler(
    logs_dir / "bot.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)


file_handler.setFormatter(formatter)
logger.addHandler(file_handler)