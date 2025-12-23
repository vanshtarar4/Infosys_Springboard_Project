"""
Threshold Optimization for Fraud Detection
Adjusts probability threshold to maximize recall.
"""

import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

def load_model_and_data():
    """Load best model and test data."""
    print("Loading model and test data...")
    
    model = joblib.load('models/best_model.joblib')
    X_test = np.load('models/X_test.npy')
    y_test = np.load('models/y_test.npy')
    
    with open('models/model_name.txt', 'r') as f:
        model_name = f.read().strip()
    
    print(f"✓ Model loaded: {model_name}")
    print(f"✓ Test samples: {len(y_test)}")
    print(f"✓ Test fraud rate: {y_test.mean()*100:.2f}%")
    
    return model, X_test, y_test, model_name


def evaluate_at_threshold(y_true, y_prob, threshold):
    """Evaluate metrics at a specific threshold."""
    y_pred = (y_prob >= threshold).astype(int)
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    return {
        'threshold': threshold,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'true_positives': int(tp),
        'false_positives': int(fp),
        'true_negatives': int(tn),
        'false_negatives': int(fn),
        'total_frauds': int(y_true.sum()),
        'frauds_caught': int(tp),
        'frauds_missed': int(fn)
    }


def print_threshold_table(results):
    """Print formatted threshold comparison table."""
    print("\n" + "="*100)
    print("THRESHOLD OPTIMIZATION - RECALL MAXIMIZATION")
    print("="*100)
    
    df = pd.DataFrame(results)
    
    print(f"\n{'Threshold':>10} {'Precision':>12} {'Recall':>12} {'F1-Score':>12} {'Frauds Caught':>15} {'Frauds Missed':>15}")
    print("-"*100)
    
    for _, row in df.iterrows():
        fraud_pct = (row['frauds_caught'] / row['total_frauds'] * 100) if row['total_frauds'] > 0 else 0
        print(f"{row['threshold']:>10.2f} {row['precision']:>12.4f} {row['recall']:>12.4f} {row['f1_score']:>12.4f} "
              f"{row['frauds_caught']:>7d} ({fraud_pct:>5.1f}%) {row['frauds_missed']:>7d}")
    
    print("-"*100)
    
    # Select best threshold
    # Maximize recall, but ensure F1 doesn't drop below 0.20 (reasonable threshold)
    viable = df[df['f1_score'] >= 0.20]
    
    if len(viable) == 0:
        # If all F1s are below 0.20, just pick highest recall
        best = df.loc[df['recall'].idxmax()]
        print("\n⚠️  Warning: All F1 scores below 0.20, selecting highest recall anyway")
    else:
        # Among viable options, pick highest recall
        best = viable.loc[viable['recall'].idxmax()]
    
    print(f"\n🎯 SELECTED THRESHOLD: {best['threshold']:.2f}")
    print(f"   ├─ Recall: {best['recall']:.4f} ({best['frauds_caught']}/{best['total_frauds']} frauds caught) ⭐")
    print(f"   ├─ Precision: {best['precision']:.4f}")
    print(f"   ├─ F1-Score: {best['f1_score']:.4f}")
    print(f"   ├─ Frauds Missed: {best['frauds_missed']} ⚠️")
    print(f"   └─ False Alarms: {best['false_positives']}")
    
    print("\n📊 Confusion Matrix at Selected Threshold:")
    print(f"                 Predicted")
    print(f"                Legit  Fraud")
    print(f"Actual Legit    {best['true_negatives']:5d}  {best['false_positives']:5d}")
    print(f"       Fraud    {best['false_negatives']:5d}  {best['true_positives']:5d}")
    
    print("="*100)
    
    return best, df


def main():
    """Main threshold optimization pipeline."""
    print("\n" + "="*100)
    print("FRAUD DETECTION - THRESHOLD OPTIMIZATION")
    print("="*100)
    
    # Load model and data
    model, X_test, y_test, model_name = load_model_and_data()
    
    # Get probability predictions
    print("\nGenerating probability predictions...")
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Test different thresholds
    thresholds = [0.5, 0.4, 0.3, 0.25]
    
    print(f"\nEvaluating at thresholds: {thresholds}")
    print(f"Total fraud cases in test set: {y_test.sum()}")
    
    results = []
    for threshold in thresholds:
        metrics = evaluate_at_threshold(y_test, y_prob, threshold)
        results.append(metrics)
    
    # Print comparison table and select best
    best_config, comparison_df = print_threshold_table(results)
    
    # Save threshold configuration
    output_dir = Path('configs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*100)
    print("SAVING THRESHOLD CONFIGURATION")
    print("="*100)
    
    threshold_config = {
        'selected_threshold': float(best_config['threshold']),
        'model_name': model_name,
        'recall': float(best_config['recall']),
        'precision': float(best_config['precision']),
        'f1_score': float(best_config['f1_score']),
        'frauds_caught': int(best_config['frauds_caught']),
        'frauds_missed': int(best_config['frauds_missed']),
        'total_frauds': int(best_config['total_frauds']),
        'false_positives': int(best_config['false_positives']),
        'note': 'Threshold optimized for maximum recall in fraud detection'
    }
    
    config_path = output_dir / 'model_threshold.json'
    with open(config_path, 'w') as f:
        json.dump(threshold_config, f, indent=2)
    
    print(f"✓ Saved threshold configuration to {config_path}")
    
    # Save comparison table
    comparison_path = output_dir / 'threshold_comparison.csv'
    comparison_df.to_csv(comparison_path, index=False)
    print(f"✓ Saved threshold comparison to {comparison_path}")
    
    # Also save all threshold results as JSON
    results_path = output_dir / 'threshold_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Saved detailed results to {results_path}")
    
    print("\n" + "="*100)
    print("✅ THRESHOLD OPTIMIZATION COMPLETE")
    print("="*100)
    print(f"Selected Threshold: {best_config['threshold']:.2f}")
    print(f"Expected Recall: {best_config['recall']:.2%}")
    print(f"Expected Precision: {best_config['precision']:.2%}")
    print("="*100)
    
    return best_config['threshold'], results


if __name__ == '__main__':
    threshold, results = main()
