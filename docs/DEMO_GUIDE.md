# 🎬 IoT Device Management System - Demo Guide

## 📋 Overview

This guide provides everything you need to run an impressive demo of the IoT Device Management System with 20 agents. The demo showcases real-world IoT scenarios including device monitoring, deployment operations, bulk updates, failure recovery, and real-time monitoring.

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Ensure you have Docker and Docker Compose installed
docker --version
docker-compose --version

# Ensure backend is running
curl http://locaclhost:8000/health
```

### 2. Start the Demo
```bash
# Navigate to Agent-RasPi directory
cd Agent-RasPi

# Start 20 agents
./scripts/demo_manager.sh start

# Check status
./scripts/demo_manager.sh status
```

### 3. Run Demo Scenarios
```bash
# Run all scenarios
./scripts/demo_manager.sh run-demo

# Or run individual scenarios
cd ../Backend-RasPi
python3 demo_script.py 1  # Basic IoT Operations
python3 demo_script.py 2  # Deployment Operations
python3 demo_script.py 3  # Bulk Operations
python3 demo_script.py 4  # Failure and Recovery
python3 demo_script.py 5  # Real-time Monitoring
```

## 🎯 Demo Scenarios

### Scenario 1: Basic IoT Operations (2-3 minutes)
**What happens:**
- 5 devices send heartbeat messages
- System monitoring data (CPU, Memory, Disk)
- Real-time status updates

**Demo points:**
- Show dashboard with live device status
- Demonstrate polling-based real-time updates
- Show device health monitoring

### Scenario 2: Deployment Operations (3-4 minutes)
**What happens:**
- 3 successful deployments
- 1 failed deployment with rollback
- Slack notifications for each event

**Demo points:**
- Show deployment process
- Demonstrate rollback capability
- Show Slack integration
- Highlight error handling

### Scenario 3: Bulk Operations (2-3 minutes)
**What happens:**
- Bulk update for all 20 devices
- Simultaneous deployment simulation
- Mass notification system

**Demo points:**
- Show scalability (20 devices)
- Demonstrate bulk operations
- Show system performance under load

### Scenario 4: Failure and Recovery (2-3 minutes)
**What happens:**
- Simulated system failure
- Device going offline
- Automatic recovery
- Error notifications

**Demo points:**
- Show fault tolerance
- Demonstrate recovery mechanisms
- Show alert system

### Scenario 5: Real-time Monitoring (2-3 minutes)
**What happens:**
- Continuous monitoring for 10 seconds
- Random device performance data
- Live dashboard updates

**Demo points:**
- Show real-time capabilities
- Demonstrate monitoring system
- Show data visualization

## 📊 Demo Management Commands

### Basic Operations
```bash
# Start demo
./scripts/demo_manager.sh start

# Stop demo
./scripts/demo_manager.sh stop

# Check status
./scripts/demo_manager.sh status

# View logs
./scripts/demo_manager.sh logs
```

### Advanced Operations
```bash
# Scale to specific number of agents
./scripts/demo_manager.sh scale 10

# Restart specific agent
./scripts/demo_manager.sh restart-agent 5

# Run demo scenarios
./scripts/demo_manager.sh run-demo

# Clean up everything
./scripts/demo_manager.sh clean
```

## 🖥️ Demo Setup

### 1. Backend Setup
```bash
cd Backend-RasPi

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend-raspi

# Install dependencies
npm install

# Start frontend
npm run dev
```

### 3. Slack Integration
Add to your `.env` file:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 📈 Demo Flow

### Pre-Demo Setup (5 minutes)
1. **Start Backend**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. **Start Frontend**: `npm run dev`
3. **Start 20 Agents**: `./scripts/demo_manager.sh start`
4. **Verify Setup**: `./scripts/demo_manager.sh status`

### Demo Presentation (15-20 minutes)

#### Introduction (2 minutes)
- "Today I'll demonstrate an IoT Device Management System"
- "We have 20 Raspberry Pi devices connected and monitored"
- "The system includes real-time monitoring, deployment, and recovery"

#### Live Demo (12-15 minutes)
1. **Dashboard Overview** (2 min)
   - Show 20 devices online
   - Explain real-time polling
   - Show device status distribution

2. **Run Demo Scenarios** (10-12 min)
   - Execute each scenario
   - Explain what's happening
   - Show Slack notifications
   - Demonstrate features

3. **Interactive Demo** (1-2 min)
   - Scale down to 10 agents: `./scripts/demo_manager.sh scale 10`
   - Restart specific agent: `./scripts/demo_manager.sh restart-agent 5`
   - Show logs: `./scripts/demo_manager.sh logs 3`

#### Conclusion (1-2 minutes)
- "This demonstrates a production-ready IoT management system"
- "Key features: scalability, real-time monitoring, fault tolerance"
- "Ready for deployment in real-world IoT environments"

## 🎭 Presentation Tips

### Technical Points to Highlight
1. **Scalability**: 20 agents running simultaneously
2. **Real-time**: Polling-based updates every 5 seconds
3. **Fault Tolerance**: Automatic recovery and rollback
4. **Monitoring**: Comprehensive system health tracking
5. **Integration**: Slack notifications and API endpoints

### Demo Script
```
"Welcome to our IoT Device Management System demo. 
Today I'll show you how we can manage 20 Raspberry Pi devices 
in a real-time, scalable environment.

Let me start by showing you our dashboard with all 20 devices 
currently online and monitoring their health..."

[Run through scenarios while explaining each feature]

"As you can see, this system demonstrates enterprise-level 
IoT management capabilities with real-time monitoring, 
automated deployment, and robust error handling."
```

## 🔧 Troubleshooting

### Common Issues
1. **Backend not accessible**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health
   
   # Restart backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Agents not starting**
   ```bash
   # Check Docker status
   docker ps
   
   # Restart agents
   ./scripts/demo_manager.sh restart
   ```

3. **Slack notifications not working**
   ```bash
   # Check environment variable
   echo $SLACK_WEBHOOK_URL
   
   # Test webhook
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test message"}' \
     $SLACK_WEBHOOK_URL
   ```

### Performance Tips
- Use `./scripts/demo_manager.sh scale 10` for lighter demos
- Monitor system resources with `./scripts/demo_manager.sh status`
- Clean up after demo with `./scripts/demo_manager.sh clean`

## 📝 Demo Checklist

### Before Demo
- [ ] Backend running and accessible
- [ ] Frontend running and accessible
- [ ] 20 agents started and online
- [ ] Slack webhook configured
- [ ] Demo script ready
- [ ] Browser tabs open (dashboard, API docs)

### During Demo
- [ ] Show dashboard with 20 devices
- [ ] Run all 5 scenarios
- [ ] Show Slack notifications
- [ ] Demonstrate scaling
- [ ] Show logs and monitoring
- [ ] Handle any errors gracefully

### After Demo
- [ ] Stop all agents
- [ ] Clean up containers
- [ ] Document any issues
- [ ] Prepare for next demo

## 🎉 Success Metrics

A successful demo should demonstrate:
- ✅ 20 agents running simultaneously
- ✅ Real-time dashboard updates
- ✅ Successful deployment operations
- ✅ Automatic rollback on failure
- ✅ Slack notifications working
- ✅ System scaling capabilities
- ✅ Comprehensive monitoring
- ✅ Professional presentation flow

## 📞 Support

If you encounter issues during the demo:
1. Check the troubleshooting section above
2. Use `./scripts/demo_manager.sh status` for diagnostics
3. Check logs with `./scripts/demo_manager.sh logs`
4. Restart components as needed

**Good luck with your demo! 🚀** 