if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


import json
import os
from datetime import datetime
import joblib
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

@data_exporter
def register_model(metrics: dict, *args, **kwargs) -> None:
    """
    Register model in a simple model registry
    """
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    if not tracking_uri:
        raise Exception('MLFLOW_TRACKING_URI is not set. Please configure MLflow in your environment.')

    registered_model_name = os.getenv('MLFLOW_REGISTERED_MODEL_NAME', 'churn-model')
    experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'mlops_demo')

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model = joblib.load(metrics['model_path'])

    scaler_path = '/home/src/mlops_demo/models/scaler.pkl'
    if not os.path.exists(scaler_path):
        raise Exception(f"Scaler not found at {scaler_path}. Please run the preprocessing/training pipeline first.")

    with mlflow.start_run(run_name=f"train_{timestamp}") as run:
        run_id = run.info.run_id

        mlflow.log_params({
            'model_type': 'RandomForestClassifier',
            'training_samples': metrics.get('training_samples'),
            'test_samples': metrics.get('test_samples'),
        })

        mlflow.log_metrics({
            'accuracy': float(metrics['accuracy']),
            'auc_score': float(metrics['auc_score']),
        })

        mlflow.log_artifact(scaler_path, artifact_path='preprocess')

        metrics_to_log = dict(metrics)
        mlflow.log_dict(metrics_to_log, 'training_metrics.json')

        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path='model',
            registered_model_name=registered_model_name,
        )

        print('✅ Model logged and registered in MLflow!')
        print(f"Run ID: {run_id}")
        print(f"Registered model: {registered_model_name}")
        print(f"Model URI: {model_info.model_uri}")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"AUC Score: {metrics['auc_score']:.4f}")

@test
def test_output(*args) -> None:
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    assert tracking_uri is not None and tracking_uri != '', 'MLFLOW_TRACKING_URI is not set'

    registered_model_name = os.getenv('MLFLOW_REGISTERED_MODEL_NAME', 'churn-model')
    client = MlflowClient(tracking_uri=tracking_uri)
    client.get_registered_model(registered_model_name)
    print('✅ MLflow model registry validation passed')
