"""
Manual API Input Validation Test Script
Tests all the new validation rules added to the /api/predict endpoint
"""

import requests
import json

API_URL = "http://localhost:8001/api/predict"

# Test cases
test_cases = [
    {
        "name": "Valid Transaction",
        "data": {
            "customer_id": "C12345",
            "transaction_amount": 5000,
            "kyc_verified": 1,
            "account_age_days": 30,
            "channel": "Mobile"
        },
        "expected_status": 200,
        "description": "Should succeed with valid data"
    },
    {
        "name": "Empty Customer ID",
        "data": {
            "customer_id": "",
            "transaction_amount": 1000
        },
        "expected_status": 400,
        "description": "Should reject empty customer_id"
    },
    {
        "name": "Negative Amount",
        "data": {
            "customer_id": "C123",
            "transaction_amount": -100
        },
        "expected_status": 400,
        "description": "Should reject negative amount"
    },
    {
        "name": "Amount Too Large",
        "data": {
            "customer_id": "C123",
            "transaction_amount": 100000000  # $100M
        },
        "expected_status": 400,
        "description": "Should reject amount over $10M"
    },
    {
        "name": "Invalid KYC Value",
        "data": {
            "customer_id": "C123",
            "transaction_amount": 1000,
            "kyc_verified": 5
        },
        "expected_status": 400,
        "description": "Should reject kyc_verified not in [0,1,true,false]"
    },
    {
        "name": "Negative Account Age",
        "data": {
            "customer_id": "C123",
            "transaction_amount": 1000,
            "account_age_days": -10
        },
        "expected_status": 400,
        "description": "Should reject negative account_age_days"
    },
    {
        "name": "Account Age Too Large",
        "data": {
            "customer_id": "C123",
            "transaction_amount": 1000,
            "account_age_days": 50000
        },
        "expected_status": 400,
        "description": "Should reject account_age_days > 36500"
    },
    {
        "name": "Invalid Channel",
        "data": {
            "customer_id": "C123",
            "transaction_amount": 1000,
            "channel": "InvalidChannel"
        },
        "expected_status": 400,
        "description": "Should reject invalid channel"
    },
    {
        "name": "Customer ID Too Long",
        "data": {
            "customer_id": "C" * 101,  # 101 characters
            "transaction_amount": 1000
        },
        "expected_status": 400,
        "description": "Should reject customer_id > 100 chars"
    },
    {
        "name": "Amount as String",
        "data": {
            "customer_id": "C123",
            "transaction_amount": "not_a_number"
        },
        "expected_status": 400,
        "description": "Should reject non-numeric amount"
    }
]

def run_tests():
    """Run all test cases"""
    print("=" * 80)
    print("API INPUT VALIDATION TESTS")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}: {test['name']}")
        print(f"Description: {test['description']}")
        
        try:
            response = requests.post(
                API_URL,
                json=test['data'],
                headers={"Content-Type": "application/json"}
            )
            
            status = response.status_code
            
            if status == test['expected_status']:
                print(f"✅ PASS - Got expected status {status}")
                passed += 1
            else:
                print(f"❌ FAIL - Expected {test['expected_status']}, got {status}")
                failed += 1
            
            # Print response for failed validations
            if status == 400:
                data = response.json()
                print(f"   Error: {data.get('error')}")
            
        except Exception as e:
            print(f"❌ FAIL - Exception: {e}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return passed, failed

if __name__ == "__main__":
    try:
        passed, failed = run_tests()
        exit(0 if failed == 0 else 1)
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API at", API_URL)
        print("   Make sure the Flask backend is running on port 8001")
        exit(1)
