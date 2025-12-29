"""
Optimize Fraud Detection Threshold
Finds the optimal decision threshold that maximizes F1-score.
Balances precision and recall for minimal false positives.
"""

import numpy as np
from sklearn.metrics import precision_recall_curve, f1_score
import joblib
import json
from pathlib import Path

def find_optimal_threshold(model, X_test, y_test):
    """
    Find threshold that maximizes F1-score.
    
    Args:
        model: Trained model with predict_proba method
        X_test: Test features
        y_test: Test labels
        
    Returns:
        Dictionary with optimal threshold and metrics
    """
    
    # Get probability predictions
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Compute precision-recall curve
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_prob)
    
    # Calculate F1 scores for each threshold
    f1_scores = 2 * (precisions[:-1] * recalls[:-1]) / (precisions[:-1] + recalls[:-1] + 1e-10)
    
    # Find threshold with best F1
    optimal_idx = np.argmax(f1_scores)
    optimal_threshold = thresholds[optimal_idx]
    
    # Get metrics at optimal threshold
    y_pred_optimal = (y_prob >= optimal_threshold).astype(int)
    
    print(f"\n{'='*80}")
    print("THRESHOLD OPTIMIZATION RESULTS")
    print(f"{'='*80}")
    print(f"Optimal Threshold: {optimal_threshold:.4f}")
    print(f"Precision: {precisions[optimal_idx]:.4f}")
    print(f"Recall: {recalls[optimal_idx]:.4f}")
    print(f"F1-Score: {f1_scores[optimal_idx]:.4f}")
    print(f"{'='*80}\n")
    
    return {
        'threshold': float(optimal_threshold),
        'precision': float(precisions[optimal_idx]),
        'recall': float(recalls[optimal_idx]),
        'f1_score': float(f1_scores[optimal_idx])
    }


def main():
    """Main threshold optimization pipeline."""
    
    print(f"\n{'='*80}")
    print("FRAUD DETECTION - THRESHOLD OPTIMIZATION")
    print(f"{'='*80}\n")
    
    # Load model
    print("Loading trained model...")
    model = joblib.load('models/best_model.pkl')
    print("✓ Model loaded\n")
    
    # Load test data
    print("Loading test data...")
    X_test = np.load('models/X_test.npy')
    y_test = np.load('models/y_test.npy')
    print(f"✓ Test data loaded: {X_test.shape[0]} samples\n")
    
    # Find optimal threshold
    result = find_optimal_threshold(model, X_test, y_test)
    
    # Read model name if it exists
    model_name_file = Path('models/model_name.txt')
    if model_name_file.exists():
        with open(model_name_file, 'r') as f:
            model_name = f.read().strip()
    else:
        model_name = "Optimized Model"
    
    # Save optimized threshold
    threshold_config = {
        'selected_threshold': round(result['threshold'], 2),
        'model_name': f"{model_name} (Optimized)",
        'precision': round(result['precision'], 2),
        'recall': round(result['recall'], 2),
        'f1_score': round(result['f1_score'], 2),
        'note': 'Threshold optimized to maximize F1-score'
    }
    
    output_path = 'configs/model_threshold.json'
    with open(output_path, 'w') as f:
        json.dump(threshold_config, f, indent=2)
    
    print(f"✓ Saved optimized threshold to {output_path}")
    print(f"\n{'='*80}")
    print("✅ OPTIMIZATION COMPLETE")
    print(f"{'='*80}\n")
    
    return result


if __name__ == '__main__':
    result = main()
