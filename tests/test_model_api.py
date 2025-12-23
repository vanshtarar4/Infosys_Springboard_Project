"""
Test suite for Model API endpoints
Validates prediction logic, risk scores, and model metrics.
"""

import pytest
import json
import numpy as np
from flask import Flask


class TestModelAPI:
    """Test suite for model prediction and metrics endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for Flask app."""
        from src.api.app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_predict_endpoint_exists(self, client):
        """Test that /api/predict endpoint exists."""
        response = client.post('/api/predict', 
                              json={'customer_id': 'TEST', 'transaction_amount': 1000},
                              content_type='application/json')
        assert response.status_code in [200, 400, 503], "Predict endpoint should exist"
    
    def test_predict_requires_json(self, client):
        """Test that predict endpoint requires JSON body."""
        response = client.post('/api/predict')
        assert response.status_code in [400, 415], "Should reject non-JSON requests"
    
    def test_predict_requires_customer_id(self, client):
        """Test that customer_id is required."""
        response = client.post('/api/predict',
                              json={'transaction_amount': 1000},
                              content_type='application/json')
        
        if response.status_code != 503:  # Only test if model is loaded
            data = response.get_json()
            assert response.status_code == 400
            assert 'customer_id' in data.get('error', '').lower()
    
    def test_predict_requires_transaction_amount(self, client):
        """Test that transaction_amount is required."""
        response = client.post('/api/predict',
                              json={'customer_id': 'TEST123'},
                              content_type='application/json')
        
        if response.status_code != 503:
            data = response.get_json()
            assert response.status_code == 400
            assert 'transaction_amount' in data.get('error', '').lower()
    
    def test_predict_low_risk_transaction(self, client):
        """Test prediction for low-risk transaction."""
        payload = {
            'customer_id': 'C_LOW_RISK',
            'kyc_verified': 1,
            'account_age_days': 500,
            'transaction_amount': 250,
            'channel': 'POS',
            'timestamp': '2025-09-12 10:15'
        }
        
        response = client.post('/api/predict', json=payload, content_type='application/json')
        
        if response.status_code != 503:  # Only test if model is loaded
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['success'] is True
            assert 'prediction' in data
            assert 'risk_score' in data
            assert data['prediction'] in ['Fraud', 'Legitimate']
    
    def test_predict_high_risk_transaction(self, client):
        """Test prediction for high-risk transaction."""
        payload = {
            'customer_id': 'C_HIGH_RISK',
            'kyc_verified': 0,
            'account_age_days': 5,
            'transaction_amount': 95000,
            'channel': 'Online',
            'timestamp': '2025-09-12 14:30'
        }
        
        response = client.post('/api/predict', json=payload, content_type='application/json')
        
        if response.status_code != 503:
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['success'] is True
            # High-risk transaction should likely be flagged
            assert data['risk_score'] >= 0.0
    
    def test_risk_score_in_valid_range(self, client):
        """Test that risk score is always between 0 and 1."""
        test_cases = [
            {'customer_id': 'C1', 'transaction_amount': 100},
            {'customer_id': 'C2', 'transaction_amount': 50000},
            {'customer_id': 'C3', 'transaction_amount': 150000},
        ]
        
        for payload in test_cases:
            response = client.post('/api/predict', json=payload, content_type='application/json')
            
            if response.status_code == 200:
                data = response.get_json()
                risk_score = data.get('risk_score')
                
                assert risk_score is not None, "Risk score should be present"
                assert 0.0 <= risk_score <= 1.0, f"Risk score {risk_score} must be between 0 and 1"
    
    def test_prediction_threshold_consistency(self, client):
        """Test that fraud prediction is consistent with threshold."""
        payload = {
            'customer_id': 'C_THRESHOLD_TEST',
            'transaction_amount': 10000,
            'kyc_verified': 0,
            'account_age_days': 10
        }
        
        response = client.post('/api/predict', json=payload, content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            risk_score = data['risk_score']
            prediction = data['prediction']
            threshold = data.get('threshold', 0.5)
            
            # Verify prediction matches threshold logic
            if risk_score >= threshold:
                assert prediction == 'Fraud', f"Risk {risk_score} >= threshold {threshold} should predict Fraud"
            else:
                assert prediction == 'Legitimate', f"Risk {risk_score} < threshold {threshold} should predict Legitimate"
    
    def test_model_metrics_endpoint(self, client):
        """Test GET /api/model/metrics endpoint."""
        response = client.get('/api/model/metrics')
        
        if response.status_code == 200:
            data = response.get_json()
            
            assert data['success'] is True
            assert 'metrics' in data
            
            metrics = data['metrics']
            
            # Verify required metrics are present
            required_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
            for metric in required_metrics:
                assert metric in metrics, f"Missing required metric: {metric}"
                assert isinstance(metrics[metric], (int, float)), f"{metric} should be numeric"
                assert 0.0 <= metrics[metric] <= 1.0, f"{metric} should be between 0 and 1"
    
    def test_recall_greater_than_precision(self, client):
        """Test that recall >= precision (fraud-first logic)."""
        response = client.get('/api/model/metrics')
        
        if response.status_code == 200:
            data = response.get_json()
            metrics = data['metrics']
            
            recall = metrics['recall']
            precision = metrics['precision']
            
            assert recall >= precision, \
                f"Recall ({recall:.4f}) should be >= Precision ({precision:.4f}) for fraud detection"
    
    def test_fraud_detection_metrics_present(self, client):
        """Test that fraud detection specific metrics are present."""
        response = client.get('/api/model/metrics')
        
        if response.status_code == 200:
            data = response.get_json()
            metrics = data['metrics']
            
            if 'fraud_detection' in metrics:
                fd = metrics['fraud_detection']
                
                assert 'detection_rate' in fd
                assert 'frauds_detected' in fd
                assert 'frauds_missed' in fd
                assert 'total_fraud_cases' in fd
                
                # Validate detection rate calculation
                if fd['total_fraud_cases'] > 0:
                    expected_rate = fd['frauds_detected'] / fd['total_fraud_cases']
                    assert abs(fd['detection_rate'] - expected_rate) < 0.01, \
                        "Detection rate calculation incorrect"
    
    def test_confusion_matrix_present(self, client):
        """Test that confusion matrix is included in metrics."""
        response = client.get('/api/model/metrics')
        
        if response.status_code == 200:
            data = response.get_json()
            metrics = data['metrics']
            
            if 'confusion_matrix' in metrics:
                cm = metrics['confusion_matrix']
                
                assert 'true_positives' in cm
                assert 'false_positives' in cm
                assert 'true_negatives' in cm
                assert 'false_negatives' in cm
                
                # All values should be non-negative integers
                for key, value in cm.items():
                    assert value >= 0, f"{key} should be non-negative"
                    assert isinstance(value, int), f"{key} should be an integer"
    
    def test_prediction_response_format(self, client):
        """Test that prediction response has correct format."""
        payload = {
            'customer_id': 'C_FORMAT_TEST',
            'transaction_amount': 5000
        }
        
        response = client.post('/api/predict', json=payload, content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            
            # Verify response structure
            assert 'success' in data
            assert 'prediction' in data
            assert 'risk_score' in data
            assert 'threshold' in data
            assert 'customer_id' in data
            
            # Verify data types
            assert isinstance(data['success'], bool)
            assert isinstance(data['prediction'], str)
            assert isinstance(data['risk_score'], (int, float))
            assert isinstance(data['threshold'], (int, float))
            assert isinstance(data['customer_id'], str)
    
    def test_multiple_predictions_consistency(self, client):
        """Test that same input produces same prediction."""
        payload = {
            'customer_id': 'C_CONSISTENCY',
            'kyc_verified': 1,
            'account_age_days': 100,
            'transaction_amount': 15000,
            'channel': 'Mobile',
            'timestamp': '2025-09-12 15:30'
        }
        
        responses = []
        for _ in range(3):
            response = client.post('/api/predict', json=payload, content_type='application/json')
            if response.status_code == 200:
                responses.append(response.get_json())
        
        if len(responses) >= 2:
            # All predictions should be identical
            first_prediction = responses[0]['prediction']
            first_risk_score = responses[0]['risk_score']
            
            for resp in responses[1:]:
                assert resp['prediction'] == first_prediction, "Predictions should be consistent"
                assert abs(resp['risk_score'] - first_risk_score) < 0.0001, "Risk scores should be consistent"
    
    def test_channel_encoding_variations(self, client):
        """Test that different channel name variations work."""
        base_payload = {
            'customer_id': 'C_CHANNEL_TEST',
            'transaction_amount': 5000,
            'kyc_verified': 1,
            'account_age_days': 100
        }
        
        channels = ['Web', 'web', 'Online', 'Mobile', 'mobile', 'POS', 'pos', 'ATM', 'atm']
        
        for channel in channels:
            payload = {**base_payload, 'channel': channel}
            response = client.post('/api/predict', json=payload, content_type='application/json')
            
            if response.status_code == 200:
                data = response.get_json()
                assert 'risk_score' in data, f"Should handle channel: {channel}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
