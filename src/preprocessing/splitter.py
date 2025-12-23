"""
Train/Test split utilities for transaction data.
Creates stratified splits to maintain class balance.
"""

import pandas as pd
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


def create_split(input_csv: str, out_train: str, out_test: str, 
                 test_size: float = 0.2, random_state: int = 42) -> dict:
    """
    Create stratified train/test split from transaction data.
    
    Args:
        input_csv: Path to input CSV file
        out_train: Path for training set output
        out_test: Path for test set output
        test_size: Proportion of data for test set (default: 0.2)
        random_state: Random seed for reproducibility (default: 42)
    
    Returns:
        Dictionary with split metadata
    """
    logger.info(f"Loading data from {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Calculate original class distribution
    original_dist = df['is_fraud'].value_counts(normalize=True) * 100
    logger.info("="*60)
    logger.info("ORIGINAL CLASS DISTRIBUTION")
    logger.info("="*60)
    logger.info(f"Total samples: {len(df)}")
    logger.info(f"Legitimate: {original_dist[0]:.2f}%")
    logger.info(f"Fraudulent: {original_dist[1]:.2f}%")
    
    # Perform stratified split
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        stratify=df['is_fraud'],
        random_state=random_state
    )
    
    # Calculate split distributions
    train_dist = train_df['is_fraud'].value_counts(normalize=True) * 100
    test_dist = test_df['is_fraud'].value_counts(normalize=True) * 100
    
    logger.info("\n" + "="*60)
    logger.info("TRAIN SET DISTRIBUTION")
    logger.info("="*60)
    logger.info(f"Total samples: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    logger.info(f"Legitimate: {train_dist[0]:.2f}%")
    logger.info(f"Fraudulent: {train_dist[1]:.2f}%")
    
    logger.info("\n" + "="*60)
    logger.info("TEST SET DISTRIBUTION")
    logger.info("="*60)
    logger.info(f"Total samples: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
    logger.info(f"Legitimate: {test_dist[0]:.2f}%")
    logger.info(f"Fraudulent: {test_dist[1]:.2f}%")
    
    # Save splits
    Path(out_train).parent.mkdir(parents=True, exist_ok=True)
    Path(out_test).parent.mkdir(parents=True, exist_ok=True)
    
    train_df.to_csv(out_train, index=False)
    test_df.to_csv(out_test, index=False)
    
    logger.info(f"\n✓ Train set saved: {out_train}")
    logger.info(f"✓ Test set saved: {out_test}")
    
    # Prepare metadata
    metadata = {
        "source_file": input_csv,
        "total_samples": len(df),
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "test_size": test_size,
        "random_state": random_state,
        "original_distribution": {
            "legitimate_pct": float(original_dist[0]),
            "fraudulent_pct": float(original_dist[1])
        },
        "train_distribution": {
            "legitimate_pct": float(train_dist[0]),
            "fraudulent_pct": float(train_dist[1]),
            "fraud_count": int(train_df['is_fraud'].sum()),
            "legit_count": int((train_df['is_fraud'] == 0).sum())
        },
        "test_distribution": {
            "legitimate_pct": float(test_dist[0]),
            "fraudulent_pct": float(test_dist[1]),
            "fraud_count": int(test_df['is_fraud'].sum()),
            "legit_count": int((test_df['is_fraud'] == 0).sum())
        }
    }
    
    return metadata


if __name__ == '__main__':
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 3:
        print("Usage: python splitter.py <input_csv> <train_output> <test_output>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    train_file = sys.argv[2] if len(sys.argv) > 2 else 'data/processed/train.csv'
    test_file = sys.argv[3] if len(sys.argv) > 3 else 'data/processed/test.csv'
    
    metadata = create_split(input_file, train_file, test_file)
    
    # Save metadata
    config_path = Path('configs/split_info.json')
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"\n✓ Metadata saved: {config_path}")
    logger.info("\n" + "="*60)
    logger.info("SPLIT COMPLETE")
    logger.info("="*60)
