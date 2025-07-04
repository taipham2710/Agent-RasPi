#!/usr/bin/env python3
"""
Development script for running IoT Agent with debug logging
"""

import os
import sys
from agent import IoTAgent


def setup_dev_environment():
    """Setup development environment"""
    # Set debug logging
    os.environ["LOG_LEVEL"] = "DEBUG"

    # Set shorter intervals for development
    os.environ["HEARTBEAT_INTERVAL"] = "30"  # 30 seconds
    os.environ["LOG_INTERVAL"] = "10"  # 10 seconds
    os.environ["UPDATE_CHECK_INTERVAL"] = "60"  # 1 minute

    print("🔧 Development environment configured:")
    print(f"  - LOG_LEVEL: {os.environ.get('LOG_LEVEL')}")
    print(f"  - HEARTBEAT_INTERVAL: {os.environ.get('HEARTBEAT_INTERVAL')}s")
    print(f"  - LOG_INTERVAL: {os.environ.get('LOG_INTERVAL')}s")
    print(f"  - UPDATE_CHECK_INTERVAL: {os.environ.get('UPDATE_CHECK_INTERVAL')}s")


def main():
    """Run agent in development mode"""
    print("🚀 Starting IoT Agent in Development Mode\n")

    try:
        # Setup development environment
        setup_dev_environment()

        # Create and start agent
        agent = IoTAgent()

        print("\n📊 Agent Status:")
        status = agent.get_status()
        print(f"  - Running: {status['agent_running']}")
        print(
            f"  - Device: {status['config']['device_name']} (ID: {status['config']['device_id']})"
        )
        print(f"  - Backend: {status['config']['backend_url']}")

        print("\n🔄 Starting agent... (Press Ctrl+C to stop)")
        agent.start()

    except KeyboardInterrupt:
        print("\n⏹️  Development mode stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Development mode failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
