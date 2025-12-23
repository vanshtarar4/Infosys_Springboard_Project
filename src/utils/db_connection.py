"""
Database connection and transaction data ingestion utilities.
Handles SQLite database operations for transaction data.
"""

import sqlite3
import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TransactionDB:
    """SQLite database manager for transaction data."""
    
    def __init__(self, db_path: str = 'data/transactions.db'):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        logger.info(f"Database initialized at {self.db_path}")
    
    def connect(self):
        """Establish database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            logger.info("Database connection established")
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")
    
    def create_transactions_table(self):
        """Create transactions table with appropriate schema."""
        self.connect()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            customer_id TEXT,
            kyc_verified INTEGER,
            account_age_days REAL,
            transaction_amount REAL,
            channel TEXT,
            timestamp TEXT,
            timestamp_utc TEXT,
            is_fraud INTEGER,
            hour INTEGER,
            minute INTEGER,
            weekday INTEGER,
            month INTEGER,
            is_high_value INTEGER,
            amount_log REAL,
            account_age_bucket TEXT
        )
        """
        
        self.conn.execute(create_table_sql)
        self.conn.commit()
        logger.info("Transactions table created/verified")
    
    def insert_transactions(self, df: pd.DataFrame, batch_size: int = 1000):
        """
        Insert transaction data in bulk.
        
        Args:
            df: DataFrame with transaction data
            batch_size: Number of rows to insert per batch
        """
        self.connect()
        self.create_transactions_table()
        
        # Select only columns that exist in both DataFrame and table
        table_columns = [
            'transaction_id', 'customer_id', 'kyc_verified', 'account_age_days',
            'transaction_amount', 'channel', 'timestamp', 'timestamp_utc', 'is_fraud',
            'hour', 'minute', 'weekday', 'month', 'is_high_value', 'amount_log',
            'account_age_bucket'
        ]
        
        # Filter to only columns that exist in DataFrame
        available_columns = [col for col in table_columns if col in df.columns]
        df_to_insert = df[available_columns].copy()
        
        # Convert timestamp columns to string for SQLite compatibility
        if 'timestamp' in df_to_insert.columns:
            df_to_insert['timestamp'] = df_to_insert['timestamp'].astype(str)
        if 'timestamp_utc' in df_to_insert.columns:
            df_to_insert['timestamp_utc'] = df_to_insert['timestamp_utc'].astype(str)
        
        # Insert in batches
        total_rows = len(df_to_insert)
        logger.info(f"Inserting {total_rows} rows into database...")
        
        for i in range(0, total_rows, batch_size):
            batch = df_to_insert.iloc[i:i + batch_size]
            batch.to_sql('transactions', self.conn, if_exists='append', index=False)
            
            if (i + batch_size) % 10000 == 0:
                logger.info(f"Inserted {min(i + batch_size, total_rows)}/{total_rows} rows")
        
        self.conn.commit()
        logger.info(f"Successfully inserted {total_rows} rows into database")
    
    def get_row_count(self) -> int:
        """Get total number of rows in transactions table."""
        self.connect()
        cursor = self.conn.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        return count
    
    def query_transactions(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
        
        Returns:
            DataFrame with query results
        """
        self.connect()
        return pd.read_sql_query(query, self.conn)
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def ingest_to_database(csv_path: str, db_path: str = 'data/transactions.db'):
    """
    Convenience function to ingest CSV data into database.
    
    Args:
        csv_path: Path to processed CSV file
        db_path: Path to SQLite database
    """
    logger.info(f"Starting database ingestion from {csv_path}")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} rows from CSV")
    
    # Insert into database
    with TransactionDB(db_path) as db:
        db.insert_transactions(df)
        row_count = db.get_row_count()
        logger.info(f"Database now contains {row_count} transactions")
    
    logger.info("Database ingestion complete")


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        db_file = sys.argv[2] if len(sys.argv) > 2 else 'data/transactions.db'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        ingest_to_database(csv_file, db_file)
    else:
        print("Usage: python db_connection.py <csv_path> [db_path]")
