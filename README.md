# IoT Agent for Raspberry Pi

Một agent Python module hóa để quản lý thiết bị IoT trên Raspberry Pi với khả năng tự động cập nhật Docker containers và gửi dữ liệu hệ thống lên backend.

## Tính năng

- ✅ **Module hóa**: Cấu trúc code rõ ràng, dễ bảo trì
- ✅ **Tự động cập nhật**: Pull và chạy Docker images mới từ Docker Hub
- ✅ **Monitoring hệ thống**: Theo dõi CPU, Memory, Disk, Network
- ✅ **Heartbeat**: Gửi trạng thái định kỳ lên backend
- ✅ **Logging**: Gửi logs và alerts lên backend
- ✅ **Retry logic**: Xử lý lỗi mạng và retry tự động
- ✅ **Graceful shutdown**: Dừng an toàn khi nhận signal
- ✅ **Multi-agent**: Chạy nhiều agents với Docker Compose

## Cấu trúc Project

```
Agent-RasPi/
├── agent.py                 # Main agent class
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image
├── docker-compose.yml     # Production multi-agent setup
├── docker-compose.dev.yml # Development multi-agent setup
├── Makefile               # Management commands
├── env.example            # Environment variables template
├── test_agent.py          # Test script
├── run_dev.py             # Development runner
├── scripts/
│   └── manage-agents.sh   # Management script
├── utils/
│   ├── __init__.py
│   └── logger.py          # Logging utilities
└── services/
    ├── __init__.py
    ├── backend_client.py  # Backend API client
    ├── docker_manager.py  # Docker operations
    └── system_monitor.py  # System monitoring
```

## 🚀 Quick Start với Docker Compose

### 1. Cài đặt dependencies

```bash
make install
# hoặc
pip install -r requirements.txt
```

### 2. Chạy development agents (3 agents)

```bash
# Build và start development agents
make dev-start

# Xem logs
make dev-logs

# Xem status
make dev-status

# Stop agents
make dev-stop
```

### 3. Chạy production agents

```bash
# Build và start production agents
make start

# Xem logs
make logs

# Xem status
make status

# Stop agents
make stop
```

## 📋 Docker Compose Commands

### Development Mode (Nhanh, debug)

```bash
# Start 3 development agents
docker-compose -f docker-compose.dev.yml up -d

# Xem logs của tất cả agents
docker-compose -f docker-compose.dev.yml logs -f

# Xem logs của agent cụ thể
docker-compose -f docker-compose.dev.yml logs -f agent-dev-01

# Stop development agents
docker-compose -f docker-compose.dev.yml down
```

### Production Mode (Đầy đủ hệ thống)

```bash
# Start toàn bộ hệ thống (agents + backend + frontend)
docker-compose up -d

# Xem logs
docker-compose logs -f

# Stop toàn bộ hệ thống
docker-compose down
```

## 🛠️ Management Commands

### Sử dụng Makefile

```bash
# Xem tất cả commands
make help

# Development
make dev-start    # Start development agents
make dev-stop     # Stop development agents
make dev-logs     # Xem logs
make dev-status   # Xem status

# Production
make start        # Start production system
make stop         # Stop production system
make logs         # Xem logs
make status       # Xem status

# Utility
make build        # Build images
make clean        # Clean up everything
make test         # Run tests
```

### Sử dụng Script

```bash
# Xem help
./scripts/manage-agents.sh

# Development
./scripts/manage-agents.sh start dev
./scripts/manage-agents.sh stop dev
./scripts/manage-agents.sh logs "" dev

# Production
./scripts/manage-agents.sh start
./scripts/manage-agents.sh stop
./scripts/manage-agents.sh logs
```

## 🔧 Cấu hình

### Environment Variables

| Variable | Default | Mô tả |
|----------|---------|-------|
| `DOCKER_IMAGE` | `taipham2710/agent:latest` | Docker image để pull |
| `BACKEND_URL` | `http://localhost:8000` | URL của backend API |
| `DEVICE_ID` | `1` | ID của thiết bị |
| `DEVICE_NAME` | `hostname` | Tên thiết bị |
| `HEARTBEAT_INTERVAL` | `300` | Khoảng thời gian gửi heartbeat (giây) |
| `UPDATE_CHECK_INTERVAL` | `600` | Khoảng thời gian kiểm tra update (giây) |

### Multi-Agent Configuration

Mỗi agent có thể có cấu hình khác nhau:

```yaml
# Agent 1 - Raspberry Pi chính
agent-01:
  environment:
    - DEVICE_ID=1
    - DEVICE_NAME=raspberry-pi-01
    - HEARTBEAT_INTERVAL=300

# Agent 2 - Raspberry Pi phụ  
agent-02:
  environment:
    - DEVICE_ID=2
    - DEVICE_NAME=raspberry-pi-02
    - HEARTBEAT_INTERVAL=300

# Agent 3 - Sensor (nhanh hơn)
agent-03:
  environment:
    - DEVICE_ID=3
    - DEVICE_NAME=raspberry-pi-sensor
    - HEARTBEAT_INTERVAL=180
    - LOG_INTERVAL=30
```

## 📊 Monitoring

### Xem status của tất cả agents

```bash
make status
# hoặc
docker-compose ps
```

### Xem logs realtime

```bash
# Tất cả agents
make logs

# Agent cụ thể
make logs-agent-01
make logs-agent-02
make logs-agent-03
```

### Xem system resources

```bash
docker stats
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Build and Deploy Agents
on:
  push:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push Docker images
        run: |
          docker build -t taipham2710/agent:latest .
          docker push taipham2710/agent:latest
```

### Auto-deploy với Docker Compose

```bash
# Pull latest images và restart
docker-compose pull
docker-compose up -d
```

## 🧪 Testing

### Test individual modules

```bash
python test_agent.py
```

### Test với Docker

```bash
# Build và test
docker build -t test-agent .
docker run --rm test-agent python test_agent.py
```

### Test multi-agent setup

```bash
# Start development agents
make dev-start

# Check logs
make dev-logs

# Stop và clean
make dev-stop
make clean
```

## 🚨 Troubleshooting

### Lỗi Docker Compose

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild images
docker-compose build --no-cache
```

### Lỗi Network

```bash
# Check network
docker network ls
docker network inspect agent-raspi_iot-network
```

### Lỗi Volume

```bash
# Check volumes
docker volume ls
docker volume inspect agent-raspi_logs
```

## 📈 Scaling

### Thêm agent mới

1. Thêm service vào `docker-compose.yml`:

```yaml
agent-04:
  build: .
  container_name: iot-agent-04
  environment:
    - DEVICE_ID=4
    - DEVICE_NAME=raspberry-pi-04
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
```

2. Start agent mới:

```bash
docker-compose up -d agent-04
```

### Horizontal Scaling

```bash
# Scale agents
docker-compose up -d --scale agent-01=3
```

## 🎯 Next Steps

1. **Backend Development**: Tạo FastAPI backend
2. **Frontend Development**: Tạo React dashboard
3. **K3s Deployment**: Triển khai lên Kubernetes
4. **Monitoring**: Thêm Prometheus/Grafana
5. **Security**: Thêm authentication/authorization
