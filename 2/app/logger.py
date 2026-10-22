import logging
import os


def setup_logger(log_file):
    logger = logging.getLogger("app")
    if logger.handlers:
        return logger

    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    for handler in (logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()):
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    return logger
