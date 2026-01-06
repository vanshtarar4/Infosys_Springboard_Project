"""
Database Initialization Script
Creates the database and tables if they don't exist
Loads full transaction data from CSV if available
"""
import sqlite3
import os
import sys

def init_database():
    """Initialize the database with required tables and load data from CSV"""
    db_path = os.getenv('DATABASE_PATH', 'data/transactions.db')
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"📊 Initializing database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            transaction_amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            merchant_category TEXT,
            device_id TEXT,
            location TEXT,
            is_fraud INTEGER DEFAULT 0,
            kyc_verified INTEGER DEFAULT 0,
            is_high_value INTEGER DEFAULT 0,
            velocity_1h INTEGER DEFAULT 0,
            velocity_24h INTEGER DEFAULT 0,
            avg_amt_24h REAL DEFAULT 0,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            prediction TEXT NOT NULL,
            risk_score REAL,
            model_version TEXT,
            confidence REAL,
            explanation TEXT,
            rule_triggered TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            predicted_label TEXT NOT NULL,
            actual_label TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
    ''')
    
    # Create alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
    ''')
    
    # Check if we need to load data
    cursor.execute('SELECT COUNT(*) FROM transactions')
    existing_count = cursor.fetchone()[0]
    
    if existing_count == 0:
        # Try to load from CSV first
        csv_path = 'data/processed/transactions_processed.csv'
        if os.path.exists(csv_path):
            print(f"📂 Loading full dataset from {csv_path}...")
            try:
                import pandas as pd
                df = pd.read_csv(csv_path)
                
                # Map CSV columns to database columns
                # Adjust these mappings based on your actual CSV structure
                if 'TransactionID' in df.columns:
                    df = df.rename(columns={
                        'TransactionID': 'transaction_id',
                        'TransactionAmount': 'transaction_amount',
                        'TransactionDate': 'timestamp',
                        'MerchantCategory': 'merchant_category',
                        'DeviceID': 'device_id',
                        'Location': 'location',
                        'IsFraud': 'is_fraud',
                        'KYCVerified': 'kyc_verified',
                        'IsHighValue': 'is_high_value',
                        'Velocity1H': 'velocity_1h',
                        'Velocity24H': 'velocity_24h',
                        'AvgAmount24H': 'avg_amt_24h',
                        'UserID': 'user_id'
                    })
                
                # Select only the columns we need
                columns_to_insert = [
                    'transaction_id', 'transaction_amount', 'timestamp',
                    'merchant_category', 'device_id', 'location', 'is_fraud',
                    'kyc_verified', 'is_high_value', 'velocity_1h',
                    'velocity_24h', 'avg_amt_24h', 'user_id'
                ]
                
                # Filter to only existing columns
                available_cols = [col for col in columns_to_insert if col in df.columns]
                df_subset = df[available_cols]
                
                # Insert data
                df_subset.to_sql('transactions', conn, if_exists='append', index=False)
                
                print(f"✅ Loaded {len(df)} transactions from CSV")
                
            except Exception as e:
                print(f"⚠️  Could not load CSV: {e}")
                print("   Falling back to sample data...")
                _load_sample_data(cursor)
        else:
            print(f"📝 CSV not found at {csv_path}, loading sample data...")
            _load_sample_data(cursor)
    else:
        print(f"✅ Database already contains {existing_count} transactions")
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")
    print(f"   Location: {db_path}")
    print(f"   Tables: transactions, predictions, feedback, alerts")


def _load_sample_data(cursor):
    """Load minimal sample data for testing"""
    print("📝 Adding sample transaction data...")
    sample_transactions = [
        ('TXN_001', 50.00, '2024-01-01 10:00:00', 'Retail', 'DEV001', 'New York', 0, 1, 0, 0, 0, 0, 'USER001'),
        ('TXN_002', 15000.00, '2024-01-01 11:00:00', 'Electronics', 'DEV002', 'Los Angeles', 1, 0, 1, 1, 5, 5000, 'USER002'),
        ('TXN_003', 100.00, '2024-01-01 12:00:00', 'Food', 'DEV003', 'Chicago', 0, 1, 0, 0, 0, 0, 'USER003'),
    ]
    
    cursor.executemany('''
        INSERT INTO transactions 
        (transaction_id, transaction_amount, timestamp, merchant_category, device_id, location, 
         is_fraud, kyc_verified, is_high_value, velocity_1h, velocity_24h, avg_amt_24h, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_transactions)


if __name__ == '__main__':
    init_database()
