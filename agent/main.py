import os
import re
import signal
import sys
import time

import requests
import schedule

from agent.client.backend_client import BackendClient
from agent.client.mqtt_client import MqttClient
from agent.config import Config
from agent.services.docker_manager import DockerManager
from agent.services.sensor_simulator import SensorSimulator
from agent.services.system_monitor import SystemMonitor
from agent.utils.logger import log_system_info, setup_logger


class IoTAgent:
    """Main IoT Agent class that coordinates all services"""

    def __init__(self):
        self.logger = setup_logger()
        self.running = False

        # Initialize services
        try:
            self.backend_client = BackendClient()
            self.docker_manager = DockerManager()
            self.system_monitor = SystemMonitor()
            self.logger.info("IoT Agent initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize IoT Agent: {e}")
            # Continue without Docker if it fails
            self.docker_manager = None
            self.system_monitor = None
            self.logger.warning("Continuing without Docker manager and system monitor")
        # Initialize MQTT client
        try:
            self.mqtt_client = MqttClient(
                broker=Config.MQTT_BROKER,
                port=Config.MQTT_PORT,
                topic_sub=Config.MQTT_TOPIC_SUB,
                topic_pub=Config.MQTT_TOPIC_PUB,
                on_message=self.handle_mqtt_message,
            )
            self.mqtt_client.start()
            self.logger.info("MQTT client started successfully")
            # Test publish to verify connection
            time.sleep(2)  # Wait for connection to establish
            self.mqtt_client.publish("Agent is online and ready to receive commands")
            self.logger.info("MQTT test message sent successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize MQTT client: {e}")
            self.mqtt_client = None
        # Initialize sensor simulator
        self.sensor_simulator = SensorSimulator()
        self.logger.info("Sensor simulator initialized successfully")

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""

        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def start(self):
        """Start the IoT Agent"""
        self.logger.info("Starting IoT Agent...")
        self.setup_signal_handlers()
        self.running = True

        # Log initial system info
        try:
            log_system_info(self.logger)
        except Exception as e:
            self.logger.warning(f"Could not log system info: {e}")

        # Schedule tasks
        self._setup_schedules()

        # Initial tasks
        self._perform_heartbeat()
        self._perform_system_monitoring()

        # Main loop
        consecutive_errors = 0
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
                consecutive_errors = 0  # Reset error counter on successful iteration
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                consecutive_errors += 1
                self.logger.error(
                    f"Error in main loop (attempt {consecutive_errors}): {e}"
                )

                # If too many consecutive errors, wait longer
                if consecutive_errors > Config.MAX_CONSECUTIVE_ERRORS:
                    self.logger.warning(
                        f"Too many consecutive errors, waiting {Config.ERROR_WAIT_TIME} seconds before retry"
                    )
                    time.sleep(Config.ERROR_WAIT_TIME)
                else:
                    time.sleep(Config.RETRY_DELAY)  # Wait before retrying

        self.logger.info("IoT Agent stopped")

    def stop(self):
        """Stop the IoT Agent"""
        self.logger.info("Stopping IoT Agent...")
        self.running = False

    def _setup_schedules(self):
        """Setup scheduled tasks"""
        # Heartbeat
        schedule.every(Config.HEARTBEAT_INTERVAL).seconds.do(self._perform_heartbeat)

        # System monitoring (only if available)
        if self.system_monitor:
            schedule.every(Config.LOG_INTERVAL).seconds.do(
                self._perform_system_monitoring
            )

        # Container updates (only if Docker is available)
        if self.docker_manager:
            schedule.every(Config.UPDATE_CHECK_INTERVAL).seconds.do(
                self._check_and_update_version
            )

        # Sensor data (every 10 seconds)
        schedule.every(10).seconds.do(self._send_sensor_data)

        self.logger.info("Scheduled tasks configured")

    def _parse_version(self, version_str):
        """Parse version string vX.Y to tuple (X, Y) for comparison"""
        match = re.match(r"v?(\d+)\.(\d+)", str(version_str))
        if match:
            return int(match.group(1)), int(match.group(2))
        return (0, 0)

    def _check_and_update_version(self):
        """Check Docker Hub for new version and update if needed (auto, không phụ thuộc biến môi trường tag)"""
        try:
            repo = os.getenv("DOCKER_IMAGE", Config.DOCKER_IMAGE)  # just repo, no tag
            if ":" in repo:
                repo = repo.split(":")[0]
            namespace, image_name = repo.split("/")

            def get_latest_dockerhub_tag(namespace, repo):
                url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo}/tags?page_size=100"
                try:
                    resp = requests.get(url, timeout=5)
                    tags = [t["name"] for t in resp.json().get("results", [])]
                    tags = [t for t in tags if re.match(r"v\d+\.\d+", t)]
                    tags.sort(
                        key=lambda x: tuple(map(int, re.findall(r"\d+", x))),
                        reverse=True,
                    )
                    return tags[0] if tags else "v1.0"
                except Exception:
                    return "v1.0"

            latest_version = get_latest_dockerhub_tag(namespace, image_name)
            # Get current image tag from running container
            if self.docker_manager is not None:
                current_image = self.docker_manager.get_current_image_tag() or repo
            else:
                current_image = repo
            if ":" in current_image:
                current_version = current_image.split(":")[-1]
            else:
                current_version = "v1.0"
            if self._parse_version(latest_version) > self._parse_version(
                current_version
            ):
                self.logger.info(
                    f"New version available: {latest_version} > {current_version}. Updating..."
                )
                self.backend_client.send_log(
                    f"Updating agent from {current_version} to {latest_version}",
                    level="info",
                    log_type="deploy",
                )
                new_image = f"{repo}:{latest_version}"
                success = False
                if self.docker_manager is not None:
                    # Pull new image
                    self.docker_manager.client.images.pull(new_image)
                    # Restart container with new image
                    success = self.docker_manager.update_container()
                else:
                    self.logger.error(
                        "Docker manager is not available. Cannot update container."
                    )
                if success:
                    self.logger.info(f"Agent updated to {latest_version} successfully.")
                    self.backend_client.send_log(
                        f"Agent updated to {latest_version} successfully.",
                        level="info",
                        log_type="deploy",
                    )
                else:
                    self.logger.error(
                        f"Agent update to {latest_version} failed. Rolling back."
                    )
                    self.backend_client.send_log(
                        f"Agent update to {latest_version} failed. Rolling back.",
                        level="error",
                        log_type="rollback",
                    )
                    if self.docker_manager is not None:
                        rollback_success = self.docker_manager.rollback_to_previous()
                        if rollback_success:
                            self.logger.info("Rollback to previous image successful.")
                            self.backend_client.send_log(
                                "Rollback to previous image successful.",
                                level="info",
                                log_type="rollback",
                            )
                        else:
                            self.logger.error("Rollback to previous image failed.")
                            self.backend_client.send_log(
                                "Rollback to previous image failed.",
                                level="error",
                                log_type="rollback",
                            )
            else:
                self.logger.info(
                    f"No update needed. Current: {current_version}, Latest: {latest_version}"
                )
        except Exception as e:
            self.logger.error(f"Error during version check/update: {e}")
            self.backend_client.send_log(
                f"Error during version check/update: {e}",
                level="error",
                log_type="rollback",
            )

    def _perform_heartbeat(self):
        """Perform heartbeat operation"""
        try:
            version = Config.DOCKER_IMAGE
            status = "online"
            success = self.backend_client.send_heartbeat(version=version, status=status)
            if success:
                self.logger.debug("Heartbeat sent successfully")
            else:
                self.logger.warning("Failed to send heartbeat")
        except Exception as e:
            self.logger.error(f"Error during heartbeat: {e}")

    def _perform_system_monitoring(self):
        """Perform system monitoring"""
        if not self.system_monitor:
            self.logger.debug("System monitor not available, skipping monitoring")
            return

        try:
            # Get system health
            health = self.system_monitor.get_health_status()

            # Send system info to backend
            if "system_info" in health:
                system_info = health["system_info"]
                self.backend_client.send_log(
                    f"System health: {health['status']}, "
                    f"CPU: {system_info['cpu']['percent']}%, "
                    f"Memory: {system_info['memory']['percent']}%, "
                    f"Disk: {system_info['disk']['percent']}%"
                )

            # Check for alerts
            alerts = self.system_monitor.check_alerts()
            for alert in alerts:
                self.backend_client.send_log(alert["message"], alert["level"])

        except Exception as e:
            self.logger.error(f"Error during system monitoring: {e}")

    def _send_sensor_data(self):
        """Send simulated sensor data via MQTT."""
        if not hasattr(self, "mqtt_client") or self.mqtt_client is None:
            self.logger.warning("MQTT client not available, skipping sensor data send")
            return
        data = self.sensor_simulator.get_data()
        self.logger.info(f"Publishing sensor data: {data}")
        self.mqtt_client.publish(f"SENSOR:{data}")

    def get_status(self) -> dict:
        """Get agent status"""
        try:
            status = {
                "agent_running": self.running,
                "config": {
                    "device_name": Config.DEVICE_NAME,
                    "device_id": Config.DEVICE_ID,
                    "backend_url": Config.BACKEND_URL,
                },
            }

            # Add Docker status if available
            if self.docker_manager:
                try:
                    container_status = self.docker_manager.get_container_status()
                    status["container_status"] = container_status
                except Exception as e:
                    status["container_status"] = {"error": str(e)}

            # Add system health if available
            if self.system_monitor:
                try:
                    system_health = self.system_monitor.get_health_status()
                    status["system_health"] = system_health
                except Exception as e:
                    status["system_health"] = {"error": str(e)}

            return status

        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {"error": str(e)}

    def handle_mqtt_message(self, topic, payload):
        self.logger.info(f"Received MQTT message: {payload} on topic: {topic}")
        if payload == "update":
            self.logger.info("Received update command via MQTT")
            self._check_and_update_version()
        elif payload == "restart":
            self.logger.info("Received restart command via MQTT")
            self.stop()
        elif payload == "status":
            self.logger.info("Received status command via MQTT")
            if self.mqtt_client:
                self.mqtt_client.publish(str(self.get_status()))
        else:
            self.logger.info(f"Unknown MQTT command: {payload}")


def main():
    """Main entry point"""
    try:
        agent = IoTAgent()
        agent.start()
    except Exception as e:
        print(f"Failed to start IoT Agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
