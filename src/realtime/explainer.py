"""
Explainable AI Module
Converts technical fraud detection results into human-readable explanations using LLMs.
"""

import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import Gemini
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Using fallback explanations.")


class FraudExplainer:
    """
    Generates human-readable fraud explanations using LLMs.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the explainer.
        
        Args:
            api_key: Gemini API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', 'AIzaSyAS4c8jLmX61OrlyUXMEiGUcqC3onpICJ0')
        self.model = None
        
        if GENAI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✓ Gemini model initialized for fraud explanations")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.model = None
    
    def generate_risk_explanation(self, payload: Dict[str, Any]) -> str:
        """
        Generate human-readable fraud risk explanation.
        
        Args:
            payload: Dictionary containing:
                - transaction_data: Transaction details
                - risk_score: Fraud risk score (0-1)
                - prediction: "Fraud" or "Legitimate"
                - triggered_rules: List of triggered rule reasons
                - ml_risk_score: ML model risk score
                - rule_risk_score: Rule-based risk score
        
        Returns:
            Human-readable explanation string
        """
        # Try LLM-based explanation first
        if self.model:
            try:
                explanation = self._generate_llm_explanation(payload)
                if explanation:
                    return explanation
            except Exception as e:
                logger.error(f"LLM explanation failed: {e}")
        
        # Fallback to template-based explanation
        return self._generate_fallback_explanation(payload)
    
    def _generate_llm_explanation(self, payload: Dict[str, Any]) -> Optional[str]:
        """Generate explanation using Gemini LLM."""
        transaction = payload.get('transaction_data', {})
        risk_score = payload.get('risk_score', 0)
        prediction = payload.get('prediction', 'Unknown')
        triggered_rules = payload.get('triggered_rules', [])
        ml_risk_score = payload.get('ml_risk_score', 0)
        rule_risk_score = payload.get('rule_risk_score', 0)
        
        # Build context for LLM
        prompt = f"""You are a fraud detection analyst explaining fraud alerts to customers and fraud investigators.

Transaction Details:
- Customer ID: {transaction.get('customer_id', 'Unknown')}
- Transaction Amount: ${transaction.get('transaction_amount', 0):,.2f}
- Channel: {transaction.get('channel', 'Unknown')}
- Account Age: {transaction.get('account_age_days', 0)} days
- KYC Verified: {'Yes' if transaction.get('kyc_verified') else 'No'}
- Transaction Time: {transaction.get('timestamp', 'Unknown')}

Risk Assessment:
- Final Prediction: {prediction}
- Overall Risk Score: {risk_score:.1%}
- ML Model Risk Score: {ml_risk_score:.1%}
- Rule-Based Risk Score: {rule_risk_score:.1%}

Triggered Fraud Rules:
{chr(10).join(f"- {rule}" for rule in triggered_rules) if triggered_rules else "- None"}

Task: Generate a clear, concise explanation (2-3 sentences) for why this transaction was flagged as {prediction.lower()}. 
- Be specific about the risk factors
- Use simple language a customer can understand
- Focus on the most important risk indicators
- Do NOT include technical jargon like "risk score" or "ML model"

Explanation:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,
                    'top_p': 0.8,
                    'max_output_tokens': 200,
                }
            )
            
            explanation = response.text.strip()
            
            # Validate response
            if len(explanation) > 20 and len(explanation) < 500:
                return explanation
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
        
        return None
    
    def _generate_fallback_explanation(self, payload: Dict[str, Any]) -> str:
        """Generate template-based explanation as fallback."""
        transaction = payload.get('transaction_data', {})
        risk_score = payload.get('risk_score', 0)
        prediction = payload.get('prediction', 'Unknown')
        triggered_rules = payload.get('triggered_rules', [])
        
        if prediction == 'Legitimate':
            return "This transaction appears to be legitimate based on normal customer behavior patterns and transaction characteristics."
        
        # Build explanation based on triggered rules
        explanations = []
        
        # Check each rule type
        for rule in triggered_rules:
            rule_lower = rule.lower()
            
            if 'high amount' in rule_lower and 'average' in rule_lower:
                explanations.append("the transaction amount is significantly higher than your usual spending pattern")
            elif 'new account' in rule_lower:
                explanations.append("this is a high-value transaction from a recently opened account")
            elif 'international' in rule_lower or 'kyc' in rule_lower:
                explanations.append("international transactions require KYC verification for security")
            elif 'odd hour' in rule_lower or 'suspicious hours' in rule_lower:
                explanations.append("the transaction occurred during unusual hours (late night/early morning)")
        
        # Combine explanations
        if explanations:
            if len(explanations) == 1:
                reason = explanations[0]
            elif len(explanations) == 2:
                reason = f"{explanations[0]} and {explanations[1]}"
            else:
                reason = f"{', '.join(explanations[:-1])}, and {explanations[-1]}"
            
            severity = "high" if risk_score >= 0.7 else "moderate"
            
            return f"This transaction is flagged as {severity} risk because {reason}. Please verify this transaction was authorized by you."
        
        # Generic fallback
        if risk_score >= 0.7:
            return "This transaction is flagged as high risk due to unusual transaction patterns. Please verify this transaction was authorized."
        else:
            return "This transaction shows some unusual characteristics and requires verification for security purposes."


# Global instance
_explainer_instance: Optional[FraudExplainer] = None


def get_explainer(api_key: str = None) -> FraudExplainer:
    """
    Get singleton explainer instance.
    
    Args:
        api_key: Optional Gemini API key
        
    Returns:
        FraudExplainer instance
    """
    global _explainer_instance
    
    if _explainer_instance is None:
        logger.info("Initializing FraudExplainer (first time)...")
        _explainer_instance = FraudExplainer(api_key=api_key)
    
    return _explainer_instance


def generate_risk_explanation(payload: Dict[str, Any], api_key: str = None) -> str:
    """
    Convenience function to generate risk explanation.
    
    Args:
        payload: Fraud detection results
        api_key: Optional Gemini API key
        
    Returns:
        Human-readable explanation
    """
    explainer = get_explainer(api_key)
    return explainer.generate_risk_explanation(payload)
