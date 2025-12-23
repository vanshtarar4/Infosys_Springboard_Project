# Explainable AI - Fraud Detection Examples

## Overview
The explainer module converts technical fraud detection results into human-readable explanations using Gemini LLM.

## Example 1: High-Risk Fraud (Multiple Rules Triggered)

**Input Payload:**
```python
{
  "transaction_data": {
    "customer_id": "C12345",
    "transaction_amount": 95000,
    "channel": "International",
    "account_age_days": 3,
    "kyc_verified": 0,
    "timestamp": "2025-12-23T03:30:00"
  },
  "risk_score": 0.95,
  "prediction": "Fraud",
  "triggered_rules": [
    "New account with high transaction amount",
    "International transaction without KYC verification",
    "Transaction during suspicious hours (2-4 AM)"
  ],
  "ml_risk_score": 0.88,
  "rule_risk_score": 0.95
}
```

**LLM-Generated Explanation:**
```
This transaction raises significant concerns due to the combination of a very new account 
(only 3 days old) attempting an unusually large international transaction ($95,000) 
without completing identity verification, and occurring during the early morning hours 
when fraudulent activity is more common. We strongly recommend completing KYC verification 
before proceeding with this transaction.
```

**Fallback Explanation (if LLM fails):**
```
This transaction is flagged as high risk because this is a high-value transaction from 
a recently opened account, international transactions require KYC verification for security, 
and the transaction occurred during unusual hours (late night/early morning). Please verify 
this transaction was authorized by you.
```

## Example 2: ML-Only Fraud Detection

**Input Payload:**
```python
{
  "transaction_data": {
    "customer_id": "C67890",
    "transaction_amount": 45000,
    "channel": "Web",
    "account_age_days": 120,
    "kyc_verified": 1,
    "timestamp": "2025-12-23T15:45:00"
  },
  "risk_score": 0.75,
  "prediction": "Fraud",
  "triggered_rules": [],
  "ml_risk_score": 0.75,
  "rule_risk_score": 0.0
}
```

**LLM-Generated Explanation:**
```
Our fraud detection system has identified unusual patterns in this transaction that 
deviate from your typical spending behavior. While your account is verified, the 
transaction amount and timing suggest this warrants additional verification to ensure 
your account security.
```

## Example 3: Rule-Based Detection (Amount vs Average)

**Input Payload:**
```python
{
  "transaction_data": {
    "customer_id": "C55555",
    "transaction_amount": 15000,
    "channel": "Mobile",
    "account_age_days": 365,
    "kyc_verified": 1,
    "timestamp": "2025-12-23T14:30:00"
  },
  "risk_score": 0.72,
  "prediction": "Fraud",
  "triggered_rules": [
    "High amount compared to user average"
  ],
  "ml_risk_score": 0.25,
  "rule_risk_score": 0.72
}
```

**LLM-Generated Explanation:**
```
This transaction amount is significantly higher than your usual spending pattern. 
While this may be a legitimate purchase, we're flagging it for your review to 
ensure your account hasn't been compromised.
```

## Example 4: Legitimate Transaction

**Input Payload:**
```python
{
  "transaction_data": {
    "customer_id": "C99999",
    "transaction_amount": 250,
    "channel": "POS",
    "account_age_days": 500,
    "kyc_verified": 1,
    "timestamp": "2025-12-23T11:00:00"
  },
  "risk_score": 0.12,
  "prediction": "Legitimate",
  "triggered_rules": [],
  "ml_risk_score": 0.12,
  "rule_risk_score": 0.0
}
```

**Explanation:**
```
This transaction appears to be legitimate based on normal customer behavior patterns 
and transaction characteristics.
```

## Implementation Details

### LLM Configuration
- **Model**: Gemini 2.0 Flash (fast, cost-effective)
- **Temperature**: 0.3 (focused, less creative)
- **Max Tokens**: 200 (concise explanations)
- **Top-P**: 0.8 (balanced diversity)

### Prompt Engineering
The prompt includes:
1. Transaction context (amount, channel, account age, KYC status)
2. Risk assessment (scores from ML and rules)
3. Triggered rule reasons
4. Clear instructions for tone and length

### Fallback Strategy
If LLM fails:
1. Template-based explanation using triggered rules
2. Risk severity assessment (high/moderate)
3. Generic security message

### Usage in Code

```python
from src.realtime.explainer import generate_risk_explanation

# After getting fraud detection results
explanation = generate_risk_explanation({
    'transaction_data': transaction,
    'risk_score': final_risk_score,
    'prediction': final_prediction,
    'triggered_rules': triggered_rules,
    'ml_risk_score': ml_score,
    'rule_risk_score': rule_score
})

# Use in response
response = {
    'prediction': final_prediction,
    'risk_score': final_risk_score,
    'explanation': explanation  # Human-readable!
}
```

## Benefits

1. **Customer-Friendly**: Non-technical language
2. **Transparent**: Clear reasons for fraud flags
3. **Actionable**: Suggests next steps
4. **Adaptive**: LLM can handle nuanced combinations
5. **Reliable**: Fallback ensures always returns explanation

## API Key Configuration

Set environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or provide in code:
```python
explainer = FraudExplainer(api_key="your-api-key")
```

## Performance
- **LLM latency**: ~500-1000ms
- **Fallback latency**: <1ms
- **Cost**: ~$0.0001 per explanation (Gemini Flash)
