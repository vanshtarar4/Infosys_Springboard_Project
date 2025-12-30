"""
Generate fresh test alerts with current timestamps
"""

import sqlite3
from datetime import datetime, timedelta
import random

# Connect to database
conn = sqlite3.connect('data/transactions.db')
cursor = conn.cursor()

# Delete old alerts
cursor.execute("DELETE FROM fraud_alerts WHERE alert_id > 0")
print("✓ Cleared old alerts")

# Generate 20 fresh alerts with recent timestamps
customers = ['78984', 'C897', 'VERIFY_999', '888', 'f786', 'C12345']
severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
channels = ['Web', 'Mobile', 'ATM', 'International']
rules = [
    'High transaction amount without KYC verification',
    'New account with high transaction amount',
    'Odd hour transaction (2-4 AM)',
    'International transaction without KYC',
    'High amount compared to user average'
]

print("\nGenerating 20 fresh alerts...")

for i in range(1, 21):
    # Random timestamps in the last 2 hours
    minutes_ago = random.randint(1, 120)
    timestamp = datetime.utcnow() - timedelta(minutes=minutes_ago)
    
    # Random data
    customer = random.choice(customers)
    risk_score = random.uniform(0.45, 0.98)
    severity = random.choice(severities) if risk_score > 0.7 else random.choice(['MEDIUM', 'LOW'])
    amount = random.uniform(5000, 150000)
    triggered_rule = random.choice(rules)
    
    # Make transaction ID
    trans_id = f"T_{customer}_{int(timestamp.timestamp())}"
    
    cursor.execute('''
        INSERT INTO fraud_alerts (
            transaction_id, customer_id, alert_type, risk_score, severity, 
            alert_message, triggered_rules, created_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trans_id,
        customer,
        'RULE',  # Required field
        risk_score,
        severity,
        f"Fraud alert: {triggered_rule}",
        f'["{triggered_rule}"]',  # JSON array format
        timestamp.isoformat(),
        'NEW'
    ))

conn.commit()
print(f"✓ Generated 20 fresh alerts with timestamps from last 2 hours")

# Show sample
cursor.execute("SELECT alert_id, customer_id, risk_score, severity, created_at FROM fraud_alerts ORDER BY created_at DESC LIMIT 5")
print("\n📊 Latest 5 alerts:")
for row in cursor.fetchall():
    alert_id, cust, risk, sev, created = row
    print(f"  #{alert_id}: {cust} - {int(risk*100)}% {sev} - {created}")

conn.close()
print("\n✅ Done! Refresh the alerts page to see fresh timestamps")
