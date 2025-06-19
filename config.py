import os
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the IoT Agent"""
    
    # Docker settings
    DOCKER_IMAGE = os.getenv("DOCKER_IMAGE", "taipham2710/agent:latest")
    CONTAINER_NAME = os.getenv("CONTAINER_NAME", "iot_app")
    
    # Backend settings
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    BACKEND_TIMEOUT = int(os.getenv("BACKEND_TIMEOUT", "30"))
    
    # Device settings
    DEVICE_NAME = os.getenv("DEVICE_NAME", socket.gethostname())
    DEVICE_ID = os.getenv("DEVICE_ID", "1")
    
    # Timing settings
    HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "300"))  # 5 minutes
    UPDATE_CHECK_INTERVAL = int(os.getenv("UPDATE_CHECK_INTERVAL", "600"))  # 10 minutes
    LOG_INTERVAL = int(os.getenv("LOG_INTERVAL", "60"))  # 1 minute
    
    # Retry settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 