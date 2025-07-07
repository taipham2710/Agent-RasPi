import logging
import time
from typing import Any, Dict, Optional

import requests

from agent.config import Config

logger = logging.getLogger("iot_agent")


class BackendClient:
    """Client for communicating with the backend API"""

    def __init__(self):
        self.base_url = Config.BACKEND_URL
        self.timeout = Config.BACKEND_TIMEOUT
        self.session = requests.Session()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        retries: Optional[int] = None,
    ) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        if retries is None:
            retries = Config.MAX_RETRIES

        url = f"{self.base_url}{endpoint}"

        for attempt in range(retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, timeout=self.timeout)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json() if response.content else None

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{retries + 1}): {e}"
                )
                if attempt < retries:
                    time.sleep(Config.RETRY_DELAY)
                else:
                    logger.error(f"Request failed after {retries + 1} attempts")
                    return None

    def send_heartbeat(
        self, version: Optional[str] = None, status: str = "online"
    ) -> bool:
        """Send heartbeat to backend"""
        data = {
            "name": Config.DEVICE_NAME,
            "version": version or Config.DOCKER_IMAGE,
            "status": status,
        }
        result = self._make_request("POST", "/device/heartbeat", data)
        if result:
            logger.info("Heartbeat sent successfully")
            return True
        else:
            logger.error("Failed to send heartbeat")
            return False

    def send_log(
        self, message: str, level: str = "info", log_type: str = "general"
    ) -> bool:
        """Send log message to backend"""
        data = {
            "device_id": Config.DEVICE_ID,
            "message": message,
            "log_level": level,
            "type": log_type,
        }
        result = self._make_request("POST", "/logs", data)
        if result:
            logger.debug(f"Log sent successfully: {message}")
            return True
        else:
            logger.error(f"Failed to send log: {message}")
            return False

    def get_device_status(self) -> Optional[Dict]:
        """Get device status from backend"""
        return self._make_request("GET", f"/device/{Config.DEVICE_ID}/status")

    def check_for_updates(self) -> Optional[Dict]:
        """Check for available updates"""
        return self._make_request("GET", f"/device/{Config.DEVICE_ID}/updates")
