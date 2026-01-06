"""
Database Initialization Script
Creates the database and tables if they don't exist
"""
import sqlite3
import os

def init_database():
    """Initialize the database with required tables"""
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
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM transactions')
    if cursor.fetchone()[0] == 0:
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
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")
    print(f"   Location: {db_path}")
    print(f"   Tables: transactions, predictions, feedback, alerts")

if __name__ == '__main__':
    init_database()
