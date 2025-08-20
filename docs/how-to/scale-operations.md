# How to Scale Scraping Operations

This guide covers scaling ScraperV4 for high-volume scraping operations with distributed processing, load balancing, and resource optimization.

## Prerequisites

- ScraperV4 working in production environment
- Understanding of distributed systems concepts
- Access to multiple servers or cloud infrastructure
- Redis or database for coordination
- Load balancing knowledge

## Overview

Scaling strategies include:
- **Horizontal Scaling**: Multiple ScraperV4 instances
- **Vertical Scaling**: Optimizing single instance performance
- **Distributed Queue Systems**: Coordinated job processing
- **Load Balancing**: Request distribution and failover
- **Resource Management**: Dynamic allocation and monitoring
- **Data Partitioning**: Efficient data handling at scale

## Horizontal Scaling Architecture

### 1. Multi-Instance Deployment

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  scraperv4-coordinator:
    build: .
    container_name: scraperv4_coordinator
    environment:
      - SCRAPERV4_ROLE=coordinator
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8080:8080"
    depends_on:
      - redis
    networks:
      - scraperv4_network

  scraperv4-worker:
    build: .
    environment:
      - SCRAPERV4_ROLE=worker
      - REDIS_URL=redis://redis:6379/0
      - WORKER_ID=${HOSTNAME}
    depends_on:
      - redis
      - scraperv4-coordinator
    networks:
      - scraperv4_network
    deploy:
      replicas: 3

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - scraperv4_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx-scale.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - scraperv4-coordinator
    networks:
      - scraperv4_network

volumes:
  redis_data:

networks:
  scraperv4_network:
    driver: bridge
```

### 2. Distributed Job Queue System

```python
# src/scaling/distributed_queue.py
import redis
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class JobStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class ScrapingJob:
    id: str
    name: str
    template_id: str
    target_url: str
    config: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    assigned_worker: Optional[str] = None
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

class DistributedJobQueue:
    """Distributed job queue using Redis for coordination."""
    
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url)
        self.worker_id = None
        self.heartbeat_interval = 30
        self.job_timeout = 3600  # 1 hour
        
    def register_worker(self, worker_id: str) -> bool:
        """Register worker instance."""
        self.worker_id = worker_id
        
        worker_info = {
            'id': worker_id,
            'registered_at': time.time(),
            'last_heartbeat': time.time(),
            'status': 'active',
            'current_jobs': []
        }
        
        self.redis_client.hset(
            "workers", 
            worker_id, 
            json.dumps(worker_info)
        )
        
        return True
    
    def submit_job(self, job: ScrapingJob) -> str:
        """Submit job to distributed queue."""
        job.id = job.id or str(uuid.uuid4())
        
        # Store job data
        self.redis_client.hset(
            "jobs",
            job.id,
            json.dumps(job.__dict__, default=str)
        )
        
        # Add to priority queue
        self.redis_client.zadd(
            "job_queue",
            {job.id: job.priority}
        )
        
        return job.id
    
    def get_next_job(self, worker_id: str) -> Optional[ScrapingJob]:
        """Get next job for worker."""
        # Get highest priority job
        job_data = self.redis_client.zpopmax("job_queue", 1)
        
        if not job_data:
            return None
        
        job_id, priority = job_data[0]
        job_id = job_id.decode('utf-8')
        
        # Get job details
        job_json = self.redis_client.hget("jobs", job_id)
        if not job_json:
            return None
        
        job_dict = json.loads(job_json)
        job = ScrapingJob(**job_dict)
        
        # Assign to worker
        job.assigned_worker = worker_id
        job.status = JobStatus.ASSIGNED
        job.started_at = time.time()
        
        # Update job in Redis
        self.redis_client.hset(
            "jobs",
            job_id,
            json.dumps(job.__dict__, default=str)
        )
        
        # Add to worker's active jobs
        self.redis_client.sadd(f"worker:{worker_id}:jobs", job_id)
        
        return job
    
    def update_job_status(self, job_id: str, status: JobStatus, 
                         error: str = None, result: Dict[str, Any] = None):
        """Update job status."""
        job_json = self.redis_client.hget("jobs", job_id)
        if not job_json:
            return False
        
        job_dict = json.loads(job_json)
        job_dict['status'] = status.value
        
        if status == JobStatus.COMPLETED:
            job_dict['completed_at'] = time.time()
            if result:
                job_dict['result'] = result
        
        elif status == JobStatus.FAILED:
            job_dict['completed_at'] = time.time()
            if error:
                job_dict['error'] = error
            
            # Handle retries
            job_dict['retry_count'] += 1
            if job_dict['retry_count'] < job_dict.get('max_retries', 3):
                # Requeue for retry
                job_dict['status'] = JobStatus.RETRYING.value
                self.redis_client.zadd(
                    "job_queue",
                    {job_id: job_dict.get('priority', 0)}
                )
        
        # Update job
        self.redis_client.hset(
            "jobs",
            job_id,
            json.dumps(job_dict, default=str)
        )
        
        # Remove from worker's active jobs if completed/failed
        if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            worker_id = job_dict.get('assigned_worker')
            if worker_id:
                self.redis_client.srem(f"worker:{worker_id}:jobs", job_id)
        
        return True
    
    def send_heartbeat(self, worker_id: str):
        """Send worker heartbeat."""
        worker_json = self.redis_client.hget("workers", worker_id)
        if worker_json:
            worker_info = json.loads(worker_json)
            worker_info['last_heartbeat'] = time.time()
            
            self.redis_client.hset(
                "workers",
                worker_id,
                json.dumps(worker_info)
            )
    
    def cleanup_stale_jobs(self):
        """Clean up stale jobs from failed workers."""
        current_time = time.time()
        
        # Get all workers
        workers = self.redis_client.hgetall("workers")
        
        for worker_id, worker_json in workers.items():
            worker_id = worker_id.decode('utf-8')
            worker_info = json.loads(worker_json)
            
            last_heartbeat = worker_info.get('last_heartbeat', 0)
            
            # Check if worker is stale (no heartbeat for 2 minutes)
            if current_time - last_heartbeat > 120:
                # Get worker's active jobs
                active_jobs = self.redis_client.smembers(f"worker:{worker_id}:jobs")
                
                for job_id in active_jobs:
                    job_id = job_id.decode('utf-8')
                    
                    # Requeue job
                    job_json = self.redis_client.hget("jobs", job_id)
                    if job_json:
                        job_dict = json.loads(job_json)
                        job_dict['status'] = JobStatus.PENDING.value
                        job_dict['assigned_worker'] = None
                        
                        self.redis_client.hset(
                            "jobs",
                            job_id,
                            json.dumps(job_dict, default=str)
                        )
                        
                        # Add back to queue
                        self.redis_client.zadd(
                            "job_queue",
                            {job_id: job_dict.get('priority', 0)}
                        )
                
                # Clear worker's job list
                self.redis_client.delete(f"worker:{worker_id}:jobs")
                
                # Mark worker as stale
                worker_info['status'] = 'stale'
                self.redis_client.hset(
                    "workers",
                    worker_id,
                    json.dumps(worker_info)
                )
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        pending_jobs = self.redis_client.zcard("job_queue")
        total_jobs = self.redis_client.hlen("jobs")
        active_workers = 0
        
        workers = self.redis_client.hgetall("workers")
        current_time = time.time()
        
        for worker_json in workers.values():
            worker_info = json.loads(worker_json)
            last_heartbeat = worker_info.get('last_heartbeat', 0)
            
            if current_time - last_heartbeat < 120:  # Active within 2 minutes
                active_workers += 1
        
        return {
            'pending_jobs': pending_jobs,
            'total_jobs': total_jobs,
            'active_workers': active_workers,
            'total_workers': len(workers)
        }

# Example usage
queue = DistributedJobQueue()

# Submit jobs
job = ScrapingJob(
    id=None,
    name="Scaled Scraping Job",
    template_id="product-template",
    target_url="https://example.com",
    config={"delay_range": [1, 3]},
    priority=10
)

job_id = queue.submit_job(job)
print(f"Submitted job: {job_id}")
```

### 3. Worker Implementation

```python
# src/scaling/worker.py
import time
import threading
import signal
import sys
import os
from src.scaling.distributed_queue import DistributedJobQueue, JobStatus
from src.services.scraping_service import ScrapingService

class ScrapingWorker:
    """Distributed scraping worker."""
    
    def __init__(self, worker_id=None, redis_url=None):
        self.worker_id = worker_id or f"worker-{os.getpid()}"
        self.queue = DistributedJobQueue(redis_url)
        self.scraping_service = ScrapingService()
        self.running = False
        self.heartbeat_thread = None
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def start(self):
        """Start worker processing."""
        print(f"Starting worker: {self.worker_id}")
        
        # Register worker
        self.queue.register_worker(self.worker_id)
        
        # Start heartbeat thread
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        # Main processing loop
        while self.running:
            try:
                # Get next job
                job = self.queue.get_next_job(self.worker_id)
                
                if job:
                    print(f"Processing job: {job.id}")
                    self._process_job(job)
                else:
                    # No jobs available, wait
                    time.sleep(5)
                    
            except Exception as e:
                print(f"Worker error: {e}")
                time.sleep(10)
    
    def _process_job(self, job):
        """Process individual scraping job."""
        try:
            # Update status to running
            self.queue.update_job_status(job.id, JobStatus.RUNNING)
            
            # Create scraping job
            scraping_job = self.scraping_service.create_job(
                name=job.name,
                template_id=job.template_id,
                target_url=job.target_url,
                config=job.config
            )
            
            # Execute scraping
            result = self.scraping_service.start_scraping_job(scraping_job.id)
            
            # Wait for completion with timeout
            timeout = job.config.get('timeout', 3600)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                status = self.scraping_service.get_job_status(scraping_job.id)
                
                if status['status'] in ['completed', 'failed']:
                    break
                
                time.sleep(10)
            
            # Get final status
            final_status = self.scraping_service.get_job_status(scraping_job.id)
            
            if final_status['status'] == 'completed':
                # Job completed successfully
                self.queue.update_job_status(
                    job.id,
                    JobStatus.COMPLETED,
                    result={'scraping_job_id': scraping_job.id, 'items_scraped': final_status.get('items_scraped', 0)}
                )
                print(f"Job {job.id} completed successfully")
                
            else:
                # Job failed
                self.queue.update_job_status(
                    job.id,
                    JobStatus.FAILED,
                    error=final_status.get('error', 'Unknown error')
                )
                print(f"Job {job.id} failed: {final_status.get('error')}")
                
        except Exception as e:
            # Job processing failed
            self.queue.update_job_status(
                job.id,
                JobStatus.FAILED,
                error=str(e)
            )
            print(f"Job {job.id} processing error: {e}")
    
    def _heartbeat_loop(self):
        """Send periodic heartbeats."""
        while self.running:
            try:
                self.queue.send_heartbeat(self.worker_id)
                time.sleep(30)
            except Exception as e:
                print(f"Heartbeat error: {e}")
                time.sleep(30)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"Worker {self.worker_id} received signal {signum}, shutting down...")
        self.running = False
        sys.exit(0)
    
    def stop(self):
        """Stop worker gracefully."""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join()

# Worker startup script
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ScraperV4 Distributed Worker')
    parser.add_argument('--worker-id', default=None, help='Worker ID')
    parser.add_argument('--redis-url', default='redis://localhost:6379/0', help='Redis URL')
    
    args = parser.parse_args()
    
    worker = ScrapingWorker(args.worker_id, args.redis_url)
    worker.start()
```

## Load Balancing and Request Distribution

### 1. Nginx Load Balancer Configuration

```nginx
# nginx/nginx-scale.conf
upstream scraperv4_backend {
    least_conn;
    
    # Health checks
    server scraperv4-coordinator:8080 max_fails=3 fail_timeout=30s;
    
    # Add more coordinators for high availability
    # server scraperv4-coordinator-2:8080 max_fails=3 fail_timeout=30s;
    # server scraperv4-coordinator-3:8080 max_fails=3 fail_timeout=30s;
}

upstream scraperv4_workers {
    # Worker nodes for direct API access if needed
    ip_hash;  # Sticky sessions for WebSocket connections
    
    server scraperv4-worker-1:8080 max_fails=2 fail_timeout=20s;
    server scraperv4-worker-2:8080 max_fails=2 fail_timeout=20s;
    server scraperv4-worker-3:8080 max_fails=2 fail_timeout=20s;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/m;
limit_req_zone $binary_remote_addr zone=submit_limit:10m rate=10r/m;

server {
    listen 80;
    server_name scraperv4.example.com;
    
    # API endpoints
    location /api/ {
        # Different rate limits for different endpoints
        location /api/scraping/start {
            limit_req zone=submit_limit burst=5 nodelay;
            proxy_pass http://scraperv4_backend;
        }
        
        location /api/scraping/status/ {
            limit_req zone=api_limit burst=10 nodelay;
            proxy_pass http://scraperv4_backend;
        }
        
        # Default API handling
        limit_req zone=api_limit burst=15 nodelay;
        proxy_pass http://scraperv4_backend;
        
        # Load balancing headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running operations
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://scraperv4_backend/api/health;
        access_log off;
    }
    
    # WebSocket support for real-time monitoring
    location /ws {
        proxy_pass http://scraperv4_workers;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 2. Dynamic Scaling with Docker Swarm

```yaml
# docker-stack.yml
version: '3.8'

services:
  coordinator:
    image: scraperv4:latest
    environment:
      - SCRAPERV4_ROLE=coordinator
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8080:8080"
    networks:
      - scraperv4_net
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  worker:
    image: scraperv4:latest
    environment:
      - SCRAPERV4_ROLE=worker
      - REDIS_URL=redis://redis:6379/0
    networks:
      - scraperv4_net
    deploy:
      replicas: 5
      restart_policy:
        condition: on-failure
        delay: 5s
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
      update_config:
        parallelism: 2
        delay: 10s
        failure_action: rollback

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    networks:
      - scraperv4_net
    volumes:
      - redis_data:/data
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    networks:
      - scraperv4_net
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  redis_data:

networks:
  scraperv4_net:
    driver: overlay
    attachable: true

configs:
  nginx_config:
    file: ./nginx/nginx-scale.conf
```

## Auto-Scaling Implementation

### 1. Kubernetes Auto-Scaling

```yaml
# k8s/scraperv4-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scraperv4-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: scraperv4-worker
  template:
    metadata:
      labels:
        app: scraperv4-worker
    spec:
      containers:
      - name: scraperv4-worker
        image: scraperv4:latest
        env:
        - name: SCRAPERV4_ROLE
          value: "worker"
        - name: REDIS_URL
          value: "redis://redis:6379/0"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scraperv4-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scraperv4-worker
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: scraperv4_queue_length
      target:
        type: AverageValue
        averageValue: "10"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### 2. Custom Auto-Scaling Logic

```python
# src/scaling/auto_scaler.py
import time
import threading
from typing import Dict, Any
from src.scaling.distributed_queue import DistributedJobQueue

class AutoScaler:
    """Auto-scaling logic for ScraperV4 workers."""
    
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.queue = DistributedJobQueue(redis_url)
        self.scaling_config = {
            'min_workers': 2,
            'max_workers': 20,
            'scale_up_threshold': 10,      # Jobs per worker
            'scale_down_threshold': 2,     # Jobs per worker
            'scale_up_cooldown': 60,       # Seconds
            'scale_down_cooldown': 300,    # Seconds
            'evaluation_interval': 30      # Seconds
        }
        self.last_scale_action = 0
        self.running = False
        
    def start_monitoring(self):
        """Start auto-scaling monitoring."""
        self.running = True
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop auto-scaling monitoring."""
        self.running = False
    
    def _monitoring_loop(self):
        """Main monitoring and scaling loop."""
        while self.running:
            try:
                # Get current metrics
                stats = self.queue.get_queue_stats()
                scaling_decision = self._evaluate_scaling(stats)
                
                if scaling_decision['action'] != 'none':
                    self._execute_scaling_action(scaling_decision)
                
                time.sleep(self.scaling_config['evaluation_interval'])
                
            except Exception as e:
                print(f"Auto-scaling error: {e}")
                time.sleep(60)
    
    def _evaluate_scaling(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate whether scaling action is needed."""
        pending_jobs = stats['pending_jobs']
        active_workers = stats['active_workers']
        current_time = time.time()
        
        decision = {
            'action': 'none',
            'reason': '',
            'target_workers': active_workers,
            'current_metrics': stats
        }
        
        if active_workers == 0:
            decision.update({
                'action': 'scale_up',
                'reason': 'No active workers',
                'target_workers': self.scaling_config['min_workers']
            })
            return decision
        
        # Calculate jobs per worker
        jobs_per_worker = pending_jobs / max(active_workers, 1)
        
        # Scale up evaluation
        if (jobs_per_worker > self.scaling_config['scale_up_threshold'] and
            active_workers < self.scaling_config['max_workers'] and
            current_time - self.last_scale_action > self.scaling_config['scale_up_cooldown']):
            
            # Calculate desired workers
            desired_workers = min(
                self.scaling_config['max_workers'],
                int(pending_jobs / self.scaling_config['scale_up_threshold']) + 1
            )
            
            decision.update({
                'action': 'scale_up',
                'reason': f'High load: {jobs_per_worker:.1f} jobs per worker',
                'target_workers': desired_workers
            })
        
        # Scale down evaluation
        elif (jobs_per_worker < self.scaling_config['scale_down_threshold'] and
              active_workers > self.scaling_config['min_workers'] and
              current_time - self.last_scale_action > self.scaling_config['scale_down_cooldown']):
            
            # Calculate desired workers
            desired_workers = max(
                self.scaling_config['min_workers'],
                int(pending_jobs / max(self.scaling_config['scale_down_threshold'], 1)) + 1
            )
            
            if desired_workers < active_workers:
                decision.update({
                    'action': 'scale_down',
                    'reason': f'Low load: {jobs_per_worker:.1f} jobs per worker',
                    'target_workers': desired_workers
                })
        
        return decision
    
    def _execute_scaling_action(self, decision: Dict[str, Any]):
        """Execute scaling action."""
        action = decision['action']
        target_workers = decision['target_workers']
        current_workers = decision['current_metrics']['active_workers']
        
        print(f"Auto-scaling: {action} from {current_workers} to {target_workers} workers")
        print(f"Reason: {decision['reason']}")
        
        if action == 'scale_up':
            # In Docker Swarm
            self._scale_docker_swarm(target_workers)
            
            # In Kubernetes
            # self._scale_kubernetes(target_workers)
            
        elif action == 'scale_down':
            # Implement graceful scale down
            self._graceful_scale_down(target_workers)
        
        self.last_scale_action = time.time()
    
    def _scale_docker_swarm(self, target_workers: int):
        """Scale Docker Swarm service."""
        import subprocess
        
        try:
            subprocess.run([
                'docker', 'service', 'scale', 
                f'scraperv4_worker={target_workers}'
            ], check=True)
            
            print(f"Docker Swarm scaled to {target_workers} workers")
            
        except subprocess.CalledProcessError as e:
            print(f"Docker scaling failed: {e}")
    
    def _scale_kubernetes(self, target_workers: int):
        """Scale Kubernetes deployment."""
        import subprocess
        
        try:
            subprocess.run([
                'kubectl', 'scale', 'deployment', 'scraperv4-worker',
                f'--replicas={target_workers}'
            ], check=True)
            
            print(f"Kubernetes scaled to {target_workers} workers")
            
        except subprocess.CalledProcessError as e:
            print(f"Kubernetes scaling failed: {e}")
    
    def _graceful_scale_down(self, target_workers: int):
        """Gracefully scale down workers."""
        current_stats = self.queue.get_queue_stats()
        current_workers = current_stats['active_workers']
        
        workers_to_remove = current_workers - target_workers
        
        if workers_to_remove > 0:
            # Mark workers for graceful shutdown
            # This would require additional Redis coordination
            print(f"Initiating graceful shutdown of {workers_to_remove} workers")
            
            # For now, just scale directly
            # In production, implement graceful worker shutdown
            self._scale_docker_swarm(target_workers)

# Auto-scaler startup
def start_auto_scaler():
    """Start auto-scaler service."""
    import os
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    auto_scaler = AutoScaler(redis_url)
    
    print("Starting auto-scaler...")
    auto_scaler.start_monitoring()
    
    # Keep running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down auto-scaler...")
        auto_scaler.stop_monitoring()

if __name__ == "__main__":
    start_auto_scaler()
```

## Performance Monitoring at Scale

### 1. Distributed Metrics Collection

```python
# src/scaling/metrics_collector.py
import time
import threading
from typing import Dict, Any, List
from dataclasses import dataclass
from src.scaling.distributed_queue import DistributedJobQueue

@dataclass
class ScalingMetrics:
    timestamp: float
    total_jobs: int
    pending_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    active_workers: int
    total_workers: int
    jobs_per_second: float
    avg_job_duration: float
    error_rate: float

class DistributedMetricsCollector:
    """Collect and aggregate metrics across distributed workers."""
    
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.queue = DistributedJobQueue(redis_url)
        self.metrics_history = []
        self.collection_interval = 30
        self.collecting = False
        
    def start_collection(self):
        """Start metrics collection."""
        self.collecting = True
        collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        collection_thread.start()
        return collection_thread
    
    def stop_collection(self):
        """Stop metrics collection."""
        self.collecting = False
    
    def _collection_loop(self):
        """Main metrics collection loop."""
        while self.collecting:
            try:
                metrics = self._collect_current_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 24 hours of metrics (assuming 30s interval)
                max_metrics = 24 * 60 * 2  # 24 hours * 60 minutes * 2 (30s intervals)
                if len(self.metrics_history) > max_metrics:
                    self.metrics_history = self.metrics_history[-max_metrics:]
                
                # Export metrics to external systems
                self._export_metrics(metrics)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                print(f"Metrics collection error: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_current_metrics(self) -> ScalingMetrics:
        """Collect current system metrics."""
        queue_stats = self.queue.get_queue_stats()
        
        # Get job status distribution
        job_statuses = self._get_job_status_distribution()
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics()
        
        return ScalingMetrics(
            timestamp=time.time(),
            total_jobs=queue_stats['total_jobs'],
            pending_jobs=queue_stats['pending_jobs'],
            running_jobs=job_statuses.get('running', 0),
            completed_jobs=job_statuses.get('completed', 0),
            failed_jobs=job_statuses.get('failed', 0),
            active_workers=queue_stats['active_workers'],
            total_workers=queue_stats['total_workers'],
            jobs_per_second=performance_metrics['jobs_per_second'],
            avg_job_duration=performance_metrics['avg_job_duration'],
            error_rate=performance_metrics['error_rate']
        )
    
    def _get_job_status_distribution(self) -> Dict[str, int]:
        """Get distribution of job statuses."""
        # This would query Redis for job status counts
        # For now, return mock data
        return {
            'running': 5,
            'completed': 100,
            'failed': 2
        }
    
    def _calculate_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics."""
        if len(self.metrics_history) < 2:
            return {
                'jobs_per_second': 0.0,
                'avg_job_duration': 0.0,
                'error_rate': 0.0
            }
        
        # Calculate jobs per second
        recent_metrics = self.metrics_history[-2:]
        time_diff = recent_metrics[1].timestamp - recent_metrics[0].timestamp
        jobs_diff = recent_metrics[1].completed_jobs - recent_metrics[0].completed_jobs
        
        jobs_per_second = jobs_diff / time_diff if time_diff > 0 else 0.0
        
        # Calculate error rate
        total_recent_jobs = jobs_diff + (recent_metrics[1].failed_jobs - recent_metrics[0].failed_jobs)
        failed_recent_jobs = recent_metrics[1].failed_jobs - recent_metrics[0].failed_jobs
        
        error_rate = failed_recent_jobs / total_recent_jobs if total_recent_jobs > 0 else 0.0
        
        return {
            'jobs_per_second': jobs_per_second,
            'avg_job_duration': 30.0,  # This would be calculated from actual job data
            'error_rate': error_rate
        }
    
    def _export_metrics(self, metrics: ScalingMetrics):
        """Export metrics to external monitoring systems."""
        # Export to Prometheus
        self._export_to_prometheus(metrics)
        
        # Export to InfluxDB
        # self._export_to_influxdb(metrics)
        
        # Export to CloudWatch
        # self._export_to_cloudwatch(metrics)
    
    def _export_to_prometheus(self, metrics: ScalingMetrics):
        """Export metrics to Prometheus."""
        # This would use prometheus_client to expose metrics
        from prometheus_client import Gauge, Counter
        
        # Define metrics if not already defined
        if not hasattr(self, 'prometheus_metrics'):
            self.prometheus_metrics = {
                'total_jobs': Gauge('scraperv4_total_jobs', 'Total jobs in system'),
                'pending_jobs': Gauge('scraperv4_pending_jobs', 'Pending jobs'),
                'active_workers': Gauge('scraperv4_active_workers', 'Active workers'),
                'jobs_per_second': Gauge('scraperv4_jobs_per_second', 'Jobs processed per second'),
                'error_rate': Gauge('scraperv4_error_rate', 'Job error rate')
            }
        
        # Update metrics
        self.prometheus_metrics['total_jobs'].set(metrics.total_jobs)
        self.prometheus_metrics['pending_jobs'].set(metrics.pending_jobs)
        self.prometheus_metrics['active_workers'].set(metrics.active_workers)
        self.prometheus_metrics['jobs_per_second'].set(metrics.jobs_per_second)
        self.prometheus_metrics['error_rate'].set(metrics.error_rate)
    
    def get_scaling_recommendations(self) -> Dict[str, Any]:
        """Get scaling recommendations based on metrics."""
        if len(self.metrics_history) < 5:
            return {'recommendation': 'insufficient_data'}
        
        recent_metrics = self.metrics_history[-5:]
        
        # Analyze trends
        avg_pending = sum(m.pending_jobs for m in recent_metrics) / len(recent_metrics)
        avg_workers = sum(m.active_workers for m in recent_metrics) / len(recent_metrics)
        avg_jobs_per_second = sum(m.jobs_per_second for m in recent_metrics) / len(recent_metrics)
        avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
        
        recommendations = {
            'current_state': {
                'avg_pending_jobs': avg_pending,
                'avg_active_workers': avg_workers,
                'avg_jobs_per_second': avg_jobs_per_second,
                'avg_error_rate': avg_error_rate
            },
            'recommendations': []
        }
        
        # Generate recommendations
        if avg_pending > avg_workers * 10:
            recommendations['recommendations'].append({
                'action': 'scale_up',
                'reason': 'High queue backlog',
                'suggested_workers': int(avg_pending / 8)
            })
        
        if avg_error_rate > 0.1:
            recommendations['recommendations'].append({
                'action': 'investigate_errors',
                'reason': f'High error rate: {avg_error_rate:.1%}',
                'priority': 'high'
            })
        
        if avg_jobs_per_second < 0.1 and avg_workers > 2:
            recommendations['recommendations'].append({
                'action': 'scale_down',
                'reason': 'Low throughput with excess workers',
                'suggested_workers': max(2, int(avg_workers * 0.7))
            })
        
        return recommendations

# Example usage
metrics_collector = DistributedMetricsCollector()
metrics_collector.start_collection()

# Let it run and collect metrics
time.sleep(300)  # 5 minutes

# Get scaling recommendations
recommendations = metrics_collector.get_scaling_recommendations()
print(f"Scaling recommendations: {recommendations}")
```

## Data Partitioning and Distribution

### 1. URL Distribution Strategy

```python
# src/scaling/data_partitioner.py
import hashlib
from typing import List, Dict, Any
from urllib.parse import urlparse

class DataPartitioner:
    """Partition scraping tasks across workers efficiently."""
    
    def __init__(self, partition_strategy="domain_hash"):
        self.partition_strategy = partition_strategy
        
    def partition_urls(self, urls: List[str], num_partitions: int) -> List[List[str]]:
        """Partition URLs into balanced groups."""
        
        if self.partition_strategy == "domain_hash":
            return self._partition_by_domain_hash(urls, num_partitions)
        elif self.partition_strategy == "round_robin":
            return self._partition_round_robin(urls, num_partitions)
        elif self.partition_strategy == "domain_grouping":
            return self._partition_by_domain_grouping(urls, num_partitions)
        else:
            return self._partition_round_robin(urls, num_partitions)
    
    def _partition_by_domain_hash(self, urls: List[str], num_partitions: int) -> List[List[str]]:
        """Partition URLs by consistent hashing of domain."""
        partitions = [[] for _ in range(num_partitions)]
        
        for url in urls:
            try:
                domain = urlparse(url).netloc
                # Use consistent hashing
                hash_value = int(hashlib.md5(domain.encode()).hexdigest(), 16)
                partition_index = hash_value % num_partitions
                partitions[partition_index].append(url)
            except Exception:
                # Fallback to round-robin for invalid URLs
                partition_index = len(partitions[0]) % num_partitions
                partitions[partition_index].append(url)
        
        return partitions
    
    def _partition_round_robin(self, urls: List[str], num_partitions: int) -> List[List[str]]:
        """Simple round-robin partitioning."""
        partitions = [[] for _ in range(num_partitions)]
        
        for i, url in enumerate(urls):
            partition_index = i % num_partitions
            partitions[partition_index].append(url)
        
        return partitions
    
    def _partition_by_domain_grouping(self, urls: List[str], num_partitions: int) -> List[List[str]]:
        """Group URLs by domain, then distribute groups."""
        domain_groups = {}
        
        # Group by domain
        for url in urls:
            try:
                domain = urlparse(url).netloc
                if domain not in domain_groups:
                    domain_groups[domain] = []
                domain_groups[domain].append(url)
            except Exception:
                # Handle invalid URLs
                if 'invalid' not in domain_groups:
                    domain_groups['invalid'] = []
                domain_groups['invalid'].append(url)
        
        # Distribute domain groups across partitions
        partitions = [[] for _ in range(num_partitions)]
        domain_list = list(domain_groups.items())
        
        for i, (domain, domain_urls) in enumerate(domain_list):
            partition_index = i % num_partitions
            partitions[partition_index].extend(domain_urls)
        
        return partitions
    
    def optimize_partitions(self, partitions: List[List[str]]) -> List[List[str]]:
        """Optimize partition balance."""
        total_urls = sum(len(partition) for partition in partitions)
        target_size = total_urls // len(partitions)
        
        # Rebalance if needed
        optimized_partitions = [[] for _ in range(len(partitions))]
        all_urls = []
        
        for partition in partitions:
            all_urls.extend(partition)
        
        # Redistribute more evenly
        for i, url in enumerate(all_urls):
            partition_index = i % len(partitions)
            optimized_partitions[partition_index].append(url)
        
        return optimized_partitions

# Example usage
partitioner = DataPartitioner("domain_hash")

urls = [
    "https://site1.com/page1",
    "https://site1.com/page2", 
    "https://site2.com/page1",
    "https://site3.com/page1"
]

partitions = partitioner.partition_urls(urls, 3)
print(f"Partitioned into {len(partitions)} groups:")
for i, partition in enumerate(partitions):
    print(f"Partition {i}: {len(partition)} URLs")
```

## Scaling Best Practices

### 1. Resource Management

```python
# src/scaling/resource_manager.py
import psutil
import time
from typing import Dict, Any

class ResourceManager:
    """Manage system resources for optimal scaling."""
    
    def __init__(self):
        self.resource_thresholds = {
            'cpu_max': 80,      # Maximum CPU usage %
            'memory_max': 85,   # Maximum memory usage %
            'disk_max': 90,     # Maximum disk usage %
            'load_max': 4.0     # Maximum system load
        }
        
    def check_resource_availability(self) -> Dict[str, Any]:
        """Check if system has resources for scaling up."""
        
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        load_avg = psutil.getloadavg()[0]  # 1-minute load average
        
        status = {
            'cpu_usage': cpu_usage,
            'memory_usage': memory.percent,
            'disk_usage': (disk.used / disk.total) * 100,
            'load_average': load_avg,
            'can_scale_up': True,
            'limiting_factors': []
        }
        
        # Check each threshold
        if cpu_usage > self.resource_thresholds['cpu_max']:
            status['can_scale_up'] = False
            status['limiting_factors'].append(f'CPU usage too high: {cpu_usage:.1f}%')
        
        if memory.percent > self.resource_thresholds['memory_max']:
            status['can_scale_up'] = False
            status['limiting_factors'].append(f'Memory usage too high: {memory.percent:.1f}%')
        
        disk_usage_pct = (disk.used / disk.total) * 100
        if disk_usage_pct > self.resource_thresholds['disk_max']:
            status['can_scale_up'] = False
            status['limiting_factors'].append(f'Disk usage too high: {disk_usage_pct:.1f}%')
        
        if load_avg > self.resource_thresholds['load_max']:
            status['can_scale_up'] = False
            status['limiting_factors'].append(f'Load average too high: {load_avg:.2f}')
        
        return status
    
    def get_optimal_worker_count(self, current_workers: int, pending_jobs: int) -> int:
        """Calculate optimal worker count based on resources and load."""
        
        resource_status = self.check_resource_availability()
        
        if not resource_status['can_scale_up']:
            return current_workers
        
        # Calculate based on available resources
        cpu_cores = psutil.cpu_count()
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
        # Conservative estimate: 1 worker per 2 CPU cores, with memory limit
        max_workers_by_cpu = max(1, cpu_cores // 2)
        max_workers_by_memory = max(1, int(available_memory_gb // 0.5))  # 512MB per worker
        
        max_workers = min(max_workers_by_cpu, max_workers_by_memory)
        
        # Consider current load
        optimal_for_jobs = min(max_workers, (pending_jobs // 5) + 1)
        
        return min(max_workers, optimal_for_jobs)

# Example usage
resource_manager = ResourceManager()
status = resource_manager.check_resource_availability()
optimal_count = resource_manager.get_optimal_worker_count(3, 50)

print(f"Resource status: {status}")
print(f"Optimal worker count: {optimal_count}")
```

## Expected Outcomes

After implementing scaling operations:

1. **High Throughput**: Process thousands of URLs efficiently
2. **Auto-Scaling**: Dynamic worker adjustment based on load
3. **Fault Tolerance**: Automatic recovery from worker failures
4. **Resource Optimization**: Efficient use of available hardware
5. **Load Distribution**: Balanced workload across workers
6. **Monitoring**: Real-time visibility into scaling metrics

## Success Criteria

- [ ] Distributed job queue operational
- [ ] Worker auto-scaling functional
- [ ] Load balancing configured and tested
- [ ] Monitoring and metrics collection working
- [ ] Resource management optimized
- [ ] Fault tolerance verified
- [ ] Performance benchmarks met
- [ ] Documentation completed