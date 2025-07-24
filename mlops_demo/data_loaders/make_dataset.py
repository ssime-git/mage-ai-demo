import io
import pandas as pd
import requests
import numpy as np
from sklearn.datasets import make_classification
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def load_customer_data(*args, **kwargs):
    """
    Generate synthetic customer data for churn prediction
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
    
    print(f"Loaded {len(df)} customer records")
    print(f"Churn rate: {df['churn'].mean():.2%}")
    
    return df

@test
def test_output(output, *args) -> None:
    assert output is not None, 'Data loading failed'
    assert len(output) > 0, 'No data loaded'
    assert 'churn' in output.columns, 'Target variable missing'
    print(f"✅ Data validation passed: {len(output)} records loaded")
