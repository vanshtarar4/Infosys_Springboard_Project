"""
Model Evaluation Module
Comprehensive evaluation with metrics and visualizations.
"""

import numpy as np
import pandas as pd
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model_and_threshold():
    """Load trained model and threshold configuration."""
    logger.info("Loading model and threshold...")
    
    # Load model
    model = joblib.load('models/best_model.joblib')
    
    # Load threshold
    with open('configs/model_threshold.json', 'r') as f:
        threshold_config = json.load(f)
    
    threshold = threshold_config.get('selected_threshold', 0.5)
    model_name = threshold_config.get('model_name', 'Unknown')
    
    logger.info(f"✓ Model: {model_name}")
    logger.info(f"✓ Threshold: {threshold}")
    
    return model, threshold, model_name


def load_test_data():
    """Load test data."""
    logger.info("Loading test data...")
    
    X_test = np.load('models/X_test.npy')
    y_test = np.load('models/y_test.npy')
    
    logger.info(f"✓ Test samples: {len(y_test)}")
    logger.info(f"✓ Test fraud rate: {y_test.mean()*100:.2f}%")
    
    return X_test, y_test


def compute_metrics(y_true, y_pred, y_prob):
    """Compute all evaluation metrics."""
    logger.info("Computing metrics...")
    
    metrics = {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred)),
        'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
        'roc_auc': float(roc_auc_score(y_true, y_prob))
    }
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    metrics['confusion_matrix'] = {
        'true_negatives': int(tn),
        'false_positives': int(fp),
        'false_negatives': int(fn),
        'true_positives': int(tp)
    }
    
    # Additional fraud-specific metrics
    total_fraud = int(y_true.sum())
    metrics['fraud_detection'] = {
        'total_fraud_cases': total_fraud,
        'frauds_detected': int(tp),
        'frauds_missed': int(fn),
        'detection_rate': float(tp / total_fraud) if total_fraud > 0 else 0.0,
        'false_alarm_rate': float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    }
    
    return metrics


def plot_confusion_matrix(y_true, y_pred, output_path):
    """Generate and save confusion matrix plot."""
    logger.info("Generating confusion matrix plot...")
    
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                xticklabels=['Legitimate', 'Fraud'],
                yticklabels=['Legitimate', 'Fraud'])
    plt.title('Confusion Matrix\nFraud Detection Model', fontsize=14, fontweight='bold')
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✓ Saved confusion matrix to {output_path}")


def plot_roc_curve(y_true, y_prob, output_path):
    """Generate and save ROC curve plot."""
    logger.info("Generating ROC curve plot...")
    
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = roc_auc_score(y_true, y_prob)
    
    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, 
             label=f'ROC curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
             label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate (Recall)', fontsize=12)
    plt.title('ROC Curve - Fraud Detection Model', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✓ Saved ROC curve to {output_path}")


def print_metrics_report(metrics, model_name, threshold):
    """Print formatted metrics report."""
    print("\n" + "="*80)
    print("MODEL EVALUATION REPORT")
    print("="*80)
    print(f"\nModel: {model_name}")
    print(f"Threshold: {threshold}")
    
    print("\n" + "-"*80)
    print("CLASSIFICATION METRICS")
    print("-"*80)
    print(f"Accuracy:   {metrics['accuracy']:.4f}")
    print(f"Precision:  {metrics['precision']:.4f}")
    print(f"Recall:     {metrics['recall']:.4f} ⭐ (Primary metric for fraud detection)")
    print(f"F1-Score:   {metrics['f1_score']:.4f}")
    print(f"ROC-AUC:    {metrics['roc_auc']:.4f}")
    
    cm = metrics['confusion_matrix']
    print("\n" + "-"*80)
    print("CONFUSION MATRIX")
    print("-"*80)
    print(f"                 Predicted")
    print(f"                Legit  Fraud")
    print(f"Actual Legit    {cm['true_negatives']:5d}  {cm['false_positives']:5d}")
    print(f"       Fraud    {cm['false_negatives']:5d}  {cm['true_positives']:5d}")
    
    fd = metrics['fraud_detection']
    print("\n" + "-"*80)
    print("FRAUD DETECTION PERFORMANCE")
    print("-"*80)
    print(f"Total Fraud Cases:     {fd['total_fraud_cases']}")
    print(f"Frauds Detected:       {fd['frauds_detected']} ({fd['detection_rate']*100:.1f}%)")
    print(f"Frauds Missed:         {fd['frauds_missed']} ⚠️")
    print(f"False Alarm Rate:      {fd['false_alarm_rate']*100:.2f}%")
    
    print("="*80)


def main():
    """Main evaluation pipeline."""
    print("\n" + "="*80)
    print("FRAUD DETECTION MODEL - COMPREHENSIVE EVALUATION")
    print("="*80)
    
    # Load model and configuration
    model, threshold, model_name = load_model_and_threshold()
    
    # Load test data
    X_test, y_test = load_test_data()
    
    # Generate predictions
    logger.info("Generating predictions...")
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)
    
    # Compute metrics
    metrics = compute_metrics(y_test, y_pred, y_prob)
    
    # Add metadata
    metrics['model_name'] = model_name
    metrics['threshold'] = float(threshold)
    metrics['test_samples'] = int(len(y_test))
    
    # Print report
    print_metrics_report(metrics, model_name, threshold)
    
    # Generate plots
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    output_dir = Path('docs/figs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Confusion matrix
    cm_path = output_dir / 'model_confusion_matrix.png'
    plot_confusion_matrix(y_test, y_pred, cm_path)
    
    # ROC curve
    roc_path = output_dir / 'model_roc_curve.png'
    plot_roc_curve(y_test, y_prob, roc_path)
    
    # Save metrics
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    
    metrics_dir = Path('configs')
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    metrics_path = metrics_dir / 'model_metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"✓ Saved metrics to {metrics_path}")
    
    # Summary
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE")
    print("="*80)
    print(f"\nMetrics saved to: {metrics_path}")
    print(f"Plots saved to: {output_dir}/")
    print(f"  - {cm_path.name}")
    print(f"  - {roc_path.name}")
    print("="*80)
    
    return metrics


if __name__ == '__main__':
    metrics = main()
