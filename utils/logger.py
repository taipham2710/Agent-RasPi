import logging
import sys
from datetime import datetime
from config import Config


def setup_logger():
    """Setup logger configuration"""
    logger = logging.getLogger("iot_agent")
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("agent.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def log_system_info(logger):
    """Log system information"""
    import psutil

    logger.info(f"Device Name: {Config.DEVICE_NAME}")
    logger.info(f"Device ID: {Config.DEVICE_ID}")
    logger.info(f"CPU Usage: {psutil.cpu_percent()}%")
    logger.info(f"Memory Usage: {psutil.virtual_memory().percent}%")
    logger.info(f"Disk Usage: {psutil.disk_usage('/').percent}%")
