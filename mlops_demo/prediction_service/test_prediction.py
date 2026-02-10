import json
import requests

TEST_CUSTOMER = {
    "account_age": 24,
    "monthly_charges": 85.5,
    "total_charges": 2052.0,
    "num_services": 5,
    "customer_service_calls": 2,
    "contract_length": 12,
    "payment_method_score": 0.8,
    "usage_frequency": 0.7,
    "support_tickets": 1,
    "satisfaction_score": 0.6,
}

if __name__ == "__main__":
    resp = requests.post(
        "http://localhost:5000/predict",
        json=TEST_CUSTOMER,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    print(json.dumps(resp.json(), indent=2))
