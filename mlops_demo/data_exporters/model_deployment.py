if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

import joblib
import json
import os
import pandas as pd

@data_exporter
def deploy_model_for_serving(data: dict, *args, **kwargs) -> None:
    """
    Simple model deployment - just save deployment info
    """
    # Create deployment directory
    deployment_path = '/home/src/mlops_demo/deployment'
    os.makedirs(deployment_path, exist_ok=True)
    
    # Handle both dictionary and list inputs
    if isinstance(data, list):
        # If it's a list, assume it's the first item that contains our metrics
        metrics = data[0] if data else {}
    else:
        metrics = data
    
    # Extract metrics safely
    accuracy = metrics.get('accuracy', 0.0)
    auc_score = metrics.get('auc_score', 0.0)
    model_path = metrics.get('model_path', '/home/src/mlops_demo/models/churn_model.pkl')
    
    # Save deployment metadata
    deployment_info = {
        'model_deployed': True,
        'deployment_timestamp': str(pd.Timestamp.now()),
        'model_accuracy': float(accuracy),
        'model_auc': float(auc_score),
        'model_path': model_path,
        'status': 'ready_for_predictions'
    }
    
    with open(os.path.join(deployment_path, 'deployment_status.json'), 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print("✅ Model deployed successfully!")
    print(f"   Accuracy: {accuracy:.4f}")
    print(f"   AUC Score: {auc_score:.4f}")
    print(f"   Model Path: {model_path}")
    print(f"   Status: Ready for predictions")
    print(f"   Next: Create prediction pipeline")
    
    # Also print the input data structure for debugging
    print(f"\n🔍 Debug Info:")
    print(f"   Input type: {type(data)}")
    if isinstance(data, list):
        print(f"   List length: {len(data)}")
        if data:
            print(f"   First item type: {type(data[0])}")
            print(f"   First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
    else:
        print(f"   Dict keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

@test
def test_output(*args) -> None:
    deployment_file = '/home/src/mlops_demo/deployment/deployment_status.json'
    assert os.path.exists(deployment_file), 'Deployment file not created'
    print("✅ Model deployment successful")
