#!/bin/bash
# Test script for fraud prediction API

echo "=========================================="
echo "Fraud Prediction API - Test Script"
echo "=========================================="

# Test 1: High-risk transaction (likely fraud)
echo -e "\n1. Testing HIGH-RISK transaction (large amount, new account):"
curl -X POST http://localhost:8001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C12345",
    "kyc_verified": 0,
    "account_age_days": 5,
    "transaction_amount": 95000,
    "channel": "Online",
    "timestamp": "2025-09-12 14:30"
  }' | json_pp

# Test 2: Low-risk transaction (likely legitimate)
echo -e "\n2. Testing LOW-RISK transaction (small amount, established account):"
curl -X POST http://localhost:8001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C67890",
    "kyc_verified": 1,
    "account_age_days": 500,
    "transaction_amount": 250,
    "channel": "POS",
    "timestamp": "2025-09-12 10:15"
  }' | json_pp

# Test 3: Get prediction history
echo -e "\n3. Fetching prediction history:"
curl http://localhost:8001/api/predictions/history?limit=5 | json_pp

echo -e "\n=========================================="
echo "Tests complete!"
echo "=========================================="
