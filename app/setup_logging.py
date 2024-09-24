from datetime import datetime,timedelta
import logging
from logging.handlers import RotatingFileHandler

def get_current_time_for_file_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def setup_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the logger's level to DEBUG

    # Create a file handler
    file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    file_handler.setLevel(logging.DEBUG)  # Set the handler's level to DEBUG

    # Create a formatter and set it for the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    # logger.addHandler(file_handler)

    # # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Set the handler's level to DEBUG
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logging setup complete.")
    logging.getLogger('apscheduler').setLevel(logging.CRITICAL)