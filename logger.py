import logging
import os
from settings import Settings


def setup_logger(log_file="conversion.log"):
    if os.path.exists(log_file):
        os.remove(log_file)

    logger = logging.getLogger("VideoConverter")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
