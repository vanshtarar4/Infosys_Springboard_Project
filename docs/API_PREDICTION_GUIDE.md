# Fraud Prediction API - Usage Guide

## Overview
REST API endpoint for real-time fraud detection on transaction data.

## Endpoint

### POST /api/predict

Predict fraud probability for a single transaction.

**URL**: `http://localhost:8001/api/predict`

## Request Format

### Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "customer_id": "C123",
  "kyc_verified": 1,
  "account_age_days": 200,
  "transaction_amount": 5000,
  "channel": "Online",
  "timestamp": "2025-09-12 14:30"
}
```

### Required Fields
- `customer_id` (string): Customer identifier
- `transaction_amount` (number): Transaction amount in currency units

### Optional Fields
- `kyc_verified` (0 or 1): KYC verification status (default: 0)
- `account_age_days` (number): Account age in days (default: 0)
- `channel` (string): Transaction channel - "Web", "Mobile", "POS", "ATM", "Other" (default: "Other")
- `timestamp` (string): Transaction timestamp (default: current time)

## Response Format

### Success Response
```json
{
  "success": true,
  "prediction": "Fraud",
  "risk_score": 0.8745,
  "threshold": 0.3,
  "customer_id": "C123",
  "confidence": 0.8745
}
```

### Response Fields
- `success` (boolean): Request success status
- `prediction` (string): "Fraud" or "Legitimate"
- `risk_score` (float): Probability of fraud (0-1)
- `threshold` (float): Threshold used for classification
- `customer_id` (string): Customer ID from request
- `confidence` (float): Confidence in prediction

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

## cURL Examples

### High-Risk Transaction
```bash
curl -X POST http://localhost:8001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C12345",
    "kyc_verified": 0,
    "account_age_days": 5,
    "transaction_amount": 95000,
    "channel": "Online",
    "timestamp": "2025-09-12 14:30"
  }'
```

Expected: High risk_score, prediction="Fraud"

### Low-Risk Transaction
```bash
curl -X POST http://localhost:8001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C67890",
    "kyc_verified": 1,
    "account_age_days": 500,
    "transaction_amount": 250,
    "channel": "POS",
    "timestamp": "2025-09-12 10:15"
  }'
```

Expected: Low risk_score, prediction="Legitimate"

### Mobile Transaction
```bash
curl -X POST http://localhost:8001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C99999",
    "kyc_verified": 1,
    "account_age_days": 300,
    "transaction_amount": 15000,
    "channel": "Mobile",
    "timestamp": "2025-09-12 20:45"
  }'
```

## Python Example

```python
import requests
import json

url = "http://localhost:8001/api/predict"

transaction = {
    "customer_id": "C12345",
    "kyc_verified": 1,
    "account_age_days": 200,
    "transaction_amount": 5000,
    "channel": "Online",
    "timestamp": "2025-09-12 14:30"
}

response = requests.post(url, json=transaction)
result = response.json()

if result['success']:
    print(f"Prediction: {result['prediction']}")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Confidence: {result['confidence']}")
else:
    print(f"Error: {result['error']}")
```

## JavaScript/React Example

```javascript
const predictFraud = async (transaction) => {
  try {
    const response = await fetch('http://localhost:8001/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(transaction),
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Prediction:', result.prediction);
      console.log('Risk Score:', result.risk_score);
      return result;
    } else {
      console.error('Error:', result.error);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
};

// Usage
const transaction = {
  customer_id: "C12345",
  kyc_verified: 1,
  account_age_days: 200,
  transaction_amount: 5000,
  channel: "Online",
  timestamp: "2025-09-12 14:30"
};

predictFraud(transaction);
```

## Prediction History

### GET /api/predictions/history

Retrieve history of predictions made by the API.

**URL**: `http://localhost:8001/api/predictions/history?limit=100`

**Parameters**:
- `limit` (optional): Number of predictions to return (default: 100, max: 1000)

**Response**:
```json
{
  "success": true,
  "predictions": [
    {
      "prediction_id": 1,
      "customer_id": "C12345",
      "transaction_amount": 95000,
      "channel": "Online",
      "timestamp": "2025-09-12 14:30",
      "prediction": "Fraud",
      "risk_score": 0.8745,
      "threshold_used": 0.3,
      "predicted_at": "2025-12-23 21:35:00"
    }
  ],
  "count": 1
}
```

### cURL Example
```bash
curl "http://localhost:8001/api/predictions/history?limit=10"
```

## Database Schema

Predictions are logged to the `model_predictions` table:

```sql
CREATE TABLE model_predictions (
    prediction_id INTEGER PRIMARY KEY AUTO INCREMENT,
    customer_id TEXT,
    transaction_amount REAL,
    channel TEXT,
    timestamp TEXT,
    prediction TEXT,
    risk_score REAL,
    threshold_used REAL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Risk Score Interpretation

| Risk Score Range | Interpretation | Recommendation |
|-----------------|----------------|----------------|
| 0.0 - 0.3 | Low Risk | Approve transaction |
| 0.3 - 0.5 | Medium Risk | Review if unusual |
| 0.5 - 0.7 | High Risk | Trigger additional verification |
| 0.7 - 1.0 | Very High Risk | Block and investigate |

**Note**: With threshold=0.3, scores ≥ 0.3 are classified as "Fraud"

## Error Codes

| Status Code | Meaning |
|------------|---------|
| 200 | Success |
| 400 | Bad Request (missing required fields) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (model not loaded) |

## Testing

### Run Test Scripts

**PowerShell (Windows)**:
```powershell
.\test_prediction_api.ps1
```

**Bash (Linux/Mac)**:
```bash
bash test_prediction_api.sh
```

## Model Details

- **Model**: Logistic Regression
- **Threshold**: 0.3
- **Features**: 11 features (7 numeric + 4 encoded categorical)
- **Performance**: 
  - Recall: 89.5% (catches most fraud)
  - Precision: 12.9%
  - ROC-AUC: 78.8%

## Production Considerations

1. **Rate Limiting**: Add rate limiting to prevent abuse
2. **Authentication**: Implement API key or JWT authentication
3. **Monitoring**: Log predictions and monitor model performance
4. **Model Updates**: Implement model versioning and A/B testing
5. **Scaling**: Use load balancer for high-volume deployments

---

**API Version**: 2.0.0  
**Last Updated**: December 23, 2024
