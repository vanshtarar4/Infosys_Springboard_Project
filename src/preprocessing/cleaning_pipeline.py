"""
Data Cleaning Pipeline for Transaction Intelligence
Handles ingestion, cleaning, feature engineering, and export of transaction data.
"""

import pandas as pd
import numpy as np
import json
import logging
import argparse
from pathlib import Path
from typing import Tuple, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_raw(input_path: str, chunk_size: int = 200000) -> pd.DataFrame:
    """
    Load raw transaction data with automatic delimiter detection and chunking.
    
    Args:
        input_path: Path to raw CSV file
        chunk_size: Number of rows to process at once if file is large
    
    Returns:
        DataFrame with raw transaction data
    """
    logger.info(f"Loading data from {input_path}")
    
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # First, detect delimiter by reading a small sample
    with open(input_path, 'r') as f:
        first_line = f.readline()
        delimiter = ',' if ',' in first_line else '\t'
    
    logger.info(f"Detected delimiter: '{delimiter}'")
    
    # Count rows to determine if chunking is needed
    row_count = sum(1 for _ in open(input_path)) - 1  # Subtract header
    logger.info(f"Total rows in file: {row_count}")
    
    if row_count > chunk_size:
        logger.info(f"Large file detected. Processing in chunks of {chunk_size}")
        chunks = []
        for chunk in pd.read_csv(input_path, delimiter=delimiter, chunksize=chunk_size):
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
    else:
        df = pd.read_csv(input_path, delimiter=delimiter)
    
    logger.info(f"Successfully loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def show_initial_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Display and return initial data statistics.
    
    Args:
        df: Raw DataFrame
    
    Returns:
        Dictionary with statistics
    """
    logger.info("=" * 60)
    logger.info("INITIAL DATA STATISTICS")
    logger.info("=" * 60)
    
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'duplicate_count': df.duplicated().sum(),
        'duplicate_transaction_ids': df['transaction_id'].duplicated().sum() if 'transaction_id' in df.columns else 0
    }
    
    logger.info(f"Total Rows: {stats['total_rows']}")
    logger.info(f"Total Columns: {stats['total_columns']}")
    logger.info(f"Columns: {stats['columns']}")
    logger.info("\nData Types:")
    for col, dtype in stats['dtypes'].items():
        logger.info(f"  {col}: {dtype}")
    
    logger.info("\nNull Counts:")
    for col, null_count in stats['null_counts'].items():
        logger.info(f"  {col}: {null_count}")
    
    if 'channel' in df.columns:
        unique_channels = df['channel'].dropna().unique()
        stats['unique_channels'] = list(unique_channels)
        logger.info(f"\nUnique Channels: {list(unique_channels)}")
    
    logger.info(f"\nTotal Duplicate Rows: {stats['duplicate_count']}")
    logger.info(f"Duplicate Transaction IDs: {stats['duplicate_transaction_ids']}")
    logger.info("=" * 60)
    
    return stats


def clean_df(df: pd.DataFrame, output_dir: str = 'data/processed') -> pd.DataFrame:
    """
    Clean DataFrame with missing value handling and duplicate resolution.
    
    Args:
        df: Raw DataFrame
        output_dir: Directory for output files
    
    Returns:
        Cleaned DataFrame
    """
    logger.info("Starting data cleaning process...")
    df_clean = df.copy()
    initial_rows = len(df_clean)
    
    # 1. Handle missing values in kyc_verified
    if 'kyc_verified' in df_clean.columns:
        kyc_missing = df_clean['kyc_verified'].isnull().sum()
        df_clean['kyc_verified'] = df_clean['kyc_verified'].fillna('No')
        logger.info(f"Filled {kyc_missing} missing values in kyc_verified with 'No'")
    
    # 2. Drop rows where transaction_amount is missing
    if 'transaction_amount' in df_clean.columns:
        amount_missing = df_clean['transaction_amount'].isnull().sum()
        if amount_missing > 0:
            df_clean = df_clean.dropna(subset=['transaction_amount'])
            logger.info(f"Dropped {amount_missing} rows with missing transaction_amount")
    
    # 3. Fill account_age_days with median grouped by kyc_verified
    if 'account_age_days' in df_clean.columns:
        age_missing = df_clean['account_age_days'].isnull().sum()
        if age_missing > 0:
            # Create a temporary kyc column for grouping
            temp_kyc = df_clean['kyc_verified'].fillna('Unknown')
            median_by_kyc = df_clean.groupby(temp_kyc)['account_age_days'].transform('median')
            df_clean['account_age_days'] = df_clean['account_age_days'].fillna(median_by_kyc)
            logger.info(f"Filled {age_missing} missing values in account_age_days with group medians")
    
    # 4. Fill other categorical columns with "Unknown"
    categorical_cols = df_clean.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col not in ['kyc_verified', 'transaction_amount', 'timestamp']:
            missing_count = df_clean[col].isnull().sum()
            if missing_count > 0:
                df_clean[col] = df_clean[col].fillna('Unknown')
                logger.info(f"Filled {missing_count} missing values in {col} with 'Unknown'")
    
    # 5. Handle duplicates
    if 'transaction_id' in df_clean.columns:
        # Find conflicting duplicates (same transaction_id, different is_fraud)
        duplicate_ids = df_clean[df_clean['transaction_id'].duplicated(keep=False)]
        
        if len(duplicate_ids) > 0 and 'is_fraud' in df_clean.columns:
            # Check for conflicts
            conflicts = duplicate_ids.groupby('transaction_id')['is_fraud'].nunique()
            conflict_ids = conflicts[conflicts > 1].index
            
            if len(conflict_ids) > 0:
                conflict_rows = df_clean[df_clean['transaction_id'].isin(conflict_ids)]
                conflict_path = Path(output_dir) / 'duplicate_conflicts.csv'
                conflict_path.parent.mkdir(parents=True, exist_ok=True)
                conflict_rows.to_csv(conflict_path, index=False)
                logger.warning(f"Found {len(conflict_ids)} transaction IDs with conflicting is_fraud values")
                logger.warning(f"Saved to {conflict_path} for manual review")
        
        # Drop duplicates by transaction_id, keeping first occurrence
        duplicates_before = df_clean['transaction_id'].duplicated().sum()
        df_clean = df_clean.drop_duplicates(subset=['transaction_id'], keep='first')
        logger.info(f"Removed {duplicates_before} duplicate transaction_ids")
    
    rows_removed = initial_rows - len(df_clean)
    logger.info(f"Cleaning complete. Rows removed: {rows_removed}")
    
    return df_clean


def standardize_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize data types for all columns.
    
    Args:
        df: DataFrame to standardize
    
    Returns:
        DataFrame with standardized types
    """
    logger.info("Standardizing data types...")
    df_std = df.copy()
    
    # 1. Timestamp → pandas datetime
    if 'timestamp' in df_std.columns:
        df_std['timestamp'] = pd.to_datetime(df_std['timestamp'], errors='coerce', infer_datetime_format=True)
        # Create UTC-aware column
        df_std['timestamp_utc'] = df_std['timestamp'].dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')
        logger.info("Converted timestamp to datetime and created UTC-aware column")
    
    # 2. Transaction amount → numeric
    if 'transaction_amount' in df_std.columns:
        # Strip commas and currency symbols
        if df_std['transaction_amount'].dtype == 'object':
            df_std['transaction_amount'] = df_std['transaction_amount'].astype(str).str.replace(',', '').str.replace('$', '').str.replace('₹', '')
        df_std['transaction_amount'] = pd.to_numeric(df_std['transaction_amount'], errors='coerce')
        logger.info("Converted transaction_amount to numeric")
    
    # 3. kyc_verified → binary
    if 'kyc_verified' in df_std.columns:
        kyc_map = {'Yes': 1, 'yes': 1, 'YES': 1, 'Y': 1, '1': 1, 1: 1,
                   'No': 0, 'no': 0, 'NO': 0, 'N': 0, '0': 0, 0: 0}
        df_std['kyc_verified'] = df_std['kyc_verified'].map(kyc_map).fillna(0).astype(int)
        logger.info("Converted kyc_verified to binary (1/0)")
    
    # 4. Channel → standardized values
    if 'channel' in df_std.columns:
        # Title case
        df_std['channel'] = df_std['channel'].str.title()
        
        # Standardize to valid values
        channel_map = {
            'Web': 'Web', 'Website': 'Web', 'Online': 'Web', 'Internet': 'Web',
            'Mobile': 'Mobile', 'App': 'Mobile', 'Phone': 'Mobile',
            'Pos': 'POS', 'Point Of Sale': 'POS', 'Point-Of-Sale': 'POS',
            'Atm': 'ATM', 'Cash Machine': 'ATM',
        }
        df_std['channel'] = df_std['channel'].replace(channel_map)
        
        # Any remaining values → Other
        valid_channels = ['Web', 'Mobile', 'POS', 'ATM']
        df_std.loc[~df_std['channel'].isin(valid_channels), 'channel'] = 'Other'
        logger.info(f"Standardized channel values: {df_std['channel'].unique()}")
    
    return df_std


def feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create engineered features from existing columns.
    
    Args:
        df: DataFrame with standardized data
    
    Returns:
        DataFrame with additional features
    """
    logger.info("Engineering features...")
    df_feat = df.copy()
    
    # 1. Time-based features
    if 'timestamp' in df_feat.columns:
        df_feat['hour'] = df_feat['timestamp'].dt.hour
        df_feat['minute'] = df_feat['timestamp'].dt.minute
        df_feat['weekday'] = df_feat['timestamp'].dt.weekday  # 0=Monday
        df_feat['month'] = df_feat['timestamp'].dt.month
        logger.info("Created time-based features: hour, minute, weekday, month")
    
    # 2. High value flag
    if 'transaction_amount' in df_feat.columns:
        df_feat['is_high_value'] = (df_feat['transaction_amount'] > 50000).astype(int)
        high_value_count = df_feat['is_high_value'].sum()
        logger.info(f"Created is_high_value flag ({high_value_count} high-value transactions)")
        
        # 3. Log-transformed amount
        df_feat['amount_log'] = np.log1p(df_feat['transaction_amount'])
        logger.info("Created amount_log feature")
    
    # 4. Account age buckets
    if 'account_age_days' in df_feat.columns:
        quartiles = df_feat['account_age_days'].quantile([0.25, 0.5, 0.75])
        
        def categorize_age(age):
            if pd.isna(age):
                return 'Unknown'
            elif age <= quartiles[0.25]:
                return 'new'
            elif age <= quartiles[0.5]:
                return 'recent'
            elif age <= quartiles[0.75]:
                return 'established'
            else:
                return 'old'
        
        df_feat['account_age_bucket'] = df_feat['account_age_days'].apply(categorize_age)
        logger.info(f"Created account_age_bucket: {df_feat['account_age_bucket'].value_counts().to_dict()}")
    
    return df_feat


def save_processed(df: pd.DataFrame, output_path: str, config_dir: str = 'configs') -> None:
    """
    Save processed data and metadata.
    
    Args:
        df: Processed DataFrame
        output_path: Path for main output CSV
        config_dir: Directory for configuration files
    """
    logger.info("Saving processed data...")
    
    # Create output directory
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Save full processed dataset
    df.to_csv(output_path, index=False)
    logger.info(f"Saved full dataset to {output_path} ({len(df)} rows)")
    
    # 2. Save preview (first 500 rows)
    preview_path = output_file.parent / 'transactions_preview.csv'
    df.head(500).to_csv(preview_path, index=False)
    logger.info(f"Saved preview (500 rows) to {preview_path}")
    
    # 3. Create data profile metadata
    profile = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'schema': []
    }
    
    for col in df.columns:
        col_profile = {
            'column_name': col,
            'dtype': str(df[col].dtype),
            'null_count': int(df[col].isnull().sum()),
            'null_percentage': float(df[col].isnull().sum() / len(df) * 100),
            'sample_value': str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else None
        }
        profile['schema'].append(col_profile)
    
    # Save metadata
    config_path = Path(config_dir)
    config_path.mkdir(parents=True, exist_ok=True)
    profile_path = config_path / 'data_profile.json'
    
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)
    
    logger.info(f"Saved data profile to {profile_path}")
    logger.info("=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 60)


def run_pipeline(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Execute the complete data cleaning pipeline.
    
    Args:
        input_path: Path to raw CSV file
        output_path: Path for processed CSV output
    
    Returns:
        Processed DataFrame
    """
    # Load raw data
    df_raw = load_raw(input_path)
    
    # Show initial statistics
    initial_stats = show_initial_stats(df_raw)
    
    # Clean data
    df_clean = clean_df(df_raw)
    
    # Standardize data types
    df_std = standardize_data_types(df_clean)
    
    # Feature engineering
    df_processed = feature_engineer(df_std)
    
    # Save processed data
    save_processed(df_processed, output_path)
    
    return df_processed


def main():
    """CLI entry point for the cleaning pipeline."""
    parser = argparse.ArgumentParser(
        description='Transaction data cleaning and preprocessing pipeline'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/raw/transactions.csv',
        help='Path to raw input CSV file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/processed/transactions_processed.csv',
        help='Path for processed output CSV file'
    )
    
    args = parser.parse_args()
    
    try:
        run_pipeline(args.input, args.output)
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
