#Standart library imports
import logging

logger = logging.getLogger(__name__)
logger.propagate = False
levels = {
    "info": logging.INFO,
    "error": logging.ERROR,
}

logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s ')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

logger.addHandler(consoleHandler)