# encoding=utf8
import logging
from conf import config


def setup_logger(name=None, level=logging.DEBUG):
    filehandler = logging.FileHandler(filename=config.logfile, encoding="utf8")
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(filehandler)
    return logger
