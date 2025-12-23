"""
Quick model training script
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
from pathlib import Path
import json

print('='*60)
print('FRAUD DETECTION MODEL TRAINING')
print('='*60)

# Load prepared data
print('\nLoading prepared data...')
X_train = np.load('models/X_train.npy')
X_test = np.load('models/X_test.npy')
y_train = np.load('models/y_train.npy')
y_test = np.load('models/y_test.npy')

print(f'Train shape: {X_train.shape}')
print(f'Test shape: {X_test.shape}')
print(f'Train fraud rate: {y_train.mean()*100:.2f}%')
print(f'Test fraud rate: {y_test.mean()*100:.2f}%')

# Train model
print('\n' + '='*60)
print('TRAINING RANDOM FOREST')
print('='*60)
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
print('✓ Training complete!')

# Evaluate
print('\n' + '='*60)
print('MODEL EVALUATION')
print('='*60)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

roc_auc = roc_auc_score(y_test, y_prob)
print(f'\nROC-AUC Score: {roc_auc:.4f}')

print('\nClassification Report:')
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud']))

cm = confusion_matrix(y_test, y_pred)
print('\nConfusion Matrix:')
print(f'                 Predicted')
print(f'                Legit  Fraud')
print(f'Actual Legit    {cm[0,0]:5d}  {cm[0,1]:5d}')
print(f'       Fraud    {cm[1,0]:5d}  {cm[1,1]:5d}')

# Save model
print('\n' + '='*60)
print('SAVING MODEL ARTIFACTS')
print('='*60)

Path('models').mkdir(exist_ok=True)
joblib.dump(model, 'models/fraud_model.joblib')
print('✓ Saved model to models/fraud_model.joblib')

# Save metrics
metrics = {
    'roc_auc': float(roc_auc),
    'train_samples': int(len(X_train)),
    'test_samples': int(len(X_test)),
    'n_features': int(X_train.shape[1]),
    'train_fraud_rate': float(y_train.mean()),
    'test_fraud_rate': float(y_test.mean())
}

with open('models/evaluation_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print('✓ Saved metrics to models/evaluation_metrics.json')

# Feature importance
with open('models/feature_names.json', 'r') as f:
    feature_data = json.load(f)
    feature_names = feature_data['all_features']

importance_df = list(zip(feature_names, model.feature_importances_))
importance_df.sort(key=lambda x: x[1], reverse=True)

print('\n' + '='*60)
print('TOP 10 FEATURE IMPORTANCES')
print('='*60)
for i, (feat, imp) in enumerate(importance_df[:10], 1):
    print(f'{i:2d}. {feat:30s} {imp:.4f}')

print('\n' + '='*60)
print('TRAINING COMPLETE!')
print('='*60)
