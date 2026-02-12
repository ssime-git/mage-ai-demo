# Mage AI: Open-Source MLOps Platform

## Executive Summary

Mage AI is a modern, open-source data pipeline platform that provides a comprehensive solution for building, deploying, and monitoring machine learning and data engineering workflows. This masterclass demonstrates how Mage addresses the complete MLOps lifecycle: experimentation, versioning, deployment, and monitoring.

**Version:** 0.9.79 (pinned for reproducibility)

---

## Table of Contents

1. [What is Mage AI?](#what-is-mage-ai)
2. [Why Mage for MLOps?](#why-mage-for-mlops)
3. [Key Features](#key-features)
4. [Architecture Overview](#architecture-overview)
5. [MLOps Workflow](#mlops-workflow)
6. [Getting Started](#getting-started)
7. [Demo Commands](#demo-commands)
8. [Comparison with Alternatives](#comparison-with-alternatives)
9. [Use Cases](#use-cases)

---

## What is Mage AI?

Mage AI is a Python-based data platform that combines the best practices from traditional data engineering with modern MLOps needs. It provides:

- **Interactive notebook-style IDE** for writing modular pipeline code
- **Built-in orchestration** with no additional framework required
- **Production-ready deployment** with Docker support
- **Distributed execution** with multiple executor options
- **Native integration** with popular data platforms and ML tools

### Core Philosophy

> *"Write once, run anywhere, monitor everywhere"*

Mage emphasizes modularity, testability, and operationalization of data and ML workflows.

---

## Why Mage for MLOps?

### Traditional Challenges

```
Problem: Fragmented MLOps Stack
┌─────────────────────────────────────┐
│ Feature Development                 │
│ └─ Jupyter Notebooks (local)       │
├─────────────────────────────────────┤
│ Experiment Tracking                 │
│ └─ MLflow / Weights & Biases       │
├─────────────────────────────────────┤
│ Model Versioning                    │
│ └─ Git / DVC / Model Registry      │
├─────────────────────────────────────┤
│ Pipeline Orchestration              │
│ └─ Airflow / Prefect               │
├─────────────────────────────────────┤
│ Model Deployment                    │
│ └─ Custom Docker / FastAPI         │
├─────────────────────────────────────┤
│ Monitoring & Observability          │
│ └─ Prometheus / Datadog / Custom   │
└─────────────────────────────────────┘

Result: High operational complexity
```

### Mage Solution

```
Unified MLOps Stack
┌─────────────────────────────────────┐
│  Mage AI (Single Platform)          │
│                                     │
│  ├─ Interactive IDE                │
│  ├─ Modular Code Blocks            │
│  ├─ Built-in Orchestration         │
│  ├─ Experiment Tracking (API)      │
│  ├─ Model Registry Integration     │
│  ├─ Multi-executor Support         │
│  ├─ Deployment Options             │
│  └─ Observability (Logs/Monitoring)│
│                                     │
└─────────────────────────────────────┘

Result: Simplified operations
```

---

## Key Features

### 1. **Modular Pipeline Design**

Each step in your pipeline is a standalone Python file that can be:
- **Tested independently** in the IDE
- **Reused** across pipelines
- **Versioned** with Git
- **Documented** inline

```python
# Example: Data Loader Block
from pandas import DataFrame
import requests

@data_loader
def load_user_data(**kwargs) -> DataFrame:
    """Fetch user data from API"""
    response = requests.get('https://api.example.com/users')
    return response.json()
```

### 2. **Built-in Experiment Tracking**

Track pipelines runs with:
- Automatic logging of inputs/outputs
- Execution time and resource usage
- Error tracking and debugging
- Manual annotations and tags

### 3. **Model Registry Integration**

Seamless integration with model registries:
- Version models alongside code
- Track model metadata and performance
- A/B test model versions
- Automatic versioning in deployment

### 4. **Multiple Execution Modes**

- **Local Python:** Development and testing
- **Docker:** Reproducible environments
- **ECS/Fargate:** AWS-native scaling
- **Kubernetes:** Enterprise deployment
- **GCP Cloud Run:** Serverless execution

### 5. **Distributed Scheduling**

- Cron-based scheduling
- Event-driven triggers
- Sensor-based conditions
- Multi-instance coordination via Redis
- Automatic retry and failure handling

### 6. **Data Quality & Validation**

Built-in validation framework:
- Column existence checks
- Data type validation
- Range checks
- Custom assertions

```python
@test
def test_data_quality(**kwargs):
    """Data quality validations"""
    df = kwargs['df']
    assert df.shape[0] > 0, "DataFrame is empty"
    assert 'required_column' in df.columns
```

---

## Architecture Overview

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed microservices architecture.

### High-Level Flow

```
User (Web UI)
    │
    ├──→ Mage Web Server
    │    (Port 6789)
    │
    ├→ PostgreSQL (Metadata)
    ├→ Redis (Coordination)
    ├→ Code Volume (Shared)
    │
    └──→ Mage Scheduler
         │
         └──→ Pipeline Executor
              │
              ├──→ Block Execution
              ├──→ Data Processing
              └──→ Model Training
              
              ↓ (Outputs)
              
              Model Registry
              Data Warehouse
              Monitoring System
```

---

## MLOps Workflow

### Phase 1: Experimentation
```
1. Write pipeline blocks in Mage IDE
2. Test blocks individually
3. View data at each step
4. Track experiments with run metadata
```

### Phase 2: Versioning
```
1. Commit pipeline code to Git
2. Tag model versions in registry
3. Link code commit to model version
4. Document model performance
```

### Phase 3: Deployment
```
1. Configure pipeline executor (local/cloud)
2. Set up triggers (schedule/event)
3. Define data quality tests
4. Deploy with `docker-compose up`
```

### Phase 4: Monitoring
```
1. Monitor pipeline runs in dashboard
2. Track model performance metrics
3. Alert on failures or data drift
4. View logs and debug issues
```

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Git

### Quick Start

```bash
# Clone the project
cd /home/seb/project/mage-ai-demo

# Start all services
make up

# View the UI
open http://localhost:6789

# Run a pipeline
make run-pipeline

# View logs
make logs
```

---

## Demo Commands

See [Makefile](#makefile) for all available commands.

### Common Workflows

**1. Build and Start Environment**
```bash
make build      # Build Docker images (pinned to 0.9.79)
make up         # Start all services
make logs       # View service logs
make health     # Check service health
```

**2. Run Pipelines**
```bash
make run-pipeline          # Execute default pipeline
make run-pipeline P=name   # Run specific pipeline
make list-pipelines        # Show available pipelines
```

**3. Check Model Registry**
```bash
make show-models           # Display model registry contents
make show-latest-model     # Show currently active model
make model-versions        # List all model versions
```

**4. Test Predictions**
```bash
make test-predict          # Make test prediction request
make predict-sample        # Predict on sample data
```

**5. Debugging**
```bash
make logs-web              # Mage web server logs
make logs-scheduler        # Mage scheduler logs
make logs-predictions      # Prediction service logs
```

**6. Cleanup**
```bash
make stop                  # Stop all services
make down                  # Stop and remove containers
make clean                 # Remove all data and caches
```

---

## Comparison with Alternatives

| Feature | Mage | Airflow | Prefect | Dagster |
|---------|------|---------|---------|---------|
| **Learning Curve** | Low | Medium | Low-Medium | High |
| **IDE Experience** | Interactive Notebook | DAG Definition | Code-based | Code-based |
| **Deployment** | Native Docker | Helm/Custom | Prefect Cloud | Kubernetes |
| **Modularity** | Excellent | Good | Good | Excellent |
| **Cost** | Free/Open-source | Free/Open-source | Free/Paid Cloud | Free/Paid Cloud |
| **Data Preview** | Built-in | No | Limited | Limited |
| **Experiment Tracking** | Native | Third-party | Third-party | Third-party |
| **Scalability** | Local → Cloud | Enterprise | Cloud-first | Enterprise |
| **Community** | Growing | Mature | Growing | Mature |

---

## Use Cases

### 1. **Feature Engineering Pipeline**
```
Data Ingestion → Feature Computation → Feature Store
                                    ↓
                            Model Training
```

### 2. **ML Model Training & Deployment**
```
Data Preparation → Feature Engineering → Model Training
                                      ↓
                                Data Validation
                                      ↓
                                Model Registry
                                      ↓
                                Prediction Service
```

### 3. **Data Quality Monitoring**
```
Data Ingestion → Data Validation → Alert on Failures
                          ↓
                    Healthy Data
                          ↓
                    Downstream Processing
```

### 4. **Real-time Inference Pipeline**
```
New Data Request → Feature Lookup → Model Prediction
                          ↓
                    Log Results → Update Monitoring
```

---

## Hands-On Demo Script

### Step 1: Start Services
```bash
cd /home/seb/project/mage-ai-demo
make build
make up
make health
```

### Step 2: Open Mage UI
```
Browser: http://localhost:6789
(Login with default credentials shown in logs)
```

### Step 3: Explore Pipelines
- View `mlops_demo` project structure
- Examine pipeline blocks:
  - Data loaders
  - Transformers
  - Data exporters
  - Sensors

### Step 4: Run Pipeline from CLI
```bash
make run-pipeline
make logs-scheduler
```

### Step 5: Check Model Registry
```bash
make show-models
cat mlops_demo/model_registry/latest.json
```

### Step 6: Test Predictions
```bash
make test-predict
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [...]}' | jq .
```

### Step 7: Monitor Execution
```bash
# In separate terminal
make logs-web

# In another terminal
docker-compose ps
```

---

## Key Takeaways

✅ **Mage AI is ideal for MLOps teams that want:**
- Single platform for experimentation through deployment
- Interactive development experience
- Easy deployment and scaling
- Built-in monitoring and observability
- Open-source with no vendor lock-in

❌ **Mage might not be best if you need:**
- Complex DAG dependencies (prefer Dagster)
- Heavy cloud integration (prefer cloud-native tools)
- Mature ecosystem (prefer Airflow)

---

## Next Steps

1. **Explore the codebase:** Check `mlops_demo/` directory
2. **Read ARCHITECTURE.md:** Understand microservices setup
3. **Review Makefile:** See all available commands
4. **Create your first pipeline:** Use Mage UI to build custom pipeline
5. **Deploy to cloud:** Modify executor configuration in `metadata.yaml`

---

## Resources

- **Official Docs:** https://docs.mage.ai
- **GitHub Repository:** https://github.com/mage-ai/mage-ai
- **Community Slack:** https://mageai.slack.com
- **Blog:** https://www.mage.ai/blog

---

## Contact & Questions

For questions about this masterclass or Mage AI implementation:
- Review logs: `make logs`
- Check services: `make health`
- Debug pipelines: Mage UI → Pipeline → Logs tab

---

**Last Updated:** February 12, 2026
**Mage AI Version:** 0.9.79 (pinned)
**Platform:** Docker Compose with microservices architecture
