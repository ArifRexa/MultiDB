import os
import logging
from logging.handlers import TimedRotatingFileHandler
from config.settings import LOG_FILE_ROTATION_INTERVAL

LEVEL = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# Create a logger instance
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

for folder_name in list(LEVEL):
    log_path = f"logs/{folder_name}/"
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_formatter = logging.Formatter('%(levelname)s - %(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(stream_formatter)
logger.addHandler(handler)

# Create separate log handlers for each log level
debug_handler = TimedRotatingFileHandler(filename='logs/debug/debug.log', when=LOG_FILE_ROTATION_INTERVAL, interval=1, backupCount=0)
debug_handler.setLevel(logging.DEBUG)
debug_handler.filter = lambda record: record.levelno == logging.DEBUG
debug_handler.setFormatter(formatter)
logger.addHandler(debug_handler)

info_handler = TimedRotatingFileHandler(filename='logs/info/info.log', when=LOG_FILE_ROTATION_INTERVAL, interval=1, backupCount=0)
info_handler.setLevel(logging.INFO)
info_handler.filter = lambda record: record.levelno == logging.INFO
info_handler.setFormatter(formatter)
logger.addHandler(info_handler)

warning_handler = TimedRotatingFileHandler(filename='logs/warning/warning.log', when=LOG_FILE_ROTATION_INTERVAL, interval=1, backupCount=0)
warning_handler.setLevel(logging.WARNING)
warning_handler.filter = lambda record: record.levelno == logging.WARNING
warning_handler.setFormatter(formatter)
logger.addHandler(warning_handler)

error_handler = TimedRotatingFileHandler(filename='logs/error/error.log', when=LOG_FILE_ROTATION_INTERVAL, interval=1, backupCount=0)
error_handler.setLevel(logging.ERROR)
error_handler.filter = lambda record: record.levelno == logging.ERROR
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)

critical_handler = TimedRotatingFileHandler(filename='logs/critical/critical.log', when=LOG_FILE_ROTATION_INTERVAL, interval=1, backupCount=0)
critical_handler.setLevel(logging.CRITICAL)
critical_handler.filter = lambda record: record.levelno == logging.CRITICAL
critical_handler.setFormatter(formatter)
logger.addHandler(critical_handler)
