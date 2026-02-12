if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

import json
import os
from datetime import datetime
import joblib
import subprocess

@data_exporter
def register_model(metrics: dict, *args, **kwargs) -> None:
    """
    Register model in a versioned model registry with full lineage tracking
    """
    # Create model registry directory
    registry_path = '/home/src/mlops_demo/model_registry'
    os.makedirs(registry_path, exist_ok=True)
    
    # Create model version
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version = f"v_{timestamp}"
    
    # Load the trained model
    model = joblib.load(metrics['model_path'])
    scaler = joblib.load('/home/src/mlops_demo/models/scaler.pkl')
    
    # Create version directory
    version_path = os.path.join(registry_path, version)
    os.makedirs(version_path, exist_ok=True)
    
    # Save model artifacts
    joblib.dump(model, os.path.join(version_path, 'model.pkl'))
    joblib.dump(scaler, os.path.join(version_path, 'scaler.pkl'))
    
    # Get git information for code lineage
    git_info = get_git_info()
    
    # Get data metadata from pipeline context if available
    data_metadata = None
    if 'data_metadata' in kwargs:
        data_metadata = kwargs.get('data_metadata')
    
    # Create comprehensive lineage information
    lineage = {
        "version": version,
        "timestamp": datetime.now().isoformat(),
        "model_type": "RandomForestClassifier",
        "status": "registered",
        "metrics": {
            "accuracy": metrics['accuracy'],
            "auc_score": metrics['auc_score'],
            "training_samples": metrics.get('training_samples', 'unknown'),
            "test_samples": metrics.get('test_samples', 'unknown')
        },
        "feature_importance": metrics['feature_importance'],
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        },
        "code_lineage": {
            "git_commit": git_info.get('commit'),
            "git_branch": git_info.get('branch'),
            "git_status": git_info.get('status'),
            "training_script": "transformers/model_training.py",
            "registry_script": "data_exporters/model_registry.py"
        },
        "data_lineage": data_metadata if data_metadata else {
            "note": "Data metadata not captured in pipeline"
        },
        "preprocessing": [
            "normalize_features",
            "handle_missing_values",
            "split_train_test"
        ],
        "artifacts": {
            "model_path": os.path.join(version_path, 'model.pkl'),
            "scaler_path": os.path.join(version_path, 'scaler.pkl')
        },
        "predictions": {
            "count": 0,
            "last_prediction_time": None,
            "history": []
        }
    }
    
    # Save lineage information
    lineage_path = os.path.join(version_path, 'lineage.json')
    with open(lineage_path, 'w') as f:
        json.dump(lineage, f, indent=2)
    
    # Update metadata (for backward compatibility)
    registry_entry = {
        'version': version,
        'timestamp': timestamp,
        'model_type': 'RandomForestClassifier',
        'status': 'registered',
        'metrics': {
            'accuracy': metrics['accuracy'],
            'auc_score': metrics['auc_score']
        },
        'feature_importance': metrics['feature_importance'],
        'artifacts': {
            'model_path': os.path.join(version_path, 'model.pkl'),
            'scaler_path': os.path.join(version_path, 'scaler.pkl')
        }
    }
    
    # Save registry entry
    with open(os.path.join(version_path, 'metadata.json'), 'w') as f:
        json.dump(registry_entry, f, indent=2)
    
    # Update latest model pointer
    latest_path = os.path.join(registry_path, 'latest.json')
    with open(latest_path, 'w') as f:
        json.dump({
            'version': version,
            'path': version_path,
            'updated_at': timestamp
        }, f, indent=2)
    
    print(f"✅ Model registered successfully!")
    print(f"   Version: {version}")
    print(f"   Registry path: {version_path}")
    print(f"   Accuracy: {metrics['accuracy']:.4f}")
    print(f"   AUC Score: {metrics['auc_score']:.4f}")
    print(f"   Git Commit: {git_info.get('commit', 'unknown')[:8]}")
    print(f"   Lineage: {lineage_path}")

def get_git_info():
    """Extract git information for code lineage tracking"""
    git_info = {
        'commit': None,
        'branch': None,
        'status': 'unknown'
    }
    
    try:
        # Get current commit hash
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd='/home/src',
            stderr=subprocess.DEVNULL
        ).decode().strip()
        git_info['commit'] = commit
        
        # Get current branch
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd='/home/src',
            stderr=subprocess.DEVNULL
        ).decode().strip()
        git_info['branch'] = branch
        
        # Check if there are uncommitted changes
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            cwd='/home/src',
            stderr=subprocess.DEVNULL
        ).decode().strip()
        git_info['status'] = 'clean' if not status else 'dirty'
        
    except Exception as e:
        print(f"⚠️  Warning: Could not retrieve git information: {str(e)}")
    
    return git_info

@test
def test_output(*args) -> None:
    registry_path = '/home/src/mlops_demo/model_registry'
    latest_path = os.path.join(registry_path, 'latest.json')
    assert os.path.exists(latest_path), 'Model registration failed'
    
    # Verify lineage was created
    with open(latest_path, 'r') as f:
        latest = json.load(f)
    
    lineage_path = os.path.join(latest['path'], 'lineage.json')
    assert os.path.exists(lineage_path), 'Lineage file not created'
    
    with open(lineage_path, 'r') as f:
        lineage = json.load(f)
    
    assert 'code_lineage' in lineage, 'Code lineage missing'
    assert 'data_lineage' in lineage, 'Data lineage missing'
    
    print("✅ Model registry validation passed")
    print(f"✅ Lineage tracking validation passed")
