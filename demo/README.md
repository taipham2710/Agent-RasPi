# IoT Agent Demo Script

This directory contains `demo_script.py` to simulate various IoT device scenarios for testing and presentation.

## How to run the demo

**Run the full demo (all scenarios):**
```bash
python demo_script.py
```

**Run a single scenario (replace N with 1-5):**
```bash
python demo_script.py N
```

**Set the backend URL via the BACKEND_URL environment variable:**
```bash
BACKEND_URL=http://your-backend-url:8000 python demo_script.py
```

## Demo Scenarios

1. **Basic IoT Operations:**
   - Simulates device heartbeats and system monitoring logs.
2. **Deployment Operations:**
   - Simulates deployments, including both successful and failed deployments with rollback.
3. **Bulk Operations:**
   - Simulates bulk update and deployment across multiple devices.
4. **Failure and Recovery:**
   - Simulates system failure, device going offline, and recovery.
5. **Real-time Monitoring:**
   - Simulates real-time monitoring data from devices over a period of time.

---

**Requirements:**
- Python 3.8+
- Install dependencies from the root of Agent-RasPi:
  ```bash
  pip install -r ../requirements.txt
  ``` 