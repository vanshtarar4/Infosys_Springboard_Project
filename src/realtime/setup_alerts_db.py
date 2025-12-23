"""
Database schema creation script for fraud alerts.
Run this to add the fraud_alerts table to the existing database.
"""

import sqlite3
from pathlib import Path


def create_fraud_alerts_table(db_path: str = 'data/transactions.db'):
    """
    Create fraud_alerts table if it doesn't exist.
    
    Args:
        db_path: Path to SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create fraud_alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            customer_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT DEFAULT 'NEW',
            risk_score REAL,
            ml_prediction TEXT,
            triggered_rules TEXT,
            alert_message TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            resolved_by TEXT,
            resolution_notes TEXT,
            
            CHECK (alert_type IN ('ML', 'RULE', 'HYBRID')),
            CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
            CHECK (status IN ('NEW', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE', 'CONFIRMED'))
        )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_alerts_customer 
        ON fraud_alerts(customer_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_alerts_status 
        ON fraud_alerts(status)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_alerts_severity 
        ON fraud_alerts(severity)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_alerts_created 
        ON fraud_alerts(created_at DESC)
    ''')
    
    # Create alert statistics view
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS alert_statistics AS
        SELECT 
            DATE(created_at) as alert_date,
            severity,
            status,
            alert_type,
            COUNT(*) as count,
            AVG(risk_score) as avg_risk_score
        FROM fraud_alerts
        GROUP BY DATE(created_at), severity, status, alert_type
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✓ fraud_alerts table created successfully in {db_path}")
    print("✓ Indexes created for optimal query performance")
    print("✓ Alert statistics view created")


def verify_table_structure(db_path: str = 'data/transactions.db'):
    """
    Verify the fraud_alerts table exists and show its structure.
    
    Args:
        db_path: Path to SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='fraud_alerts'
    ''')
    
    if cursor.fetchone():
        print("\n✓ fraud_alerts table exists")
        
        # Show table schema
        cursor.execute('PRAGMA table_info(fraud_alerts)')
        columns = cursor.fetchall()
        
        print("\nTable Schema:")
        print(f"{'Column':<20} {'Type':<15} {'Not Null':<10} {'Default':<20}")
        print("-" * 70)
        for col in columns:
            print(f"{col[1]:<20} {col[2]:<15} {'YES' if col[3] else 'NO':<10} {str(col[4]):<20}")
        
        # Show indexes
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='fraud_alerts'
        ''')
        indexes = cursor.fetchall()
        
        if indexes:
            print("\nIndexes:")
            for idx in indexes:
                print(f"  - {idx[0]}")
    else:
        print("✗ fraud_alerts table does not exist")
    
    conn.close()


if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'data/transactions.db'
    
    print("="*70)
    print("Fraud Alerts Table Setup")
    print("="*70)
    
    create_fraud_alerts_table(db_path)
    verify_table_structure(db_path)
    
    print("\n" + "="*70)
    print("✅ Setup Complete!")
    print("="*70)
