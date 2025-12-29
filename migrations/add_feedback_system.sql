-- Feedback Collection Schema
-- Phase 1 of Continuous Learning System

-- Table to store user feedback on predictions
CREATE TABLE IF NOT EXISTS transaction_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    customer_id TEXT,
    predicted_label TEXT NOT NULL,        -- What model predicted: 'Fraud' or 'Legitimate'
    actual_label TEXT NOT NULL,           -- What user confirmed: 'Fraud' or 'Legitimate'
    ml_confidence REAL,                   -- Model's confidence score (0-1)
    rule_risk_score REAL,                 -- Rule engine score
    rules_triggered TEXT,                 -- JSON array of triggered rules
    feedback_source TEXT DEFAULT 'user',  -- 'user', 'automated', 'analyst'
    feedback_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,                           -- Optional user notes
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON transaction_feedback(feedback_timestamp);
CREATE INDEX IF NOT EXISTS idx_feedback_customer ON transaction_feedback(customer_id);
CREATE INDEX IF NOT EXISTS idx_feedback_label ON transaction_feedback(actual_label);

-- Add feedback tracking columns to transactions table
ALTER TABLE transactions ADD COLUMN feedback_confirmed INTEGER DEFAULT 0;
ALTER TABLE transactions ADD COLUMN confirmed_label TEXT;
ALTER TABLE transactions ADD COLUMN feedback_timestamp DATETIME;

-- View for labeled training data
CREATE VIEW IF NOT EXISTS labeled_training_data AS
SELECT 
    t.*,
    f.actual_label as true_label,
    f.feedback_timestamp,
    CASE 
        WHEN f.actual_label = 'Fraud' THEN 1
        ELSE 0
    END as is_fraud_confirmed
FROM transactions t
INNER JOIN transaction_feedback f ON t.transaction_id = f.transaction_id
WHERE f.feedback_confirmed = 1;
