import joblib
import os

from pandas import DataFrame
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def preprocess_data(df: DataFrame, *args, **kwargs) -> dict:
    """
    Preprocess customer data for ML training
    """
    # Create preprocessing directory
    os.makedirs('/home/src/mlops_demo/models', exist_ok=True)
    
    # Separate features and target
    feature_cols = [col for col in df.columns if col not in ['customer_id', 'churn']]
    X = df[feature_cols]
    y = df['churn']
    
    # Handle missing values
    X = X.fillna(X.median())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save the scaler for later use
    joblib.dump(scaler, '/home/src/mlops_demo/models/scaler.pkl')
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    print(f"Features: {len(feature_cols)}")
    
    # Convert numpy arrays to lists for JSON serialization
    # But keep the original arrays for ML training
    return {
        'X_train': X_train.tolist(),
        'X_test': X_test.tolist(),
        'y_train': y_train.tolist(),
        'y_test': y_test.tolist(),
        'feature_names': feature_cols,
        'scaler_path': '/home/src/mlops_demo/models/scaler.pkl',
        'data_shapes': {
            'X_train_shape': X_train.shape,
            'X_test_shape': X_test.shape,
            'y_train_shape': y_train.shape,
            'y_test_shape': y_test.shape
        }
    }

@test
def test_output(output, *args) -> None:
    assert output is not None, 'Output is None'
    assert isinstance(output, dict), 'Output should be a dictionary'
    assert 'X_train' in output, 'Training features missing'
    assert 'y_train' in output, 'Training target missing'
    assert 'X_test' in output, 'Test features missing'
    assert 'y_test' in output, 'Test target missing'
    assert 'data_shapes' in output, 'Data shapes missing'
    
    # Check data shapes using the stored shape info
    shapes = output['data_shapes']
    assert shapes['X_train_shape'][0] > 0, 'No training data'
    assert shapes['X_test_shape'][0] > 0, 'No test data'
    assert shapes['y_train_shape'][0] > 0, 'No training labels'
    assert shapes['y_test_shape'][0] > 0, 'No test labels'
    
    # Check that data is in list format (JSON serializable)
    assert isinstance(output['X_train'], list), 'X_train should be a list'
    assert isinstance(output['y_train'], list), 'y_train should be a list'
    
    print(f"✅ Preprocessing validation passed")
    print(f"   Training samples: {shapes['X_train_shape'][0]}")
    print(f"   Test samples: {shapes['X_test_shape'][0]}")
    print(f"   Features: {len(output['feature_names'])}")

