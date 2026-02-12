import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


import joblib
import json
import os
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient


def _load_model_and_scaler():
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    if not tracking_uri:
        raise Exception('MLFLOW_TRACKING_URI is not set. Please configure MLflow in your environment.')

    model_name = os.getenv('MLFLOW_REGISTERED_MODEL_NAME', 'churn-model')
    stage = os.getenv('MLFLOW_MODEL_STAGE', 'Production')

    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri=tracking_uri)

    versions = client.get_latest_versions(model_name, stages=[stage])
    if not versions:
        versions = client.get_latest_versions(model_name)
    if not versions:
        raise Exception(f'No models found in MLflow registry for {model_name}. Please run the training pipeline first.')

    mv = versions[0]

    model_uri = f'models:/{model_name}/{mv.version}'
    model = mlflow.sklearn.load_model(model_uri)

    scaler_local_path = client.download_artifacts(mv.run_id, 'preprocess/scaler.pkl')
    scaler = joblib.load(scaler_local_path)

    return model, scaler, str(mv.version)

@data_loader
def predict_churn(*args, **kwargs):
    """
    Load model and make predictions via API trigger
    """
    # Get prediction data from API call variables
    if 'input_data' in kwargs:
        input_data = kwargs['input_data']
    else:
        # Default test data for demonstration
        input_data = {
            "account_age": 24,
            "monthly_charges": 85.5,
            "total_charges": 2052.0,
            "num_services": 5,
            "customer_service_calls": 2,
            "contract_length": 12,
            "payment_method_score": 0.8,
            "usage_frequency": 0.7,
            "support_tickets": 1,
            "satisfaction_score": 0.6
        }
    
    model, scaler, model_version = _load_model_and_scaler()
    
    # Feature names (should match training)
    feature_names = [
        'account_age', 'monthly_charges', 'total_charges', 'num_services',
        'customer_service_calls', 'contract_length', 'payment_method_score',
        'usage_frequency', 'support_tickets', 'satisfaction_score'
    ]
    
    # Prepare input data
    df = pd.DataFrame([input_data])
    
    # Ensure all features are present
    for feature in feature_names:
        if feature not in df.columns:
            df[feature] = 0
    
    # Select and order features
    X = df[feature_names].values
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Make prediction
    prediction = model.predict(X_scaled)[0]
    probability = model.predict_proba(X_scaled)[0]
    
    result = {
        'customer_data': input_data,
        'prediction': int(prediction),
        'probability': {
            'no_churn': float(probability[0]),
            'churn': float(probability[1])
        },
        'risk_level': 'High' if probability[1] > 0.7 else 'Medium' if probability[1] > 0.3 else 'Low',
        'model_version': model_version,
        'prediction_timestamp': pd.Timestamp.now().isoformat()
    }
    
    print(f"Prediction made: {result}")
    return result

@test
def test_output(output, *args) -> None:
    assert 'prediction' in output, 'Prediction missing'
    assert 'probability' in output, 'Probability missing'
    assert 'risk_level' in output, 'Risk level missing'
    print("✅ Prediction service validation passed")
