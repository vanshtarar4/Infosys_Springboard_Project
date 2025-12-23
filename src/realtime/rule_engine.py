"""
Rule Engine Module
Implements business rule-based fraud detection logic.
Combines deterministic rules with ML predictions for hybrid fraud detection.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Business rule engine for fraud detection.
    Applies configurable rules alongside ML predictions.
    """
    
    def __init__(self, db_path: str = 'data/transactions.db', rules_config: Dict = None):
        """
        Initialize the rule engine.
        
        Args:
            db_path: Path to database for historical data lookups
            rules_config: Configuration dictionary for rules
        """
        self.db_path = db_path
        self.rules_config = rules_config or self._default_config()
        self.rules = []
        self.load_rules()
        
    def _default_config(self) -> Dict:
        """Default rule configuration."""
        return {
            'high_amount_multiplier': 5.0,  # Amount > 5x average
            'new_account_days': 7,           # Account age < 7 days
            'high_risk_amount': 20000,       # High-risk threshold
            'suspicious_hour_start': 2,      # 2 AM
            'suspicious_hour_end': 4,        # 4 AM
        }
        
    def load_rules(self):
        """Load fraud detection rules."""
        # Define rules with priority (higher = more important)
        self.rules = [
            {
                'name': 'new_account_high_amount',
                'priority': 5,
                'func': self.check_new_account_high_amount,
                'reason': 'New account with high transaction amount'
            },
            {
                'name': 'high_amount_vs_average',
                'priority': 4,
                'func': self.check_high_amount_vs_average,
                'reason': 'High amount compared to user average'
            },
            {
                'name': 'international_unverified',
                'priority': 3,
                'func': self.check_international_unverified,
                'reason': 'International transaction without KYC verification'
            },
            {
                'name': 'odd_hour_transaction',
                'priority': 2,
                'func': self.check_odd_hour,
                'reason': 'Transaction during suspicious hours (2-4 AM)'
            }
        ]
        
        # Sort by priority (highest first)
        self.rules.sort(key=lambda x: x['priority'], reverse=True)
        logger.info(f"✓ Loaded {len(self.rules)} fraud detection rules")
    
    def add_rule(self, rule_name: str, rule_func: callable, priority: int = 1, reason: str = None):
        """
        Add a new rule to the engine.
        
        Args:
            rule_name: Unique identifier for the rule
            rule_func: Callable that takes transaction data and returns bool
            priority: Rule priority (higher = executed first)
            reason: Human-readable reason for the rule
        """
        self.rules.append({
            'name': rule_name,
            'priority': priority,
            'func': rule_func,
            'reason': reason or rule_name
        })
        self.rules.sort(key=lambda x: x['priority'], reverse=True)
    
    def evaluate_transaction(self, 
                            transaction_data: Dict[str, Any],
                            ml_prediction: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate a transaction against all rules and combine with ML prediction.
        
        Args:
            transaction_data: Transaction details
            ml_prediction: ML model prediction result (optional)
            
        Returns:
            Combined evaluation result with triggered rules and final decision
        """
        triggered_rules = []
        rule_risk_scores = []
        
        # Evaluate each rule
        for rule in self.rules:
            try:
                is_triggered, risk_contribution = rule['func'](transaction_data)
                
                if is_triggered:
                    triggered_rules.append({
                        'name': rule['name'],
                        'reason': rule['reason'],
                        'priority': rule['priority'],
                        'risk_contribution': risk_contribution
                    })
                    rule_risk_scores.append(risk_contribution)
                    
            except Exception as e:
                logger.error(f"Error evaluating rule '{rule['name']}': {e}")
        
        # Calculate rule-based risk score (max of triggered rules)
        rule_risk_score = max(rule_risk_scores) if rule_risk_scores else 0.0
        
        # Combine with ML prediction
        if ml_prediction:
            ml_risk_score = ml_prediction.get('risk_score', 0.0)
            ml_prediction_result = ml_prediction.get('prediction', 'Legitimate')
            
            # Final risk score = max(ML score, rule score)
            final_risk_score = max(ml_risk_score, rule_risk_score)
            
            # Final decision: Fraud if ANY rule triggers OR ML predicts fraud
            final_prediction = "Fraud" if (triggered_rules or ml_prediction_result == "Fraud") else "Legitimate"
        else:
            # Rules only (no ML)
            final_risk_score = rule_risk_score
            final_prediction = "Fraud" if triggered_rules else "Legitimate"
        
        # Build result
        result = {
            'final_prediction': final_prediction,
            'risk_score': round(final_risk_score, 4),
            'ml_risk_score': round(ml_prediction.get('risk_score', 0.0), 4) if ml_prediction else 0.0,
            'rule_risk_score': round(rule_risk_score, 4),
            'rules_triggered': [r['reason'] for r in triggered_rules],
            'rule_details': triggered_rules,
            'rules_count': len(triggered_rules)
        }
        
        return result
    
    def check_high_amount_vs_average(self, transaction_data: Dict) -> Tuple[bool, float]:
        """
        Rule 1: Check if transaction amount > 5x user's average.
        
        Args:
            transaction_data: Current transaction
            
        Returns:
            (triggered, risk_contribution)
        """
        customer_id = transaction_data.get('customer_id')
        current_amount = float(transaction_data.get('transaction_amount', 0))
        
        if not customer_id:
            return False, 0.0
        
        # Get user's average transaction amount from database
        try:
            avg_amount = self.get_customer_average_amount(customer_id)
            
            if avg_amount and avg_amount > 0:
                multiplier = self.rules_config.get('high_amount_multiplier', 5.0)
                
                if current_amount > (multiplier * avg_amount):
                    # Risk contribution based on how much higher
                    ratio = current_amount / avg_amount
                    risk_contribution = min(0.7 + (ratio - multiplier) * 0.05, 0.95)
                    return True, risk_contribution
                    
        except Exception as e:
            logger.error(f"Error checking average amount: {e}")
        
        return False, 0.0
    
    def check_international_unverified(self, transaction_data: Dict) -> Tuple[bool, float]:
        """
        Rule 2: Check if international transaction without KYC.
        
        Args:
            transaction_data: Current transaction
            
        Returns:
            (triggered, risk_contribution)
        """
        channel = transaction_data.get('channel', '').lower()
        kyc_verified = int(transaction_data.get('kyc_verified', 0))
        
        # Check if international transaction
        is_international = channel in ['international', 'foreign', 'overseas']
        
        if is_international and kyc_verified == 0:
            return True, 0.85  # High risk
        
        return False, 0.0
    
    def check_odd_hour(self, transaction_data: Dict) -> Tuple[bool, float]:
        """
        Rule 3: Check if transaction occurs between 2-4 AM.
        
        Args:
            transaction_data: Current transaction
            
        Returns:
            (triggered, risk_contribution)
        """
        timestamp_str = transaction_data.get('timestamp')
        
        if not timestamp_str:
            return False, 0.0
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            hour = timestamp.hour
            
            start_hour = self.rules_config.get('suspicious_hour_start', 2)
            end_hour = self.rules_config.get('suspicious_hour_end', 4)
            
            if start_hour <= hour <= end_hour:
                return True, 0.60  # Moderate risk
                
        except Exception as e:
            logger.error(f"Error parsing timestamp: {e}")
        
        return False, 0.0
    
    def check_new_account_high_amount(self, transaction_data: Dict) -> Tuple[bool, float]:
        """
        Rule 4: Check if new account (<7 days) with high amount (>20k).
        
        Args:
            transaction_data: Current transaction
            
        Returns:
            (triggered, risk_contribution)
        """
        account_age_days = float(transaction_data.get('account_age_days', 0))
        transaction_amount = float(transaction_data.get('transaction_amount', 0))
        
        new_account_threshold = self.rules_config.get('new_account_days', 7)
        high_amount_threshold = self.rules_config.get('high_risk_amount', 20000)
        
        if account_age_days < new_account_threshold and transaction_amount > high_amount_threshold:
            # Risk increases with amount
            risk_base = 0.75
            amount_factor = min((transaction_amount - high_amount_threshold) / 100000, 0.2)
            return True, min(risk_base + amount_factor, 0.95)
        
        return False, 0.0
    
    def get_customer_average_amount(self, customer_id: str) -> float:
        """
        Get customer's historical average transaction amount.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Average transaction amount
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT AVG(transaction_amount)
                FROM transactions
                WHERE customer_id = ?
                AND is_fraud = 0
                LIMIT 100
            ''', (customer_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return float(result[0])
                
        except Exception as e:
            logger.error(f"Error getting customer average: {e}")
        
        return None
    
    def get_triggered_rules(self, transaction_data: Dict) -> List[str]:
        """
        Get list of rules triggered by a transaction.
        
        Args:
            transaction_data: Transaction details
            
        Returns:
            List of triggered rule names
        """
        triggered = []
        
        for rule in self.rules:
            try:
                is_triggered, _ = rule['func'](transaction_data)
                if is_triggered:
                    triggered.append(rule['name'])
            except Exception as e:
                logger.error(f"Error checking rule '{rule['name']}': {e}")
        
        return triggered


# Global instance
_rule_engine_instance = None


def get_rule_engine(db_path: str = 'data/transactions.db') -> RuleEngine:
    """
    Get singleton rule engine instance.
    
    Args:
        db_path: Path to database
        
    Returns:
        RuleEngine instance
    """
    global _rule_engine_instance
    
    if _rule_engine_instance is None:
        logger.info("Initializing RuleEngine (first time)...")
        _rule_engine_instance = RuleEngine(db_path=db_path)
    
    return _rule_engine_instance
