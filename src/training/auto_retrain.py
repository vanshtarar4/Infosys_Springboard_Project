"""
Automated Model Retraining Pipeline
Phase 3 of Continuous Learning System

Automatically retrain model with new labeled data.
"""

import pandas as pd
import numpy as np
import joblib
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.data_aggregator import DataAggregator
from src.modeling.train_model import (
    train_logistic_regression,
    train_random_forest,
    train_gradient_boosting,
    evaluate_model
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MIN_SAMPLES = 100  # Minimum labeled samples needed for retraining


class ModelRetrainer:
    """Orchestrates automated model retraining."""
    
    def __init__(self, models_dir='models', data_dir='data'):
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.aggregator = DataAggregator()
    
    def get_next_version(self) -> str:
        """Get next model version number."""
        production_dir = self.models_dir / 'production'
        
        if not production_dir.exists():
            return '1.0'
        
        # Find highest version
        versions = []
        for version_dir in production_dir.iterdir():
            if version_dir.is_dir():
                version = version_dir.name.split('_')[0].replace('v', '')
                try:
                    versions.append(float(version))
                except:
                    pass
        
        if not versions:
            return '1.0'
        
        max_version = max(versions)
        return f"{max_version + 0.1:.1f}"
    
    def retrain_pipeline(self):
        """
        Complete retraining pipeline.
        
        Steps:
        1. Collect new labeled data
        2. Combine with historical data
        3. Train new models
        4. Evaluate performance
        5. Save as candidate if better
        
        Returns:
            Dictionary with retraining results
        """
        logger.info("="*80)
        logger.info("AUTOMATED MODEL RETRAINING STARTED")
        logger.info("="*80)
        
        # Step 1: Collect labeled data
        logger.info("\n[1/6] Collecting labeled data...")
        new_data = self.aggregator.collect_labeled_data(since_date='90 days ago')
        
        if len(new_data) < MIN_SAMPLES:
            logger.warning(f"Insufficient data: {len(new_data)} < {MIN_SAMPLES} samples")
            return {
                'status': 'skipped',
                'reason': f'Insufficient data ({len(new_data)} < {MIN_SAMPLES})',
                'samples_needed': MIN_SAMPLES - len(new_data)
            }
        
        # Step 2: Validate quality
        logger.info("\n[2/6] Validating data quality...")
        quality_stats = self.aggregator.validate_data_quality(new_data)
        
        # Step 3: Prepare training data
        logger.info("\n[3/6] Preparing training data...")
        X, y = self._prepare_features(new_data)
        
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
        
        # Step 4: Train models
        logger.info("\n[4/6] Training models...")
        models = {}
        results = []
        
        # Logistic Regression
        logger.info("Training Logistic Regression...")
        models['Logistic Regression'] = train_logistic_regression(X_train, y_train)
        metrics = evaluate_model(models['Logistic Regression'], X_test, y_test, 'Logistic Regression')
        results.append(metrics)
        
        # Random Forest
        logger.info("Training Random Forest...")
        models['Random Forest'] = train_random_forest(X_train, y_train)
        metrics = evaluate_model(models['Random Forest'], X_test, y_test, 'Random Forest')
        results.append(metrics)
        
        # Step 5: Select best model
        logger.info("\n[5/6] Selecting best model...")
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(['f1_score', 'recall'], ascending=False)
        best = results_df.iloc[0]
        best_model = models[best['model_name']]
        
        logger.info(f"Best model: {best['model_name']}")
        logger.info(f"  F1-Score: {best['f1_score']:.4f}")
        logger.info(f"  Precision: {best['precision']:.4f}")
        logger.info(f"  Recall: {best['recall']:.4f}")
        
        # Step 6: Compare with production
        logger.info("\n[6/6] Comparing with production model...")
        production_better = self._compare_with_production(best)
        
        # Save model
        version = f"v{self.get_next_version()}_{datetime.now():%Y-%m-%d}"
        save_dir = 'candidates' if not production_better else 'production'
        
        saved_path = self._save_model(
            model=best_model,
            version=version,
            metrics=best.to_dict(),
            save_dir=save_dir,
            training_samples=len(new_data)
        )
        
        logger.info("="*80)
        if production_better:
            logger.info("✅ NEW MODEL BETTER - SAVED TO PRODUCTION")
        else:
            logger.info("⚠️  PRODUCTION BETTER - SAVED AS CANDIDATE")
        logger.info(f"Model: {saved_path}")
        logger.info("="*80)
        
        return {
            'status': 'success',
            'version': version,
            'model_name': best['model_name'],
            'metrics': best.to_dict(),
            'production_better': production_better,
            'saved_to': save_dir,
            'path': str(saved_path)
        }
    
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features from raw data.
        
        Returns:
            (X, y) tuple
        """
        # Use same feature engineering as original model
        # For now, simplified version
        feature_cols = [
            'transaction_amount',
            'kyc_verified',
            'account_age_days'
        ]
        
        X = df[feature_cols].values
        y = df['is_fraud'].values
        
        return X, y
    
    def _compare_with_production(self, new_metrics: pd.Series) -> bool:
        """
        Compare new model with production.
        
        Returns:
            True if new model is better
        """
        try:
            # Load production metrics
            current_symlink = self.models_dir / 'current'
            if current_symlink.exists() and current_symlink.is_symlink():
                production_path = current_symlink.resolve()
                perf_file = production_path / 'performance.json'
                
                if perf_file.exists():
                    with open(perf_file, 'r') as f:
                        prod_metrics = json.load(f)
                    
                    # Compare F1 scores
                    new_f1 = new_metrics['f1_score']
                    prod_f1 = prod_metrics.get('f1_score', 0)
                    
                    logger.info(f"Production F1: {prod_f1:.4f}")
                    logger.info(f"New F1: {new_f1:.4f}")
                    
                    # New model needs to be at least 5% better
                    return new_f1 > (prod_f1 * 1.05)
            
            # No production model yet
            return True
            
        except Exception as e:
            logger.warning(f"Could not compare with production: {e}")
            return False
    
    def _save_model(self, model, version: str, metrics: dict, save_dir: str, training_samples: int):
        """Save model with metadata."""
        # Create directory
        save_path = self.models_dir / save_dir / version
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_file = save_path / 'model.pkl'
        joblib.dump(model, model_file)
        
        # Save metadata
        metadata = {
            'version': version,
            'created_at': datetime.now().isoformat(),
            'training_samples': training_samples,
            'model_type': type(model).__name__,
            'retrained': True
        }
        
        with open(save_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save performance
        with open(save_path / 'performance.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"✓ Model saved to {save_path}")
        
        return save_path


def main():
    """Run retraining pipeline."""
    retrainer = ModelRetrainer()
    result = retrainer.retrain_pipeline()
    
    print("\n" + "="*80)
    print("RETRAINING RESULT")
    print("="*80)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
