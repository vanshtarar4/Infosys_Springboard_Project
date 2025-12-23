"""
Data Integrity Tests for Processed Transaction Data
Validates data quality and business rules compliance.
"""

import pytest
import pandas as pd
from pathlib import Path


class TestDataIntegrity:
    """Test suite for data quality and integrity checks."""
    
    @pytest.fixture
    def processed_data_path(self):
        """Path to processed transactions CSV."""
        return Path('data/processed/transactions_processed.csv')
    
    @pytest.fixture
    def df(self, processed_data_path):
        """Load processed DataFrame."""
        if not processed_data_path.exists():
            pytest.skip(f"Processed data not found: {processed_data_path}")
        return pd.read_csv(processed_data_path)
    
    def test_file_exists(self, processed_data_path):
        """Verify processed data file exists."""
        assert processed_data_path.exists(), "Processed transactions file not found"
    
    def test_no_null_transaction_ids(self, df):
        """Assert no null transaction IDs in processed data."""
        null_count = df['transaction_id'].isnull().sum()
        assert null_count == 0, f"Found {null_count} null transaction IDs"
    
    def test_unique_transaction_ids(self, df):
        """Assert all transaction IDs are unique."""
        duplicate_count = df['transaction_id'].duplicated().sum()
        assert duplicate_count == 0, f"Found {duplicate_count} duplicate transaction IDs"
    
    def test_transaction_amounts_positive(self, df):
        """Assert all transaction amounts are greater than 0."""
        non_positive = (df['transaction_amount'] <= 0).sum()
        assert non_positive == 0, f"Found {non_positive} non-positive transaction amounts"
    
    def test_is_fraud_binary(self, df):
        """Assert is_fraud contains only 0 or 1."""
        valid_values = {0, 1}
        unique_values = set(df['is_fraud'].unique())
        invalid_values = unique_values - valid_values
        assert len(invalid_values) == 0, f"Invalid is_fraud values: {invalid_values}"
    
    def test_kyc_verified_binary(self, df):
        """Assert kyc_verified contains only 0 or 1."""
        if 'kyc_verified' in df.columns:
            valid_values = {0, 1}
            unique_values = set(df['kyc_verified'].unique())
            invalid_values = unique_values - valid_values
            assert len(invalid_values) == 0, f"Invalid kyc_verified values: {invalid_values}"
    
    def test_channel_standardized(self, df):
        """Assert channel values are standardized."""
        if 'channel' in df.columns:
            valid_channels = {'Web', 'Mobile', 'POS', 'ATM', 'Other'}
            unique_channels = set(df['channel'].unique())
            invalid_channels = unique_channels - valid_channels
            assert len(invalid_channels) == 0, f"Invalid channels: {invalid_channels}"
    
    def test_account_age_non_negative(self, df):
        """Assert account age days is non-negative."""
        if 'account_age_days' in df.columns:
            negative_count = (df['account_age_days'] < 0).sum()
            assert negative_count == 0, f"Found {negative_count} negative account ages"
    
    def test_is_high_value_binary(self, df):
        """Assert is_high_value flag is binary."""
        if 'is_high_value' in df.columns:
            valid_values = {0, 1}
            unique_values = set(df['is_high_value'].unique())
            invalid_values = unique_values - valid_values
            assert len(invalid_values) == 0, f"Invalid is_high_value values: {invalid_values}"
    
    def test_is_high_value_correctness(self, df):
        """Assert is_high_value flag matches transaction amount threshold."""
        if 'is_high_value' in df.columns and 'transaction_amount' in df.columns:
            threshold = 50000
            expected_high_value = (df['transaction_amount'] > threshold).astype(int)
            mismatches = (df['is_high_value'] != expected_high_value).sum()
            assert mismatches == 0, f"Found {mismatches} is_high_value flag mismatches"
    
    def test_timestamp_format(self, df):
        """Assert timestamp can be parsed as datetime."""
        if 'timestamp' in df.columns:
            try:
                pd.to_datetime(df['timestamp'])
            except Exception as e:
                pytest.fail(f"Timestamp parsing failed: {e}")
    
    def test_no_missing_required_columns(self, df):
        """Assert all required columns are present."""
        required_columns = [
            'transaction_id',
            'customer_id',
            'transaction_amount',
            'channel',
            'is_fraud'
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        assert len(missing_columns) == 0, f"Missing required columns: {missing_columns}"
    
    def test_data_not_empty(self, df):
        """Assert dataset contains data."""
        assert len(df) > 0, "Dataset is empty"
    
    def test_fraud_rate_reasonable(self, df):
        """Assert fraud rate is within a reasonable range (0-50%)."""
        fraud_rate = df['is_fraud'].mean() * 100
        assert 0 <= fraud_rate <= 50, f"Unusual fraud rate: {fraud_rate:.2f}%"
    
    def test_no_null_amounts(self, df):
        """Assert no null transaction amounts."""
        null_count = df['transaction_amount'].isnull().sum()
        assert null_count == 0, f"Found {null_count} null transaction amounts"
    
    def test_customer_ids_format(self, df):
        """Assert customer IDs are non-empty strings."""
        if 'customer_id' in df.columns:
            empty_count = df['customer_id'].isnull().sum()
            assert empty_count == 0, f"Found {empty_count} null customer IDs"


class TestTrainTestSplit:
    """Test suite for train/test split integrity."""
    
    @pytest.fixture
    def train_df(self):
        """Load training data."""
        train_path = Path('data/processed/train.csv')
        if not train_path.exists():
            pytest.skip("Train data not found")
        return pd.read_csv(train_path)
    
    @pytest.fixture
    def test_df(self):
        """Load test data."""
        test_path = Path('data/processed/test.csv')
        if not test_path.exists():
            pytest.skip("Test data not found")
        return pd.read_csv(test_path)
    
    def test_no_overlap_transaction_ids(self, train_df, test_df):
        """Assert no transaction ID overlap between train and test."""
        train_ids = set(train_df['transaction_id'])
        test_ids = set(test_df['transaction_id'])
        overlap = train_ids & test_ids
        assert len(overlap) == 0, f"Found {len(overlap)} overlapping transaction IDs"
    
    def test_class_balance_maintained(self, train_df, test_df):
        """Assert fraud rate is similar in train and test sets."""
        train_fraud_rate = train_df['is_fraud'].mean()
        test_fraud_rate = test_df['is_fraud'].mean()
        difference = abs(train_fraud_rate - test_fraud_rate)
        # Allow up to 2% difference
        assert difference < 0.02, f"Fraud rate difference too large: {difference:.4f}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
