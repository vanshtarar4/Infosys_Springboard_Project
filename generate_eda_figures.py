"""
Generate EDA visualizations and statistics
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Setup
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create output directory
fig_dir = Path('docs/figs')
fig_dir.mkdir(parents=True, exist_ok=True)

print("="*80)
print("GENERATING EDA VISUALIZATIONS")
print("="*80)

# Load data
print("\n1. Loading data...")
df = pd.read_csv('data/processed/transactions_processed.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")

# Calculate statistics
fraud_counts = df['is_fraud'].value_counts()
fraud_pct = df['is_fraud'].value_counts(normalize=True) * 100

print(f"\n2. Fraud Statistics:")
print(f"   - Total Transactions: {len(df):,}")
print(f"   - Legitimate: {fraud_counts[0]:,} ({fraud_pct[0]:.2f}%)")
print(f"   - Fraudulent: {fraud_counts[1]:,} ({fraud_pct[1]:.2f}%)")

# Amount statistics
fraud_stats = df.groupby('is_fraud')['transaction_amount'].agg(['mean', 'median', 'std'])
print(f"\n3. Transaction Amounts:")
print(f"   - Legit Mean: ${fraud_stats.loc[0, 'mean']:,.2f}")
print(f"   - Fraud Mean: ${fraud_stats.loc[1, 'mean']:,.2f}")
print(f"   - Fraud/Legit Ratio: {fraud_stats.loc[1, 'mean']/fraud_stats.loc[0, 'mean']:.2f}x")

# Figure 1: Fraud Count
print("\n4. Generating Figure 1: Fraud Count...")
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#2ecc71', '#e74c3c']
bars = ax.bar(['Legitimate', 'Fraudulent'], fraud_counts.values, color=colors, alpha=0.8, edgecolor='black')

for i, (bar, count, pct) in enumerate(zip(bars, fraud_counts.values, fraud_pct.values)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{count:,}\n({pct:.2f}%)',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
ax.set_xlabel('Transaction Type', fontsize=12, fontweight='bold')
ax.set_title('Distribution of Legitimate vs Fraudulent Transactions', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(fig_dir / 'fig1_fraud_count.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: fig1_fraud_count.png")

# Figure 2: Boxplot
print("\n5. Generating Figure 2: Transaction Amount Boxplots...")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
df_plot = df.copy()
df_plot['fraud_label'] = df_plot['is_fraud'].map({0: 'Legitimate', 1: 'Fraudulent'})

sns.boxplot(data=df_plot, x='fraud_label', y='transaction_amount', 
            palette=['#2ecc71', '#e74c3c'], ax=axes[0])
axes[0].set_ylabel('Transaction Amount ($)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Transaction Type', fontsize=12, fontweight='bold')
axes[0].set_title('Transaction Amount Distribution (Linear Scale)', fontsize=13, fontweight='bold')
axes[0].grid(axis='y', alpha=0.3)

sns.boxplot(data=df_plot, x='fraud_label', y='transaction_amount', 
            palette=['#2ecc71', '#e74c3c'], ax=axes[1])
axes[1].set_yscale('log')
axes[1].set_ylabel('Transaction Amount ($) - Log Scale', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Transaction Type', fontsize=12, fontweight='bold')
axes[1].set_title('Transaction Amount Distribution (Log Scale)', fontsize=13, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(fig_dir / 'fig2_box_amount.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: fig2_box_amount.png")

# Figure 3: Heatmap
print("\n6. Generating Figure 3: Time Heatmap...")
pivot_table = df.pivot_table(
    values='transaction_id', 
    index='weekday', 
    columns='hour', 
    aggfunc='count', 
    fill_value=0
)

weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
pivot_table.index = [weekday_names[i] if i < len(weekday_names) else f'Day {i}' for i in pivot_table.index]

fig, ax = plt.subplots(figsize=(16, 8))
sns.heatmap(pivot_table, annot=False, fmt='d', cmap='YlOrRd', 
            cbar_kws={'label': 'Number of Transactions'}, ax=ax)
ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
ax.set_ylabel('Day of Week', fontsize=12, fontweight='bold')
ax.set_title('Transaction Activity Heatmap: Weekday vs Hour', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(fig_dir / 'fig3_heatmap_time.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: fig3_heatmap_time.png")

# Figure 4: Channel Analysis
print("\n7. Generating Figure 4: Channel Fraud Rates...")
channel_analysis = df.groupby('channel').agg({
    'is_fraud': ['sum', 'count', 'mean']
})
channel_analysis.columns = ['fraud_count', 'total_transactions', 'fraud_rate']
channel_analysis['fraud_percentage'] = channel_analysis['fraud_rate'] * 100
channel_analysis = channel_analysis.sort_values('fraud_rate', ascending=False)

top_n = min(5, len(channel_analysis))
top_channels = channel_analysis.head(top_n)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(len(top_channels)), top_channels['fraud_percentage'], 
              color='#e74c3c', alpha=0.7, edgecolor='black')

for i, (idx, row) in enumerate(top_channels.iterrows()):
    ax.text(i, row['fraud_percentage'], 
            f"{row['fraud_percentage']:.2f}%\n({int(row['fraud_count'])}/{int(row['total_transactions'])})",
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xticks(range(len(top_channels)))
ax.set_xticklabels(top_channels.index, fontsize=11, fontweight='bold')
ax.set_ylabel('Fraud Rate (%)', fontsize=12, fontweight='bold')
ax.set_xlabel('Channel', fontsize=12, fontweight='bold')
ax.set_title(f'Top {top_n} Channels by Fraud Rate', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(fig_dir / 'fig4_channel_fraud.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: fig4_channel_fraud.png")

# Figure 5: Account Age Segments
print("\n8. Generating Figure 5: Account Age Risk Segments...")
segment_analysis = df.groupby('account_age_bucket').agg({
    'is_fraud': ['sum', 'count', 'mean']
})
segment_analysis.columns = ['fraud_count', 'total_transactions', 'fraud_rate']
segment_analysis['fraud_percentage'] = segment_analysis['fraud_rate'] * 100
segment_analysis = segment_analysis.sort_values('fraud_rate', ascending=False)

age_order = ['new', 'recent', 'established', 'old']
segment_plot = segment_analysis.reindex([x for x in age_order if x in segment_analysis.index])

fig, ax = plt.subplots(figsize=(12, 6))
colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.8, len(segment_plot)))
bars = ax.bar(range(len(segment_plot)), segment_plot['fraud_percentage'], 
              color=colors, alpha=0.8, edgecolor='black')

for i, (idx, row) in enumerate(segment_plot.iterrows()):
    ax.text(i, row['fraud_percentage'], 
            f"{row['fraud_percentage']:.2f}%\n({int(row['fraud_count'])}/{int(row['total_transactions'])})",
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xticks(range(len(segment_plot)))
ax.set_xticklabels([x.title() for x in segment_plot.index], fontsize=11, fontweight='bold')
ax.set_ylabel('Fraud Rate (%)', fontsize=12, fontweight='bold')
ax.set_xlabel('Account Age Bucket', fontsize=12, fontweight='bold')
ax.set_title('High-Risk Customer Segments by Account Age', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(fig_dir / 'fig5_segment_risk.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: fig5_segment_risk.png")

# Bonus Figure 6: KYC Impact
print("\n9. Generating Bonus Figure 6: KYC Impact...")
kyc_analysis = df.groupby('kyc_verified').agg({
    'is_fraud': ['sum', 'count', 'mean']
})
kyc_analysis.columns = ['fraud_count', 'total_transactions', 'fraud_rate']
kyc_analysis['fraud_percentage'] = kyc_analysis['fraud_rate'] * 100
kyc_analysis.index = ['Not Verified', 'Verified']

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#e74c3c', '#2ecc71']
bars = ax.bar(kyc_analysis.index, kyc_analysis['fraud_percentage'], 
              color=colors, alpha=0.7, edgecolor='black')

for i, (idx, row) in enumerate(kyc_analysis.iterrows()):
    ax.text(i, row['fraud_percentage'], 
            f"{row['fraud_percentage']:.2f}%\n({int(row['fraud_count'])}/{int(row['total_transactions'])})",
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Fraud Rate (%)', fontsize=12, fontweight='bold')
ax.set_xlabel('KYC Verification Status', fontsize=12, fontweight='bold')
ax.set_title('Impact of KYC Verification on Fraud Rate', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(fig_dir / 'fig6_kyc_impact.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Saved: fig6_kyc_impact.png")

# Save statistics for summary
stats = {
    'fraud_rate': fraud_pct[1],
    'legit_mean': fraud_stats.loc[0, 'mean'],
    'fraud_mean': fraud_stats.loc[1, 'mean'],
    'ratio': fraud_stats.loc[1, 'mean']/fraud_stats.loc[0, 'mean'],
    'top_risk_channel': top_channels.index[0],
    'top_risk_channel_rate': top_channels.iloc[0]['fraud_percentage'],
    'top_risk_segment': segment_plot.index[0],
    'top_risk_segment_rate': segment_plot.iloc[0]['fraud_percentage']
}

print("\n" + "="*80)
print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
print("="*80)
print(f"\nFigures saved to: {fig_dir}")
print("  - fig1_fraud_count.png")
print("  - fig2_box_amount.png")
print("  - fig3_heatmap_time.png")
print("  - fig4_channel_fraud.png")
print("  - fig5_segment_risk.png")
print("  - fig6_kyc_impact.png")

# Return stats for summary document
import json
with open('eda_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)
print("\n✓ Statistics saved to: eda_stats.json")
