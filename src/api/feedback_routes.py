"""
Feedback API Routes
Handles user feedback collection for continuous learning.
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__)

DB_PATH = 'data/transactions.db'


@feedback_bp.route('/api/feedback', methods=['POST', 'OPTIONS'])
def submit_feedback():
    """
    Submit user feedback on a fraud prediction.
    
    Request body:
    {
        "transaction_id": "T_123_456",
        "actual_label": "Fraud" | "Legitimate",
        "notes": "optional user notes"
    }
    
    Returns:
        JSON with success status and feedback_id
    """
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        logger.info("Feedback submission request received")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        # Validate required fields
        if not data:
            logger.error("No JSON data in request")
            return jsonify({'error': 'No data provided'}), 400
            
        if not data.get('transaction_id'):
            logger.error("Missing transaction_id")
            return jsonify({'error': 'transaction_id required'}), 400
        
        if data.get('actual_label') not in ['Fraud', 'Legitimate']:
            logger.error(f"Invalid actual_label: {data.get('actual_label')}")
            return jsonify({'error': 'actual_label must be "Fraud" or "Legitimate"'}), 400
        
        # Get transaction details for context
        logger.info(f"Looking up transaction: {data['transaction_id']}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, transaction_amount, is_fraud 
            FROM transactions 
            WHERE transaction_id = ?
        ''', (data['transaction_id'],))
        
        transaction = cursor.fetchone()
        
        if not transaction:
            logger.error(f"Transaction not found: {data['transaction_id']}")
            conn.close()
            return jsonify({'error': 'Transaction not found'}), 404
        
        user_id = transaction[0]
        predicted_label = 'Fraud' if transaction[2] == 1 else 'Legitimate'
        
        logger.info(f"Transaction found - User: {user_id}, Predicted: {predicted_label}")
        
        # Insert feedback
        cursor.execute('''
            INSERT INTO transaction_feedback (
                transaction_id,
                customer_id,
                predicted_label,
                actual_label,
                notes,
                feedback_source
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['transaction_id'],
            customer_id,
            predicted_label,
            data['actual_label'],
            data.get('notes', ''),
            data.get('feedback_source', 'user')
        ))
        
        feedback_id = cursor.lastrowid
        logger.info(f"Feedback inserted with ID: {feedback_id}")
        
        # Update transaction with feedback
        cursor.execute('''
            UPDATE transactions 
            SET feedback_confirmed = 1,
                confirmed_label = ?,
                feedback_timestamp = CURRENT_TIMESTAMP
            WHERE transaction_id = ?
        ''', (data['actual_label'], data['transaction_id']))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Feedback recorded: {data['transaction_id']} → {data['actual_label']}")
        
        response_data = {
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback recorded successfully'
        }
        logger.info(f"Sending response: {response_data}")
        
        return jsonify(response_data), 201
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error submitting feedback: {e}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@feedback_bp.route('/api/feedback/stats', methods=['GET'])
def feedback_stats():
    """
    Get feedback collection statistics.
    
    Returns:
        JSON with feedback metrics
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total feedback count
        cursor.execute('SELECT COUNT(*) FROM transaction_feedback')
        total_feedback = cursor.fetchone()[0]
        
        # Feedback by label
        cursor.execute('''
            SELECT actual_label, COUNT(*) 
            FROM transaction_feedback 
            GROUP BY actual_label
        ''')
        by_label = dict(cursor.fetchall())
        
        # Accuracy (predictions that matched feedback)
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN predicted_label = actual_label THEN 1 ELSE 0 END) as correct
            FROM transaction_feedback
        ''')
        accuracy_data = cursor.fetchone()
        accuracy = (accuracy_data[1] / accuracy_data[0] * 100) if accuracy_data[0] > 0 else 0
        
        # Recent feedback (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM transaction_feedback 
            WHERE feedback_timestamp >= datetime('now', '-7 days')
        ''')
        recent_count = cursor.fetchone()[0]
        
        # Labeled data ready for training
        cursor.execute('''
            SELECT COUNT(*) 
            FROM transactions 
            WHERE feedback_confirmed = 1
        ''')
        training_ready = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_feedback': total_feedback,
            'by_label': by_label,
            'model_accuracy': round(accuracy, 2),
            'recent_7days': recent_count,
            'training_ready': training_ready,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        return jsonify({'error': str(e)}), 500


@feedback_bp.route('/api/feedback/recent', methods=['GET'])
def recent_feedback():
    """
    Get recent feedback submissions.
    
    Query params:
        limit: Number of results (default 10)
    
    Returns:
        JSON array of recent feedback
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                f.feedback_id,
                f.transaction_id,
                f.customer_id,
                f.predicted_label,
                f.actual_label,
                f.feedback_timestamp,
                f.notes,
                t.transaction_amount
            FROM transaction_feedback f
            LEFT JOIN transactions t ON f.transaction_id = t.transaction_id
            ORDER BY f.feedback_timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        feedback_list = []
        for row in results:
            feedback_list.append({
                'feedback_id': row[0],
                'transaction_id': row[1],
                'customer_id': row[2],
                'predicted': row[3],
                'actual': row[4],
                'timestamp': row[5],
                'notes': row[6],
                'amount': row[7],
                'correct': row[3] == row[4]
            })
        
        return jsonify({
            'feedback': feedback_list,
            'count': len(feedback_list)
        })
        
    except Exception as e:
        logger.error(f"Error getting recent feedback: {e}")
        return jsonify({'error': str(e)}), 500
