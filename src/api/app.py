"""
Flask API for Transaction Intelligence System
Provides RESTful endpoints for transaction data access, metrics, and fraud prediction.
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import json
import sys
from pathlib import Path
from datetime import datetime
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.db_connection import TransactionDB

app = Flask(__name__)

# Enable CORS for development (wide-open)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
DB_PATH = 'data/transactions.db'
PROCESSED_CSV = 'data/processed/transactions_processed.csv'
PREVIEW_CSV = 'data/processed/transactions_preview.csv'
MODEL_PATH = 'models/best_model.joblib'
SCALER_PATH = 'models/scaler.joblib'
ENCODER_PATH = 'models/encoder.joblib'
THRESHOLD_PATH = 'configs/model_threshold.json'

# Load model and preprocessing artifacts on startup
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    encoder = joblib.load(ENCODER_PATH)
    
    with open(THRESHOLD_PATH, 'r') as f:
        threshold_config = json.load(f)
        FRAUD_THRESHOLD = threshold_config.get('selected_threshold', 0.5)
    
    print(f"✓ Model loaded successfully")
    print(f"✓ Fraud threshold: {FRAUD_THRESHOLD}")
    MODEL_LOADED = True
except Exception as e:
    print(f"⚠ Warning: Could not load model - {e}")
    print("Prediction endpoint will not be available")
    MODEL_LOADED = False


def create_predictions_table():
    """Create model_predictions table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_predictions (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            transaction_amount REAL,
            channel TEXT,
            timestamp TEXT,
            prediction TEXT,
            risk_score REAL,
            threshold_used REAL,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


# Create predictions table on startup
try:
    create_predictions_table()
    print("✓ Predictions table ready")
except Exception as e:
    print(f"⚠ Warning: Could not create predictions table - {e}")


def preprocess_transaction(transaction_data):
    """
    Preprocess single transaction for prediction.
    
    Args:
        transaction_data: Dict with transaction details
    
    Returns:
        Preprocessed feature array
    """
    # Extract timestamp features
    timestamp = pd.to_datetime(transaction_data.get('timestamp', datetime.now()))
    
    # Build numeric features
    numeric_features = np.array([[
        transaction_data.get('kyc_verified', 0),
        transaction_data.get('account_age_days', 0),
        transaction_data.get('transaction_amount', 0),
        np.log1p(transaction_data.get('transaction_amount', 0)),  # amount_log
        timestamp.hour,
        timestamp.weekday(),
        1 if transaction_data.get('transaction_amount', 0) > 50000 else 0  # is_high_value
    ]])
    
    # Scale numeric features
    numeric_scaled = scaler.transform(numeric_features)
    
    # Encode categorical (channel)
    channel = transaction_data.get('channel', 'Other')
    # Map common variations
    channel_map = {
        'online': 'Web',
        'web': 'Web',
        'mobile': 'Mobile',
        'app': 'Mobile',
        'pos': 'POS',
        'atm': 'ATM'
    }
    channel = channel_map.get(channel.lower(), channel.title())
    
    categorical_encoded = encoder.transform([[channel]])
    
    # Combine features
    features = np.hstack([numeric_scaled, categorical_encoded])
    
    return features


def log_prediction(customer_id, transaction_data, prediction, risk_score):
    """Log prediction to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_predictions 
            (customer_id, transaction_amount, channel, timestamp, prediction, risk_score, threshold_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_id,
            transaction_data.get('transaction_amount'),
            transaction_data.get('channel'),
            transaction_data.get('timestamp'),
            prediction,
            risk_score,
            FRAUD_THRESHOLD
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging prediction: {e}")
        return False


@app.route('/api/predict', methods=['POST'])
def predict_fraud():
    """
    Predict fraud for a single transaction.
    
    Request JSON:
    {
        "customer_id": "C123",
        "kyc_verified": 1,
        "account_age_days": 200,
        "transaction_amount": 5000,
        "channel": "Online",
        "timestamp": "2025-09-12 14:30"
    }
    
    Response:
    {
        "success": true,
        "prediction": "Fraud" or "Legitimate",
        "risk_score": 0.87,
        "threshold": 0.3
    }
    """
    if not MODEL_LOADED:
        return jsonify({
            'success': False,
            'error': 'Prediction model not available'
        }), 503
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['customer_id', 'transaction_amount']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Preprocess transaction
        features = preprocess_transaction(data)
        
        # Predict
        risk_score = float(model.predict_proba(features)[0, 1])
        prediction = "Fraud" if risk_score >= FRAUD_THRESHOLD else "Legitimate"
        
        # Log prediction
        log_prediction(data['customer_id'], data, prediction, risk_score)
        
        # Return response
        return jsonify({
            'success': True,
            'prediction': prediction,
            'risk_score': round(risk_score, 4),
            'threshold': FRAUD_THRESHOLD,
            'customer_id': data['customer_id'],
            'confidence': round(risk_score if prediction == "Fraud" else (1 - risk_score), 4)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/predictions/history', methods=['GET'])
def get_prediction_history():
    """Get prediction history from database."""
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prediction_id, customer_id, transaction_amount, channel, 
                   timestamp, prediction, risk_score, threshold_used, predicted_at
            FROM model_predictions
            ORDER BY predicted_at DESC
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        predictions = [dict(zip(columns, row)) for row in rows]
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/model/metrics', methods=['GET'])
def get_model_metrics():
    """
    Get model performance metrics.
    
    Returns:
        JSON with model performance metrics (accuracy, precision, recall, F1, ROC-AUC)
    """
    try:
        with open('configs/model_metrics.json', 'r') as f:
            metrics_data = json.load(f)
        
        # Extract key metrics for frontend
        metrics = {
            'accuracy': round(metrics_data.get('accuracy', 0), 4),
            'precision': round(metrics_data.get('precision', 0), 4),
            'recall': round(metrics_data.get('recall', 0), 4),
            'f1_score': round(metrics_data.get('f1_score', 0), 4),
            'roc_auc': round(metrics_data.get('roc_auc', 0), 4),
            'model_name': metrics_data.get('model_name', 'Unknown'),
            'threshold': metrics_data.get('threshold', 0.5),
            'test_samples': metrics_data.get('test_samples', 0)
        }
        
        # Add fraud detection specific metrics if available
        if 'fraud_detection' in metrics_data:
            fd = metrics_data['fraud_detection']
            metrics['fraud_detection'] = {
                'detection_rate': round(fd.get('detection_rate', 0), 4),
                'frauds_detected': fd.get('frauds_detected', 0),
                'frauds_missed': fd.get('frauds_missed', 0),
                'total_fraud_cases': fd.get('total_fraud_cases', 0)
            }
        
        # Add confusion matrix if available
        if 'confusion_matrix' in metrics_data:
            metrics['confusion_matrix'] = metrics_data['confusion_matrix']
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Model metrics not found. Please run model evaluation first.'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """
    Get latest N transactions from database.
    Query params:
        - limit: number of records to return (default: 100, max: 1000)
        - offset: number of records to skip (default: 0)
    """
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        
        with TransactionDB(DB_PATH) as db:
            query = f"""
                SELECT * FROM transactions 
                ORDER BY timestamp DESC 
                LIMIT {limit} OFFSET {offset}
            """
            df = db.query_transactions(query)
            
            # Get total count for pagination
            total_count = db.get_row_count()
            
            # Convert to JSON-friendly format
            transactions = df.to_dict(orient='records')
            
            return jsonify({
                'success': True,
                'data': transactions,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'total': total_count,
                    'returned': len(transactions)
                }
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/transactions/sample', methods=['GET'])
def get_sample_transactions():
    """
    Get sample transactions from preview CSV.
    Returns first 500 rows from transactions_preview.csv
    """
    try:
        df = pd.read_csv(PREVIEW_CSV)
        transactions = df.to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'data': transactions,
            'count': len(transactions)
        })
    
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Preview file not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Get overall transaction metrics and statistics.
    Returns:
        - total_transactions: total number of transactions
        - fraud_count: number of fraudulent transactions
        - fraud_rate: percentage of fraudulent transactions
        - avg_amount: average transaction amount (all)
        - avg_amount_fraud: average amount for fraudulent transactions
        - avg_amount_legit: average amount for legitimate transactions
    """
    try:
        with TransactionDB(DB_PATH) as db:
            # Total transactions
            total_query = "SELECT COUNT(*) as total FROM transactions"
            total_result = db.query_transactions(total_query)
            total_transactions = int(total_result.iloc[0]['total'])
            
            # Fraud count
            fraud_query = "SELECT COUNT(*) as fraud_count FROM transactions WHERE is_fraud = 1"
            fraud_result = db.query_transactions(fraud_query)
            fraud_count = int(fraud_result.iloc[0]['fraud_count'])
            
            # Calculate fraud rate
            fraud_rate = (fraud_count / total_transactions * 100) if total_transactions > 0 else 0
            
            # Average amounts
            avg_query = """
                SELECT 
                    AVG(transaction_amount) as avg_all,
                    AVG(CASE WHEN is_fraud = 1 THEN transaction_amount END) as avg_fraud,
                    AVG(CASE WHEN is_fraud = 0 THEN transaction_amount END) as avg_legit
                FROM transactions
            """
            avg_result = db.query_transactions(avg_query)
            
            avg_amount = float(avg_result.iloc[0]['avg_all']) if avg_result.iloc[0]['avg_all'] else 0
            avg_amount_fraud = float(avg_result.iloc[0]['avg_fraud']) if avg_result.iloc[0]['avg_fraud'] else 0
            avg_amount_legit = float(avg_result.iloc[0]['avg_legit']) if avg_result.iloc[0]['avg_legit'] else 0
            
            return jsonify({
                'success': True,
                'metrics': {
                    'total_transactions': total_transactions,
                    'fraud_count': fraud_count,
                    'fraud_rate': round(fraud_rate, 2),
                    'avg_amount': round(avg_amount, 2),
                    'avg_amount_fraud': round(avg_amount_fraud, 2),
                    'avg_amount_legit': round(avg_amount_legit, 2)
                }
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/processed', methods=['GET'])
def download_processed():
    """
    Download the full processed transactions CSV file.
    """
    try:
        return send_file(
            PROCESSED_CSV,
            mimetype='text/csv',
            as_attachment=True,
            download_name='transactions_processed.csv'
        )
    
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Processed file not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'Transaction Intelligence API'
    })


@app.route('/', methods=['GET'])
def index():
    """
    API documentation root.
    """
    return jsonify({
        'service': 'Transaction Intelligence API',
        'version': '2.0.0',
        'endpoints': {
            'GET /api/transactions': 'Get paginated transactions (params: limit, offset)',
            'GET /api/transactions/sample': 'Get sample transactions preview',
            'GET /api/metrics': 'Get transaction metrics and statistics',
            'GET /api/model/metrics': 'Get model performance metrics',
            'GET /api/download/processed': 'Download full processed CSV',
            'POST /api/predict': 'Predict fraud for a transaction',
            'GET /api/predictions/history': 'Get prediction history',
            'GET /api/health': 'Health check endpoint'
        }
    })


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Transaction Intelligence API')
    parser.add_argument('--port', type=int, default=8001, help='Port to run the API on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Transaction Intelligence API")
    print("=" * 60)
    print(f"Starting server on http://{args.host}:{args.port}")
    print(f"Debug mode: {args.debug}")
    print("\nAvailable endpoints:")
    print("  GET  /api/transactions")
    print("  GET  /api/transactions/sample")
    print("  GET  /api/metrics")
    print("  GET  /api/download/processed")
    print("  GET  /api/health")
    print("=" * 60)
    
    app.run(host=args.host, port=args.port, debug=args.debug)
