"""
Model Training Module for Fraud Detection - Multi-Model Comparison
Trains and compares multiple models optimized for RECALL.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import json
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    precision_score, recall_score, f1_score, roc_auc_score
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_prepared_data(data_dir='models'):
    """Load prepared feature matrices."""
    logger.info(f"Loading prepared data from {data_dir}/")
    
    X_train = np.load(f'{data_dir}/X_train.npy')
    X_test = np.load(f'{data_dir}/X_test.npy')
    y_train = np.load(f'{data_dir}/y_train.npy')
    y_test = np.load(f'{data_dir}/y_test.npy')
    
    logger.info(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
    logger.info(f"Train fraud rate: {y_train.mean()*100:.2f}%")
    
    return X_train, X_test, y_train, y_test


def train_logistic_regression(X_train, y_train):
    """Train Logistic Regression with class balancing."""
    logger.info("Training Logistic Regression...")
    
    model = LogisticRegression(
        class_weight='balanced',
        max_iter=1000,
        random_state=42,
        solver='liblinear'
    )
    
    model.fit(X_train, y_train)
    logger.info("✓ Logistic Regression trained")
    
    return model


def train_random_forest(X_train, y_train):
    """Train Random Forest with class balancing."""
    logger.info("Training Random Forest...")
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    logger.info("✓ Random Forest trained")
    
    return model


def train_gradient_boosting(X_train, y_train):
    """Train Gradient Boosting with class balancing."""
    logger.info("Training Gradient Boosting...")
    
    # Calculate scale_pos_weight for imbalance
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    scale_pos_weight = n_neg / n_pos
    
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42
    )
    
    # For GradientBoosting, we use sample_weight instead
    sample_weights = np.ones(len(y_train))
    sample_weights[y_train == 1] = scale_pos_weight
    
    model.fit(X_train, y_train, sample_weight=sample_weights)
    logger.info("✓ Gradient Boosting trained")
    
    return model


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate model and return metrics."""
    y_pred = model.predict(X_test)
    
    try:
        y_prob = model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_prob)
    except:
        roc_auc = None
    
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    metrics = {
        'model_name': model_name,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'roc_auc': roc_auc,
        'true_positives': int(tp),
        'false_positives': int(fp),
        'true_negatives': int(tn),
        'false_negatives': int(fn)
    }
    
    return metrics


def print_comparison_table(results):
    """Print formatted comparison table."""
    print("\n" + "="*80)
    print("MODEL COMPARISON - OPTIMIZED FOR RECALL (Fraud Detection)")
    print("="*80)
    
    # Create DataFrame for easy formatting
    df = pd.DataFrame(results)
    
    # Sort by Recall (primary), then F1 (secondary)
    df = df.sort_values(['recall', 'f1_score'], ascending=False)
    
    print(f"\n{'Model':<25} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'ROC-AUC':>10}")
    print("-"*80)
    
    for _, row in df.iterrows():
        roc_str = f"{row['roc_auc']:.4f}" if row['roc_auc'] is not None else "N/A"
        print(f"{row['model_name']:<25} {row['precision']:>10.4f} {row['recall']:>10.4f} {row['f1_score']:>10.4f} {roc_str:>10}")
    
    print("-"*80)
    
    # Highlight best model
    best = df.iloc[0]
    print(f"\n🏆 BEST MODEL: {best['model_name']}")
    print(f"   ├─ Recall (primary): {best['recall']:.4f} ⭐")
    print(f"   ├─ F1-Score: {best['f1_score']:.4f}")
    print(f"   ├─ Precision: {best['precision']:.4f}")
    print(f"   └─ ROC-AUC: {best['roc_auc']:.4f}" if best['roc_auc'] else "")
    
    # Show confusion matrix for best model
    print(f"\n📊 Confusion Matrix (Best Model):")
    print(f"   ├─ True Positives: {best['true_positives']} (Fraud correctly detected)")
    print(f"   ├─ False Negatives: {best['false_negatives']} (Fraud missed) ⚠️")
    print(f"   ├─ True Negatives: {best['true_negatives']} (Legit correctly classified)")
    print(f"   └─ False Positives: {best['false_positives']} (False alarms)")
    
    print("="*80)
    
    return df


def main():
    """Main training pipeline with model comparison."""
    print("\n" + "="*80)
    print("FRAUD DETECTION - MULTI-MODEL TRAINING")
    print("Focus: RECALL optimization (minimize missed fraud)")
    print("="*80)
    
    # Load data
    X_train, X_test, y_train, y_test = load_prepared_data()
    
    # Train models
    print("\n" + "="*80)
    print("TRAINING MODELS")
    print("="*80)
    
    models = {}
    
    # 1. Logistic Regression (baseline)
    models['Logistic Regression'] = train_logistic_regression(X_train, y_train)
    
    # 2. Random Forest
    models['Random Forest'] = train_random_forest(X_train, y_train)
    
    # 3. Gradient Boosting
    try:
        models['Gradient Boosting'] = train_gradient_boosting(X_train, y_train)
    except Exception as e:
        logger.warning(f"Gradient Boosting training failed: {e}")
    
    # Evaluate all models
    print("\n" + "="*80)
    print("EVALUATING MODELS")
    print("="*80)
    
    results = []
    for name, model in models.items():
        logger.info(f"Evaluating {name}...")
        metrics = evaluate_model(model, X_test, y_test, name)
        results.append(metrics)
    
    # Print comparison table
    comparison_df = print_comparison_table(results)
    
    # Select best model
    best_model_name = comparison_df.iloc[0]['model_name']
    best_model = models[best_model_name]
    
    # Save best model
    output_dir = Path('models')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print("SAVING BEST MODEL")
    print("="*80)
    
    best_model_path = output_dir / 'best_model.pkl'
    joblib.dump(best_model, best_model_path)
    logger.info(f"✓ Saved best model to {best_model_path}")
    
    # Save model name
    model_name_path = output_dir / 'model_name.txt'
    with open(model_name_path, 'w') as f:
        f.write(best_model_name)
    logger.info(f"✓ Saved model name to {model_name_path}")
    
    # Save all results
    results_path = output_dir / 'model_comparison.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"✓ Saved comparison results to {results_path}")
    
    # Save comparison table as CSV
    comparison_path = output_dir / 'model_comparison.csv'
    comparison_df.to_csv(comparison_path, index=False)
    logger.info(f"✓ Saved comparison table to {comparison_path}")
    
    print("\n" + "="*80)
    print("✅ TRAINING COMPLETE")
    print("="*80)
    print(f"Best model: {best_model_name}")
    print(f"Saved to: models/best_model.pkl")
    print("="*80)
    
    return best_model_name, results


if __name__ == '__main__':
    best_model_name, results = main()
