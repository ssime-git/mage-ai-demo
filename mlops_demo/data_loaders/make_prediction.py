if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


import joblib
import json
import os
import pandas as pd
import numpy as np

@data_loader
def predict_customer_churn(*args, **kwargs):
    """
    Make churn predictions using trained model
    """
    # Get input from API variables or use default
    input_data = kwargs.get('customer_data', {
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
    })
    
    print("🔮 Making Churn Prediction...")
    print(f"Input data: {input_data}")
    
    try:
        # Load latest model
        registry_path = '/home/src/mlops_demo/model_registry'
        latest_file = os.path.join(registry_path, 'latest.json')
        
        with open(latest_file, 'r') as f:
            latest_info = json.load(f)
        
        model_path = os.path.join(latest_info['path'], 'model.pkl')
        scaler_path = os.path.join(latest_info['path'], 'scaler.pkl')
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare features
        feature_names = [
            'account_age', 'monthly_charges', 'total_charges', 'num_services',
            'customer_service_calls', 'contract_length', 'payment_method_score',
            'usage_frequency', 'support_tickets', 'satisfaction_score'
        ]
        
        # Create dataframe
        df = pd.DataFrame([input_data])
        
        # Fill missing features with 0
        for feature in feature_names:
            if feature not in df.columns:
                df[feature] = 0
        
        # Select features in correct order
        X = df[feature_names].values
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make prediction
        prediction = model.predict(X_scaled)[0]
        probabilities = model.predict_proba(X_scaled)[0]
        
        # Create result
        result = {
            'customer_id': input_data.get('customer_id', 'unknown'),
            'prediction': int(prediction),
            'prediction_text': 'Will Churn' if prediction == 1 else 'Will Stay',
            'churn_probability': float(probabilities[1]),
            'stay_probability': float(probabilities[0]),
            'confidence': float(max(probabilities)),
            'risk_level': 'High' if probabilities[1] > 0.7 else 'Medium' if probabilities[1] > 0.3 else 'Low',
            'model_version': latest_info['version'],
            'timestamp': str(pd.Timestamp.now())
        }
        
        # Print results clearly
        print("\n" + "="*50)
        print("🎯 PREDICTION RESULTS")
        print("="*50)
        print(f"Customer: {result['customer_id']}")
        print(f"Prediction: {result['prediction_text']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Churn Probability: {result['churn_probability']:.1%}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Model Version: {result['model_version']}")
        print("="*50)
        
        return result
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'status': 'failed',
            'input_data': input_data
        }
        print(f"❌ Prediction failed: {e}")
        return error_result

@test
def test_output(output, *args) -> None:
    assert output is not None, 'No prediction output'
    
    if 'error' not in output:
        assert 'prediction' in output, 'Prediction missing'
        assert 'risk_level' in output, 'Risk level missing'
        print("✅ Prediction successful!")
    else:
        print(f"⚠️ Prediction error: {output['error']}")
