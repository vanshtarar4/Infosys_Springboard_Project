"""
Manual Database Initialization Script for Render
Run this once to set up the database on Render
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.init_db import init_database

if __name__ == '__main__':
    print("=" * 60)
    print("INITIALIZING DATABASE FOR PRODUCTION")
    print("=" * 60)
    
    # Set database path
    os.environ.setdefault('DATABASE_PATH', 'data/transactions.db')
    
    # Initialize
    try:
        init_database()
        print("\n" + "=" * 60)
        print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now start the application.")
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ DATABASE INITIALIZATION FAILED!")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
