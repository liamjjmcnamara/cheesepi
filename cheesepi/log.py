
import os
import logging

def get_logger(source=""):
    """Return logger for the specific file"""

    LOG_DIR = "/tmp"
    log_file = os.path.join(LOG_DIR, ".cheesepi.log")
    LOG_FORMAT = "%(asctime)s-%(name)s:%(levelname)s; %(message)s"
    logging.basicConfig(filename=log_file, level=logging.INFO, format=LOG_FORMAT)

    return logging.getLogger(source)
