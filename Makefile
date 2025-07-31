# Mage AI Prediction Makefile - Container-friendly version with jq support
API_URL = http://localhost:6789/api/pipeline_schedules/4/pipeline_runs/0171f97ef1cf421bbc825bf90d90bc66
BASE_URL = http://localhost:6789/api/pipeline_runs

.PHONY: help
help:
	@echo "🔮 Mage AI Prediction Commands"
	@echo "=============================="
	@echo "make high-risk      - Test high-risk customer"
	@echo "make low-risk       - Test low-risk customer"  
	@echo "make medium-risk    - Test medium-risk customer"
	@echo "make show-result ID=X - Show prediction result for run X"
	@echo "make latest-result  - Show latest prediction result"
	@echo "make predict-show   - Make prediction and show result"

.PHONY: high-risk
high-risk:
	@echo "📊 Testing HIGH RISK customer..."
	@curl -s -X POST "$(API_URL)" \
		-H "Content-Type: application/json" \
		-d '{"pipeline_run": {"variables": {"customer_data": {"customer_id": "HIGH_RISK_001", "account_age": 6, "monthly_charges": 150.0, "total_charges": 900.0, "num_services": 10, "customer_service_calls": 8, "contract_length": 1, "payment_method_score": 0.1, "usage_frequency": 0.2, "support_tickets": 5, "satisfaction_score": 0.1}}}}' \
		| jq -r '"Run ID: " + (.pipeline_run.id | tostring)'

.PHONY: low-risk  
low-risk:
	@echo "📊 Testing LOW RISK customer..."
	@curl -s -X POST "$(API_URL)" \
		-H "Content-Type: application/json" \
		-d '{"pipeline_run": {"variables": {"customer_data": {"customer_id": "LOW_RISK_001", "account_age": 48, "monthly_charges": 65.0, "total_charges": 3120.0, "num_services": 2, "customer_service_calls": 0, "contract_length": 24, "payment_method_score": 0.95, "usage_frequency": 0.9, "support_tickets": 0, "satisfaction_score": 0.95}}}}' \
		| jq -r '"Run ID: " + (.pipeline_run.id | tostring)'

.PHONY: medium-risk
medium-risk:
	@echo "📊 Testing MEDIUM RISK customer..."
	@curl -s -X POST "$(API_URL)" \
		-H "Content-Type: application/json" \
		-d '{"pipeline_run": {"variables": {"customer_data": {"customer_id": "MEDIUM_RISK_001", "account_age": 24, "monthly_charges": 85.0, "total_charges": 2040.0, "num_services": 5, "customer_service_calls": 2, "contract_length": 12, "payment_method_score": 0.7, "usage_frequency": 0.6, "support_tickets": 1, "satisfaction_score": 0.6}}}}' \
		| jq -r '"Run ID: " + (.pipeline_run.id | tostring)'

# Show prediction result by reading the data file directly
.PHONY: show-result
show-result:
	@echo "🎯 Getting prediction result for run $(ID)..."
	@EXECUTION_PARTITION=$$(curl -s -X GET "$(BASE_URL)/$(ID)" -H "Content-Type: application/json" | jq -r '.pipeline_run.variables.execution_partition'); \
	echo "Execution Partition: $$EXECUTION_PARTITION"; \
	DATA_FILE="/home/src/mage_data/mlops_demo/pipelines/online_prediction/.variables/$$EXECUTION_PARTITION/make_prediction/output_0/data.json"; \
	echo "Reading from: $$DATA_FILE"; \
	echo ""; \
	echo "🎯 PREDICTION RESULT:"; \
	echo "====================="; \
	if [ -f "$$DATA_FILE" ]; then \
		cat "$$DATA_FILE" | jq '.'; \
	else \
		echo "❌ Data file not found"; \
	fi

# Show the latest prediction result
.PHONY: latest-result
latest-result:
	@echo "📊 Getting latest prediction result..."
	@LATEST_FILE=$$(find /home/src/mage_data/mlops_demo/pipelines/online_prediction/.variables -name "data.json" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- | tr -d '\n'); \
	echo "Latest file: $$LATEST_FILE"; \
	echo ""; \
	echo "🎯 LATEST PREDICTION RESULT:"; \
	echo "============================"; \
	if [ -f "$$LATEST_FILE" ]; then \
		cat "$$LATEST_FILE" | jq '.'; \
	else \
		echo "❌ Could not find latest file"; \
	fi

# Make prediction and show result immediately
.PHONY: predict-show
predict-show:
	@echo "🚀 Making prediction and showing result..."
	@RUN_ID=$$(curl -s -X POST "$(API_URL)" -H "Content-Type: application/json" -d '{"pipeline_run": {"variables": {"customer_data": {"customer_id": "INSTANT_TEST", "account_age": 8, "monthly_charges": 200.0, "total_charges": 1600.0, "num_services": 15, "customer_service_calls": 12, "contract_length": 1, "payment_method_score": 0.1, "usage_frequency": 0.2, "support_tickets": 8, "satisfaction_score": 0.1}}}}' | jq -r '.pipeline_run.id'); \
	echo "Pipeline Run ID: $$RUN_ID"; \
	echo "⏳ Waiting for completion..."; \
	sleep 8; \
	$(MAKE) show-result ID=$$RUN_ID

# Show all available data files
.PHONY: list-files
list-files:
	@echo "📁 Available prediction data files:"
	@find /home/src/mage_data/mlops_demo/pipelines/online_prediction/.variables -name "data.json" -type f 2>/dev/null | sort || echo "❌ No data files found"

# Show the raw data file content for debugging
.PHONY: debug-file
debug-file:
	@echo "🔍 Debug: Latest data file content..."
	@LATEST_FILE=$$(find /home/src/mage_data/mlops_demo/pipelines/online_prediction/.variables -name "data.json" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- | tr -d '\n'); \
	echo "File: $$LATEST_FILE"; \
	echo "Raw content:"; \
	if [ -f "$$LATEST_FILE" ]; then \
		cat "$$LATEST_FILE"; \
	else \
		echo "❌ Could not read file"; \
	fi

# Clean formatted display
.PHONY: clean-result
clean-result:
	@echo "✨ Clean prediction result for run $(ID):"
	@EXECUTION_PARTITION=$$(curl -s -X GET "$(BASE_URL)/$(ID)" -H "Content-Type: application/json" | jq -r '.pipeline_run.variables.execution_partition'); \
	DATA_FILE="/home/src/mage_data/mlops_demo/pipelines/online_prediction/.variables/$$EXECUTION_PARTITION/make_prediction/output_0/data.json"; \
	echo ""; \
	if [ -f "$$DATA_FILE" ]; then \
		RESULT=$$(cat "$$DATA_FILE" | jq -r '.' 2>/dev/null); \
		if [ "$$RESULT" != "" ]; then \
			echo "Customer ID: $$(echo "$$RESULT" | jq -r '.customer_id // "N/A"')"; \
			echo "Prediction: $$(echo "$$RESULT" | jq -r '.prediction_text // "N/A"')"; \
			echo "Risk Level: $$(echo "$$RESULT" | jq -r '.risk_level // "N/A"')"; \
			echo "Churn Probability: $$(echo "$$RESULT" | jq -r '.churn_probability // "N/A"')"; \
			echo "Confidence: $$(echo "$$RESULT" | jq -r '.confidence // "N/A"')"; \
			echo "Model Version: $$(echo "$$RESULT" | jq -r '.model_version // "N/A"')"; \
		else \
			echo "❌ Could not parse prediction result"; \
		fi; \
	else \
		echo "❌ Could not find prediction result file"; \
	fi
