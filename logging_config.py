import logging
import colorlog
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Create formatter for color logs
color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

# Create formatters for file logs
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console Handler with colors
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(color_formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    # File Handler for all logs
    log_file = os.path.join(LOGS_DIR, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # Error File Handler
    error_file = os.path.join(LOGS_DIR, f'{name}_errors_{datetime.now().strftime("%Y%m%d")}.log')
    error_file_handler = logging.FileHandler(error_file)
    error_file_handler.setFormatter(file_formatter)
    error_file_handler.setLevel(logging.ERROR)
    logger.addHandler(error_file_handler)

    return logger