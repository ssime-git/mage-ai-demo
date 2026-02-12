import io
import pandas as pd
import requests
import numpy as np
import hashlib
import json
from sklearn.datasets import make_classification
from datetime import datetime

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def load_customer_data(*args, **kwargs):
    """
    Generate synthetic customer data for churn prediction
    Includes data versioning with SHA256 hashing for lineage tracking
    """
    # Generate synthetic dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_clusters_per_class=1,
        random_state=42
    )
    
    # Create DataFrame with meaningful column names
    feature_names = [
        'account_age', 'monthly_charges', 'total_charges', 'num_services',
        'customer_service_calls', 'contract_length', 'payment_method_score',
        'usage_frequency', 'support_tickets', 'satisfaction_score'
    ]
    
    df = pd.DataFrame(X, columns=feature_names)
    df['customer_id'] = range(1, len(df) + 1)
    df['churn'] = y
    
    # Add some realistic data transformations
    df['account_age'] = np.abs(df['account_age'] * 12).astype(int)  # months
    df['monthly_charges'] = np.abs(df['monthly_charges'] * 50 + 100)  # dollars
    df['total_charges'] = df['monthly_charges'] * df['account_age']
    df['num_services'] = np.abs(df['num_services']).astype(int) % 10 + 1
    
    # Calculate data hash for versioning
    data_hash = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
    
    # Create data version identifier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_version = f"data_v_{timestamp}"
    
    # Create data metadata
    data_metadata = {
        "version": data_version,
        "timestamp": datetime.now().isoformat(),
        "hash": data_hash,
        "row_count": len(df),
        "feature_count": len(feature_names),
        "features": feature_names,
        "target": "churn",
        "churn_rate": float(df['churn'].mean()),
        "data_shape": list(df.shape)
    }
    
    # Store data metadata in kwargs for downstream blocks
    if 'data_metadata' not in kwargs:
        kwargs['data_metadata'] = data_metadata
    
    print(f"✅ Loaded {len(df)} customer records")
    print(f"   Data Version: {data_version}")
    print(f"   Data Hash: {data_hash}")
    print(f"   Churn rate: {df['churn'].mean():.2%}")
    print(f"   Shape: {df.shape}")
    
    # Return DataFrame with metadata attached
    return df

@test
def test_output(output, *args) -> None:
    assert output is not None, 'Data loading failed'
    assert len(output) > 0, 'No data loaded'
    assert 'churn' in output.columns, 'Target variable missing'
    print(f"✅ Data validation passed: {len(output)} records loaded")
