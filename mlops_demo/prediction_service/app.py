import json
import os
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load latest model metadata
LATEST_INFO_PATH = os.environ.get("LATEST_INFO_PATH", "/home/src/mlops_demo/model_registry/latest.json")
with open(LATEST_INFO_PATH, "r") as f:
    latest_info = json.load(f)

MODEL_PATH = os.path.join(latest_info["path"], "model.pkl")
SCALER_PATH = os.path.join(latest_info["path"], "scaler.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "version": latest_info["version"]})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        df = pd.DataFrame([data])

        for feature in FEATURE_NAMES:
            if feature not in df.columns:
                df[feature] = 0

        X = df[FEATURE_NAMES]
        X_scaled = scaler.transform(X)
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]

        return jsonify(
            {
                "prediction": int(prediction),
                "probability": {
                    "no_churn": float(probability[0]),
                    "churn": float(probability[1]),
                },
                "risk_level": "High"
                if probability[1] > 0.7
                else "Medium" if probability[1] > 0.3 else "Low",
            }
        )
    except Exception as exc:  # pragma: no cover - runtime safety
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
