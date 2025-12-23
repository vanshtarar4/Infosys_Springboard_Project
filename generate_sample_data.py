"""
Generate sample transaction data for testing the pipeline.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# Generate 5000 sample transactions
n_samples = 5000

# Generate timestamps
start_date = datetime(2024, 1, 1)
timestamps = [start_date + timedelta(hours=np.random.randint(0, 8760)) for _ in range(n_samples)]

# Generate transaction data
data = {
    'transaction_id': [f'TXN{str(i).zfill(6)}' for i in range(1, n_samples + 1)],
    'customer_id': [f'CUST{np.random.randint(1000, 9999)}' for _ in range(n_samples)],
    'kyc_verified': np.random.choice(['Yes', 'No', 'YES', 'no', None], n_samples, p=[0.4, 0.3, 0.1, 0.1, 0.1]),
    'account_age_days': np.random.randint(1, 3650, n_samples).astype(float),
    'transaction_amount': np.random.choice(
        [np.random.uniform(10, 1000), np.random.uniform(1000, 50000), np.random.uniform(50000, 200000)],
        n_samples,
        p=[0.7, 0.25, 0.05]
    ),
    'channel': np.random.choice(['web', 'Mobile', 'POS', 'atm', 'ONLINE', 'App', None], n_samples, p=[0.3, 0.25, 0.2, 0.15, 0.05, 0.04, 0.01]),
    'timestamp': timestamps,
    'is_fraud': np.random.choice([0, 1], n_samples, p=[0.95, 0.05])
}

# Introduce some missing values in account_age_days
missing_indices = np.random.choice(n_samples, size=100, replace=False)
for idx in missing_indices:
    data['account_age_days'][idx] = np.nan

# Introduce some missing values in transaction_amount (should be dropped)
missing_amount_indices = np.random.choice(n_samples, size=20, replace=False)
for idx in missing_amount_indices:
    data['transaction_amount'][idx] = np.nan

# Create duplicate transactions (some with conflicts)
duplicate_ids = ['TXN000050', 'TXN000100', 'TXN000150']
for dup_id in duplicate_ids:
    # Add duplicate with same fraud label
    dup_row = {
        'transaction_id': dup_id,
        'customer_id': f'CUST{np.random.randint(1000, 9999)}',
        'kyc_verified': 'Yes',
        'account_age_days': float(np.random.randint(100, 1000)),
        'transaction_amount': np.random.uniform(100, 5000),
        'channel': 'Web',
        'timestamp': datetime(2024, 6, 15, 10, 30),
        'is_fraud': 0
    }
    for key in data:
        if isinstance(data[key], list):
            data[key].append(dup_row[key])
        else:
            data[key] = np.append(data[key], dup_row[key])

# Add conflicting duplicate
conflict_row = {
    'transaction_id': 'TXN000050',
    'customer_id': 'CUST5555',
    'kyc_verified': 'No',
    'account_age_days': 500.0,
    'transaction_amount': 75000.0,
    'channel': 'Mobile',
    'timestamp': datetime(2024, 6, 15, 11, 0),
    'is_fraud': 1  # Different fraud label!
}
for key in data:
    if isinstance(data[key], list):
        data[key].append(conflict_row[key])
    else:
        data[key] = np.append(data[key], conflict_row[key])

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
output_path = 'data/raw/transactions.csv'
df.to_csv(output_path, index=False)

print(f"Generated {len(df)} sample transactions")
print(f"Saved to {output_path}")
print(f"\nData summary:")
print(f"- Nulls in kyc_verified: {df['kyc_verified'].isnull().sum()}")
print(f"- Nulls in account_age_days: {df['account_age_days'].isnull().sum()}")
print(f"- Nulls in transaction_amount: {df['transaction_amount'].isnull().sum()}")
print(f"- Duplicate transaction_ids: {df['transaction_id'].duplicated().sum()}")
print(f"- Unique channels: {df['channel'].unique()}")
