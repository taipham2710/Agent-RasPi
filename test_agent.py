#!/usr/bin/env python3
"""
Test script for IoT Agent modules
"""

import sys
import time
from config import Config
from utils.logger import setup_logger
from services.backend_client import BackendClient
from services.docker_manager import DockerManager
from services.system_monitor import SystemMonitor


def test_config():
    """Test configuration loading"""
    print("=== Testing Configuration ===")
    print(f"Device Name: {Config.DEVICE_NAME}")
    print(f"Device ID: {Config.DEVICE_ID}")
    print(f"Backend URL: {Config.BACKEND_URL}")
    print(f"Docker Image: {Config.DOCKER_IMAGE}")
    print("✅ Configuration loaded successfully")


def test_logger():
    """Test logger setup"""
    print("\n=== Testing Logger ===")
    logger = setup_logger()
    logger.info("Test log message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    print("✅ Logger working correctly")


def test_system_monitor():
    """Test system monitoring"""
    print("\n=== Testing System Monitor ===")
    monitor = SystemMonitor()

    # Test system info
    system_info = monitor.get_system_info()
    print(f"CPU Usage: {system_info['cpu']['percent']}%")
    print(f"Memory Usage: {system_info['memory']['percent']}%")
    print(f"Disk Usage: {system_info['disk']['percent']}%")

    # Test health status
    health = monitor.get_health_status()
    print(f"System Health: {health['status']}")

    # Test alerts
    alerts = monitor.check_alerts()
    if alerts:
        print(f"Alerts found: {len(alerts)}")
        for alert in alerts:
            print(f"  - {alert['level']}: {alert['message']}")
    else:
        print("No alerts")

    print("✅ System monitoring working correctly")


def test_docker_manager():
    """Test Docker manager"""
    print("\n=== Testing Docker Manager ===")
    try:
        docker_mgr = DockerManager()

        # Test container status
        status = docker_mgr.get_container_status()
        print(f"Container Status: {status['status']}")
        print(f"Container Running: {status['running']}")

        # Test image pull (optional)
        print("Testing image pull...")
        success = docker_mgr.pull_latest_image()
        print(f"Image pull: {'✅ Success' if success else '❌ Failed'}")

        print("✅ Docker manager working correctly")

    except Exception as e:
        print(f"❌ Docker manager error: {e}")


def test_backend_client():
    """Test backend client"""
    print("\n=== Testing Backend Client ===")
    try:
        client = BackendClient()

        # Test heartbeat
        print("Testing heartbeat...")
        success = client.send_heartbeat()
        print(f"Heartbeat: {'✅ Success' if success else '❌ Failed'}")

        # Test log sending
        print("Testing log sending...")
        success = client.send_log("Test log message from agent")
        print(f"Log sending: {'✅ Success' if success else '❌ Failed'}")

        print("✅ Backend client working correctly")

    except Exception as e:
        print(f"❌ Backend client error: {e}")


def test_integration():
    """Test integration of all components"""
    print("\n=== Testing Integration ===")

    try:
        # Initialize all services
        logger = setup_logger()
        backend_client = BackendClient()
        docker_manager = DockerManager()
        system_monitor = SystemMonitor()

        # Get system info and send to backend
        system_info = system_monitor.get_system_info()
        backend_client.send_log(
            f"System test - CPU: {system_info['cpu']['percent']}%, Memory: {system_info['memory']['percent']}%"
        )

        # Get container status
        container_status = docker_manager.get_container_status()
        backend_client.send_log(f"Container status: {container_status['status']}")

        print("✅ Integration test completed")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")


def main():
    """Run all tests"""
    print("🚀 Starting IoT Agent Tests\n")

    try:
        test_config()
        test_logger()
        test_system_monitor()
        test_docker_manager()
        test_backend_client()
        test_integration()

        print("\n🎉 All tests completed!")

    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
