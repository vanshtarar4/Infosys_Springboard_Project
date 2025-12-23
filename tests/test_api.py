"""
API endpoint tests for Transaction Intelligence API
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint returns 200."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['status'] == 'healthy'
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint returns 200 and required keys."""
        response = client.get('/api/metrics')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'metrics' in data
        
        metrics = data['metrics']
        required_keys = [
            'total_transactions',
            'fraud_count',
            'fraud_rate',
            'avg_amount',
            'avg_amount_fraud'
        ]
        
        for key in required_keys:
            assert key in metrics, f"Missing required key: {key}"
        
        # Validate data types
        assert isinstance(metrics['total_transactions'], int)
        assert isinstance(metrics['fraud_count'], int)
        assert isinstance(metrics['fraud_rate'], (int, float))
        assert isinstance(metrics['avg_amount'], (int, float))
        assert isinstance(metrics['avg_amount_fraud'], (int, float))
        
        # Validate numeric constraints
        assert metrics['total_transactions'] >= 0, "Total transactions cannot be negative"
        assert metrics['fraud_count'] >= 0, "Fraud count cannot be negative"
        assert 0 <= metrics['fraud_rate'] <= 100, f"Invalid fraud rate: {metrics['fraud_rate']}"
        assert metrics['avg_amount'] >= 0, "Average amount cannot be negative"
        assert metrics['avg_amount_fraud'] >= 0, "Average fraud amount cannot be negative"
        
        # Validate business logic
        assert metrics['fraud_count'] <= metrics['total_transactions'], \
            "Fraud count cannot exceed total transactions"
    
    def test_metrics_values_non_null(self, client):
        """Test that all metric values are non-null."""
        response = client.get('/api/metrics')
        data = response.get_json()
        metrics = data['metrics']
        
        for key, value in metrics.items():
            assert value is not None, f"Metric {key} is null"
    
    def test_metrics_fraud_rate_calculation(self, client):
        """Test fraud rate is correctly calculated."""
        response = client.get('/api/metrics')
        data = response.get_json()
        metrics = data['metrics']
        
        expected_rate = (metrics['fraud_count'] / metrics['total_transactions'] * 100) \
            if metrics['total_transactions'] > 0 else 0
        
        # Allow small floating point difference
        assert abs(metrics['fraud_rate'] - expected_rate) < 0.01, \
            f"Fraud rate calculation mismatch: expected {expected_rate}, got {metrics['fraud_rate']}"
    
    def test_index_endpoint(self, client):
        """Test index endpoint returns API documentation."""
        response = client.get('/')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'service' in data
        assert 'endpoints' in data
    
    def test_transactions_endpoint(self, client):
        """Test transactions endpoint with pagination."""
        response = client.get('/api/transactions?limit=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'pagination' in data
        
        pagination = data['pagination']
        assert 'limit' in pagination
        assert 'offset' in pagination
        assert 'total' in pagination
        assert pagination['limit'] == 10
    
    def test_sample_endpoint(self, client):
        """Test sample transactions endpoint."""
        response = client.get('/api/transactions/sample')
        
        # Should return 200 or 404 if preview file doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert 'count' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
