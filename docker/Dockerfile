FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies including build tools for psutil
RUN apk add --no-cache curl gcc musl-dev python3-dev linux-headers

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (copy everything except files ignored by .dockerignore)
COPY . .

# Create non-root user
RUN adduser -D -u 1000 agent && chown -R agent:agent /app
USER agent

# Health check (optional, adjust or remove <url> as needed)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# Run the main agent (use run_dev.py for dev/demo)
CMD ["python", "run_dev.py"] 