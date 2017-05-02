import logging.config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("paper")

logger.debug('This is debug message')
logger.info('This is info message')
logger.warning('This is warning message')