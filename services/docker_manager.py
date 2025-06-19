import docker
import time
from typing import Optional, Dict, Any
from config import Config
import logging
from docker.errors import NotFound

logger = logging.getLogger('iot_agent')

class DockerManager:
    """Manager for Docker operations"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
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
            logger.info(f"Successfully pulled image: {image.tags[0] if image.tags else 'untagged'}")
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
            logger.info(f"Container {Config.CONTAINER_NAME} not found, nothing to remove")
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
                "BACKEND_URL": Config.BACKEND_URL
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
                network_mode="host"  # Use host network for better performance
            )
            
            logger.info(f"Container started successfully with ID: {container.short_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            return False
    
    def update_container(self) -> bool:
        """Update container with latest image"""
        try:
            # Pull latest image
            if not self.pull_latest_image():
                return False
            
            # Stop and remove old container
            if not self.stop_container():
                return False
            
            if not self.remove_container():
                return False
            
            # Start new container
            if not self.start_container():
                return False
            
            logger.info("Container updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update container: {e}")
            return False
    
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
                "running": container.status == "running"
            }
        except NotFound:
            return {"status": "not_found", "running": False}
        except Exception as e:
            logger.error(f"Error getting container status: {e}")
            return {"status": "error", "error": str(e), "running": False} 