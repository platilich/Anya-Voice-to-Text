import logging
import sys
from pathlib import Path
import os




def setup_logger(name: str = "bot") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    BASE_DIR = Path(__file__).resolve().parent.parent
    logs_dir = BASE_DIR / "logs"
    os.makedirs(logs_dir, exist_ok=True)


    # --- to avoid duplicating handlers when re-importing ---
    if logger.handlers:
        return logger

    # --- format ---
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # --- output to the console ---
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # save to file
    file_handler = logging.FileHandler(BASE_DIR / "bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()