import json
import os
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Global cache for model artifacts
_model_cache = None
_scaler_cache = None
_version_cache = None
_last_reload_time = None

FEATURE_NAMES = [
    "account_age",
    "monthly_charges",
    "total_charges",
    "num_services",
    "customer_service_calls",
    "contract_length",
    "payment_method_score",
    "usage_frequency",
    "support_tickets",
    "satisfaction_score",
]


def load_model():
    """
    Dynamically load or reload model from latest.json
    Returns: (model, scaler, version)
    """
    global _model_cache, _scaler_cache, _version_cache, _last_reload_time
    
    try:
        # Read latest.json to get current model path
        latest_info_path = os.environ.get(
            "LATEST_INFO_PATH",
            "/home/src/mlops_demo/model_registry/latest.json"
        )
        
        with open(latest_info_path, "r") as f:
            latest_info = json.load(f)
        
        # Construct paths to model and scaler
        model_path = os.path.join(latest_info["path"], "model.pkl")
        scaler_path = os.path.join(latest_info["path"], "scaler.pkl")
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        version = latest_info["version"]
        
        # Update cache
        _model_cache = model
        _scaler_cache = scaler
        _version_cache = version
        _last_reload_time = datetime.now().isoformat()
        
        return model, scaler, version
    
    except Exception as e:
        raise Exception(f"Failed to load model: {str(e)}")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint with current model version"""
    try:
        model, scaler, version = load_model()
        return jsonify({
            "status": "healthy",
            "version": version,
            "last_reload": _last_reload_time
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/reload", methods=["POST"])
def reload():
    """
    Manually reload model from latest.json
    Useful after new model training completes
    """
    try:
        model, scaler, version = load_model()
        return jsonify({
            "status": "success",
            "version": version,
            "message": "Model reloaded successfully",
            "reload_time": _last_reload_time
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict with automatic model reload
    Ensures always serving the latest model
    """
    try:
        # Load/reload model before each prediction
        model, scaler, version = load_model()
        
        # Parse input data
        data = request.get_json(force=True)
        df = pd.DataFrame([data])
        
        # Ensure all features are present
        for feature in FEATURE_NAMES:
            if feature not in df.columns:
                df[feature] = 0
        
        # Prepare features
        X = df[FEATURE_NAMES]
        X_scaled = scaler.transform(X)
        
        # Make prediction
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]
        
        # Determine risk level
        risk_level = "High" if probability[1] > 0.7 else "Medium" if probability[1] > 0.3 else "Low"
        
        return jsonify({
            "prediction": int(prediction),
            "model_version": version,
            "probability": {
                "no_churn": float(probability[0]),
                "churn": float(probability[1])
            },
            "risk_level": risk_level,
            "prediction_time": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400


@app.route("/model-info", methods=["GET"])
def model_info():
    """Get current model metadata and lineage information"""
    try:
        model, scaler, version = load_model()
        
        latest_info_path = os.environ.get(
            "LATEST_INFO_PATH",
            "/home/src/mlops_demo/model_registry/latest.json"
        )
        
        with open(latest_info_path, "r") as f:
            latest_info = json.load(f)
        
        # Try to load lineage if it exists
        version_path = latest_info.get("path", "")
        lineage_path = os.path.join(version_path, "lineage.json")
        
        lineage = None
        if os.path.exists(lineage_path):
            with open(lineage_path, "r") as f:
                lineage = json.load(f)
        
        return jsonify({
            "version": version,
            "model_path": version_path,
            "lineage": lineage,
            "last_reload": _last_reload_time
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


@app.route("/log-prediction", methods=["POST"])
def log_prediction():
    """
    Log prediction back to model lineage for audit trail
    Call this after making predictions to maintain lineage history
    """
    try:
        data = request.get_json(force=True)
        
        # Get current model version
        latest_info_path = os.environ.get(
            "LATEST_INFO_PATH",
            "/home/src/mlops_demo/model_registry/latest.json"
        )
        
        with open(latest_info_path, "r") as f:
            latest_info = json.load(f)
        
        # Load lineage file
        version_path = latest_info.get("path", "")
        lineage_path = os.path.join(version_path, "lineage.json")
        
        if not os.path.exists(lineage_path):
            return jsonify({
                "status": "error",
                "message": "Lineage file not found"
            }), 404
        
        with open(lineage_path, "r") as f:
            lineage = json.load(f)
        
        # Create prediction log entry
        prediction_log = {
            "timestamp": datetime.now().isoformat(),
            "input_features": data.get("input_features", {}),
            "prediction": data.get("prediction"),
            "probability": data.get("probability"),
            "risk_level": data.get("risk_level"),
            "user_id": data.get("user_id", "unknown")
        }
        
        # Update prediction count and history
        if "predictions" not in lineage:
            lineage["predictions"] = {
                "count": 0,
                "last_prediction_time": None,
                "history": []
            }
        
        lineage["predictions"]["count"] += 1
        lineage["predictions"]["last_prediction_time"] = datetime.now().isoformat()
        lineage["predictions"]["history"].append(prediction_log)
        
        # Keep only last 100 predictions to avoid file bloat
        if len(lineage["predictions"]["history"]) > 100:
            lineage["predictions"]["history"] = lineage["predictions"]["history"][-100:]
        
        # Save updated lineage
        with open(lineage_path, "w") as f:
            json.dump(lineage, f, indent=2)
        
        return jsonify({
            "status": "success",
            "message": "Prediction logged successfully",
            "total_predictions": lineage["predictions"]["count"],
            "model_version": latest_info["version"]
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/lineage", methods=["GET"])
def get_lineage():
    """Get full lineage history for current model"""
    try:
        latest_info_path = os.environ.get(
            "LATEST_INFO_PATH",
            "/home/src/mlops_demo/model_registry/latest.json"
        )
        
        with open(latest_info_path, "r") as f:
            latest_info = json.load(f)
        
        version_path = latest_info.get("path", "")
        lineage_path = os.path.join(version_path, "lineage.json")
        
        if not os.path.exists(lineage_path):
            return jsonify({
                "status": "error",
                "message": "Lineage file not found"
            }), 404
        
        with open(lineage_path, "r") as f:
            lineage = json.load(f)
        
        return jsonify({
            "status": "success",
            "version": latest_info["version"],
            "lineage": lineage
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
