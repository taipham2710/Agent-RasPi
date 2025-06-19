import time
import signal
import sys
import schedule
from typing import Optional
from config import Config
from utils.logger import setup_logger, log_system_info
from services.backend_client import BackendClient
from services.docker_manager import DockerManager
from services.system_monitor import SystemMonitor

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
            raise
    
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
        log_system_info(self.logger)
        
        # Schedule tasks
        self._setup_schedules()
        
        # Initial tasks
        self._perform_heartbeat()
        self._perform_system_monitoring()
        
        # Main loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying
        
        self.logger.info("IoT Agent stopped")
    
    def stop(self):
        """Stop the IoT Agent"""
        self.logger.info("Stopping IoT Agent...")
        self.running = False
    
    def _setup_schedules(self):
        """Setup scheduled tasks"""
        # Heartbeat
        schedule.every(Config.HEARTBEAT_INTERVAL).seconds.do(self._perform_heartbeat)
        
        # System monitoring
        schedule.every(Config.LOG_INTERVAL).seconds.do(self._perform_system_monitoring)
        
        # Container updates
        schedule.every(Config.UPDATE_CHECK_INTERVAL).seconds.do(self._perform_container_update)
        
        self.logger.info("Scheduled tasks configured")
    
    def _perform_heartbeat(self):
        """Perform heartbeat operation"""
        try:
            success = self.backend_client.send_heartbeat()
            if success:
                self.logger.debug("Heartbeat sent successfully")
            else:
                self.logger.warning("Failed to send heartbeat")
        except Exception as e:
            self.logger.error(f"Error during heartbeat: {e}")
    
    def _perform_system_monitoring(self):
        """Perform system monitoring"""
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
    
    def _perform_container_update(self):
        """Perform container update check"""
        try:
            # Check for updates from backend
            update_info = self.backend_client.check_for_updates()
            
            if update_info and update_info.get("update_available", False):
                self.logger.info("Update available, performing container update")
                
                # Send log before update
                self.backend_client.send_log("Starting container update")
                
                # Perform update
                success = self.docker_manager.update_container()
                
                if success:
                    self.backend_client.send_log("Container updated successfully")
                else:
                    self.backend_client.send_log("Container update failed", "ERROR")
            else:
                self.logger.debug("No updates available")
                
        except Exception as e:
            self.logger.error(f"Error during container update check: {e}")
    
    def get_status(self) -> dict:
        """Get agent status"""
        try:
            container_status = self.docker_manager.get_container_status()
            system_health = self.system_monitor.get_health_status()
            
            return {
                "agent_running": self.running,
                "container_status": container_status,
                "system_health": system_health,
                "config": {
                    "device_name": Config.DEVICE_NAME,
                    "device_id": Config.DEVICE_ID,
                    "backend_url": Config.BACKEND_URL
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {"error": str(e)}

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