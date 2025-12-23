"""
Real-time Fraud Predictor Module
Handles real-time fraud prediction using the trained model.
Optimized for low-latency inference.
"""

import joblib
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RealtimePredictor:
    """
    Real-time fraud prediction engine.
    Loads model artifacts once and provides fast inference.
    """
    
    def __init__(self, 
                 model_path: str = 'models/best_model.joblib',
                 scaler_path: str = 'models/scaler.joblib',
                 encoder_path: str = 'models/encoder.joblib',
                 threshold_path: str = 'configs/model_threshold.json'):
        """
        Initialize the real-time predictor.
        
        Args:
            model_path: Path to trained model file
            scaler_path: Path to fitted scaler
            encoder_path: Path to fitted encoder
            threshold_path: Path to threshold configuration
        """
        self.model = None
        self.scaler = None
        self.encoder = None
        self.threshold = 0.5
        self.model_name = "Unknown"
        self.model_loaded = False
        
        # Store paths
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.encoder_path = encoder_path
        self.threshold_path = threshold_path
        
        # Load artifacts on initialization (once)
        self.load_artifacts()
        
    def load_artifacts(self):
        """Load model, scaler, encoder, and threshold configuration."""
        try:
            # Load model
            self.model = joblib.load(self.model_path)
            logger.info(f"✓ Model loaded from {self.model_path}")
            
            # Load scaler
            self.scaler = joblib.load(self.scaler_path)
            logger.info(f"✓ Scaler loaded from {self.scaler_path}")
            
            # Load encoder
            self.encoder = joblib.load(self.encoder_path)
            logger.info(f"✓ Encoder loaded from {self.encoder_path}")
            
            # Load threshold
            if Path(self.threshold_path).exists():
                with open(self.threshold_path, 'r') as f:
                    config = json.load(f)
                    self.threshold = config.get('selected_threshold', 0.5)
                    self.model_name = config.get('model_name', 'Unknown')
                logger.info(f"✓ Threshold loaded: {self.threshold}")
            
            self.model_loaded = True
            logger.info(f"✓ All artifacts loaded successfully. Ready for predictions.")
            
        except Exception as e:
            logger.error(f"✗ Failed to load artifacts: {e}")
            self.model_loaded = False
            raise
    
    def preprocess_transaction(self, transaction_data: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess a single transaction for prediction.
        Applies same transformations as training pipeline.
        
        Args:
            transaction_data: Raw transaction data dictionary
            
        Returns:
            Preprocessed feature array (1, n_features)
        """
        # Extract timestamp features
        timestamp_str = transaction_data.get('timestamp', datetime.now().isoformat())
        try:
            timestamp = pd.to_datetime(timestamp_str)
        except:
            timestamp = datetime.now()
        
        # Build numeric features (7 features)
        # Order: kyc_verified, account_age_days, transaction_amount, amount_log, hour, weekday, is_high_value
        transaction_amount = float(transaction_data.get('transaction_amount', 0))
        
        numeric_features = np.array([[
            int(transaction_data.get('kyc_verified', 0)),
            float(transaction_data.get('account_age_days', 0)),
            transaction_amount,
            np.log1p(transaction_amount),  # amount_log
            timestamp.hour,
            timestamp.weekday(),
            1 if transaction_amount > 50000 else 0  # is_high_value
        ]])
        
        # Scale numeric features
        numeric_scaled = self.scaler.transform(numeric_features)
        
        # Encode categorical (channel)
        channel = transaction_data.get('channel', 'Other')
        
        # Map common variations to standard channel names
        channel_map = {
            'online': 'Web',
            'web': 'Web',
            'internet': 'Web',
            'mobile': 'Mobile',
            'app': 'Mobile',
            'smartphone': 'Mobile',
            'pos': 'POS',
            'terminal': 'POS',
            'atm': 'ATM',
            'cash': 'ATM'
        }
        
        # Normalize channel name
        channel_normalized = channel_map.get(channel.lower(), channel.title())
        
        # One-hot encode channel (5 features: ATM, Mobile, Other, POS, Web)
        try:
            categorical_encoded = self.encoder.transform([[channel_normalized]])
        except:
            # If unknown channel, use 'Other'
            categorical_encoded = self.encoder.transform([['Other']])
        
        # Combine features: [7 numeric scaled] + [5 categorical one-hot] = 12 features
        features = np.hstack([numeric_scaled, categorical_encoded])
        
        return features
    
    def predict(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict fraud probability for a transaction.
        
        Args:
            transaction_data: Transaction details
            
        Returns:
            Prediction result with risk score and classification
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        # Preprocess transaction
        features = self.preprocess_transaction(transaction_data)
        
        # Predict probability
        risk_score = float(self.model.predict_proba(features)[0, 1])
        
        # Apply threshold
        prediction = "Fraud" if risk_score >= self.threshold else "Legitimate"
        
        # Calculate confidence (how far from threshold)
        confidence = risk_score if prediction == "Fraud" else (1 - risk_score)
        
        # Build result
        result = {
            'transaction_id': transaction_data.get('transaction_id', 'unknown'),
            'customer_id': transaction_data.get('customer_id', 'unknown'),
            'prediction': prediction,
            'risk_score': round(risk_score, 4),
            'threshold': self.threshold,
            'confidence': round(confidence, 4),
            'model_name': self.model_name
        }
        
        return result
    
    def predict_batch(self, transactions: list) -> list:
        """
        Predict fraud for multiple transactions (batch processing).
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of prediction results
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        results = []
        for transaction in transactions:
            try:
                result = self.predict(transaction)
                results.append(result)
            except Exception as e:
                logger.error(f"Error predicting transaction {transaction.get('transaction_id')}: {e}")
                results.append({
                    'transaction_id': transaction.get('transaction_id', 'unknown'),
                    'error': str(e),
                    'prediction': None
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            'model_loaded': self.model_loaded,
            'model_name': self.model_name,
            'threshold': self.threshold,
            'model_type': type(self.model).__name__ if self.model else None
        }


# Global instance (loaded once at module import)
_predictor_instance: Optional[RealtimePredictor] = None


def get_predictor() -> RealtimePredictor:
    """
    Get singleton predictor instance.
    Loads model artifacts only once for efficiency.
    
    Returns:
        RealtimePredictor instance
    """
    global _predictor_instance
    
    if _predictor_instance is None:
        logger.info("Initializing RealtimePredictor (first time)...")
        _predictor_instance = RealtimePredictor()
    
    return _predictor_instance
