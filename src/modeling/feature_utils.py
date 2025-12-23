"""
Feature Preparation and Encoding Utilities
Handles feature engineering, scaling, and encoding for fraud detection models.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeaturePreparator:
    """Handles feature preparation, scaling, and encoding."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.numeric_features = [
            'kyc_verified',
            'account_age_days',
            'transaction_amount',
            'amount_log',
            'hour',
            'weekday',
            'is_high_value'
        ]
        self.categorical_features = ['channel']
        self.feature_names = None
        self.is_fitted = False
    
    def prepare_features(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        """
        Prepare features for modeling.
        
        Args:
            df: Input DataFrame
            fit: Whether to fit transformers (True for train, False for test)
        
        Returns:
            Transformed feature matrix
        """
        logger.info(f"Preparing features (fit={fit})...")
        
        # Extract numeric features
        X_numeric = df[self.numeric_features].values
        
        # Extract and encode categorical features
        X_categorical = df[self.categorical_features].values
        
        if fit:
            # Fit and transform on training data
            logger.info("Fitting transformers on training data...")
            X_numeric_scaled = self.scaler.fit_transform(X_numeric)
            X_categorical_encoded = self.encoder.fit_transform(X_categorical)
            
            # Store feature names
            cat_feature_names = self.encoder.get_feature_names_out(self.categorical_features)
            self.feature_names = self.numeric_features + list(cat_feature_names)
            self.is_fitted = True
            
            logger.info(f"Fitted transformers. Total features: {len(self.feature_names)}")
        else:
            # Transform only (for test data)
            if not self.is_fitted:
                raise ValueError("Transformers not fitted. Call with fit=True first.")
            
            logger.info("Transforming data with fitted transformers...")
            X_numeric_scaled = self.scaler.transform(X_numeric)
            X_categorical_encoded = self.encoder.transform(X_categorical)
        
        # Combine numeric and categorical features
        X = np.hstack([X_numeric_scaled, X_categorical_encoded])
        
        logger.info(f"Feature matrix shape: {X.shape}")
        return X
    
    def get_feature_names(self) -> List[str]:
        """Get feature names after transformation."""
        if self.feature_names is None:
            raise ValueError("Feature names not available. Fit transformers first.")
        return self.feature_names


def prepare_train_test_data(train_path: str = 'data/processed/train.csv',
                            test_path: str = 'data/processed/test.csv',
                            output_dir: str = 'models') -> dict:
    """
    Prepare train and test data with proper transformations.
    
    Args:
        train_path: Path to training CSV
        test_path: Path to test CSV
        output_dir: Directory to save artifacts
    
    Returns:
        Dictionary with data shapes and info
    """
    logger.info("="*60)
    logger.info("FEATURE PREPARATION PIPELINE")
    logger.info("="*60)
    
    # Load data
    logger.info(f"\nLoading training data from {train_path}")
    train_df = pd.read_csv(train_path)
    logger.info(f"Training data: {len(train_df)} rows, {len(train_df.columns)} columns")
    
    logger.info(f"\nLoading test data from {test_path}")
    test_df = pd.read_csv(test_path)
    logger.info(f"Test data: {len(test_df)} rows, {len(test_df.columns)} columns")
    
    # Extract labels
    y_train = train_df['is_fraud'].values
    y_test = test_df['is_fraud'].values
    
    logger.info(f"\nTrain fraud rate: {y_train.mean()*100:.2f}%")
    logger.info(f"Test fraud rate: {y_test.mean()*100:.2f}%")
    
    # Initialize preparator
    preparator = FeaturePreparator()
    
    # Prepare features
    X_train = preparator.prepare_features(train_df, fit=True)
    X_test = preparator.prepare_features(test_df, fit=False)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save feature matrices
    logger.info(f"\nSaving feature matrices to {output_dir}/")
    np.save(output_path / 'X_train.npy', X_train)
    np.save(output_path / 'X_test.npy', X_test)
    np.save(output_path / 'y_train.npy', y_train)
    np.save(output_path / 'y_test.npy', y_test)
    
    logger.info("✓ Saved X_train.npy")
    logger.info("✓ Saved X_test.npy")
    logger.info("✓ Saved y_train.npy")
    logger.info("✓ Saved y_test.npy")
    
    # Save artifacts
    save_artifacts(preparator, output_dir)
    
    # Summary
    summary = {
        'X_train_shape': X_train.shape,
        'X_test_shape': X_test.shape,
        'y_train_shape': y_train.shape,
        'y_test_shape': y_test.shape,
        'n_features': X_train.shape[1],
        'feature_names': preparator.get_feature_names(),
        'train_fraud_rate': float(y_train.mean()),
        'test_fraud_rate': float(y_test.mean())
    }
    
    logger.info("\n" + "="*60)
    logger.info("FEATURE PREPARATION COMPLETE")
    logger.info("="*60)
    logger.info(f"\nX_train shape: {X_train.shape}")
    logger.info(f"X_test shape: {X_test.shape}")
    logger.info(f"y_train shape: {y_train.shape}")
    logger.info(f"y_test shape: {y_test.shape}")
    logger.info(f"\nTotal features: {X_train.shape[1]}")
    logger.info(f"Feature names: {preparator.get_feature_names()}")
    
    return summary


def save_artifacts(preparator: FeaturePreparator, output_dir: str = 'models'):
    """
    Save fitted transformers and metadata.
    
    Args:
        preparator: Fitted FeaturePreparator instance
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save scaler
    scaler_path = output_path / 'scaler.joblib'
    joblib.dump(preparator.scaler, scaler_path)
    logger.info(f"✓ Saved scaler to {scaler_path}")
    
    # Save encoder
    encoder_path = output_path / 'encoder.joblib'
    joblib.dump(preparator.encoder, encoder_path)
    logger.info(f"✓ Saved encoder to {encoder_path}")
    
    # Save feature names
    import json
    features_path = output_path / 'feature_names.json'
    with open(features_path, 'w') as f:
        json.dump({
            'numeric_features': preparator.numeric_features,
            'categorical_features': preparator.categorical_features,
            'all_features': preparator.get_feature_names()
        }, f, indent=2)
    logger.info(f"✓ Saved feature names to {features_path}")


def load_artifacts(artifact_dir: str = 'models') -> FeaturePreparator:
    """
    Load fitted transformers.
    
    Args:
        artifact_dir: Directory with saved artifacts
    
    Returns:
        FeaturePreparator with loaded transformers
    """
    artifact_path = Path(artifact_dir)
    
    logger.info(f"Loading artifacts from {artifact_dir}/")
    
    preparator = FeaturePreparator()
    
    # Load scaler
    scaler_path = artifact_path / 'scaler.joblib'
    preparator.scaler = joblib.load(scaler_path)
    logger.info(f"✓ Loaded scaler from {scaler_path}")
    
    # Load encoder
    encoder_path = artifact_path / 'encoder.joblib'
    preparator.encoder = joblib.load(encoder_path)
    logger.info(f"✓ Loaded encoder from {encoder_path}")
    
    # Load feature names
    import json
    features_path = artifact_path / 'feature_names.json'
    with open(features_path, 'r') as f:
        feature_data = json.load(f)
        preparator.feature_names = feature_data['all_features']
        preparator.numeric_features = feature_data['numeric_features']
        preparator.categorical_features = feature_data['categorical_features']
    
    preparator.is_fitted = True
    logger.info(f"✓ Loaded feature names ({len(preparator.feature_names)} features)")
    
    return preparator


def load_prepared_data(data_dir: str = 'models') -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load prepared feature matrices and labels.
    
    Args:
        data_dir: Directory with saved data
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    data_path = Path(data_dir)
    
    logger.info(f"Loading prepared data from {data_dir}/")
    
    X_train = np.load(data_path / 'X_train.npy')
    X_test = np.load(data_path / 'X_test.npy')
    y_train = np.load(data_path / 'y_train.npy')
    y_test = np.load(data_path / 'y_test.npy')
    
    logger.info(f"✓ Loaded X_train: {X_train.shape}")
    logger.info(f"✓ Loaded X_test: {X_test.shape}")
    logger.info(f"✓ Loaded y_train: {y_train.shape}")
    logger.info(f"✓ Loaded y_test: {y_test.shape}")
    
    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    # Run feature preparation pipeline
    summary = prepare_train_test_data()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for key, value in summary.items():
        if key == 'feature_names':
            print(f"{key}:")
            for i, feat in enumerate(value, 1):
                print(f"  {i}. {feat}")
        else:
            print(f"{key}: {value}")
