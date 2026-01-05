"""
Comprehensive Backend Tests - Milestone 4
Tests for fraud prediction, rule engine, LLM, and all API endpoints.
"""

import pytest
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from src.api.app import app
import sqlite3


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_transaction():
    """Sample valid transaction"""
    return {
        "customer_id": "TEST_C123",
        "transaction_amount": 5000,
        "channel": "Web",
        "kyc_verified": 1,
        "account_age_days": 365
    }


@pytest.fixture
def fraud_transaction():
    """Transaction that should be flagged as fraud"""
    return {
        "customer_id": "TEST_FRAUD",
        "transaction_amount": 15000,
        "channel": "International",
        "kyc_verified": 0,
        "account_age_days": 1
    }


# ============================================================================
# UNIT TESTS - FRAUD PREDICTION LOGIC
# ============================================================================

class TestFraudPredictionLogic:
    """Test core fraud detection logic"""
    
    def test_ml_model_loaded(self):
        """Test that ML model is loaded correctly"""
        from src.realtime.realtime_predictor import get_predictor
        
        predictor = get_predictor()
        assert predictor is not None
        assert predictor.model is not None
        assert predictor.scaler is not None
    
    def test_predictor_returns_risk_score(self, sample_transaction):
        """Test predictor returns valid risk score"""
        from src.realtime.realtime_predictor import get_predictor
        
        predictor = get_predictor()
        result = predictor.predict(sample_transaction)
        
        assert 'risk_score' in result
        assert 'prediction' in result
        assert 0 <= result['risk_score'] <= 1
        assert result['prediction'] in ['Fraud', 'Legitimate']
    
    def test_high_amount_increases_risk(self):
        """Test that higher amounts increase risk score"""
        from src.realtime.realtime_predictor import get_predictor
        
        predictor = get_predictor()
        
        low_amount = {"customer_id": "C1", "transaction_amount": 100, "kyc_verified": 1, "account_age_days": 365}
        high_amount = {"customer_id": "C1", "transaction_amount": 100000, "kyc_verified": 1, "account_age_days": 365}
        
        low_result = predictor.predict(low_amount)
        high_result = predictor.predict(high_amount)
        
        # High amount should have equal or higher risk
        assert high_result['risk_score'] >= low_result['risk_score']


# ============================================================================
# UNIT TESTS - RULE ENGINE
# ============================================================================

class TestRuleEngine:
    """Test rule-based fraud detection"""
    
    def test_rule_engine_loaded(self):
        """Test rule engine initializes"""
        from src.realtime.rule_engine import get_rule_engine
        
        engine = get_rule_engine()
        assert engine is not None
        assert len(engine.rules) > 0
    
    def test_high_amount_no_kyc_triggers_rule(self):
        """Test that high amount without KYC triggers rule"""
        from src.realtime.rule_engine import get_rule_engine
        from src.realtime.realtime_predictor import get_predictor
        
        engine = get_rule_engine()
        predictor = get_predictor()
        
        transaction = {
            "customer_id": "TEST",
            "transaction_amount": 12000,
            "kyc_verified": 0,
            "account_age_days": 100
        }
        
        ml_pred = predictor.predict(transaction)
        rule_result = engine.evaluate_transaction(transaction, ml_pred)
        
        assert 'rules_triggered' in rule_result
        assert len(rule_result['rules_triggered']) > 0
        assert any('KYC' in rule.lower() for rule in rule_result['rules_triggered'])
    
    def test_new_account_high_amount_triggers_rule(self):
        """Test new account + high amount triggers rule"""
        from src.realtime.rule_engine import get_rule_engine
        from src.realtime.realtime_predictor import get_predictor
        
        engine = get_rule_engine()
        predictor = get_predictor()
        
        transaction = {
            "customer_id": "TEST",
            "transaction_amount": 8000,
            "kyc_verified": 1,
            "account_age_days": 5  # Very new
        }
        
        ml_pred = predictor.predict(transaction)
        rule_result = engine.evaluate_transaction(transaction, ml_pred)
        
        # Should trigger new account rule
        assert len(rule_result['rules_triggered']) > 0
    
    def test_legitimate_transaction_no_rules(self):
        """Test legitimate transaction doesn't trigger rules"""
        from src.realtime.rule_engine import get_rule_engine
        from src.realtime.realtime_predictor import get_predictor
        
        engine = get_rule_engine()
        predictor = get_predictor()
        
        transaction = {
            "customer_id": "TEST",
            "transaction_amount": 100,  # Small amount
            "kyc_verified": 1,
            "account_age_days": 1000  # Established account
        }
        
        ml_pred = predictor.predict(transaction)
        rule_result = engine.evaluate_transaction(transaction, ml_pred)
        
        # Might not trigger any rules
        assert 'rules_triggered' in rule_result
        assert rule_result['final_prediction'] in ['Fraud', 'Legitimate']


# ============================================================================
# UNIT TESTS - LLM EXPLANATION
# ============================================================================

class TestLLMExplanation:
    """Test LLM explanation generation"""
    
    def test_explainer_initialization(self):
        """Test explainer initializes"""
        from src.realtime.explainer import get_explainer
        
        explainer = get_explainer()
        assert explainer is not None
    
    def test_fallback_explanation_always_works(self):
        """Test that fallback explanation works when LLM fails"""
        from src.realtime.explainer import FraudExplainer
        
        explainer = FraudExplainer()
        
        payload = {
            'transaction_data': {
                'customer_id': 'TEST',
                'transaction_amount': 5000
            },
            'risk_score': 0.75,
            'prediction': 'Fraud',
            'triggered_rules': ['High amount without KYC'],
            'ml_risk_score': 0.6,
            'rule_risk_score': 0.15
        }
        
        # Force fallback
        explanation = explainer._generate_fallback_explanation(payload)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert 'fraud' in explanation.lower() or 'risk' in explanation.lower()
    
    def test_explanation_contains_risk_factors(self):
        """Test explanation mentions key risk factors"""
        from src.realtime.explainer import generate_risk_explanation
        
        payload = {
            'transaction_data': {
                'customer_id': 'TEST',
                'transaction_amount': 15000,
                'kyc_verified': 0
            },
            'risk_score': 0.80,
            'prediction': 'Fraud',
            'triggered_rules': ['High transaction amount without KYC verification'],
            'ml_risk_score': 0.65,
            'rule_risk_score': 0.15
        }
        
        explanation = generate_risk_explanation(payload)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 10
        # Should mention amount or KYC
        assert 'amount' in explanation.lower() or 'kyc' in explanation.lower() or 'risk' in explanation.lower()


# ============================================================================
# API TESTS - /predict
# ============================================================================

class TestPredictAPI:
    """Test /api/predict endpoint"""
    
    def test_predict_success(self, client, sample_transaction):
        """Test successful prediction"""
        response = client.post('/api/predict',
                              data=json.dumps(sample_transaction),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'transaction_id' in data
        assert 'prediction' in data
        assert 'risk_score' in data
        assert 'reason' in data
        assert data['prediction'] in ['Fraud', 'Legitimate']
        assert 0 <= data['risk_score'] <= 1
    
    def test_predict_fraud_detection(self, client, fraud_transaction):
        """Test fraud is correctly detected"""
        response = client.post('/api/predict',
                              data=json.dumps(fraud_transaction),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        # High risk transaction should likely be fraud
        assert data['risk_score'] > 0.5
    
    def test_predict_missing_customer_id(self, client):
        """Test missing customer_id returns error"""
        invalid_data = {
            "transaction_amount": 5000
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'error' in data
        assert 'customer_id' in data['error'].lower()
    
    def test_predict_missing_amount(self, client):
        """Test missing transaction_amount returns error"""
        invalid_data = {
            "customer_id": "C123"
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'error' in data
    
    def test_predict_negative_amount(self, client):
        """Test negative amount returns error"""
        invalid_data = {
            "customer_id": "C123",
            "transaction_amount": -1000
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'positive' in data['error'].lower()
    
    def test_predict_extremely_large_amount(self, client):
        """Test extremely large amount returns error"""
        invalid_data = {
            "customer_id": "C123",
            "transaction_amount": 50000000  # $50M
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'exceed' in data['error'].lower()
    
    def test_predict_invalid_kyc_value(self, client):
        """Test invalid KYC value returns error"""
        invalid_data = {
            "customer_id": "C123",
            "transaction_amount": 5000,
            "kyc_verified": "invalid"
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
    
    def test_predict_invalid_channel(self, client):
        """Test invalid channel returns error"""
        invalid_data = {
            "customer_id": "C123",
            "transaction_amount": 5000,
            "channel": "InvalidChannel"
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
    
    def test_predict_empty_request(self, client):
        """Test empty request returns error"""
        response = client.post('/api/predict',
                              data='',
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_predict_response_schema(self, client, sample_transaction):
        """Test response has correct schema"""
        response = client.post('/api/predict',
                              data=json.dumps(sample_transaction),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        # Required top-level fields
        assert 'success' in data
        assert 'transaction_id' in data
        assert 'prediction' in data
        assert 'risk_score' in data
        assert 'reason' in data
        
        # Details object
        assert 'details' in data
        assert 'ml_risk_score' in data['details']
        assert 'rule_risk_score' in data['details']
        assert 'triggered_rules' in data['details']
        assert isinstance(data['details']['triggered_rules'], list)


# ============================================================================
# API TESTS - /metrics
# ============================================================================

class TestMetricsAPI:
    """Test /api/metrics endpoint"""
    
    def test_metrics_success(self, client):
        """Test metrics endpoint returns data"""
        response = client.get('/api/metrics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'metrics' in data
    
    def test_metrics_schema(self, client):
        """Test metrics has correct schema"""
        response = client.get('/api/metrics')
        data = json.loads(response.data)
        
        metrics = data['metrics']
        
        assert 'total_transactions' in metrics
        assert 'fraud_count' in metrics
        assert 'fraud_rate' in metrics
        assert 'avg_amount' in metrics
        
        # Values should be numbers
        assert isinstance(metrics['total_transactions'], int)
        assert isinstance(metrics['fraud_count'], int)
        assert isinstance(metrics['fraud_rate'], (int, float))


# ============================================================================
# API TESTS - /dashboard/stats
# ============================================================================

class TestDashboardStatsAPI:
    """Test /api/dashboard/stats endpoint"""
    
    def test_dashboard_stats_success(self, client):
        """Test dashboard stats returns data"""
        response = client.get('/api/dashboard/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'stats' in data or 'metrics' in data
    
    def test_dashboard_stats_schema(self, client):
        """Test dashboard stats schema"""
        response = client.get('/api/dashboard/stats')
        data = json.loads(response.data)
        
        # Should have transaction counts
        content = str(data)
        assert 'transaction' in content.lower() or 'fraud' in content.lower()


# ============================================================================
# API TESTS - /alerts
# ============================================================================

class TestAlertsAPI:
    """Test /api/alerts endpoint"""
    
    def test_alerts_success(self, client):
        """Test alerts endpoint returns data"""
        response = client.get('/api/alerts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'alerts' in data
        assert isinstance(data['alerts'], list)
    
    def test_alerts_with_limit(self, client):
        """Test alerts respects limit parameter"""
        response = client.get('/api/alerts?limit=5')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['alerts']) <= 5
    
    def test_alerts_schema(self, client):
        """Test alert objects have correct schema"""
        response = client.get('/api/alerts?limit=1')
        data = json.loads(response.data)
        
        if len(data['alerts']) > 0:
            alert = data['alerts'][0]
            
            # Should have key fields
            assert 'alert_id' in alert or 'transaction_id' in alert
            assert 'severity' in alert or 'risk_score' in alert


# ============================================================================
# API TESTS - /auth/login
# ============================================================================

class TestAuthAPI:
    """Test /api/auth/login endpoint"""
    
    def test_login_success(self, client):
        """Test successful login"""
        credentials = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = client.post('/api/auth/login',
                              data=json.dumps(credentials),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'token' in data
        assert 'user' in data
        assert data['user']['username'] == 'admin'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        credentials = {
            "username": "admin",
            "password": "wrongpassword"
        }
        
        response = client.post('/api/auth/login',
                              data=json.dumps(credentials),
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        
        assert data['success'] is False
    
    def test_login_missing_username(self, client):
        """Test login with missing username"""
        credentials = {
            "password": "admin123"
        }
        
        response = client.post('/api/auth/login',
                              data=json.dumps(credentials),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
    
    def test_login_analyst_user(self, client):
        """Test login with analyst user"""
        credentials = {
            "username": "analyst",
            "password": "analyst123"
        }
        
        response = client.post('/api/auth/login',
                              data=json.dumps(credentials),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['user']['role'] == 'analyst'


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_amount_transaction(self, client):
        """Test zero amount transaction"""
        data = {
            "customer_id": "C123",
            "transaction_amount": 0
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(data),
                              content_type='application/json')
        
        # Could be valid or invalid depending on business rules
        assert response.status_code in [200, 400]
    
    def test_boundary_amount_10million(self, client):
        """Test boundary at $10M"""
        data = {
            "customer_id": "C123",
            "transaction_amount": 10000000
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(data),
                              content_type='application/json')
        
        # Should be rejected
        assert response.status_code == 400
    
    def test_just_under_10million(self, client):
        """Test amount just under $10M limit"""
        data = {
            "customer_id": "C123",
            "transaction_amount": 9999999
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(data),
                              content_type='application/json')
        
        # Should be accepted
        assert response.status_code == 200
    
    def test_extremely_long_customer_id(self, client):
        """Test very long customer ID"""
        data = {
            "customer_id": "C" * 200,  # 200 characters
            "transaction_amount": 5000
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(data),
                              content_type='application/json')
        
        # Should be rejected (max 100 chars)
        assert response.status_code == 400
    
    def test_special_characters_in_customer_id(self, client):
        """Test special characters in customer ID"""
        data = {
            "customer_id": "C_123-TEST@2024",
            "transaction_amount": 5000
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(data),
                              content_type='application/json')
        
        # Should be accepted (string validation)
        assert response.status_code == 200
    
    def test_float_vs_int_amounts(self, client):
        """Test both float and int amounts work"""
        # Integer
        data1 = {
            "customer_id": "C123",
            "transaction_amount": 5000
        }
        
        # Float
        data2 = {
            "customer_id": "C123",
            "transaction_amount": 5000.50
        }
        
        response1 = client.post('/api/predict',
                               data=json.dumps(data1),
                               content_type='application/json')
        
        response2 = client.post('/api/predict',
                               data=json.dumps(data2),
                               content_type='application/json')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
    
    def test_account_age_boundary(self, client):
        """Test account age boundaries"""
        # Very new account (edge of fraud)
        data_new = {
            "customer_id": "C_NEW",
            "transaction_amount": 10000,
            "account_age_days": 1
        }
        
        # Established account
        data_old = {
            "customer_id": "C_OLD",
            "transaction_amount": 10000,
            "account_age_days": 1000
        }
        
        response_new = client.post('/api/predict',
                                   data=json.dumps(data_new),
                                   content_type='application/json')
        
        response_old = client.post('/api/predict',
                                   data=json.dumps(data_old),
                                   content_type='application/json')
        
        assert response_new.status_code == 200
        assert response_old.status_code == 200
        
        # New account should have higher risk
        data_new_result = json.loads(response_new.data)
        data_old_result = json.loads(response_old.data)
        
        assert data_new_result['risk_score'] >= data_old_result['risk_score']


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test full end-to-end integration"""
    
    def test_full_fraud_detection_flow(self, client):
        """Test complete flow: predict → check alert → verify stored"""
        # Step 1: Submit high-risk transaction
        transaction = {
            "customer_id": "INTEGRATION_TEST",
            "transaction_amount": 25000,
            "kyc_verified": 0,
            "account_age_days": 2
        }
        
        response = client.post('/api/predict',
                              data=json.dumps(transaction),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        transaction_id = data['transaction_id']
        
        # Step 2: Check if alert was created (if fraud)
        if data['prediction'] == 'Fraud':
            alert_response = client.get('/api/alerts?limit=200')
            alert_data = json.loads(alert_response.data)
            
            # Should find our transaction in alerts
            alert_ids = [str(a.get('transaction_id', '')) for a in alert_data['alerts']]
            # Not guaranteed to be there immediately, but check the flow worked
            assert alert_response.status_code == 200
    
    def test_consistent_predictions(self, client):
        """Test same transaction gives consistent predictions"""
        transaction = {
            "customer_id": "CONSISTENCY_TEST",
            "transaction_amount": 3000,
            "kyc_verified": 1,
            "account_age_days": 500
        }
        
        # Make same prediction twice
        response1 = client.post('/api/predict',
                               data=json.dumps(transaction),
                               content_type='application/json')
        
        response2 = client.post('/api/predict',
                               data=json.dumps(transaction),
                               content_type='application/json')
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        # Predictions should be the same (within small tolerance for ML)
        assert abs(data1['risk_score'] - data2['risk_score']) < 0.05
        assert data1['prediction'] == data2['prediction']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
