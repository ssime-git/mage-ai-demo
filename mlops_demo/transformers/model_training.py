if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import joblib
import json
import os

@transformer
def train_model(data: dict, *args, **kwargs) -> dict:
    """
    Train machine learning model for churn prediction
    """
    # Convert lists back to numpy arrays for ML training
    import numpy as np
    X_train = np.array(data['X_train'])
    y_train = np.array(data['y_train'])
    X_test = np.array(data['X_test'])
    y_test = np.array(data['y_test'])
    
    # Initialize and train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc_score = roc_auc_score(y_test, y_pred_proba)
    
    # Feature importance
    feature_importance = dict(zip(
        data['feature_names'], 
        model.feature_importances_
    ))
    
    # Sort by importance
    feature_importance = dict(sorted(
        feature_importance.items(), 
        key=lambda x: x[1], 
        reverse=True
    ))
    
    # Save model
    model_path = '/home/src/mlops_demo/models/churn_model.pkl'
    joblib.dump(model, model_path)
    
    # Save metrics
    metrics = {
        'accuracy': float(accuracy),
        'auc_score': float(auc_score),
        'feature_importance': feature_importance,
        'model_path': model_path,
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }
    
    with open('/home/src/mlops_demo/models/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Model trained successfully!")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"AUC Score: {auc_score:.4f}")
    print(f"Top 3 features: {list(feature_importance.keys())[:3]}")
    
    return metrics

@test
def test_output(output, *args) -> None:
    assert 'accuracy' in output, 'Accuracy metric missing'
    assert output['accuracy'] > 0.5, 'Model accuracy too low'
    assert 'model_path' in output, 'Model path missing'
    print(f"✅ Model training validation passed")
