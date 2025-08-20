# How to Deploy ScraperV4 to Production

This guide covers deploying ScraperV4 in production environments with monitoring, security, and scalability considerations.

## Prerequisites

- ScraperV4 working in development environment
- Docker and docker-compose installed
- Basic understanding of containerization
- Access to production server/cloud platform
- SSL certificate for HTTPS (recommended)

## Overview

Production deployment involves:
- **Containerization**: Docker-based deployment for consistency
- **Environment Configuration**: Production-ready settings
- **Security Hardening**: Authentication, HTTPS, and access controls
- **Monitoring Setup**: Health checks, logging, and alerting
- **Scalability Planning**: Load balancing and horizontal scaling
- **Backup Strategy**: Data persistence and recovery

## Docker Deployment

### 1. Create Production Dockerfile

```dockerfile
# Production Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SCRAPERV4_ENV=production

# Create app user for security
RUN groupadd -r scraperv4 && useradd --no-log-init -r -g scraperv4 scraperv4

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY web/ ./web/
COPY templates/ ./templates/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p data/jobs data/results data/exports logs && \
    chown -R scraperv4:scraperv4 /app

# Switch to non-root user
USER scraperv4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Expose port
EXPOSE 8080

# Start application
CMD ["python", "-m", "src.main"]
```

### 2. Create docker-compose.yml for Production

```yaml
version: '3.8'

services:
  scraperv4:
    build: .
    container_name: scraperv4_app
    restart: unless-stopped
    environment:
      - SCRAPERV4_ENV=production
      - SCRAPERV4_PORT=8080
      - SCRAPERV4_DEBUG=false
      - SCRAPERV4_LOG_LEVEL=INFO
      - SCRAPERV4_MAX_CONCURRENT_JOBS=3
      - SCRAPERV4_DATA_DIR=/app/data
    volumes:
      - scraperv4_data:/app/data
      - scraperv4_logs:/app/logs
      - ./config/production.env:/app/.env:ro
    ports:
      - "8080:8080"
    networks:
      - scraperv4_network
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    container_name: scraperv4_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - scraperv4_network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: scraperv4_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - scraperv4_logs:/var/log/nginx
    networks:
      - scraperv4_network
    depends_on:
      - scraperv4
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    container_name: scraperv4_prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - scraperv4_network

  grafana:
    image: grafana/grafana:latest
    container_name: scraperv4_grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "3000:3000"
    networks:
      - scraperv4_network

volumes:
  scraperv4_data:
  scraperv4_logs:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  scraperv4_network:
    driver: bridge
```

### 3. Production Environment Configuration

```bash
# config/production.env
# Basic Configuration
SCRAPERV4_ENV=production
SCRAPERV4_PORT=8080
SCRAPERV4_DEBUG=false
SCRAPERV4_LOG_LEVEL=INFO

# Security
SCRAPERV4_SECRET_KEY=your-super-secret-key-here
SCRAPERV4_API_KEY=your-api-key-here
SCRAPERV4_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database/Cache
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# Scraping Configuration
SCRAPERV4_MAX_CONCURRENT_JOBS=3
SCRAPERV4_DEFAULT_DELAY=2.0
SCRAPERV4_PROXY_TIMEOUT=30
SCRAPERV4_REQUEST_TIMEOUT=30

# Storage
SCRAPERV4_DATA_DIR=/app/data
SCRAPERV4_EXPORT_DIR=/app/data/exports
SCRAPERV4_LOG_DIR=/app/logs

# Monitoring
SCRAPERV4_METRICS_ENABLED=true
SCRAPERV4_HEALTH_CHECK_ENABLED=true

# Third-party Services
SENTRY_DSN=your-sentry-dsn-here
GRAFANA_PASSWORD=your-grafana-password
```

## Load Balancer and Reverse Proxy Setup

### 1. Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=5r/s;

    # Upstream servers
    upstream scraperv4_backend {
        least_conn;
        server scraperv4:8080 max_fails=3 fail_timeout=30s;
        # Add more instances for load balancing
        # server scraperv4_2:8080 max_fails=3 fail_timeout=30s;
    }

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Health check endpoint
        location /health {
            proxy_pass http://scraperv4_backend/api/health;
            access_log off;
        }
        
        # Redirect all other traffic to HTTPS
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Client max body size for file uploads
        client_max_body_size 50M;

        # API endpoints with rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://scraperv4_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Web interface
        location / {
            limit_req zone=general burst=10 nodelay;
            
            proxy_pass http://scraperv4_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for real-time updates
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Static files (if served directly by nginx)
        location /static/ {
            alias /app/web/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Health check
        location /health {
            proxy_pass http://scraperv4_backend/api/health;
            access_log off;
        }
    }
}
```

## Monitoring and Alerting

### 1. Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'scraperv4'
    static_configs:
      - targets: ['scraperv4:8080']
    metrics_path: '/api/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 2. Application Health Checks

```python
# Add to src/web/api_routes.py
from flask import jsonify
import psutil
import time

@app.route('/api/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint."""
    try:
        # Basic application status
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0',
            'environment': os.getenv('SCRAPERV4_ENV', 'development')
        }
        
        # System metrics
        health_status['system'] = {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }
        
        # Application metrics
        from src.services.scraping_service import ScrapingService
        service = ScrapingService()
        
        health_status['application'] = {
            'active_jobs': len(service.get_active_jobs()),
            'total_jobs_processed': service.get_job_statistics()['total_jobs'],
            'database_status': 'connected'  # Add actual DB check
        }
        
        # Check if any critical thresholds are exceeded
        if (health_status['system']['cpu_usage'] > 90 or 
            health_status['system']['memory_usage'] > 90 or
            health_status['system']['disk_usage'] > 90):
            health_status['status'] = 'degraded'
            return jsonify(health_status), 503
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 503

@app.route('/api/readiness', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe."""
    try:
        # Check if application is ready to receive traffic
        # Add checks for database connections, external services, etc.
        
        return jsonify({
            'status': 'ready',
            'timestamp': time.time()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': time.time()
        }), 503

@app.route('/api/metrics', methods=['GET'])
def metrics_endpoint():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    
    # Add custom metrics here
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
```

### 3. Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "ScraperV4 Production Dashboard",
    "panels": [
      {
        "title": "System Metrics",
        "type": "graph",
        "targets": [
          {
            "expr": "cpu_usage",
            "legendFormat": "CPU Usage"
          },
          {
            "expr": "memory_usage",
            "legendFormat": "Memory Usage"
          }
        ]
      },
      {
        "title": "Scraping Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(scraperv4_requests_total[5m])",
            "legendFormat": "Requests/sec"
          },
          {
            "expr": "scraperv4_active_jobs",
            "legendFormat": "Active Jobs"
          }
        ]
      },
      {
        "title": "Error Rates",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(scraperv4_errors_total[5m])",
            "legendFormat": "Errors/sec"
          }
        ]
      }
    ]
  }
}
```

## Security Hardening

### 1. Authentication and Authorization

```python
# Add to src/web/auth.py
from functools import wraps
from flask import request, jsonify
import jwt
import os

def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            # Remove 'Bearer ' prefix
            token = token.replace('Bearer ', '')
            
            # Verify JWT token
            jwt.decode(
                token, 
                os.getenv('SCRAPERV4_SECRET_KEY'), 
                algorithms=['HS256']
            )
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_api_key(f):
    """Decorator to require API key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key != os.getenv('SCRAPERV4_API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# Apply to API routes
@app.route('/api/scraping/start', methods=['POST'])
@require_api_key
def start_scraping():
    # Implementation here
    pass
```

### 2. Input Validation and Sanitization

```python
# Add to src/utils/validation_utils.py
import re
from urllib.parse import urlparse

class SecurityValidator:
    """Security validation utilities."""
    
    @staticmethod
    def validate_url(url):
        """Validate URL for security issues."""
        try:
            parsed = urlparse(url)
            
            # Check for valid scheme
            if parsed.scheme not in ['http', 'https']:
                raise ValueError("Invalid URL scheme")
            
            # Check for local/private IPs
            if SecurityValidator.is_private_ip(parsed.hostname):
                raise ValueError("Private IP addresses not allowed")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")
    
    @staticmethod
    def is_private_ip(hostname):
        """Check if hostname is a private IP."""
        import ipaddress
        
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_loopback
        except:
            return False
    
    @staticmethod
    def sanitize_input(text, max_length=1000):
        """Sanitize text input."""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>&"\'`]', '', str(text))
        
        # Truncate to max length
        return sanitized[:max_length]
    
    @staticmethod
    def validate_template_selectors(selectors):
        """Validate CSS selectors for security."""
        dangerous_patterns = [
            'javascript:',
            'data:',
            'vbscript:',
            '<script',
            '</script'
        ]
        
        for selector in selectors.values():
            selector_str = str(selector).lower()
            for pattern in dangerous_patterns:
                if pattern in selector_str:
                    raise ValueError(f"Dangerous pattern detected: {pattern}")
        
        return True
```

## Backup and Recovery

### 1. Data Backup Strategy

```bash
#!/bin/bash
# scripts/backup.sh

# Configuration
BACKUP_DIR="/backups/scraperv4"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup application data
echo "Backing up application data..."
docker run --rm \
    --volumes-from scraperv4_app \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar czf "/backup/scraperv4_data_$DATE.tar.gz" /app/data

# Backup Redis data
echo "Backing up Redis data..."
docker exec scraperv4_redis redis-cli BGSAVE
docker run --rm \
    --volumes-from scraperv4_redis \
    -v "$BACKUP_DIR":/backup \
    alpine \
    cp /data/dump.rdb "/backup/redis_dump_$DATE.rdb"

# Backup configuration
echo "Backing up configuration..."
tar czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    config/ \
    docker-compose.yml \
    nginx/

# Clean up old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

### 2. Disaster Recovery Procedures

```bash
#!/bin/bash
# scripts/restore.sh

# Configuration
BACKUP_DIR="/backups/scraperv4"
RESTORE_DATE=$1

if [ -z "$RESTORE_DATE" ]; then
    echo "Usage: $0 YYYYMMDD_HHMMSS"
    exit 1
fi

echo "Restoring ScraperV4 from backup: $RESTORE_DATE"

# Stop services
echo "Stopping services..."
docker-compose down

# Restore application data
echo "Restoring application data..."
docker run --rm \
    -v scraperv4_data:/app/data \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar xzf "/backup/scraperv4_data_$RESTORE_DATE.tar.gz" -C /

# Restore Redis data
echo "Restoring Redis data..."
docker run --rm \
    -v redis_data:/data \
    -v "$BACKUP_DIR":/backup \
    alpine \
    cp "/backup/redis_dump_$RESTORE_DATE.rdb" /data/dump.rdb

# Start services
echo "Starting services..."
docker-compose up -d

echo "Restore completed"
```

## Deployment Automation

### 1. CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run tests
        run: pytest tests/
      
      - name: Security scan
        run: |
          pip install bandit safety
          bandit -r src/
          safety check

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        uses: appleboy/ssh-action@v0.1.7
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/scraperv4
            git pull origin main
            docker-compose down
            docker-compose build
            docker-compose up -d
            
            # Wait for health check
            sleep 30
            curl -f http://localhost/health || exit 1
```

### 2. Rolling Updates Script

```bash
#!/bin/bash
# scripts/rolling-update.sh

# Zero-downtime rolling update

echo "Starting rolling update..."

# Build new image
docker-compose build scraperv4

# Scale up with new version
docker-compose up -d --scale scraperv4=2 --no-recreate

# Wait for new instance to be healthy
echo "Waiting for new instance to be healthy..."
sleep 30

# Check health
if curl -f http://localhost/health; then
    echo "New instance is healthy, removing old instance..."
    
    # Remove old instance
    OLD_CONTAINER=$(docker ps --filter "name=scraperv4_app" --format "{{.ID}}" | head -1)
    docker stop $OLD_CONTAINER
    docker rm $OLD_CONTAINER
    
    echo "Rolling update completed successfully"
else
    echo "New instance failed health check, rolling back..."
    
    # Remove failed new instance
    NEW_CONTAINER=$(docker ps --filter "name=scraperv4_app" --format "{{.ID}}" | tail -1)
    docker stop $NEW_CONTAINER
    docker rm $NEW_CONTAINER
    
    echo "Rollback completed"
    exit 1
fi
```

## Production Checklist

### Pre-Deployment Checklist

- [ ] **Security Configuration**
  - [ ] Environment variables properly set
  - [ ] SSL certificates installed
  - [ ] Authentication configured
  - [ ] Input validation implemented
  - [ ] Rate limiting configured

- [ ] **Performance Optimization**
  - [ ] Resource limits configured
  - [ ] Caching enabled
  - [ ] Connection pooling set up
  - [ ] Monitoring configured

- [ ] **Reliability**
  - [ ] Health checks implemented
  - [ ] Backup strategy in place
  - [ ] Log rotation configured
  - [ ] Error handling tested

- [ ] **Monitoring**
  - [ ] Prometheus metrics configured
  - [ ] Grafana dashboards set up
  - [ ] Alerting rules defined
  - [ ] Log aggregation working

### Post-Deployment Verification

```bash
#!/bin/bash
# scripts/verify-deployment.sh

echo "Verifying production deployment..."

# Check health endpoint
echo "Checking health endpoint..."
if curl -f https://yourdomain.com/health; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    exit 1
fi

# Check API endpoints
echo "Checking API endpoints..."
if curl -f -H "X-API-Key: $API_KEY" https://yourdomain.com/api/templates; then
    echo "✓ API endpoints accessible"
else
    echo "✗ API endpoints failed"
    exit 1
fi

# Check monitoring
echo "Checking monitoring..."
if curl -f http://localhost:9090/targets; then
    echo "✓ Prometheus is running"
else
    echo "✗ Prometheus check failed"
fi

if curl -f http://localhost:3000/api/health; then
    echo "✓ Grafana is running"
else
    echo "✗ Grafana check failed"
fi

# Check resource usage
echo "Checking resource usage..."
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo "Deployment verification completed"
```

## Expected Outcomes

After successful production deployment:

1. **High Availability**: 99.9% uptime with load balancing and failover
2. **Security**: Encrypted traffic, authentication, and input validation
3. **Scalability**: Horizontal scaling capability with load balancing
4. **Monitoring**: Real-time visibility into system performance and health
5. **Backup & Recovery**: Automated backups with tested recovery procedures
6. **Performance**: Optimized for production workloads with resource management

## Success Criteria

- [ ] Application deployed and accessible via HTTPS
- [ ] Health checks passing consistently
- [ ] Monitoring dashboards showing metrics
- [ ] Security measures implemented and tested
- [ ] Backup and recovery procedures working
- [ ] Load balancing and scaling operational
- [ ] Documentation updated with production procedures