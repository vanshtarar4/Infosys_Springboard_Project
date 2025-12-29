"""
A/B Testing Framework
Phase 4 of Continuous Learning System

Manage experiments comparing model versions in production.
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Literal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ABExperiment:
    """Manage A/B tests between two model versions."""
    
    def __init__(
        self,
        experiment_name: str,
        control_model_path: str,
        treatment_model_path: str,
        split_ratio: float = 0.5,
        db_path: str = 'data/experiments.db'
    ):
        self.experiment_name = experiment_name
        self.control_model_path = control_model_path
        self.treatment_model_path = treatment_model_path
        self.split_ratio = split_ratio  # Fraction assigned to treatment
        self.db_path = db_path
        
        self._create_experiment_tables()
    
    def _create_experiment_tables(self):
        """Create tables for tracking experiments."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_name TEXT UNIQUE,
                control_model TEXT,
                treatment_model TEXT,
                split_ratio REAL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_name TEXT,
                customer_id TEXT,
                variant TEXT,
                prediction TEXT,
                risk_score REAL,
                actual_outcome TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def assign_variant(self, customer_id: str) -> Literal['control', 'treatment']:
        """
        Consistently assign customer to variant based on hash.
        Same customer always gets same variant.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            'control' or 'treatment'
        """
        # Hash customer ID to get consistent assignment
        hash_val = int(hashlib.md5(customer_id.encode()).hexdigest(), 16)
        percentile = (hash_val % 100) / 100.0
        
        return 'treatment' if percentile < self.split_ratio else 'control'
    
    def log_prediction(
        self, 
        customer_id: str,
        variant: str,
        prediction: str,
        risk_score: float
    ):
        """
        Log prediction for analysis.
        
        Args:
            customer_id: Customer ID
            variant: 'control' or 'treatment'
            prediction: Model prediction
            risk_score: Risk score
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO experiment_results (
                experiment_name, customer_id, variant, prediction, risk_score
            ) VALUES (?, ?, ?, ?, ?)
        ''', (self.experiment_name, customer_id, variant, prediction, risk_score))
        
        conn.commit()
        conn.close()
    
    def get_results(self) -> Dict:
        """
        Analyze experiment results.
        
        Returns:
            Dictionary with performance metrics for each variant
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get counts by variant
        cursor.execute('''
            SELECT variant, COUNT(*), 
                   AVG(risk_score),
                   SUM(CASE WHEN prediction = 'Fraud' THEN 1 ELSE 0 END)
            FROM experiment_results
            WHERE experiment_name = ?
            GROUP BY variant
        ''', (self.experiment_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {}
        for variant, count, avg_risk, fraud_count in results:
            stats[variant] = {
                'total_predictions': count,
                'avg_risk_score': avg_risk,
                'fraud_predictions': fraud_count,
                'fraud_rate': fraud_count / count if count > 0 else 0
            }
        
        return stats


class ExperimentManager:
    """Manage multiple A/B experiments."""
    
    def __init__(self, db_path: str = 'data/experiments.db'):
        self.db_path = db_path
        self.active_experiments = {}
    
    def create_experiment(
        self,
        name: str,
        control_model: str,
        treatment_model: str,
        split_ratio: float = 0.5
    ) -> ABExperiment:
        """Create and track new experiment."""
        experiment = ABExperiment(
            experiment_name=name,
            control_model_path=control_model,
            treatment_model_path=treatment_model,
            split_ratio=split_ratio,
            db_path=self.db_path
        )
        
        self.active_experiments[name] = experiment
        logger.info(f"✓ Created experiment '{name}'")
        
        return experiment
    
    def end_experiment(self, name: str, winner: Literal['control', 'treatment']):
        """Mark experiment as complete."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE experiments
            SET ended_at = CURRENT_TIMESTAMP, status = 'completed'
            WHERE experiment_name = ?
        ''', (name,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Ended experiment '{name}' - Winner: {winner}")
        
        if name in self.active_experiments:
            del self.active_experiments[name]
