"""
Enhanced Fraud Detection Model Training
Includes hyperparameter tuning, SMOTE, and comprehensive evaluation
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report, roc_auc_score, confusion_matrix,
    precision_recall_curve, auc, f1_score, precision_score, recall_score
)
from imblearn.over_sampling import SMOTE
import joblib
from pathlib import Path
import json
from datetime import datetime

print('='*70)
print('ENHANCED FRAUD DETECTION MODEL TRAINING')
print('='*70)
print(f'Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

# Load prepared data
print('\n[1/6] Loading prepared data...')
X_train = np.load('models/X_train.npy')
X_test = np.load('models/X_test.npy')
y_train = np.load('models/y_train.npy')
y_test = np.load('models/y_test.npy')

print(f'  Train shape: {X_train.shape}')
print(f'  Test shape: {X_test.shape}')
print(f'  Train fraud rate: {y_train.mean()*100:.2f}%')
print(f'  Test fraud rate: {y_test.mean()*100:.2f}%')

# Handle class imbalance with SMOTE
print('\n[2/6] Applying SMOTE for class imbalance...')
print(f'  Before SMOTE: {X_train.shape[0]} samples')
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
print(f'  After SMOTE: {X_train_balanced.shape[0]} samples')
print(f'  Balanced fraud rate: {y_train_balanced.mean()*100:.2f}%')

# Hyperparameter tuning
print('\n[3/6] Hyperparameter tuning with RandomizedSearchCV...')
param_distributions = {
    'n_estimators': [100, 200, 300, 500],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10, 15],
    'min_samples_leaf': [1, 2, 4, 8],
    'max_features': ['sqrt', 'log2', None],
    'class_weight': ['balanced', 'balanced_subsample', None],
    'criterion': ['gini', 'entropy']
}

base_model = RandomForestClassifier(random_state=42, n_jobs=-1)

random_search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_distributions,
    n_iter=50,  # Try 50 random combinations
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    scoring='f1',  # Optimize for F1 score
    n_jobs=-1,
    random_state=42,
    verbose=1
)

print('  Searching for best parameters (this may take a few minutes)...')
random_search.fit(X_train_balanced, y_train_balanced)

print(f'\n  ✓ Best parameters found:')
for param, value in random_search.best_params_.items():
    print(f'    {param}: {value}')
print(f'  Best CV F1 Score: {random_search.best_score_:.4f}')

# Get best model
model = random_search.best_estimator_

# Cross-validation on original (unbalanced) data
print('\n[4/6] Cross-validation on original data...')
cv_scores = cross_val_score(
    model, X_train, y_train,
    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    scoring='f1',
    n_jobs=-1
)
print(f'  CV F1 Scores: {cv_scores}')
print(f'  Mean F1: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})')

# Final training on balanced data
print('\n[5/6] Training final model on balanced data...')
model.fit(X_train_balanced, y_train_balanced)
print('  ✓ Training complete!')

# Comprehensive evaluation
print('\n[6/6] Comprehensive model evaluation...')
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# Calculate metrics
accuracy = (y_pred == y_test).mean()
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)

# Precision-Recall AUC
precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_prob)
pr_auc = auc(recall_curve, precision_curve)

print(f'\n{"="*70}')
print('MODEL PERFORMANCE METRICS')
print(f'{"="*70}')
print(f'  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)')
print(f'  Precision: {precision:.4f} ({precision*100:.2f}%)')
print(f'  Recall:    {recall:.4f} ({recall*100:.2f}%)')
print(f'  F1 Score:  {f1:.4f} ({f1*100:.2f}%)')
print(f'  ROC-AUC:   {roc_auc:.4f}')
print(f'  PR-AUC:    {pr_auc:.4f}')

print(f'\n{"="*70}')
print('CLASSIFICATION REPORT')
print(f'{"="*70}')
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud']))

cm = confusion_matrix(y_test, y_pred)
print(f'{"="*70}')
print('CONFUSION MATRIX')
print(f'{"="*70}')
print(f'                 Predicted')
print(f'                Legit  Fraud')
print(f'Actual Legit    {cm[0,0]:5d}  {cm[0,1]:5d}')
print(f'       Fraud    {cm[1,0]:5d}  {cm[1,1]:5d}')

# Calculate improvement vs old model
try:
    with open('models/evaluation_metrics_backup.json', 'r') as f:
        old_metrics = json.load(f)
    old_roc_auc = old_metrics.get('roc_auc', 0)
    
    print(f'\n{"="*70}')
    print('IMPROVEMENT vs OLD MODEL')
    print(f'{"="*70}')
    print(f'  ROC-AUC: {old_roc_auc:.4f} → {roc_auc:.4f} ({"+" if roc_auc > old_roc_auc else ""}{(roc_auc - old_roc_auc):.4f})')
    
except:
    print('\n  (No previous metrics available for comparison)')

# Save model
print(f'\n{"="*70}')
print('SAVING MODEL ARTIFACTS')
print(f'{"="*70}')

Path('models').mkdir(exist_ok=True)
joblib.dump(model, 'models/fraud_model.joblib')
print('  ✓ Saved model to models/fraud_model.joblib')

# Also save as best_model for API compatibility
joblib.dump(model, 'models/best_model.joblib')
print('  ✓ Saved model to models/best_model.joblib')

# Save comprehensive metrics
metrics = {
    'accuracy': float(accuracy),
    'precision': float(precision),
    'recall': float(recall),
    'f1_score': float(f1),
    'roc_auc': float(roc_auc),
    'pr_auc': float(pr_auc),
    'train_samples': int(len(X_train_balanced)),
    'test_samples': int(len(X_test)),
    'n_features': int(X_train.shape[1]),
    'train_fraud_rate': float(y_train_balanced.mean()),
    'test_fraud_rate': float(y_test.mean()),
    'best_params': random_search.best_params_,
    'cv_f1_mean': float(cv_scores.mean()),
    'cv_f1_std': float(cv_scores.std()),
    'trained_at': datetime.now().isoformat()
}

with open('models/evaluation_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print('  ✓ Saved metrics to models/evaluation_metrics.json')

# Feature importance
try:
    with open('models/feature_names.json', 'r') as f:
        feature_data = json.load(f)
        feature_names = feature_data['all_features']
    
    importance_df = list(zip(feature_names, model.feature_importances_))
    importance_df.sort(key=lambda x: x[1], reverse=True)
    
    print(f'\n{"="*70}')
    print('TOP 10 FEATURE IMPORTANCES')
    print(f'{"="*70}')
    for i, (feat, imp) in enumerate(importance_df[:10], 1):
        print(f'  {i:2d}. {feat:35s} {imp:.4f}')
except:
    print('\n  (Feature names not available)')

print(f'\n{"="*70}')
print('✅ ENHANCED TRAINING COMPLETE!')
print(f'{"="*70}')
print(f'Finished: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'\nNew model saved and ready for deployment!')
print(f'Key improvements:')
print(f'  • Hyperparameter optimization')
print(f'  • SMOTE for class imbalance')
print(f'  • Cross-validation')
print(f'  • Comprehensive metrics')
