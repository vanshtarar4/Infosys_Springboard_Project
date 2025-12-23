"""
Example API calls using curl and Python requests.
"""

# ==============================================================================
# CURL EXAMPLES
# ==============================================================================

# 1. Health Check
curl http://localhost:8001/api/health

# 2. Get Transaction Metrics
curl http://localhost:8001/api/metrics

# 3. Get Latest 10 Transactions
curl "http://localhost:8001/api/transactions?limit=10"

# 4. Get Transactions with Pagination
curl "http://localhost:8001/api/transactions?limit=50&offset=100"

# 5. Get Sample Transactions
curl http://localhost:8001/api/transactions/sample

# 6. Download Processed CSV
curl -O http://localhost:8001/api/download/processed

# 7. API Documentation (root)
curl http://localhost:8001/


# ==============================================================================
# PYTHON REQUESTS EXAMPLES
# ==============================================================================

"""
import requests

BASE_URL = "http://localhost:8001"

# Health check
response = requests.get(f"{BASE_URL}/api/health")
print("Health:", response.json())

# Get metrics
response = requests.get(f"{BASE_URL}/api/metrics")
metrics = response.json()['metrics']
print(f"Total Transactions: {metrics['total_transactions']}")
print(f"Fraud Rate: {metrics['fraud_rate']}%")

# Get transactions with pagination
response = requests.get(f"{BASE_URL}/api/transactions", params={'limit': 20, 'offset': 0})
data = response.json()
print(f"Retrieved {data['pagination']['returned']} transactions")

# Get sample data
response = requests.get(f"{BASE_URL}/api/transactions/sample")
sample = response.json()
print(f"Sample contains {sample['count']} records")

# Download CSV
response = requests.get(f"{BASE_URL}/api/download/processed")
with open('downloaded_transactions.csv', 'wb') as f:
    f.write(response.content)
print("CSV downloaded successfully")
"""
