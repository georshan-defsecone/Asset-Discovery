# logging_config.py
import logging
import os

def setup_logging():
    """Set up logging configuration."""
    logger = logging.getLogger()

    # Check if any handler is already present (prevents adding multiple handlers)
    if not logger.hasHandlers():
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Set up a file handler to save logs
        file_handler = logging.FileHandler("logs/application.log")
        file_handler.setLevel(logging.INFO)
        
        # Create a formatter
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        logger.addHandler(file_handler)

        # Set the root logger to INFO level
        logger.setLevel(logging.INFO)
        
        # Optionally, add a console handler if you want console logs too
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
