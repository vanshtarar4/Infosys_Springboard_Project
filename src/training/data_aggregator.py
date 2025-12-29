"""
Data Aggregation Pipeline
Phase 2 of Continuous Learning System

Collects labeled transactions from feedback for model retraining.
"""

import pandas as pd
import numpy as np
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'data/transactions.db'


class DataAggregator:
    """Aggregate labeled transactions for model retraining."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def collect_labeled_data(self, since_date: str = None, min_samples: int = 50) -> pd.DataFrame:
        """
        Collect all transactions with confirmed labels from feedback.
        
        Args:
            since_date: Collect data since this date (e.g., '2024-12-01' or '7 days ago')
            min_samples: Minimum number of samples required
            
        Returns:
            DataFrame with features + confirmed labels
        """
        logger.info("Collecting labeled training data...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Build query
        if since_date:
            if 'days ago' in since_date:
                days = int(since_date.split()[0])
                date_filter = f"AND f.feedback_timestamp >= datetime('now', '-{days} days')"
            else:
                date_filter = f"AND f.feedback_timestamp >= '{since_date}'"
        else:
            date_filter = ""
        
        query = f"""
        SELECT 
            t.transaction_id,
            t.customer_id,
            t.transaction_amount,
            t.transaction_timestamp,
            t.channel,
            t.kyc_verified,
            t.account_age_days,
            CASE 
                WHEN f.actual_label = 'Fraud' THEN 1
                ELSE 0
            END as is_fraud,
            f.feedback_timestamp,
            f.predicted_label,
            f.actual_label
        FROM transactions t
        INNER JOIN transaction_feedback f ON t.transaction_id = f.transaction_id
        WHERE t.feedback_confirmed = 1
        {date_filter}
        ORDER BY f.feedback_timestamp DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        logger.info(f"✓ Collected {len(df)} labeled transactions")
        
        if len(df) < min_samples:
            logger.warning(f"Only {len(df)} samples available (need {min_samples})")
        
        return df
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """
        Check data quality metrics.
        
        Returns:
            Dictionary with quality statistics
        """
        logger.info("Validating data quality...")
        
        stats = {
            'total_samples': len(df),
            'fraud_count': df['is_fraud'].sum(),
            'legit_count': (df['is_fraud'] == 0).sum(),
            'fraud_rate': df['is_fraud'].mean(),
            'missing_values': df.isnull().sum().to_dict(),
            'date_range': {
                'start': df['feedback_timestamp'].min(),
                'end': df['feedback_timestamp'].max()
            }
        }
        
        # Check class imbalance
        fraud_rate = stats['fraud_rate']
        if fraud_rate < 0.01 or fraud_rate > 0.99:
            logger.warning(f"Severe class imbalance: {fraud_rate:.2%} fraud rate")
            stats['imbalance_warning'] = True
        else:
            stats['imbalance_warning'] = False
        
        # Check missing values
        missing_cols = [col for col, count in stats['missing_values'].items() if count > 0]
        if missing_cols:
            logger.warning(f"Missing values in columns: {missing_cols}")
            stats['missing_warning'] = True
        else:
            stats['missing_warning'] = False
        
        logger.info(f"✓ Quality check complete: {stats['total_samples']} samples, {stats['fraud_rate']:.2%} fraud")
        
        return stats
    
    def detect_data_drift(self, new_df: pd.DataFrame, reference_csv: str = 'data/processed/transactions_processed.csv') -> Dict:
        """
        Detect if new data has drifted from reference distribution.
        
        Returns:
            Dictionary with drift metrics
        """
        try:
            reference_df = pd.read_csv(reference_csv)
            
            drift_stats = {}
            
            # Compare distributions for key features
            numeric_cols = ['transaction_amount', 'account_age_days']
            
            for col in numeric_cols:
                if col in new_df.columns and col in reference_df.columns:
                    new_mean = new_df[col].mean()
                    ref_mean = reference_df[col].mean()
                    
                    # Percentage change
                    pct_change = abs((new_mean - ref_mean) / ref_mean) if ref_mean != 0 else 0
                    
                    drift_stats[col] = {
                        'new_mean': new_mean,
                        'ref_mean': ref_mean,
                        'pct_change': pct_change,
                        'drifted': pct_change > 0.3  # 30% change threshold
                    }
            
            # Overall drift score (average of changes)
            drift_score = np.mean([s['pct_change'] for s in drift_stats.values()])
            
            logger.info(f"Drift score: {drift_score:.2%}")
            
            return {
                'drift_score': drift_score,
                'feature_drift': drift_stats,
                'significant_drift': drift_score > 0.3
            }
            
        except Exception as e:
            logger.warning(f"Could not detect drift: {e}")
            return {'drift_score': 0, 'significant_drift': False}
    
    def export_training_data(self, df: pd.DataFrame, output_path: str = 'data/retraining/labeled_data.csv'):
        """
        Export labeled data for training.
        
        Args:
            df: DataFrame with labeled transactions
            output_path: Where to save the CSV
        """
        # Create directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        df.to_csv(output_path, index=False)
        
        logger.info(f"✓ Exported {len(df)} samples to {output_path}")
        
        return output_path


def main():
    """Test data aggregation pipeline."""
    aggregator = DataAggregator()
    
    # Collect labeled data
    df = aggregator.collect_labeled_data(since_date='30 days ago')
    
    if len(df) == 0:
        logger.warning("No labeled data available yet. Submit feedback first!")
        return
    
    # Validate quality
    stats = aggregator.validate_data_quality(df)
    print("\n=== Data Quality ===")
    print(f"Total samples: {stats['total_samples']}")
    print(f"Fraud: {stats['fraud_count']} ({stats['fraud_rate']:.2%})")
    print(f"Legitimate: {stats['legit_count']}")
    
    # Check drift
    drift = aggregator.detect_data_drift(df)
    print(f"\nDrift score: {drift['drift_score']:.2%}")
    
    # Export
    if stats['total_samples'] >= 50:
        output_path = aggregator.export_training_data(df)
        print(f"\n✓ Data exported to: {output_path}")
    else:
        print(f"\nNeed {50 - stats['total_samples']} more labeled samples for training")


if __name__ == '__main__':
    main()
