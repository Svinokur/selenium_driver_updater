#Standart library imports
import logging

logger = logging.getLogger('selenium_driver_updater')
logger.propagate = False
levels = {
    "info": logging.INFO,
    "error": logging.ERROR,
}

logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s ')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

logger.addHandler(consoleHandler)
