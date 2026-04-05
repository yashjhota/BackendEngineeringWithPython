import logging
import sys
from datetime import datetime


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # format — timestamp + level + message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # console handler — prints to terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # file handler — writes to file
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# create app-wide logger
logger = setup_logger("user_management")
