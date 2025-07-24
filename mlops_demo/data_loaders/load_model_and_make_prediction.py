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
    
    # Load latest model from registry
    registry_path = '/home/src/mlops_demo/model_registry'
    latest_path = os.path.join(registry_path, 'latest.json')
    
    if not os.path.exists(latest_path):
        raise Exception("No trained model found. Please run the training pipeline first.")
    
    with open(latest_path, 'r') as f:
        latest_info = json.load(f)
    
    # Load model and scaler
    model_path = os.path.join(latest_info['path'], 'model.pkl')
    scaler_path = os.path.join(latest_info['path'], 'scaler.pkl')
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
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
        'model_version': latest_info['version'],
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
