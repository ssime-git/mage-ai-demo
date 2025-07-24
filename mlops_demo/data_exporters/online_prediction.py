if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


import joblib
import json
import os
from datetime import datetime

@data_exporter
def create_prediction_utility(metrics: dict, *args, **kwargs) -> None:
    """
    Create a simple prediction utility function
    """
    # Create prediction utility code
    prediction_code = f'''import joblib
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime

def predict_churn(input_data):
    """
    Simple prediction function for churn prediction
    """
    try:
        # Load latest model from registry
        registry_path = '/home/src/mlops_demo/model_registry'
        latest_path = os.path.join(registry_path, 'latest.json')
        
        if not os.path.exists(latest_path):
            return {{
                'error': 'No trained model found. Please run the training pipeline first.',
                'status': 'error'
            }}
        
        with open(latest_path, 'r') as f:
            latest_info = json.load(f)
        
        # Load model and scaler
        model_path = os.path.join(latest_info['path'], 'model.pkl')
        scaler_path = os.path.join(latest_info['path'], 'scaler.pkl')
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Feature names
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
        
        result = {{
            'input_data': input_data,
            'prediction': int(prediction),
            'prediction_label': 'Will Churn' if prediction == 1 else 'Will Not Churn',
            'probability': {{
                'no_churn': float(probability[0]),
                'churn': float(probability[1])
            }},
            'confidence': float(max(probability)),
            'risk_level': 'High' if probability[1] > 0.7 else 'Medium' if probability[1] > 0.3 else 'Low',
            'model_version': latest_info['version'],
            'prediction_timestamp': datetime.now().isoformat(),
            'status': 'success'
        }}
        
        return result
        
    except Exception as e:
        return {{
            'error': str(e),
            'status': 'error'
        }}

def batch_predict(data_list):
    """
    Make predictions for multiple customers
    """
    results = []
    for i, customer_data in enumerate(data_list):
        print(f"Processing customer {{i+1}}/{{len(data_list)}}...")
        result = predict_churn(customer_data)
        results.append(result)
    return results

if __name__ == "__main__":
    # Test the function
    test_data = {{
        "account_age": 36,
        "monthly_charges": 120.0,
        "total_charges": 4320.0,
        "num_services": 8,
        "customer_service_calls": 5,
        "contract_length": 6,
        "payment_method_score": 0.3,
        "usage_frequency": 0.4,
        "support_tickets": 3,
        "satisfaction_score": 0.2
    }}
    
    print("Testing Prediction Function...")
    print("=" * 50)
    result = predict_churn(test_data)
    print(json.dumps(result, indent=2))
    print("=" * 50)
'''
    
    # Save the prediction utility
    utility_path = '/home/src/mlops_demo/predict.py'
    with open(utility_path, 'w') as f:
        f.write(prediction_code)
    
    # Create a simple test script
    test_script = f'''#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/src/mlops_demo')

from predict import predict_churn
import json

# Test cases
test_cases = [
    {{
        "name": "High Risk Customer",
        "data": {{
            "account_age": 36,
            "monthly_charges": 120.0,
            "total_charges": 4320.0,
            "num_services": 8,
            "customer_service_calls": 5,
            "contract_length": 6,
            "payment_method_score": 0.3,
            "usage_frequency": 0.4,
            "support_tickets": 3,
            "satisfaction_score": 0.2
        }}
    }},
    {{
        "name": "Low Risk Customer",
        "data": {{
            "account_age": 48,
            "monthly_charges": 75.0,
            "total_charges": 3600.0,
            "num_services": 3,
            "customer_service_calls": 1,
            "contract_length": 24,
            "payment_method_score": 0.9,
            "usage_frequency": 0.8,
            "support_tickets": 0,
            "satisfaction_score": 0.9
        }}
    }}
]

print("🔮 Mage AI Churn Prediction Service")
print("=" * 50)

for test_case in test_cases:
    print(f"\\n📊 Testing: {{test_case['name']}}")
    print("-" * 30)
    result = predict_churn(test_case['data'])
    
    if result['status'] == 'success':
        print(f"Prediction: {{result['prediction_label']}}")
        print(f"Risk Level: {{result['risk_level']}}")
        print(f"Confidence: {{result['confidence']:.2%}}")
        print(f"Churn Probability: {{result['probability']['churn']:.2%}}")
    else:
        print(f"Error: {{result['error']}}")

print("\\n" + "=" * 50)
print("✅ Prediction service is ready!")
print("💡 Usage: from predict import predict_churn")
'''
    
    test_script_path = '/home/src/mlops_demo/test_predictions.py'
    with open(test_script_path, 'w') as f:
        f.write(test_script)
    
    # Make it executable
    os.chmod(test_script_path, 0o755)
    
    print(f"✅ Prediction utility created successfully!")
    print(f"📁 Utility file: {utility_path}")
    print(f"🧪 Test script: {test_script_path}")
    print(f"")
    print(f"🚀 To test your prediction service:")
    print(f"   cd /home/src/mlops_demo")
    print(f"   python test_predictions.py")
    print(f"")
    print(f"📝 To use in code:")
    print(f"   from predict import predict_churn")
    print(f"   result = predict_churn(customer_data)")
    
    # Test the function immediately
    print(f"")
    print(f"🔍 Quick test...")
    try:
        exec(open(utility_path).read())
        test_data = {
            "account_age": 36,
            "monthly_charges": 120.0,
            "total_charges": 4320.0,
            "num_services": 8,
            "customer_service_calls": 5,
            "contract_length": 6,
            "payment_method_score": 0.3,
            "usage_frequency": 0.4,
            "support_tickets": 3,
            "satisfaction_score": 0.2
        }
        # Note: predict_churn function is now available in local scope
        result = predict_churn(test_data)
        if result['status'] == 'success':
            print(f"✅ Test prediction successful!")
            print(f"   Prediction: {result['prediction_label']}")
            print(f"   Risk Level: {result['risk_level']}")
        else:
            print(f"❌ Test failed: {result['error']}")
    except Exception as e:
        print(f"⚠️ Quick test failed: {str(e)}")
        print(f"   Run the test script manually after pipeline completion")

@test
def test_output(*args) -> None:
    utility_path = '/home/src/mlops_demo/predict.py'
    test_path = '/home/src/mlops_demo/test_predictions.py'
    assert os.path.exists(utility_path), 'Prediction utility not created'
    assert os.path.exists(test_path), 'Test script not created'
    print("✅ Prediction utility validation passed")
