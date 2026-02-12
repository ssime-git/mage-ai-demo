# Mage AI: Open-Source MLOps Platform with Advanced Model Management

## Executive Summary

Mage AI is a modern, open-source data pipeline platform that provides a comprehensive solution for building, deploying, and monitoring machine learning and data engineering workflows. This masterclass demonstrates how Mage addresses the complete MLOps lifecycle with **advanced features including dynamic model reloading, data versioning, and comprehensive lineage tracking**.

**Version:** 0.9.79 (pinned for reproducibility)
**Enhanced with:** Dynamic Model Reload, Data Versioning, Complete Lineage Tracking


## Table of Contents

1. [What is Mage AI?](#what-is-mage-ai)
2. [Why Mage for MLOps?](#why-mage-for-mlops)
3. [Key Features](#key-features)
4. [Architecture Overview](#architecture-overview)
5. [Advanced MLOps Features](#advanced-mlops-features)
6. [MLOps Workflow](#mlops-workflow)
7. [Getting Started](#getting-started)
8. [Demo Commands](#demo-commands)
9. [Comparison with Alternatives](#comparison-with-alternatives)
10. [Use Cases](#use-cases)


## What is Mage AI?

Mage AI is a Python-based data platform that combines the best practices from traditional data engineering with modern MLOps needs. It provides:

- **Interactive notebook-style IDE** for writing modular pipeline code
- **Built-in orchestration** with no additional framework required
- **Production-ready deployment** with Docker support
- **Distributed execution** with multiple executor options
- **Dynamic model management** with zero-downtime updates
- **Complete lineage tracking** for data and code provenance
- **Native integration** with popular data platforms and ML tools

### Core Philosophy

> *"Write once, run anywhere, monitor everywhere - with complete lineage and versioning"*

Mage emphasizes modularity, testability, operationalization, and traceability of data and ML workflows.


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
├─────────────────────────────────────┤
│ Data Lineage & Versioning           │
│ └─ Manual tracking / Hooks         │
└─────────────────────────────────────┘

Result: High operational complexity, difficult debugging, poor audit trails
```

### Mage Solution

```
Unified MLOps Stack with Advanced Features
┌─────────────────────────────────────────────┐
│  Mage AI (Single Integrated Platform)       │
│                                             │
│  ├─ Interactive IDE                        │
│  ├─ Modular Code Blocks                    │
│  ├─ Built-in Orchestration                 │
│  ├─ Dynamic Model Reload (Zero-downtime)   │
│  ├─ Data Versioning (SHA256 hashing)       │
│  ├─ Complete Lineage Tracking              │
│  ├─ Experiment Tracking (API)              │
│  ├─ Model Registry Integration             │
│  ├─ Multi-executor Support                 │
│  ├─ Deployment Options                     │
│  └─ Observability (Logs/Monitoring)        │
│                                             │
└─────────────────────────────────────────────┘

Result: Simplified operations, complete audit trail, zero-downtime updates
```


## Key Features

### 1. **Modular Pipeline Design**

Each step in your pipeline is a standalone Python file that can be:
- **Tested independently** in the IDE
- **Reused across pipelines** without duplication
- **Monitored individually** with logs and metrics
- **Updated without affecting others** in the pipeline

### 2. **Built-in Orchestration**

No need for Airflow or Prefect:
- Native support for scheduling with cron expressions
- Event-based triggers (file arrival, API webhooks)
- Conditional execution and branching
- Dependency management with automatic topological sorting
- Retry logic and error handling

### 3. **Dynamic Model Reload**

Zero-downtime model updates:
- Models load on every prediction request
- No service restart needed after training
- Automatic version detection from latest.json
- Version tracking in prediction responses
- `/reload` endpoint for explicit refresh

### 4. **Data Versioning**

Complete data provenance:
- SHA256 hashing of datasets for versioning
- Automatic data version ID: `data_v_YYYYMMDD_HHMMSS`
- Tracks: row count, feature count, churn rate
- Metadata flows through entire pipeline

### 5. **Comprehensive Lineage Tracking**

Full audit trail for compliance:
- **Data Lineage:** Which data trained which model
- **Code Lineage:** Git commit, branch, training script
- **Hyperparameters:** Model configuration captured
- **Prediction History:** Audit trail of all predictions
- **Feature Importance:** Tracked with model version


## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                        │
│              (http://localhost:6789)                    │
│                                                         │
│  ├─ Pipeline Editor                                    │
│  ├─ Block Code Writing                                │
│  ├─ Execution Monitoring                              │
│  ├─ Run History & Logs                                │
│  └─ Data Preview at Each Step                         │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
┌────────▼────────┐  ┌───▼────────────┐
│  Mage Web       │  │ Mage Scheduler │
│  (Port 6789)    │  │  (Background)  │
│                 │  │                │
│ - Python        │  │ - Trigger      │
│ - PostgreSQL    │  │   Management   │
│ - Redis         │  │ - Queue        │
└────────┬────────┘  │   Processing   │
         │           └───┬────────────┘
         │               │
         └───────┬───────┘
                 │
         ┌───────▼──────────────┐
         │  Shared Services     │
         │                      │
         │ - PostgreSQL (Data)  │
         │ - Redis (Queue)      │
         │ - File System (Code) │
         └──────────────────────┘

┌─────────────────────────────────────────────────────────┐
│            Prediction Service (Port 5000)               │
│                                                         │
│  ├─ Dynamic Model Loader                              │
│  ├─ /predict - Auto-reload & predict                  │
│  ├─ /reload - Manual model reload                     │
│  ├─ /lineage - Full lineage history                   │
│  ├─ /log-prediction - Audit trail logging            │
│  └─ /health - Health check with version              │
└─────────────────────────────────────────────────────────┘
```


## Advanced MLOps Features

### Feature 1: Dynamic Model Reload

**Problem Solved:** Traditional services require restart to use new models

**Solution:**
- Models load on every prediction request
- Latest model path read from `latest.json`
- Version included in prediction response
- No downtime during model updates

**Usage:**
```bash
# Automatic (happens on every prediction)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{...features...}'

# Explicit reload
curl -X POST http://localhost:5000/reload
```

### Feature 2: Data Versioning

**Problem Solved:** Unclear which data trained which model

**Solution:**
- SHA256 hash of dataset for unique identification
- Timestamped data version: `data_v_20260212_160000`
- Metadata includes: row count, features, churn rate
- Passed through entire pipeline

**Tracked Metadata:**
```json
{
  "version": "data_v_20260212_160000",
  "hash": "sha256:abc123...",
  "row_count": 1000,
  "feature_count": 10,
  "features": [...],
  "churn_rate": 0.26
}
```

### Feature 3: Complete Lineage Tracking

**Problem Solved:** Cannot trace model decisions back to source data and code

**Solution:**
- `lineage.json` per model version with complete provenance
- Automatic git commit capture
- Hyperparameters recorded
- Prediction audit trail

**Lineage Contents:**
```json
{
  "version": "v_20260212_161000",
  "metrics": {
    "accuracy": 0.92,
    "auc_score": 0.88
  },
  "code_lineage": {
    "git_commit": "abc123def456...",
    "git_branch": "main",
    "training_script": "transformers/model_training.py"
  },
  "data_lineage": {
    "version": "data_v_20260212_160000",
    "hash": "sha256:abc123...",
    "row_count": 1000
  },
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10
  },
  "predictions": {
    "count": 5,
    "last_prediction_time": "2026-02-12T16:30:45",
    "history": [...]
  }
}
```


## MLOps Workflow

### Complete Training & Deployment Flow

```
1. TRAINING (Mage Web UI or CLI)
   │
   ├─ Load Data
   │  └─ Calculate SHA256 hash → data_v_YYYYMMDD_HHMMSS
   │
   ├─ Preprocess
   │  └─ Feature engineering
   │
   ├─ Train Model
   │  └─ RandomForest with metrics
   │
   └─ Register Model
      ├─ Save model.pkl & scaler.pkl
      ├─ Create lineage.json with:
      │  ├─ Data hash & version
      │  ├─ Git commit & branch
      │  ├─ Hyperparameters
      │  └─ Metrics
      └─ Update latest.json → v_YYYYMMDD_HHMMSS

2. DEPLOYMENT (Automatic, Zero-downtime)
   │
   └─ Next /predict request automatically:
      ├─ Reads latest.json
      ├─ Loads new model
      ├─ Serves prediction with version
      └─ Logs to lineage if requested

3. MONITORING (Query Lineage)
   │
   └─ GET /lineage
      ├─ View data version used
      ├─ Check git commit
      ├─ Review metrics
      └─ Audit prediction history
```


## Getting Started

### 1. Start Services

```bash
docker-compose up -d
```

### 2. Access Mage UI

```
http://localhost:6789
```

### 3. Open demo_mlops Pipeline

```
Navigate to "demo_mlops" in the left panel
```

### 4. Run Training

```bash
Click "Run" button or use CLI:
docker-compose exec -T mage-web mage run demo_mlops
```

### 5. Make Predictions

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"account_age": 24, "monthly_charges": 65.5, ...}'
```

### 6. Check Lineage

```bash
curl http://localhost:5000/lineage | jq .
```


## Demo Commands

### Model Training

```bash
# Train model (creates data version, lineage, metrics)
docker-compose exec -T mage-web mage run demo_mlops

# Check training output
docker-compose logs mage-web | grep "✅"
```

### Prediction API

```bash
# Single prediction (auto-reloads model)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "account_age": 24,
    "monthly_charges": 65.5,
    "total_charges": 1569.5,
    "num_services": 3,
    "customer_service_calls": 4,
    "contract_length": 12,
    "payment_method_score": 0.8,
    "usage_frequency": 0.7,
    "support_tickets": 2,
    "satisfaction_score": 0.6
  }'
```

### Model Management

```bash
# Health check
curl http://localhost:5000/health | jq .

# Reload model explicitly
curl -X POST http://localhost:5000/reload | jq .

# Get model info with lineage
curl http://localhost:5000/model-info | jq .

# View full lineage
curl http://localhost:5000/lineage | jq '.lineage.code_lineage'
```

### Prediction Logging

```bash
# Log prediction to audit trail
curl -X POST http://localhost:5000/log-prediction \
  -H "Content-Type: application/json" \
  -d '{
    "prediction": 1,
    "probability": {"churn": 0.65, "no_churn": 0.35},
    "risk_level": "High",
    "user_id": "user123"
  }'
```


## Comparison with Alternatives

| Feature | Mage | Airflow | Prefect | MLflow |
|---------|------|---------|---------|---------|
| **Setup Complexity** | Simple | Complex | Moderate | Simple |
| **Code Modularity** | Excellent | Good | Good | N/A |
| **Built-in UI** | Yes | Yes (separate) | Yes | Yes |
| **Dynamic Model Reload** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Data Versioning** | ✅ Built-in | ❌ No | ❌ No | ❌ No |
| **Lineage Tracking** | ✅ Automatic | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual |
| **Learning Curve** | Low | High | Moderate | Low |
| **Python Native** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Distributed Execution** | ✅ Yes | ✅ Yes | ✅ Yes | N/A |
| **Model Deployment** | ✅ Integrated | ❌ Separate | ❌ Separate | ✅ Integrated |


## Key Takeaways

✅ **Single Platform** - No need for Airflow + MLflow + Custom code
✅ **Zero-Downtime Updates** - Models update without service restart
✅ **Complete Lineage** - Trace any prediction back to data and code
✅ **Data Versioning** - Know exactly which data trained each model
✅ **Production Ready** - Docker support, health checks, logging
✅ **Developer Friendly** - Python-based, interactive IDE
✅ **Low Operational Overhead** - Reduced complexity vs. traditional stack


## Use Cases

### 1. **Churn Prediction (This Demo)**
- Predict which customers will churn
- Monitor model performance over time
- Retrain with new data weekly
- Audit predictions for compliance

### 2. **Fraud Detection**
- Train models on daily transaction data
- Deploy with zero downtime
- Track data drift with versioning
- Lineage for regulatory investigations

### 3. **Demand Forecasting**
- Multiple models for different regions
- Daily retraining with new sales data
- Quick rollback if performance degrades
- Complete audit trail for stakeholders

### 4. **Recommendation Systems**
- Real-time model updates
- A/B test different models
- Track user behavior changes
- Monitor feature importance over time


## Next Steps

1. **Explore the Pipeline** - Open demo_mlops in Mage UI
2. **Run Training** - Click "Run" to see data versioning and lineage
3. **Make Predictions** - Use /predict endpoint with curl
4. **Check Lineage** - View /lineage endpoint to see complete provenance
5. **Modify & Deploy** - Edit pipeline blocks and retrain
6. **Monitor** - Watch /health endpoint as you make predictions


**Documentation:** See `./README.md` for complete setup instructions
**Lineage Guide:** See `./QUICK_START.md` for presentation tips
**Architecture:** See `./ARCHITECTURE.md` for system design details


## How to Retrain the Model - Step-by-Step Guide

### Overview

The model retraining process in Mage AI is fully automated with data versioning and lineage tracking. Each training run captures:
- **Data Version** - SHA256 hash of the dataset
- **Code Version** - Git commit and branch information
- **Model Metrics** - Accuracy, AUC score, feature importance
- **Lineage** - Complete audit trail linking data → code → model

### Prerequisites

Ensure all services are running:

```bash
docker-compose ps
```

You should see:
- ✅ mage-ai-demo-postgres-1 (Healthy)
- ✅ mage-ai-demo-redis-1 (Healthy)
- ✅ mage-ai-demo-mage-web-1 (Running)
- ✅ mage-ai-demo-mage-scheduler-1 (Running)
- ✅ mage-ai-demo-prediction-service-1 (Running)


## Method 1: Retrain via Mage Web UI (Recommended)

### Step 1: Open Mage UI

```
http://localhost:6789
```

### Step 2: Navigate to Pipeline

```
Left Panel → Pipelines → demo_mlops
```

You'll see the pipeline structure:

```
Make Dataset
    ↓
Data Preprocessing
    ↓
Model Training
    ↓
Model Registry
    ↓
Model Deployment
```

### Step 3: Click "Run"

- Green "Run" button in top-right
- Pipeline executes all blocks in order
- Monitor progress in the logs panel

### Step 4: Watch Execution

The logs show:

```
✅ Loaded 1000 customer records
   Data Version: data_v_20260212_160000
   Data Hash: sha256:abc123def456
   Churn rate: 26.00%
   Shape: (1000, 11)

✅ Model trained successfully!
   Accuracy: 0.9234
   AUC Score: 0.8876
   Top 3 features: [monthly_charges, total_charges, account_age]

✅ Model registered successfully!
   Version: v_20260212_160000
   Accuracy: 0.9234
   AUC Score: 0.8876
   Git Commit: abc123def456
   Lineage: /home/src/mlops_demo/model_registry/v_20260212_160000/lineage.json
```

### Step 5: Model Automatically Available

No restart needed! The prediction service automatically picks up the new model:

```bash
# Next prediction automatically uses new model
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{...}'

# Response includes model version
{
  "prediction": 0,
  "model_version": "v_20260212_160000",
  "probability": {...}
}
```


## Method 2: Retrain via Command Line

### Option A: Using Mage CLI

```bash
# Trigger training pipeline
docker-compose exec -T mage-web mage run demo_mlops
```

Output:
```
Executing pipeline demo_mlops
✅ Block: make dataset
✅ Block: data_preproecessing
✅ Block: model_training
✅ Block: model_registry
✅ Block: model_deployment
Pipeline demo_mlops completed successfully
```

### Option B: Using Docker Compose

```bash
# Run training in Mage container
cd /home/seb/project/mage-ai-demo
docker-compose exec -T mage-web bash -c "cd mlops_demo && mage run demo_mlops"
```

### Option C: Using Makefile (if available)

```bash
# Check available make commands
make help

# Run training
make retrain-model
```


## What Happens During Retraining

### Stage 1: Data Loading

```python
# make_dataset block
├─ Generate 1000 synthetic customer records
├─ Calculate data hash: sha256:abc123...
├─ Create data version: data_v_YYYYMMDD_HHMMSS
└─ Store metadata for lineage
```

**Output:**
```json
{
  "version": "data_v_20260212_160000",
  "hash": "sha256:abc123def456...",
  "row_count": 1000,
  "feature_count": 10,
  "churn_rate": 0.26,
  "timestamp": "2026-02-12T16:00:00"
}
```

### Stage 2: Data Preprocessing

```python
# data_preproecessing block
├─ Split into train/test (80/20)
├─ Normalize features with StandardScaler
├─ Handle missing values
└─ Prepare X_train, X_test, y_train, y_test
```

### Stage 3: Model Training

```python
# model_training block
├─ Initialize RandomForestClassifier
├─ Train on 800 samples
├─ Test on 200 samples
├─ Calculate metrics:
│  ├─ Accuracy: 0.9234
│  ├─ AUC Score: 0.8876
│  └─ Feature Importance: {...}
└─ Save model.pkl to /home/src/mlops_demo/models/
```

**Output Metrics:**
```json
{
  "accuracy": 0.9234,
  "auc_score": 0.8876,
  "feature_importance": {
    "monthly_charges": 0.25,
    "total_charges": 0.20,
    "account_age": 0.15,
    ...
  },
  "training_samples": 800,
  "test_samples": 200,
  "model_path": "/home/src/mlops_demo/models/churn_model.pkl"
}
```

### Stage 4: Model Registry

```python
# model_registry block
├─ Create version directory: v_YYYYMMDD_HHMMSS/
├─ Save model.pkl
├─ Save scaler.pkl
├─ Create metadata.json (backward compatible)
├─ Create lineage.json (COMPLETE AUDIT TRAIL)
└─ Update latest.json pointer
```

**lineage.json Contains:**
```json
{
  "version": "v_20260212_160000",
  "timestamp": "2026-02-12T16:10:00",
  "metrics": {
    "accuracy": 0.9234,
    "auc_score": 0.8876,
    "training_samples": 800,
    "test_samples": 200
  },
  "code_lineage": {
    "git_commit": "abc123def456...",
    "git_branch": "master",
    "git_status": "clean",
    "training_script": "transformers/model_training.py"
  },
  "data_lineage": {
    "version": "data_v_20260212_160000",
    "hash": "sha256:abc123def456...",
    "row_count": 1000,
    "feature_count": 10,
    "churn_rate": 0.26
  },
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
  },
  "predictions": {
    "count": 0,
    "last_prediction_time": null,
    "history": []
  }
}
```

### Stage 5: Model Deployment

```python
# model_deployment block
└─ Log deployment status
  └─ Save to deployment/deployment_status.json
```


## Post-Training Verification

### 1. Check Model was Registered

```bash
# List all model versions
ls -lha /home/seb/project/mage-ai-demo/mlops_demo/model_registry/

# Output:
# drwxr-xr-x v_20260212_160000/
# -rw-r--r-- latest.json
```

### 2. Verify Latest Model Pointer

```bash
cat /home/seb/project/mage-ai-demo/mlops_demo/model_registry/latest.json

# Output:
# {
#   "version": "v_20260212_160000",
#   "path": "/home/src/mlops_demo/model_registry/v_20260212_160000",
#   "updated_at": "20260212_160000"
# }
```

### 3. Check Lineage was Created

```bash
# View lineage.json
cat /home/seb/project/mage-ai-demo/mlops_demo/model_registry/v_20260212_160000/lineage.json | jq .

# Or get via API
curl http://localhost:5000/lineage | jq '.lineage.code_lineage'
```

### 4. Verify Model Metrics

```bash
# View model metadata
cat /home/seb/project/mage-ai-demo/mlops_demo/model_registry/v_20260212_160000/metadata.json | jq '.metrics'

# Output:
# {
#   "accuracy": 0.9234,
#   "auc_score": 0.8876
# }
```

### 5. Test Prediction with New Model

```bash
# Make prediction - automatically uses new model
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "account_age": 24,
    "monthly_charges": 65.5,
    "total_charges": 1569.5,
    "num_services": 3,
    "customer_service_calls": 4,
    "contract_length": 12,
    "payment_method_score": 0.8,
    "usage_frequency": 0.7,
    "support_tickets": 2,
    "satisfaction_score": 0.6
  }' | jq .

# Output shows new model version:
# {
#   "prediction": 0,
#   "model_version": "v_20260212_160000",
#   "prediction_time": "2026-02-12T16:30:45.123456",
#   "probability": {
#     "churn": 0.04,
#     "no_churn": 0.96
#   },
#   "risk_level": "Low"
# }
```


## Complete Retraining Workflow Example

### Scenario: Weekly Model Retraining

```bash
# 1. Schedule weekly retraining (cron)
# Add to crontab: 0 2 * * 0 (every Sunday 2 AM)

# 2. Run the pipeline
docker-compose exec -T mage-web mage run demo_mlops

# 3. Verify in logs
docker-compose logs mage-web | grep "✅ Model registered"

# 4. Monitor metrics
curl http://localhost:5000/health | jq '.version'

# 5. Make test prediction (auto-loads new model)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{...}'

# 6. View lineage for audit
curl http://localhost:5000/lineage | jq '.lineage'

# 7. Log production predictions
curl -X POST http://localhost:5000/log-prediction \
  -H "Content-Type: application/json" \
  -d '{
    "prediction": 1,
    "user_id": "prod_user_123",
    "probability": {...}
  }'
```


## Comparing Model Versions

### View All Model Versions

```bash
ls /home/seb/project/mage-ai-demo/mlops_demo/model_registry/
# v_20250522_112442/
# v_20260210_143000/
# v_20260212_160000/
# latest.json
```

### Compare Metrics Between Versions

```bash
echo "=== Version 1 ===" && \
cat /home/seb/project/mage-ai-demo/mlops_demo/model_registry/v_20260210_143000/metadata.json | jq '.metrics' && \
echo "=== Version 2 ===" && \
cat /home/seb/project/mage-ai-demo/mlops_demo/model_registry/v_20260212_160000/metadata.json | jq '.metrics'
```

### Rollback to Previous Model

```bash
# View previous version path
PREV_VERSION="v_20260210_143000"
PREV_PATH="/home/src/mlops_demo/model_registry/$PREV_VERSION"

# Update latest.json to point to previous version
jq --arg path "$PREV_PATH" --arg ver "$PREV_VERSION" \
  '{version: $ver, path: $path, updated_at: now|todate}' \
  /home/seb/project/mage-ai-demo/mlops_demo/model_registry/latest.json > \
  /tmp/latest.json && \
  cp /tmp/latest.json /home/seb/project/mage-ai-demo/mlops_demo/model_registry/latest.json

# Reload prediction service
curl -X POST http://localhost:5000/reload

# Verify rollback
curl http://localhost:5000/health | jq '.version'
# Output: "v_20260210_143000"
```


## Troubleshooting Retraining

### Issue: Pipeline Fails

```bash
# Check logs for error
docker-compose logs mage-web | grep -i error

# Common causes:
# 1. Data loading issue - check make_dataset.py
# 2. Feature mismatch - verify feature_names
# 3. Model path issue - check /home/src/mlops_demo/models/
# 4. Permission issue - check directory permissions
```

### Issue: Model Not Updating

```bash
# Verify latest.json is updated
cat /home/seb/project/mage-ai-demo/mlops_demo/model_registry/latest.json

# Check if lineage.json was created
ls /home/seb/project/mage-ai-demo/mlops_demo/model_registry/v_*/lineage.json

# Manually reload prediction service
curl -X POST http://localhost:5000/reload
```

### Issue: Git Commit Not Captured

```bash
# Check if git is available in mage-web container
docker-compose exec -T mage-web git --version

# Check repository status
docker-compose exec -T mage-web git -C /home/src log --oneline -1

# If git not available, lineage will show:
# "git_commit": null,
# "git_status": "unknown"
```


## Key Takeaways

✅ **Zero-Downtime Retraining** - No service restart needed
✅ **Automatic Data Versioning** - SHA256 hash captures dataset uniqueness
✅ **Complete Lineage** - Data + Code + Metrics tracked together
✅ **Easy Rollback** - Update latest.json to switch model versions
✅ **Audit Trail** - Every prediction logged with timestamp and model version
✅ **Git Integration** - Training code version captured automatically
✅ **Web UI & CLI** - Multiple ways to trigger retraining


## Next Steps

1. **Run Your First Training** - Click "Run" in demo_mlops pipeline
2. **Check Lineage** - View /lineage endpoint
3. **Make Predictions** - Use /predict with new model
4. **Schedule Weekly Training** - Set up cron job
5. **Monitor Performance** - Track metrics over time
6. **Audit Trail** - Log production predictions

