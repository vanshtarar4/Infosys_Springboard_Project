# Model Metrics API Endpoint

## Endpoint
```
GET /api/model/metrics
```

## Description
Returns model performance metrics for frontend display.

## Example Request
```bash
curl http://localhost:8001/api/model/metrics
```

## Example Response
```json
{
  "success": true,
  "metrics": {
    "accuracy": 0.47,
    "precision": 0.1288,
    "recall": 0.8953,
    "f1_score": 0.2251,
    "roc_auc": 0.7881,
    "model_name": "Logistic Regression",
    "threshold": 0.3,
    "test_samples": 1000,
    "fraud_detection": {
      "detection_rate": 0.8953,
      "frauds_detected": 77,
      "frauds_missed": 9,
      "total_fraud_cases": 86
    },
    "confusion_matrix": {
      "true_negatives": 393,
      "false_positives": 521,
      "false_negatives": 9,
      "true_positives": 77
    }
  }
}
```

## Response Fields

### Core Metrics
- `accuracy` (float): Overall accuracy (0-1)
- `precision` (float): Precision score (0-1)
- `recall` (float): Recall/Sensitivity (0-1) ⭐ Primary metric
- `f1_score` (float): F1 score (0-1)
- `roc_auc` (float): ROC-AUC score (0-1)

### Model Information
- `model_name` (string): Model type used
- `threshold` (float): Classification threshold applied
- `test_samples` (int): Number of test samples

### Fraud Detection Metrics
- `detection_rate` (float): Percentage of fraud detected
- `frauds_detected` (int): Number of frauds caught
- `frauds_missed` (int): Number of frauds missed
- `total_fraud_cases` (int): Total fraud cases in test set

### Confusion Matrix
- `true_negatives` (int): Correct legit predictions
- `false_positives` (int): False fraud alarms
- `false_negatives` (int): Missed fraud cases
- `true_positives` (int): Correct fraud predictions

## Error Responses

### 404 - Metrics Not Found
```json
{
  "success": false,
  "error": "Model metrics not found. Please run model evaluation first."
}
```

### 500 - Server Error
```json
{
  "success": false,
  "error": "Error message"
}
```

## Frontend Integration

### React/Next.js Example
```javascript
const fetchModelMetrics = async () => {
  try {
    const response = await fetch('http://localhost:8001/api/model/metrics');
    const data = await response.json();
    
    if (data.success) {
      console.log('Model Performance:', data.metrics);
      console.log('Recall:', data.metrics.recall);
      console.log('Precision:', data.metrics.precision);
      return data.metrics;
    }
  } catch (error) {
    console.error('Error fetching metrics:', error);
  }
};
```

### Display Example
```jsx
function ModelMetricsCard({ metrics }) {
  return (
    <div className="metrics-card">
      <h3>{metrics.model_name}</h3>
      <div className="metric-row">
        <span>Recall:</span>
        <span>{(metrics.recall * 100).toFixed(1)}%</span>
      </div>
      <div className="metric-row">
        <span>Precision:</span>
        <span>{(metrics.precision * 100).toFixed(1)}%</span>
      </div>
      <div className="metric-row">
        <span>F1-Score:</span>
        <span>{(metrics.f1_score * 100).toFixed(1)}%</span>
      </div>
      <div className="metric-row">
        <span>ROC-AUC:</span>
        <span>{metrics.roc_auc.toFixed(3)}</span>
      </div>
      <p className="detection-info">
        Detected {metrics.fraud_detection.frauds_detected} of {metrics.fraud_detection.total_fraud_cases} frauds
      </p>
    </div>
  );
}
```

## Notes
- All numeric values are rounded to 4 decimal places
- Frontend-safe JSON formatting (no NaN, Infinity, etc.)
- Loads data from `configs/model_metrics.json`
- Updated on each model evaluation run
