"""
Quick test script to verify feedback system is working.
"""

import sqlite3
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8001"
DB_PATH = "data/transactions.db"

print("\n" + "="*80)
print("FEEDBACK SYSTEM VERIFICATION")
print("="*80)

# Step 1: Test a transaction
print("\n[Step 1] Testing transaction prediction...")
test_data = {
    "customer_id": "8",
    "transaction_amount": 2000,
    "kyc_verified": 0,
    "account_age_days": 87,
    "channel": "Web",
    "timestamp": datetime.now().isoformat()
}

try:
    response = requests.post(f"{API_URL}/api/predict", json=test_data)
    prediction = response.json()
    
    print(f"✓ Transaction ID: {prediction['transaction_id']}")
    print(f"✓ Prediction: {prediction['prediction']}")
    print(f"✓ Risk Score: {prediction['risk_score']*100:.0f}%")
    
    txn_id = prediction['transaction_id']
    
except Exception as e:
    print(f"❌ Error testing transaction: {e}")
    exit(1)

# Step 2: Submit feedback
print("\n[Step 2] Submitting feedback...")
feedback_data = {
    "transaction_id": txn_id,
    "actual_label": "Legitimate",  # Confirming prediction
    "notes": "Automated test feedback"
}

try:
    response = requests.post(f"{API_URL}/api/feedback", json=feedback_data)
    feedback_result = response.json()
    
    print(f"✓ Feedback ID: {feedback_result['feedback_id']}")
    print(f"✓ Status: {feedback_result['message']}")
    
except Exception as e:
    print(f"❌ Error submitting feedback: {e}")
    exit(1)

# Step 3: Check feedback stats
print("\n[Step 3] Checking feedback statistics...")
try:
    response = requests.get(f"{API_URL}/api/feedback/stats")
    stats = response.json()
    
    print(f"✓ Total Feedback: {stats['total_feedback']}")
    print(f"✓ Fraud: {stats['by_label'].get('Fraud', 0)}")
    print(f"✓ Legitimate: {stats['by_label'].get('Legitimate', 0)}")
    print(f"✓ Model Accuracy: {stats['model_accuracy']:.1f}%")
    print(f"✓ Training-Ready: {stats['training_ready']}")
    
except Exception as e:
    print(f"❌ Error checking stats: {e}")
    exit(1)

# Step 4: Query database directly
print("\n[Step 4] Verifying database storage...")
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get count
    cursor.execute("SELECT COUNT(*) FROM transaction_feedback")
    count = cursor.fetchone()[0]
    print(f"✓ Total records in database: {count}")
    
    # Get latest feedback
    cursor.execute("""
        SELECT transaction_id, predicted_label, actual_label, feedback_timestamp
        FROM transaction_feedback 
        ORDER BY feedback_timestamp DESC 
        LIMIT 5
    """)
    
    print("\nRecent feedback:")
    for row in cursor.fetchall():
        print(f"  - {row[0][:30]}... Predicted:{row[1]} → Actual:{row[2]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error querying database: {e}")

# Summary
print("\n" + "="*80)
print("RESULTS:")
print("="*80)
print(f"✅ Feedback system is WORKING!")
print(f"✅ {stats['training_ready']} samples ready for training")

if stats['training_ready'] >= 100:
    print("\n🎉 READY TO RETRAIN MODEL!")
    print("Run: python src/training/auto_retrain.py")
else:
    needed = 100 - stats['training_ready']
    print(f"\n⏳ Need {needed} more samples before retraining")
    print("Keep testing transactions and providing feedback!")

print("\n💡 TIP: Try the UI at http://localhost:3000/fraud-detection")
print("="*80 + "\n")
