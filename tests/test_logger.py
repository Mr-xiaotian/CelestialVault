import sys, pytest
from loguru import logger
import logging

logger.remove()
logger.add(sys.stderr, level="INFO")

def test_log():
    logger.info('"logger success"')
    print("print success")
    logging.info("logging success")