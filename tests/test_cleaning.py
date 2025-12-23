"""
Unit tests for data cleaning pipeline.
"""

import pytest
import pandas as pd
from pathlib import Path


class TestDataCleaning:
    """Test suite for cleaned transaction data."""
    
    @pytest.fixture
    def processed_csv_path(self):
        """Path to processed CSV file."""
        return Path('data/processed/transactions_processed.csv')
    
    @pytest.fixture
    def processed_df(self, processed_csv_path):
        """Load processed DataFrame."""
        if not processed_csv_path.exists():
            pytest.skip(f"Processed CSV not found: {processed_csv_path}")
        return pd.read_csv(processed_csv_path)
    
    def test_no_null_transaction_ids(self, processed_df):
        """Assert no nulls in transaction_id column."""
        null_count = processed_df['transaction_id'].isnull().sum()
        assert null_count == 0, f"Found {null_count} null transaction_ids"
    
    def test_no_null_transaction_amounts(self, processed_df):
        """Assert no nulls in transaction_amount column."""
        null_count = processed_df['transaction_amount'].isnull().sum()
        assert null_count == 0, f"Found {null_count} null transaction_amounts"
    
    def test_transaction_amount_positive(self, processed_df):
        """Assert all transaction amounts are positive."""
        negative_count = (processed_df['transaction_amount'] <= 0).sum()
        assert negative_count == 0, f"Found {negative_count} non-positive amounts"
    
    def test_kyc_verified_binary(self, processed_df):
        """Assert kyc_verified contains only 0 or 1."""
        if 'kyc_verified' in processed_df.columns:
            unique_values = processed_df['kyc_verified'].unique()
            assert set(unique_values).issubset({0, 1}), f"Invalid kyc_verified values: {unique_values}"
    
    def test_channel_standardized(self, processed_df):
        """Assert channel values are standardized."""
        if 'channel' in processed_df.columns:
            valid_channels = {'Web', 'Mobile', 'POS', 'ATM', 'Other'}
            unique_channels = set(processed_df['channel'].unique())
            assert unique_channels.issubset(valid_channels), f"Invalid channels: {unique_channels - valid_channels}"
    
    def test_timestamp_format(self, processed_df):
        """Assert timestamp is in datetime format."""
        if 'timestamp' in processed_df.columns:
            # Try to parse timestamp
            try:
                pd.to_datetime(processed_df['timestamp'])
            except Exception as e:
                pytest.fail(f"Timestamp parsing failed: {e}")
    
    def test_high_value_flag_correctness(self, processed_df):
        """Assert is_high_value flag is correctly calculated."""
        if 'is_high_value' in processed_df.columns and 'transaction_amount' in processed_df.columns:
            expected_high_value = (processed_df['transaction_amount'] > 50000).astype(int)
            assert (processed_df['is_high_value'] == expected_high_value).all(), "is_high_value flag incorrect"
    
    def test_required_columns_exist(self, processed_df):
        """Assert all required columns exist."""
        required_columns = [
            'transaction_id', 'customer_id', 'transaction_amount', 
            'channel', 'timestamp'
        ]
        missing_columns = [col for col in required_columns if col not in processed_df.columns]
        assert len(missing_columns) == 0, f"Missing required columns: {missing_columns}"
    
    def test_no_duplicate_transaction_ids(self, processed_df):
        """Assert no duplicate transaction IDs."""
        duplicate_count = processed_df['transaction_id'].duplicated().sum()
        assert duplicate_count == 0, f"Found {duplicate_count} duplicate transaction_ids"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
