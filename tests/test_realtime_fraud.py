"""
Real-time Fraud Detection Pipeline QA Tests
Validates integrated ML + Rules + Explainer + AlertManager system.
"""

import pytest
import requests
import time
import json
from datetime import datetime


BASE_URL = "http://localhost:8001"
PREDICT_ENDPOINT = f"{BASE_URL}/api/predict"
ALERTS_ENDPOINT = f"{BASE_URL}/api/alerts"


class TestRealtimeFraudDetection:
    """QA test suite for real-time fraud detection pipeline."""
    
    def test_predict_endpoint_exists(self):
        """Test that /api/predict endpoint is accessible."""
        response = requests.post(PREDICT_ENDPOINT, json={
            'customer_id': 'TEST',
            'transaction_amount': 1000
        })
        assert response.status_code in [200, 400], "Endpoint should be accessible"
    
    def test_predict_latency_under_500ms(self):
        """Test that prediction latency is under 500ms."""
        payload = {
            'customer_id': 'C_LATENCY_TEST',
            'transaction_amount': 5000,
            'kyc_verified': 1,
            'account_age_days': 100,
            'channel': 'Web'
        }
        
        # Run 5 times to get average latency
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.post(PREDICT_ENDPOINT, json=payload)
            latency = (time.time() - start) * 1000  # Convert to ms
            latencies.append(latency)
            
            if response.status_code == 200:
                assert response.json()['success'], "Request should succeed"
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        print(f"\n✓ Average latency: {avg_latency:.2f}ms")
        print(f"✓ Max latency: {max_latency:.2f}ms")
        
        assert avg_latency < 500, f"Average latency {avg_latency:.2f}ms should be < 500ms"
        assert max_latency < 1000, f"Max latency {max_latency:.2f}ms should be reasonable"
    
    def test_risk_score_always_in_range(self):
        """Test that risk_score is always between 0 and 1."""
        test_cases = [
            {'customer_id': 'C1', 'transaction_amount': 10},
            {'customer_id': 'C2', 'transaction_amount': 5000},
            {'customer_id': 'C3', 'transaction_amount': 95000, 'kyc_verified': 0, 'account_age_days': 1},
            {'customer_id': 'C4', 'transaction_amount': 150000},
            {'customer_id': 'C5', 'transaction_amount': 250, 'kyc_verified': 1, 'account_age_days': 500}
        ]
        
        for payload in test_cases:
            response = requests.post(PREDICT_ENDPOINT, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                risk_score = data.get('risk_score')
                
                assert risk_score is not None, "Risk score should be present"
                assert 0.0 <= risk_score <= 1.0, f"Risk score {risk_score} must be in [0, 1]"
                
                # Also check ML and Rule scores
                if 'details' in data:
                    ml_score = data['details'].get('ml_risk_score', 0)
                    rule_score = data['details'].get('rule_risk_score', 0)
                    
                    assert 0.0 <= ml_score <= 1.0, f"ML score {ml_score} must be in [0, 1]"
                    assert 0.0 <= rule_score <= 1.0, f"Rule score {rule_score} must be in [0, 1]"
    
    def test_legitimate_transaction(self):
        """Test legitimate transaction with normal characteristics."""
        payload = {
            'transaction_id': 'T_LEGIT_TEST',
            'customer_id': 'C_LEGITIMATE',
            'transaction_amount': 250,
            'kyc_verified': 1,
            'account_age_days': 500,
            'channel': 'POS',
            'timestamp': '2025-12-23T14:30:00'
        }
        
        response = requests.post(PREDICT_ENDPOINT, json=payload)
        assert response.status_code == 200, "Request should succeed"
        
        data = response.json()
        
        print(f"\n✓ Legit Transaction Test:")
        print(f"  Prediction: {data['prediction']}")
        print(f"  Risk Score: {data['risk_score']:.2%}")
        print(f"  ML Score: {data['details']['ml_risk_score']:.2%}")
        print(f"  Rule Score: {data['details']['rule_risk_score']:.2%}")
        print(f"  Rules Triggered: {len(data['details']['triggered_rules'])}")
        
        # Low-risk transactions should typically have low risk scores
        assert data['risk_score'] <= 0.7, "Low-risk transaction should have reasonable score"
    
    def test_high_risk_fraud_transaction(self):
        """Test high-risk fraudulent transaction."""
        payload = {
            'transaction_id': 'T_FRAUD_TEST',
            'customer_id': 'C_HIGH_RISK_FRAUD',
            'transaction_amount': 95000,
            'kyc_verified': 0,
            'account_age_days': 3,
            'channel': 'International',
            'timestamp': '2025-12-23T03:30:00'  # Suspicious hour (3:30 AM)
        }
        
        response = requests.post(PREDICT_ENDPOINT, json=payload)
        assert response.status_code == 200, "Request should succeed"
        
        data = response.json()
        
        print(f"\n✓ High-Risk Fraud Test:")
        print(f"  Prediction: {data['prediction']}")
        print(f"  Risk Score: {data['risk_score']:.2%}")
        print(f"  ML Score: {data['details']['ml_risk_score']:.2%}")
        print(f"  Rule Score: {data['details']['rule_risk_score']:.2%}")
        print(f"  Rules Triggered: {data['details']['triggered_rules']}")
        print(f"  Alert ID: {data['details'].get('alert_id')}")
        print(f"  Explanation: {data['reason'][:100]}...")
        
        # High-risk fraud should be flagged
        assert data['prediction'] == 'Fraud', "Should be flagged as fraud"
        assert data['risk_score'] >= 0.5, "Should have high risk score"
        
        # Should trigger multiple rules
        assert len(data['details']['triggered_rules']) > 0, "Should trigger at least one rule"
    
    def test_rule_triggers_align_with_input(self):
        """Test that rule triggers align with transaction characteristics."""
        
        # Test 1: New account + high amount should trigger rule
        payload = {
            'customer_id': 'C_NEW_ACCOUNT',
            'transaction_amount': 50000,
            'account_age_days': 2,  # Very new
            'kyc_verified': 1
        }
        
        response = requests.post(PREDICT_ENDPOINT, json=payload)
        data = response.json()
        
        triggered_rules = [r.lower() for r in data['details']['triggered_rules']]
        has_new_account_rule = any('new account' in r for r in triggered_rules)
        
        print(f"\n✓ Rule Alignment Test 1 (New Account + High Amount):")
        print(f"  Rules: {data['details']['triggered_rules']}")
        assert has_new_account_rule, "Should trigger new account rule"
        
        # Test 2: Odd hour transaction should trigger rule
        payload2 = {
            'customer_id': 'C_ODD_HOUR',
            'transaction_amount': 5000,
            'timestamp': '2025-12-23T03:00:00'  # 3 AM
        }
        
        response2 = requests.post(PREDICT_ENDPOINT, json=payload2)
        data2 = response2.json()
        
        triggered_rules2 = [r.lower() for r in data2['details']['triggered_rules']]
        has_odd_hour_rule = any('odd hour' in r or 'suspicious hours' in r for r in triggered_rules2)
        
        print(f"\n✓ Rule Alignment Test 2 (Odd Hour):")
        print(f"  Rules: {data2['details']['triggered_rules']}")
        assert has_odd_hour_rule, "Should trigger odd hour rule"
    
    def test_fraud_alerts_stored_only_for_fraud(self):
        """Test that alerts are stored only when prediction == Fraud."""
        
        # Get initial alert count
        alerts_before = requests.get(ALERTS_ENDPOINT).json()
        initial_count = alerts_before.get('count', 0)
        
        # Test 1: Legitimate transaction should NOT create alert
        legit_payload = {
            'transaction_id': 'T_NO_ALERT',
            'customer_id': 'C_LEGIT_NO_ALERT',
            'transaction_amount': 100,
            'kyc_verified': 1,
            'account_age_days': 365
        }
        
        response1 = requests.post(PREDICT_ENDPOINT, json=legit_payload)
        data1 = response1.json()
        
        print(f"\n✓ Legit Transaction Alert Test:")
        print(f"  Prediction: {data1['prediction']}")
        print(f"  Alert ID: {data1['details'].get('alert_id')}")
        
        if data1['prediction'] == 'Legitimate':
            assert data1['details']['alert_id'] is None, "Legit transaction should not create alert"
        
        # Test 2: Fraud transaction SHOULD create alert
        fraud_payload = {
            'transaction_id': 'T_WITH_ALERT',
            'customer_id': 'C_FRAUD_WITH_ALERT',
            'transaction_amount': 99000,
            'kyc_verified': 0,
            'account_age_days': 1,
            'timestamp': '2025-12-23T02:30:00'
        }
        
        response2 = requests.post(PREDICT_ENDPOINT, json=fraud_payload)
        data2 = response2.json()
        
        print(f"\n✓ Fraud Transaction Alert Test:")
        print(f"  Prediction: {data2['prediction']}")
        print(f"  Alert ID: {data2['details'].get('alert_id')}")
        
        if data2['prediction'] == 'Fraud':
            assert data2['details']['alert_id'] is not None, "Fraud should create alert"
            assert isinstance(data2['details']['alert_id'], int), "Alert ID should be integer"
            
            # Verify alert exists in database
            alerts_after = requests.get(ALERTS_ENDPOINT).json()
            final_count = alerts_after.get('count', 0)
            
            assert final_count > initial_count, "Alert count should increase"
    
    def test_response_format_complete(self):
        """Test that response contains all required fields."""
        payload = {
            'customer_id': 'C_FORMAT_TEST',
            'transaction_amount': 5000
        }
        
        response = requests.post(PREDICT_ENDPOINT, json=payload)
        data = response.json()
        
        # Required top-level fields
        assert 'success' in data
        assert 'transaction_id' in data
        assert 'prediction' in data
        assert 'risk_score' in data
        assert 'reason' in data
        assert 'details' in data
        
        # Required details fields
        details = data['details']
        assert 'ml_risk_score' in details
        assert 'rule_risk_score' in details
        assert 'triggered_rules' in details
        assert 'rules_count' in details
        
        # Verify types
        assert isinstance(data['success'], bool)
        assert isinstance(data['prediction'], str)
        assert isinstance(data['risk_score'], (int, float))
        assert isinstance(data['reason'], str)
        assert isinstance(details['triggered_rules'], list)
        
        print(f"\n✓ Response Format Test: All fields present and correct types")
    
    def test_explanation_quality(self):
        """Test that explanations are human-readable."""
        payload = {
            'customer_id': 'C_EXPLAIN_TEST',
            'transaction_amount': 75000,
            'kyc_verified': 0,
            'account_age_days': 5
        }
        
        response = requests.post(PREDICT_ENDPOINT, json=payload)
        data = response.json()
        
        reason = data['reason']
        
        print(f"\n✓ Explanation Quality Test:")
        print(f"  Length: {len(reason)} characters")
        print(f"  Explanation: {reason}")
        
        # Basic quality checks
        assert len(reason) > 20, "Explanation should be substantial"
        assert len(reason) < 500, "Explanation should be concise"
        assert not reason.startswith('Error'), "Should not be an error message"
    
    def test_concurrent_requests(self):
        """Test that system handles concurrent requests properly."""
        import concurrent.futures
        
        def make_request(i):
            payload = {
                'customer_id': f'C_CONCURRENT_{i}',
                'transaction_amount': 5000 + (i * 100)
            }
            response = requests.post(PREDICT_ENDPOINT, json=payload)
            return response.status_code == 200
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        success_rate = sum(results) / len(results)
        print(f"\n✓ Concurrent Requests Test: {success_rate:.0%} success rate")
        
        assert success_rate >= 0.9, "Should handle concurrent requests successfully"


if __name__ == '__main__':
    print("="*80)
    print("Real-time Fraud Detection Pipeline - QA Test Suite")
    print("="*80)
    
    # Run pytest with verbose output
    pytest.main([__file__, '-v', '--tb=short', '-s'])
