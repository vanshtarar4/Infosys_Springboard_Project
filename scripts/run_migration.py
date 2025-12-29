"""
Run database migrations for feedback system.
"""

import sqlite3
import os

DB_PATH = 'data/transactions.db'
MIGRATION_FILE = 'migrations/add_feedback_system.sql'

def run_migration():
    """Execute SQL migration file."""
    print("Running feedback system migration...")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return False
    
    if not os.path.exists(MIGRATION_FILE):
        print(f"Error: Migration file not found at {MIGRATION_FILE}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        with open(MIGRATION_FILE, 'r') as f:
            sql_script = f.read()
        
        # Execute the entire script
        cursor.executescript(sql_script)
        
        conn.commit()
        conn.close()
        
        print("✓ Feedback system migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    run_migration()
