import logging
import os

log_level = os.environ.get('LOG_LEVEL', 'ERROR')
logging.basicConfig(level=getattr(logging, log_level))

def log_error(message):
    logging.error(message)

def log_info(message):
    if log_level in ['INFO', 'DEBUG']:
        logging.info(message)

def log_warning(message):
    logging.warning(message)
