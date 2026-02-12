import os

import mlflow


def configure_mlflow(experiment_name: str = 'mlops_demo'):
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://mlflow:5000')
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    return mlflow
