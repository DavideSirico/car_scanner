# logger_config.py
import logging

def setup_logger():
    # Create the logger (can use root or create a named one)
    logger = logging.getLogger('car_scanner')  # Create a logger for the entire app
    logger.setLevel(logging.DEBUG)  # Set the logging level

    # Create a file handler
    file_handler = logging.FileHandler('debug_log.log')
    file_handler.setLevel(logging.DEBUG)

    # Create a stream handler (for console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Define a common format for log messages
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Add handlers to the logger
    if not logger.hasHandlers():  # Avoid adding multiple handlers if already added
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger, file_handler