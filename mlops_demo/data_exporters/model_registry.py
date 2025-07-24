if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


import json
import os
from datetime import datetime
import joblib

@data_exporter
def register_model(metrics: dict, *args, **kwargs) -> None:
    """
    Register model in a simple model registry
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
    
    # Update metrics with version info
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
    print(f"Version: {version}")
    print(f"Registry path: {version_path}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"AUC Score: {metrics['auc_score']:.4f}")

@test
def test_output(*args) -> None:
    registry_path = '/home/src/mlops_demo/model_registry'
    latest_path = os.path.join(registry_path, 'latest.json')
    assert os.path.exists(latest_path), 'Model registration failed'
    print("✅ Model registry validation passed")
