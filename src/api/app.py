"""
Flask API for Transaction Intelligence System
Provides RESTful endpoints for transaction data access, metrics, and fraud prediction.
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask.json.provider import DefaultJSONProvider
import pandas as pd
import numpy as np
import joblib
import json
import sys
from pathlib import Path
from datetime import datetime
import sqlite3

# Custom JSON provider to handle NaN values
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        # Convert numpy/pandas types to Python types
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            # Convert NaN/Inf to None (null in JSON)
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.db_connection import TransactionDB
from src.api.feedback_routes import feedback_bp

app = Flask(__name__)
app.json = CustomJSONProvider(app)

# Enable CORS for production (allow Netlify + localhost)
CORS(app, resources={r"/api/*": {
    "origins": "*"  # TODO: Update with actual Netlify URL after deployment
}})

# Register feedback routes blueprint
app.register_blueprint(feedback_bp)

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
    Unified fraud detection endpoint - Full Pipeline.
    
    Flow:
    1. Preprocess transaction & feature engineering
    2. ML model prediction
    3. Rule engine evaluation
    4. Risk explanation via LLM  
    5. Store fraud alert if applicable
    6. Return comprehensive response
    
    Request JSON:
    {
        "transaction_id": "T12345",
        "customer_id": "C123",
        "kyc_verified": 1,
        "account_age_days": 200,
        "transaction_amount": 5000,
        "channel": "Online",
        "timestamp": "2025-09-12 14:30"
    }
    
    Response:
    {
        "transaction_id": "T12345",
        "prediction": "Fraud",
        "risk_score": 0.92,
        "reason": "Human-readable explanation"
    }
    """
    try:
        # Import real-time components
        from src.realtime.realtime_predictor import get_predictor
        from src.realtime.rule_engine import get_rule_engine
        from src.realtime.explainer import generate_risk_explanation
        from src.realtime.alert_manager import get_alert_manager
        
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
        
        # Validate field types and ranges
        # Validate customer_id
        customer_id = data.get('customer_id')
        if not isinstance(customer_id, str) or len(customer_id) == 0 or len(customer_id) > 100:
            return jsonify({
                'success': False,
                'error': 'Invalid customer_id format. Must be non-empty string with max 100 characters.'
            }), 400
        
        # Validate transaction_amount
        try:
            amount = float(data['transaction_amount'])
            if amount < 0:
                return jsonify({
                    'success': False,
                    'error': 'Transaction amount must be positive'
                }), 400
            if amount > 10000000:  # $10M limit
                return jsonify({
                    'success': False,
                    'error': 'Transaction amount exceeds maximum allowed ($10,000,000)'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid transaction amount format. Must be a number.'
            }), 400
        
        # Validate optional fields if provided
        if 'kyc_verified' in data:
            if data['kyc_verified'] not in [0, 1, True, False]:
                return jsonify({
                    'success': False,
                    'error': 'kyc_verified must be 0/1 or true/false'
                }), 400
        
        if 'account_age_days' in data:
            try:
                age_days = float(data['account_age_days'])
                if age_days < 0 or age_days > 36500:  # 100 years max
                    return jsonify({
                        'success': False,
                        'error': 'account_age_days must be between 0 and 36500'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid account_age_days format. Must be a number.'
                }), 400
        
        if 'channel' in data:
            valid_channels = ['ATM', 'Mobile', 'Web', 'POS', 'International', 'Other']
            if data['channel'] not in valid_channels:
                # Try case-insensitive match
                channel_lower = data['channel'].lower() if isinstance(data['channel'], str) else ''
                if not any(channel_lower == vc.lower() for vc in valid_channels):
                    return jsonify({
                        'success': False,
                        'error': f'channel must be one of: {", ".join(valid_channels)}'
                    }), 400
        
        # Add transaction ID if not provided
        transaction_id = data.get('transaction_id', f"T_{data['customer_id']}_{int(datetime.now().timestamp())}")
        data['transaction_id'] = transaction_id
        
        # STEP 1 & 2: ML Model Prediction
        predictor = get_predictor()
        ml_prediction = predictor.predict(data)
        
        # STEP 3: Rule Engine Evaluation
        rule_engine = get_rule_engine()
        rule_evaluation = rule_engine.evaluate_transaction(data, ml_prediction)
        
        # Extract final decision
        final_prediction = rule_evaluation['final_prediction']
        final_risk_score = rule_evaluation['risk_score']
        triggered_rules = rule_evaluation['rules_triggered']
        
        # STEP 4: Generate Human-Readable Explanation
        try:
            explanation_payload = {
                'transaction_data': data,
                'risk_score': final_risk_score,
                'prediction': final_prediction,
                'triggered_rules': triggered_rules,
                'ml_risk_score': ml_prediction.get('risk_score', 0),
                'rule_risk_score': rule_evaluation.get('rule_risk_score', 0)
            }
            reason = generate_risk_explanation(explanation_payload)
        except Exception as e:
            # Fallback reason if explainer fails
            reason = f"Transaction flagged as {final_prediction.lower()} with risk score {final_risk_score:.1%}"
            print(f"Explanation generation failed: {e}")
        
        # STEP 5: Store Fraud Alert (only if fraud detected)
        alert_id = None
        if final_prediction == 'Fraud':
            try:
                alert_manager = get_alert_manager()
                alert_id = alert_manager.create_alert(
                    transaction_id=transaction_id,
                    customer_id=data['customer_id'],
                    risk_score=final_risk_score,
                    ml_prediction=ml_prediction,
                    rule_evaluation=rule_evaluation,
                    metadata={'timestamp': datetime.now().isoformat()}
                )
            except Exception as e:
                print(f"Alert creation failed: {e}")
        
        # STEP 6: Store Transaction in Database (for feedback system)
        print(f"\n[DEBUG] Attempting to store transaction: {transaction_id}")
        print(f"[DEBUG] Customer ID: {data['customer_id']}")
        print(f"[DEBUG] DB Path: {DB_PATH}")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            print("[DEBUG] Database connection established")
            
            # Store transaction with prediction
            # Note: Using 'timestamp' column name (not 'transaction_timestamp')
            cursor.execute('''
                INSERT INTO transactions (
                    transaction_id,
                    customer_id,
                    transaction_amount,
                    timestamp,
                    channel,
                    kyc_verified,
                    account_age_days,
                    is_fraud
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_id,
                data['customer_id'],
                data['transaction_amount'],
                data.get('timestamp', datetime.now().isoformat()),
                data.get('channel', 'Unknown'),
                int(data.get('kyc_verified', 0)),
                int(data.get('account_age_days', 0)),
                1 if final_prediction == 'Fraud' else 0
            ))
            
            print("[DEBUG] INSERT executed")
            
            conn.commit()
            print("[DEBUG] Committed to database")
            
            conn.close()
            print(f"✓ Transaction saved: {transaction_id}")
            
        except Exception as e:
            print(f"❌ ERROR storing transaction: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            # Don't fail the request if storage fails
        
        # STEP 7: Return Final Response
        response = {
            'success': True,
            'transaction_id': transaction_id,
            'prediction': final_prediction,
            'risk_score': round(final_risk_score, 4),
            'reason': reason,
            'details': {
                'ml_risk_score': round(ml_prediction.get('risk_score', 0), 4),
                'rule_risk_score': round(rule_evaluation.get('rule_risk_score', 0), 4),
                'triggered_rules': triggered_rules,
                'rules_count': len(triggered_rules),
                'alert_id': alert_id
            }
        }
        
        # Clean response to remove any NaN values
        def clean_nan(obj):
            """Recursively clean NaN values from nested dict/list"""
            if isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(item) for item in obj]
            elif isinstance(obj, float):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return obj
            elif isinstance(obj, (np.integer, np.floating)):
                val = float(obj) if isinstance(obj, np.floating) else int(obj)
                if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
                    return None
                return val
            return obj
        
        response = clean_nan(response)
        
        return jsonify(response)
    
    except ValueError as e:
        # Validation errors - safe to expose
        logger.warning(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR',
            'transaction_id': data.get('transaction_id') if data else None
        }), 400
    except Exception as e:
        # Internal errors - don't expose details
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An internal error occurred processing the transaction. Please try again.',
            'error_code': 'PREDICTION_ERROR',
            'transaction_id': data.get('transaction_id') if data else None
        }), 500



@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """
    Get fraud alerts from database.
    
    Query params:
        - limit: number of alerts to return (default: 50, max: 500)
        - severity: filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
        - status: filter by status (NEW, INVESTIGATING, RESOLVED, etc.)
    """
    try:
        from src.realtime.alert_manager import get_alert_manager
        
        limit = min(int(request.args.get('limit', 50)), 500)
        severity = request.args.get('severity')
        status = request.args.get('status')
        
        alert_manager = get_alert_manager()
        alerts = alert_manager.get_alerts(
            severity=severity,
            status=status,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
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
            
            # Replace NaN values with None before converting to dict
            df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
            
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
        
        # Replace NaN values with None before converting to dict
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        
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


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Mock authentication endpoint for demo/testing.
    
    Request JSON:
    {
        "username": "admin",
        "password": "admin123"
    }
    
    Response:
    {
        "success": true,
        "token": "mock_jwt_token_...",
        "user": {
            "username": "admin",
            "role": "admin"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Mock credentials (hardcoded for demo)
        MOCK_USERS = {
            'admin': {'password': 'admin123', 'role': 'admin'},
            'analyst': {'password': 'analyst123', 'role': 'analyst'},
            'viewer': {'password': 'viewer123', 'role': 'viewer'}
        }
        
        # Validate username and password
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        # Check credentials
        if username not in MOCK_USERS:
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        if MOCK_USERS[username]['password'] != password:
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        # Generate mock token (in production, use JWT)
        import hashlib
        import time
        token_string = f"{username}:{time.time()}:secret"
        mock_token = hashlib.sha256(token_string.encode()).hexdigest()
        
        # Successful login
        return jsonify({
            'success': True,
            'token': f"Bearer {mock_token}",
            'user': {
                'username': username,
                'role': MOCK_USERS[username]['role']
            },
            'message': 'Login successful'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Login failed. Please try again.'
        }), 500


@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Get dashboard statistics (alias for /api/metrics).
    
    Returns:
        - total_transactions: total number of transactions
        - fraud_count: number of fraudulent transactions
        - legit_count: number of legitimate transactions
        - fraud_percentage: percentage of fraudulent transactions
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
            
            # Calculate legit count and fraud percentage
            legit_count = total_transactions - fraud_count
            fraud_percentage = (fraud_count / total_transactions * 100) if total_transactions > 0 else 0
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_transactions': total_transactions,
                    'fraud_count': fraud_count,
                    'legit_count': legit_count,
                    'fraud_percentage': round(fraud_percentage, 2)
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
            'POST /api/predict': 'Predict fraud for a transaction (ML + Rules + LLM)',
            'POST /api/auth/login': 'Mock authentication (username: admin, password: admin123)',
            'GET /api/alerts': 'Get fraud alerts (params: limit, severity, status)',
            'GET /api/metrics': 'Get transaction statistics',
            'GET /api/dashboard/stats': 'Get dashboard statistics (total, fraud, legit counts)',
            'GET /api/model/metrics': 'Get model performance metrics (accuracy, precision, recall, F1, AUC)',
            'GET /api/transactions': 'Get paginated transactions (params: limit, offset)',
            'GET /api/transactions/sample': 'Get sample transactions preview',
            'GET /api/predictions/history': 'Get prediction history',
            'GET /api/download/processed': 'Download full processed CSV',
            'GET /api/health': 'Health check endpoint'
        },
        'mock_credentials': {
            'admin': 'admin123',
            'analyst': 'analyst123',
            'viewer': 'viewer123'
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
