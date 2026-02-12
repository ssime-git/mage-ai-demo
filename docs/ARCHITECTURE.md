> **Mage AI Version:** 0.9.79 (pinned for reproducibility)

# Mage AI Microservices Architecture

## Overview

This project uses Mage AI with a microservices architecture that separates concerns across multiple containers while maintaining clear communication patterns. The native `mageai/mageai` Docker image is extended with role-specific Dockerfiles to optimize resource usage.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    External Users                           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP (6789)
                     ▼
            ┌────────────────────┐
            │   Mage Web Server  │
            │ (web_server role)  │
            │                    │
            │  - UI serving      │
            │  - API endpoints   │
            │  - Project state   │
            └────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    PostgreSQL    Redis      Code Files
   (metadata)  (coordination) (volumes)
        ▲            ▲            ▲
        │            │            │
        └────────────┼────────────┘
                     │
            ┌────────▼───────────┐
            │  Mage Scheduler    │
            │ (scheduler role)   │
            │                    │
            │ - Monitor triggers │
            │ - Enqueue runs     │
            │ - Distribute locks │
            └────────────────────┘
                     │
        Enqueued     │
        Runs         ▼ (in-memory queue)
                ┌─────────────────┐
                │ Executor Thread │
                │   Pool (20)     │
                │                 │
                │ Executes blocks │
                └─────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   Datasets            Prediction API
                      (Flask, port 5000)
                        - /predict
                        - /health
```

## Services

### 1. PostgreSQL (postgres)
- **Role**: Metadata storage
- **Data**: Pipeline definitions, runs, triggers, users, authentication
- **Image**: `postgres:14`
- **Port**: Internal only (5432)
- **Persistence**: Volume mount `pgdata`
- **Health Check**: `pg_isready` command

### 2. Redis (redis)
- **Role**: Scheduler coordination and distributed locking
- **Purpose**: 
  - Prevents duplicate pipeline runs in multi-scheduler setups
  - Shared state for scheduler elections
  - Run queue storage (when using remote executors)
- **Image**: `redis:7-alpine`
- **Port**: Internal only (6379)
- **Configuration**: In-memory only (AOF disabled, no persistence)

### 3. Mage Web Server (mage-web)
- **Role**: HTTP API and UI server
- **Instance Type**: `web_server`
- **Port**: 6789 (external)
- **Responsibilities**:
  - Serve Mage UI (notebook interface)
  - Handle REST API requests
  - Manage project state and configuration
  - Execute blocks on-demand (manual runs)
- **Image**: Built from `Dockerfile.web` (minimal utilities: curl, jq)
- **Health Check**: HTTP GET `/` on port 6789
- **Scaling**: Multiple instances supported behind load balancer
- **Dependencies**: PostgreSQL, Redis

### 4. Mage Scheduler (mage-scheduler)
- **Role**: Pipeline scheduling and trigger management
- **Instance Type**: `scheduler`
- **Responsibilities**:
  - Monitor pipeline triggers (schedules, sensors, webhooks)
  - Enqueue scheduled runs to execution queue
  - Manage distributed locking via Redis (prevents duplicate runs)
  - Track trigger state and run history
- **Image**: Built from `Dockerfile.scheduler` (minimal utilities: redis-cli)
- **Port**: None (internal only)
- **Health Check**: Redis connectivity `redis-cli ping`
- **Scaling**: Multiple instances supported with Redis coordination
- **Important**: Requires `REDIS_URL` for distributed locking
- **Dependencies**: PostgreSQL, Redis

### 5. Prediction Service (prediction-service)
- **Role**: Model inference microservice
- **Technology**: Flask + scikit-learn (independent from Mage)
- **Port**: 5000 (external)
- **Endpoints**:
  - `POST /predict` - Make predictions
  - `GET /health` - Health check
- **Data**: Model files mounted from `mlops_demo/model_registry/` (read-only)
- **Scaling**: Multiple instances supported independently
- **Note**: Entirely separate from Mage core; can be deployed independently
- **Dependencies**: Requires `mlops_demo/model_registry/latest.json` to exist

## Data Flow

### Manual Pipeline Execution (via UI)
1. User clicks "Run" in Mage UI (mage-web)
2. mage-web creates run record in PostgreSQL
3. mage-web executes blocks in local kernel
4. Results stored in PostgreSQL and code outputs

### Scheduled Pipeline Execution
1. mage-scheduler detects active trigger (schedule, sensor)
2. Scheduler checks Redis lock to prevent duplicates
3. Scheduler acquires lock via Redis
4. Scheduler creates PipelineRun record in PostgreSQL
5. Enqueues run to in-memory execution queue
6. Executor thread pool picks up run
7. Executor runs pipeline blocks sequentially
8. Results stored in PostgreSQL and outputs
9. Lock released in Redis

### Scaling to Multiple Executors (Future)
1. Add `mage-executor` containers (see commented section in docker-compose.yml)
2. Configure pipeline-specific `metadata.yaml`:
   ```yaml
   executor_type: local_python  # or ecs, k8s, gcp_cloud_run
   executor_config:
     queue_size: 10  # Parallel executions
   ```
3. Each executor pulls from shared queue coordinated by scheduler

## Environment Variables

### Common (All Mage services)
- `PROJECT_NAME`: Mage project name (default: `mlops_demo`)
- `USER_CODE_PATH`: Base path to project code (default: `/home/src`)
- `ENV`: Environment (dev/prod, default: `dev`)

### Database Configuration
- `POSTGRES_DB`: Database name (default: `mage`)
- `POSTGRES_USER`: Database user (default: `mage`)
- `POSTGRES_PASSWORD`: Database password (default: `mage`)
- `POSTGRES_HOST`: Database host (default: `postgres`)
- `POSTGRES_PORT`: Database port (default: `5432`)
- `DATABASE_URL`: Full connection string (overrides individual params)

### Redis Configuration
- `REDIS_URL`: Redis connection URL (default: `redis://redis:6379/0`)
- **Critical for multi-scheduler setups** (distributed locking)

## Scaling Strategies

### Horizontal Scaling - Web Servers
```yaml
mage-web-1:
  # ... same config as mage-web

mage-web-2:
  # ... same config as mage-web
  ports:
    - "6790:6789"  # Different external port
```
- Place behind load balancer (e.g., Nginx)
- State is stateless (all stored in PostgreSQL)

### Horizontal Scaling - Schedulers
```yaml
mage-scheduler-1:
  # ... same config

mage-scheduler-2:
  # ... same config
```
- Redis REDIS_URL ensures distributed locking
- Prevents duplicate runs from multiple schedulers

### Scaling Executors (For Higher Throughput)

#### Option 1: Local Python Executor (Multi-container)
```yaml
# Uncomment and replicate mage-executor service in docker-compose.yml
# Default queue size: 20 parallel executions per service
```

#### Option 2: Cloud Executors (Production)
Configure in `mlops_demo/metadata.yaml`:
```yaml
# For AWS ECS
executor_type: ecs
executor_config:
  task_definition: my-mage-task
  cluster: my-cluster
  cpu: 256
  memory: 512

# For Kubernetes
executor_type: kubernetes
executor_config:
  namespace: mage
  image: mageai/mageai:latest
  cpu_request: 256m
  memory_request: 512Mi
```

## Communication Patterns

### Synchronous (HTTP)
- **mage-web** ←→ **PostgreSQL**: Read/write metadata, pipelines, runs
- **mage-web** ←→ **prediction-service**: Call `/predict` endpoint for inference
- **User** ←→ **mage-web**: UI/API requests

### Asynchronous/Coordinated
- **mage-scheduler** ←→ **PostgreSQL**: Read triggers, write run records
- **mage-scheduler** ←→ **Redis**: Distributed locking, trigger state
- **executor** ←→ **PostgreSQL**: Update run status, log outputs

### Independent
- **prediction-service**: Can run on separate host, database, or cloud function

## Health Checks

| Service | Health Check | Expected Response |
|---------|-------------|-------------------|
| postgres | `pg_isready` command | Exit code 0 |
| redis | `redis-cli ping` command | PONG |
| mage-web | `curl http://localhost:6789` | HTTP 200 |
| mage-scheduler | `redis-cli ping` (via Redis) | PONG |
| prediction-service | `curl http://localhost:5000/health` | JSON response |

## File Structure

```
/home/src/
├── Dockerfile                    # Original (now Dockerfile.web)
├── Dockerfile.web               # Web server role
├── Dockerfile.scheduler         # Scheduler role
├── docker-compose.yml           # Service orchestration
├── ARCHITECTURE.md              # This file
├── mlops_demo/
│   ├── metadata.yaml           # Mage project config (executor settings)
│   ├── mage_project/           # Mage project code
│   ├── prediction_service/
│   │   ├── Dockerfile          # Flask app
│   │   ├── app.py
│   │   └── requirements.txt
│   └── model_registry/         # Models (mounted read-only to prediction-service)
```

## Development vs Production

### Development (Current)
- SQLite database (Mage stores metadata locally)
- Single scheduler instance
- Local Python executor (in-memory queue)
- All services on one host

### Production (Recommended)
- PostgreSQL database (persistent, distributed)
- Multiple scheduler instances (Redis coordination)
- Cloud executor (ECS/Kubernetes/GCP Cloud Run)
- Services distributed across multiple hosts
- Load balancer for mage-web instances
- Separate prediction-service deployment

## Troubleshooting

### Scheduler Not Picking Up Triggers
1. Check Redis connectivity: `docker-compose logs mage-scheduler`
2. Verify `REDIS_URL` environment variable
3. Check PostgreSQL has data: Run query in mage database

### Pipelines Executing Twice
- Likely multiple schedulers without Redis lock
- Ensure `REDIS_URL` is set and Redis is healthy
- Verify only one scheduler running in test environment

### Prediction Service Returns 404
- Check `mlops_demo/model_registry/latest.json` exists
- Verify mount path in docker-compose.yml

## References

- [Mage Architecture Documentation](https://docs.mage.ai/production/deploying-to-cloud/architecture)
- [Mage Executors](https://docs.mage.ai/production/configuring-production-settings/compute-resource)
- [Mage Triggers](https://docs.mage.ai/orchestration/triggers/overview)
