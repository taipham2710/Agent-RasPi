import logging
import time
from typing import Any, Dict, Optional

import docker
from docker.errors import NotFound

from config import Config

logger = logging.getLogger("iot_agent")


class DockerManager:
    """Manager for Docker operations with rollback support"""

    def __init__(self):
        try:
            self.client = docker.from_env()
            self.previous_image_tag = None  # Store previous image for rollback
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise

    def save_current_state(self) -> bool:
        """Save current container state for potential rollback"""
        try:
            current_tag = self.get_current_image_tag()
            if current_tag:
                self.previous_image_tag = current_tag
                logger.info(f"Saved current image for rollback: {current_tag}")
                return True
            else:
                logger.warning("No current image found to save for rollback")
                return False
        except Exception as e:
            logger.error(f"Failed to save current state: {e}")
            return False

    def rollback_to_previous(self) -> bool:
        """Rollback to previous image if available"""
        if not self.previous_image_tag:
            logger.error("No previous image available for rollback")
            return False

        try:
            logger.info(
                f"Starting rollback to previous image: {self.previous_image_tag}"
            )

            # Stop and remove current container
            if not self.stop_container():
                logger.warning("Failed to stop container during rollback")

            if not self.remove_container():
                logger.warning("Failed to remove container during rollback")

            # Start container with previous image
            if not self.start_container_with_image(self.previous_image_tag):
                logger.error("Failed to start container with previous image")
                return False

            logger.info(f"Successfully rolled back to: {self.previous_image_tag}")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def start_container_with_image(self, image_tag: str) -> bool:
        """Start container with specific image tag"""
        try:
            logger.info(f"Starting container with image: {image_tag}")

            # Default environment variables
            env_vars = {
                "DEVICE_ID": Config.DEVICE_ID,
                "DEVICE_NAME": Config.DEVICE_NAME,
                "BACKEND_URL": Config.BACKEND_URL,
            }

            container = self.client.containers.run(
                image_tag,
                name=Config.CONTAINER_NAME,
                environment=env_vars,
                detach=True,
                restart_policy={"Name": "always"},
                network_mode="host",
            )

            logger.info(
                f"Container started successfully with image {image_tag}, ID: {container.short_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start container with image {image_tag}: {e}")
            return False

    def get_current_image_tag(self) -> Optional[str]:
        """Get current running container's image tag"""
        try:
            container = self.client.containers.get(Config.CONTAINER_NAME)
            if container.image and container.image.tags:
                return container.image.tags[0]
            return None
        except NotFound:
            logger.warning(f"Container {Config.CONTAINER_NAME} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting current image tag: {e}")
            return None

    def pull_latest_image(self) -> bool:
        """Pull the latest image from Docker Hub"""
        try:
            logger.info(f"Pulling latest image: {Config.DOCKER_IMAGE}")
            image = self.client.images.pull(Config.DOCKER_IMAGE)
            logger.info(
                f"Successfully pulled image: {image.tags[0] if image.tags else 'untagged'}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to pull image: {e}")
            return False

    def stop_container(self) -> bool:
        """Stop the running container"""
        try:
            container = self.client.containers.get(Config.CONTAINER_NAME)
            logger.info(f"Stopping container: {Config.CONTAINER_NAME}")
            container.stop(timeout=30)
            logger.info("Container stopped successfully")
            return True
        except NotFound:
            logger.info(f"Container {Config.CONTAINER_NAME} not found, nothing to stop")
            return True
        except Exception as e:
            logger.error(f"Failed to stop container: {e}")
            return False

    def remove_container(self) -> bool:
        """Remove the container"""
        try:
            container = self.client.containers.get(Config.CONTAINER_NAME)
            logger.info(f"Removing container: {Config.CONTAINER_NAME}")
            container.remove(force=True)
            logger.info("Container removed successfully")
            return True
        except NotFound:
            logger.info(
                f"Container {Config.CONTAINER_NAME} not found, nothing to remove"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to remove container: {e}")
            return False

    def start_container(self, environment: Optional[Dict[str, str]] = None) -> bool:
        """Start a new container"""
        try:
            logger.info(f"Starting new container: {Config.CONTAINER_NAME}")

            # Default environment variables
            env_vars = {
                "DEVICE_ID": Config.DEVICE_ID,
                "DEVICE_NAME": Config.DEVICE_NAME,
                "BACKEND_URL": Config.BACKEND_URL,
            }

            # Merge with provided environment variables
            if environment:
                env_vars.update(environment)

            container = self.client.containers.run(
                Config.DOCKER_IMAGE,
                name=Config.CONTAINER_NAME,
                environment=env_vars,
                detach=True,
                restart_policy={"Name": "always"},
                network_mode="host",  # Use host network for better performance
            )

            logger.info(f"Container started successfully with ID: {container.short_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            return False

    def update_container(self) -> bool:
        """Update container with latest image and rollback support"""
        try:
            logger.info("Starting container update with rollback support")

            # Save current state for potential rollback
            if not self.save_current_state():
                logger.warning(
                    "Could not save current state, but continuing with update"
                )

            # Pull latest image
            if not self.pull_latest_image():
                logger.error("Failed to pull latest image, attempting rollback")
                return self.rollback_to_previous()

            # Stop and remove old container
            if not self.stop_container():
                logger.error("Failed to stop container, attempting rollback")
                return self.rollback_to_previous()

            if not self.remove_container():
                logger.error("Failed to remove container, attempting rollback")
                return self.rollback_to_previous()

            # Start new container
            if not self.start_container():
                logger.error("Failed to start new container, attempting rollback")
                return self.rollback_to_previous()

            # Verify new container is running
            time.sleep(5)  # Wait a bit for container to fully start
            status = self.get_container_status()
            if not status.get("running", False):
                logger.error("New container is not running, attempting rollback")
                return self.rollback_to_previous()

            logger.info("Container updated successfully")
            return True

        except Exception as e:
            logger.error(f"Update failed with exception: {e}, attempting rollback")
            return self.rollback_to_previous()

    def get_container_status(self) -> Dict[str, Any]:
        """Get container status information"""
        try:
            container = self.client.containers.get(Config.CONTAINER_NAME)
            image_tag = "untagged"
            if container.image and container.image.tags:
                image_tag = container.image.tags[0]

            return {
                "status": container.status,
                "image": image_tag,
                "created": container.attrs["Created"],
                "ports": container.attrs["NetworkSettings"]["Ports"],
                "running": container.status == "running",
            }
        except NotFound:
            return {"status": "not_found", "running": False}
        except Exception as e:
            logger.error(f"Error getting container status: {e}")
            return {"status": "error", "error": str(e), "running": False}
