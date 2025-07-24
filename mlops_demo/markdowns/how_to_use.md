# How to use

```bash
# Test prediction API
curl -X POST http://localhost:6789/api/pipeline_schedules/1/pipeline_runs/c92cc53194484103a63d3cf4446a3b4f \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_run": {
      "variables": {
        "input_data": {
          "account_age": 36,
          "monthly_charges": 120.0,
          "total_charges": 4320.0,
          "num_services": 8,
          "customer_service_calls": 5,
          "contract_length": 6,
          "payment_method_score": 0.3,
          "usage_frequency": 0.4,
          "support_tickets": 3,
          "satisfaction_score": 0.2
        }
      }
    }
  }'
```