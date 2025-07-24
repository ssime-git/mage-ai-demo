if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


import joblib
import json
import os
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

@data_exporter
def create_prediction_service(metrics: dict, *args, **kwargs) -> None:
    """
    Create a simple prediction service
    """
    # Create service directory
    service_path = '/home/src/mlops_demo/prediction_service'
    os.makedirs(service_path, exist_ok=True)
    
    # Create Flask app code
    flask_app_code = '''
import joblib
import json
import os
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load latest model
with open('/home/src/mlops_demo/model_registry/latest.json', 'r') as f:
    latest_info = json.load(f)

model_path = os.path.join(latest_info['path'], 'model.pkl')
scaler_path = os.path.join(latest_info['path'], 'scaler.pkl')

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

feature_names = [
    'account_age', 'monthly_charges', 'total_charges', 'num_services',
    'customer_service_calls', 'contract_length', 'payment_method_score',
    'usage_frequency', 'support_tickets', 'satisfaction_score'
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': latest_info['version']})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Ensure all features are present
        for feature in feature_names:
            if feature not in df.columns:
                df[feature] = 0
        
        # Select and order features
        X = df[feature_names]
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make prediction
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]
        
        return jsonify({
            'prediction': int(prediction),
            'probability': {
                'no_churn': float(probability[0]),
                'churn': float(probability[1])
            },
            'risk_level': 'High' if probability[1] > 0.7 else 'Medium' if probability[1] > 0.3 else 'Low'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
    
    # Save Flask app
    with open(os.path.join(service_path, 'app.py'), 'w') as f:
        f.write(flask_app_code)
    
    # Create requirements.txt
    requirements = '''flask==2.3.3
joblib==1.3.2
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
'''
    
    with open(os.path.join(service_path, 'requirements.txt'), 'w') as f:
        f.write(requirements)
    
    # Create test script
    test_script = '''
import requests
import json

# Test data
test_customer = {
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

# Make prediction request
response = requests.post('http://localhost:5000/predict', 
                        json=test_customer,
                        headers={'Content-Type': 'application/json'})

print("Prediction Result:")
print(json.dumps(response.json(), indent=2))
'''
    
    with open(os.path.join(service_path, 'test_prediction.py'), 'w') as f:
        f.write(test_script)
    
    print(f"✅ Prediction service created!")
    print(f"Service path: {service_path}")
    print(f"To start the service:")
    print(f"  cd {service_path}")
    print(f"  pip install -r requirements.txt")
    print(f"  python app.py")

@test
def test_output(*args) -> None:
    service_path = '/home/src/mlops_demo/prediction_service'
    app_path = os.path.join(service_path, 'app.py')
    assert os.path.exists(app_path), 'Prediction service creation failed'
    print("✅ Prediction service validation passed")
