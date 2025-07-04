import psutil
import time
from typing import Dict, Any
from config import Config
import logging

logger = logging.getLogger("iot_agent")


class SystemMonitor:
    """Monitor system resources and health"""

    def __init__(self):
        self.last_cpu_percent = 0
        self.last_memory_percent = 0

    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Memory information
            memory = psutil.virtual_memory()

            # Disk information
            disk = psutil.disk_usage("/")

            # Network information
            network = psutil.net_io_counters()

            # Boot time
            boot_time = psutil.boot_time()

            return {
                "timestamp": time.time(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": {
                        "current": cpu_freq.current if cpu_freq else 0,
                        "min": cpu_freq.min if cpu_freq else 0,
                        "max": cpu_freq.max if cpu_freq else 0,
                    },
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                "system": {"boot_time": boot_time, "uptime": time.time() - boot_time},
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status with thresholds"""
        system_info = self.get_system_info()

        if "error" in system_info:
            return {"status": "error", "message": system_info["error"]}

        # Define thresholds
        cpu_threshold = 80
        memory_threshold = 85
        disk_threshold = 90

        # Check health
        cpu_ok = system_info["cpu"]["percent"] < cpu_threshold
        memory_ok = system_info["memory"]["percent"] < memory_threshold
        disk_ok = system_info["disk"]["percent"] < disk_threshold

        overall_status = "healthy" if all([cpu_ok, memory_ok, disk_ok]) else "warning"

        return {
            "status": overall_status,
            "checks": {
                "cpu": {
                    "status": "ok" if cpu_ok else "warning",
                    "value": system_info["cpu"]["percent"],
                    "threshold": cpu_threshold,
                },
                "memory": {
                    "status": "ok" if memory_ok else "warning",
                    "value": system_info["memory"]["percent"],
                    "threshold": memory_threshold,
                },
                "disk": {
                    "status": "ok" if disk_ok else "warning",
                    "value": system_info["disk"]["percent"],
                    "threshold": disk_threshold,
                },
            },
            "system_info": system_info,
        }

    def check_alerts(self) -> list:
        """Check for system alerts"""
        alerts = []
        health = self.get_health_status()

        if health["status"] == "error":
            alerts.append(
                {
                    "level": "ERROR",
                    "message": f"System monitoring error: {health.get('message', 'Unknown error')}",
                    "timestamp": time.time(),
                }
            )
            return alerts

        checks = health["checks"]

        if not checks["cpu"]["status"] == "ok":
            alerts.append(
                {
                    "level": "WARNING",
                    "message": f"High CPU usage: {checks['cpu']['value']}%",
                    "timestamp": time.time(),
                }
            )

        if not checks["memory"]["status"] == "ok":
            alerts.append(
                {
                    "level": "WARNING",
                    "message": f"High memory usage: {checks['memory']['value']}%",
                    "timestamp": time.time(),
                }
            )

        if not checks["disk"]["status"] == "ok":
            alerts.append(
                {
                    "level": "WARNING",
                    "message": f"High disk usage: {checks['disk']['value']}%",
                    "timestamp": time.time(),
                }
            )

        return alerts
