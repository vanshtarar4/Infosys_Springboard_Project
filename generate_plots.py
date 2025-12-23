"""
Generate model evaluation plots
"""
import numpy as np
from sklearn.metrics import roc_curve, precision_recall_curve, roc_auc_score, average_precision_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Set style
sns.set_style('whitegrid')

# Load data
print('Loading test data and model...')
X_test = np.load('models/X_test.npy')
y_test = np.load('models/y_test.npy')
model = joblib.load('models/fraud_model.joblib')

# Get predictions
y_prob = model.predict_proba(X_test)[:, 1]

# ROC Curve
print('Generating ROC curve...')
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = roc_auc_score(y_test, y_prob)

plt.figure(figsize=(10, 8))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f}')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('Receiver Operating Characteristic (ROC) Curve\nFraud Detection Model', fontsize=14, fontweight='bold')
plt.legend(loc="lower right", fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('models/roc_curve.png', dpi=300, bbox_inches='tight')
plt.close()
print('✓ Saved models/roc_curve.png')

# Precision-Recall Curve
print('Generating Precision-Recall curve...')
precision, recall, _ = precision_recall_curve(y_test, y_prob)
avg_precision = average_precision_score(y_test, y_prob)

plt.figure(figsize=(10, 8))
plt.plot(recall, precision, color='blue', lw=2, label=f'PR curve (AP = {avg_precision:.4f})')
plt.xlabel('Recall', fontsize=12)
plt.ylabel('Precision', fontsize=12)
plt.title('Precision-Recall Curve\nFraud Detection Model', fontsize=14, fontweight='bold')
plt.legend(loc="lower left", fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('models/precision_recall_curve.png', dpi=300, bbox_inches='tight')
plt.close()
print('✓ Saved models/precision_recall_curve.png')

# Feature Importance
print('Generating feature importance plot...')
import json
with open('models/feature_names.json', 'r') as f:
    feature_names = json.load(f)['all_features']

importances = model.feature_importances_
indices = np.argsort(importances)[::-1][:10]

plt.figure(figsize=(10, 8))
plt.barh(range(10), importances[indices], color='steelblue')
plt.yticks(range(10), [feature_names[i] for i in indices])
plt.xlabel('Feature Importance', fontsize=12)
plt.title('Top 10 Feature Importance\nRandom Forest Model', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('models/feature_importance.png', dpi=300, bbox_inches='tight')
plt.close()
print('✓ Saved models/feature_importance.png')

print('\n✓ All evaluation plots generated successfully!')
