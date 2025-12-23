"""
Alert Manager Module
Manages fraud alerts and notifications.
Persists alerts to database and provides alert lifecycle management.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sqlite3
import json
import logging

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Alert management system for fraud detection.
    Handles alert generation, storage, and notification.
    """
    
    def __init__(self, db_path: str = 'data/transactions.db'):
        """
        Initialize the alert manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure fraud_alerts table exists
        self._ensure_table_exists()
        
    def _ensure_table_exists(self):
        """Ensure fraud_alerts table exists in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create fraud_alerts table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fraud_alerts (
                    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT,
                    customer_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT DEFAULT 'NEW',
                    risk_score REAL,
                    ml_prediction TEXT,
                    triggered_rules TEXT,
                    alert_message TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    resolved_by TEXT,
                    resolution_notes TEXT,
                    
                    CHECK (alert_type IN ('ML', 'RULE', 'HYBRID')),
                    CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
                    CHECK (status IN ('NEW', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE', 'CONFIRMED'))
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_customer ON fraud_alerts(customer_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON fraud_alerts(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_created ON fraud_alerts(created_at DESC)')
            
            conn.commit()
            conn.close()
            
            logger.info("✓ fraud_alerts table verified/created")
            
        except Exception as e:
            logger.error(f"Error ensuring table exists: {e}")
    
    def create_alert(self, 
                    transaction_id: str,
                    customer_id: str,
                    risk_score: float,
                    ml_prediction: Dict[str, Any] = None,
                    rule_evaluation: Dict[str, Any] = None,
                    metadata: Dict = None) -> int:
        """
        Create a fraud alert (only if prediction is Fraud).
        
        Args:
            transaction_id: Transaction identifier
            customer_id: Customer identifier
            risk_score: Final fraud risk score
            ml_prediction: ML model prediction result
            rule_evaluation: Rule engine evaluation result
            metadata: Additional metadata
            
        Returns:
            Alert ID (or None if not fraud)
        """
        try:
            # Determine if this is fraud
            final_prediction = rule_evaluation.get('final_prediction', 'Legitimate') if rule_evaluation else \
                              ml_prediction.get('prediction', 'Legitimate') if ml_prediction else 'Legitimate'
            
            # Only create alert for fraud predictions
            if final_prediction != 'Fraud':
                return None
            
            # Determine alert type
            has_ml = ml_prediction is not None
            has_rules = rule_evaluation and rule_evaluation.get('rules_count', 0) > 0
            
            if has_ml and has_rules:
                alert_type = 'HYBRID'
            elif has_rules:
                alert_type = 'RULE'
            else:
                alert_type = 'ML'
            
            # Determine severity based on risk score
            if risk_score >= 0.9:
                severity = 'CRITICAL'
            elif risk_score >= 0.7:
                severity = 'HIGH'
            elif risk_score >= 0.5:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
            
            # Build combined reason
            reasons = []
            
            if ml_prediction:
                ml_score = ml_prediction.get('risk_score', 0)
                reasons.append(f"ML model risk score: {ml_score:.2%}")
            
            if rule_evaluation and rule_evaluation.get('rules_triggered'):
                triggered_rules = rule_evaluation['rules_triggered']
                reasons.append(f"Rules triggered ({len(triggered_rules)}): {', '.join(triggered_rules)}")
            
            alert_message = "; ".join(reasons)
            
            # Prepare triggered rules as JSON
            triggered_rules_json = json.dumps(rule_evaluation.get('rules_triggered', [])) if rule_evaluation else None
            
            # Prepare metadata
            metadata_json = json.dumps(metadata) if metadata else None
            
            # Insert alert
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO fraud_alerts 
                (transaction_id, customer_id, alert_type, severity, status, 
                 risk_score, ml_prediction, triggered_rules, alert_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_id,
                customer_id,
                alert_type,
                severity,
                'NEW',
                risk_score,
                ml_prediction.get('prediction') if ml_prediction else None,
                triggered_rules_json,
                alert_message,
                metadata_json
            ))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Created {severity} fraud alert {alert_id} for transaction {transaction_id}")
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return None
    
    def get_alerts(self, 
                   customer_id: str = None,
                   severity: str = None,
                   status: str = None,
                   limit: int = 100) -> List[Dict]:
        """
        Retrieve fraud alerts from database.
        
        Args:
            customer_id: Filter by customer ID
            severity: Filter by severity
            status: Filter by status
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = 'SELECT * FROM fraud_alerts WHERE 1=1'
            params = []
            
            if customer_id:
                query += ' AND customer_id = ?'
                params.append(customer_id)
            
            if severity:
                query += ' AND severity = ?'
                params.append(severity)
            
            if status:
                query += ' AND status = ?'
                params.append(status)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alert_dict = dict(zip(columns, row))
                
                # Parse JSON fields
                if alert_dict.get('triggered_rules'):
                    try:
                        alert_dict['triggered_rules'] = json.loads(alert_dict['triggered_rules'])
                    except:
                        pass
                
                if alert_dict.get('metadata'):
                    try:
                        alert_dict['metadata'] = json.loads(alert_dict['metadata'])
                    except:
                        pass
                
                alerts.append(alert_dict)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error retrieving alerts: {e}")
            return []
    
    def update_alert_status(self, alert_id: int, status: str, notes: str = None, resolved_by: str = None):
        """
        Update alert status.
        
        Args:
            alert_id: Alert identifier
            status: New status (INVESTIGATING, RESOLVED, FALSE_POSITIVE, CONFIRMED)
            notes: Optional investigation notes
            resolved_by: User who resolved the alert
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update
            if status in ['RESOLVED', 'FALSE_POSITIVE', 'CONFIRMED']:
                cursor.execute('''
                    UPDATE fraud_alerts
                    SET status = ?,
                        updated_at = CURRENT_TIMESTAMP,
                        resolved_at = CURRENT_TIMESTAMP,
                        resolution_notes = ?,
                        resolved_by = ?
                    WHERE alert_id = ?
                ''', (status, notes, resolved_by, alert_id))
            else:
                cursor.execute('''
                    UPDATE fraud_alerts
                    SET status = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE alert_id = ?
                ''', (status, alert_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Updated alert {alert_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating alert status: {e}")
    
    def get_alert_statistics(self, 
                            start_date: datetime = None, 
                            end_date: datetime = None) -> Dict:
        """
        Get alert statistics for a time period.
        
        Args:
            start_date: Start of time period
            end_date: End of time period
            
        Returns:
            Statistics dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query_base = 'FROM fraud_alerts WHERE 1=1'
            params = []
            
            if start_date:
                query_base += ' AND created_at >= ?'
                params.append(start_date.isoformat())
            
            if end_date:
                query_base += ' AND created_at <= ?'
                params.append(end_date.isoformat())
            
            # Total alerts
            cursor.execute(f'SELECT COUNT(*) {query_base}', params)
            total_alerts = cursor.fetchone()[0]
            
            # By severity
            cursor.execute(f'SELECT severity, COUNT(*) {query_base} GROUP BY severity', params)
            by_severity = dict(cursor.fetchall())
            
            # By status
            cursor.execute(f'SELECT status, COUNT(*) {query_base} GROUP BY status', params)
            by_status = dict(cursor.fetchall())
            
            # By type
            cursor.execute(f'SELECT alert_type, COUNT(*) {query_base} GROUP BY alert_type', params)
            by_type = dict(cursor.fetchall())
            
            # Average risk score
            cursor.execute(f'SELECT AVG(risk_score) {query_base}', params)
            avg_risk_score = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_alerts': total_alerts,
                'by_severity': by_severity,
                'by_status': by_status,
                'by_type': by_type,
                'avg_risk_score': round(avg_risk_score, 4)
            }
            
        except Exception as e:
            logger.error(f"Error getting alert statistics: {e}")
            return {}
    
    def send_notification(self, alert_data: Dict, channel: str = 'log'):
        """
        Send alert notification.
        
        Args:
            alert_data: Alert information
            channel: Notification channel (log, email, sms, webhook)
        """
        # For now, just log the alert
        # In production, integrate with email/SMS/webhook services
        
        if channel == 'log':
            logger.warning(
                f"🚨 FRAUD ALERT: "
                f"Transaction {alert_data.get('transaction_id')} "
                f"- Customer {alert_data.get('customer_id')} "
                f"- Risk: {alert_data.get('risk_score', 0):.2%} "
                f"- Severity: {alert_data.get('severity')}"
            )


# Global instance
_alert_manager_instance: Optional[AlertManager] = None


def get_alert_manager(db_path: str = 'data/transactions.db') -> AlertManager:
    """
    Get singleton alert manager instance.
    
    Args:
        db_path: Path to database
        
    Returns:
        AlertManager instance
    """
    global _alert_manager_instance
    
    if _alert_manager_instance is None:
        logger.info("Initializing AlertManager (first time)...")
        _alert_manager_instance = AlertManager(db_path=db_path)
    
    return _alert_manager_instance
