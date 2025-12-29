"""
Model Monitoring
Tracks model health and performance metrics.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelMonitor:
    """Monitor production model health and performance."""
    
    def __init__(self, db_path: str = 'data/transactions.db'):
        self.db_path = db_path
    
    def check_model_health(self) -> Dict:
        """
        Check various model health metrics.
        
        Returns:
            Dictionary with health metrics
        """
        metrics = {}
        
        # Recent prediction accuracy (from feedback)
        metrics['recent_accuracy'] = self._get_recent_accuracy()
        
        # Prediction volume
        metrics['prediction_volume'] = self._get_prediction_volume()
        
        # Fraud rate trend
        metrics['fraud_rate'] = self._get_fraud_rate()
        
        # Data drift warning
        metrics['drift_warning'] = self._check_drift()
        
        return metrics
    
    def _get_recent_accuracy(self, days: int = 7) -> float:
        """Get model accuracy from recent feedback."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN predicted_label = actual_label THEN 1 ELSE 0 END) as correct
            FROM transaction_feedback
            WHERE feedback_timestamp >= datetime('now', '-{} days')
        '''.format(days))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            return (result[1] / result[0]) * 100
        
        return None
    
    def _get_prediction_volume(self, days: int = 1) -> int:
        """Get number of predictions in last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*)
            FROM transactions
            WHERE transaction_timestamp >= datetime('now', '-{} days')
        '''.format(days))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
    
    def _get_fraud_rate(self, days: int = 7) -> float:
        """Get recent fraud prediction rate."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(is_fraud) as fraud_count
            FROM transactions
            WHERE transaction_timestamp >= datetime('now', '-{} days')
        '''.format(days))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            return (result[1] / result[0]) * 100
        
        return 0
    
    def _check_drift(self) -> bool:
        """Simple drift check - rapid change in fraud rate."""
        # Compare recent week to previous week
        current_rate = self._get_fraud_rate(days=7)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(is_fraud) as fraud_count
            FROM transactions
            WHERE transaction_timestamp BETWEEN datetime('now', '-14 days') AND datetime('now', '-7 days')
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 10:
            previous_rate = (result[1] / result[0]) * 100
            
            # Alert if >30% change
            change = abs(current_rate - previous_rate) / previous_rate if previous_rate > 0 else 0
            
            return change > 0.3
        
        return False
