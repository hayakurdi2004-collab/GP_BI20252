import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Load data
# ============================================================
df = pd.read_csv('outputs/LPI_clean.csv')

df_score = df[
    (df['Indicator Code'] == 'LP.LPI.OVRL.XQ') &
    (df['Value'].notna())
].copy()

# ============================================================
# Method 1: IQR — find countries far from the middle
# ============================================================
Q1  = df_score['Value'].quantile(0.25)
Q3  = df_score['Value'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers_iqr = df_score[
    (df_score['Value'] < lower) | (df_score['Value'] > upper)
]

print(f"IQR bounds: {lower:.3f} to {upper:.3f}")
print(f"Outlier records found: {len(outliers_iqr)}")
print("\nOutlier countries:")
print(outliers_iqr.groupby('Country Name')['Value'].agg(['mean','count','min','max'])
      .sort_values('mean').round(3).to_string())

# ============================================================
# Method 2: Z-score per year — outliers relative to each year
# ============================================================
df_score['Z_Score'] = df_score.groupby('Year')['Value'].transform(
    lambda x: np.abs(stats.zscore(x))
)
outliers_z = df_score[df_score['Z_Score'] > 2.5]

print(f"\nZ-score outliers (|z| > 2.5): {len(outliers_z)} records")
print(outliers_z.groupby('Country Name')['Value'].mean()
      .sort_values().round(3).to_string())

# ============================================================
# Decision: are these real outliers or data errors?
# ============================================================
print("\n" + "=" * 55)
print("Decision: Keep or Remove?")
print("=" * 55)
print("""
These outliers represent REAL country performance:
- High outliers (Singapore, Germany 4.0+): genuinely top logistics
- Low outliers (Haiti, Yemen, etc. <2.0): genuinely poor logistics

Decision: KEEP all outliers in the dataset.
Reason: They reflect real-world variation, not data errors.

However, for Jordan forecasting:
- Jordan shows unusual downward trend
- We will use Linear instead of Polynomial regression
  to avoid over-extrapolation of the negative trend
""")

# ============================================================
# Plot: distribution with outlier bounds
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Outlier Analysis — LPI Overall Score', fontsize=13, fontweight='bold')

# Histogram with IQR bounds
axes[0].hist(df_score['Value'], bins=30, color='steelblue',
             edgecolor='white', linewidth=0.5, alpha=0.8)
axes[0].axvline(x=lower, color='tomato', linewidth=2,
                linestyle='--', label=f'Lower bound: {lower:.2f}')
axes[0].axvline(x=upper, color='tomato', linewidth=2,
                linestyle='--', label=f'Upper bound: {upper:.2f}')
axes[0].axvline(x=df_score['Value'].mean(), color='green',
                linewidth=1.5, linestyle='-', label=f'Mean: {df_score["Value"].mean():.2f}')
axes[0].set_title('Score Distribution with IQR Bounds')
axes[0].set_xlabel('LPI Overall Score')
axes[0].set_ylabel('Count')
axes[0].legend(fontsize=9)
axes[0].grid(True, alpha=0.3)

# Boxplot per year
df_score.boxplot(column='Value', by='Year', ax=axes[1])
axes[1].set_title('Score Distribution per Year')
axes[1].set_xlabel('Year')
axes[1].set_ylabel('LPI Score')
plt.sca(axes[1])
plt.title('Boxplot per Year — showing outlier dots')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/LPI_Outliers.png', dpi=150, bbox_inches='tight')
print("Saved: outputs/LPI_Outliers.png")
plt.show()

# ============================================================
# Save outlier report
# ============================================================
outliers_iqr[['Country Code', 'Country Name', 'Region',
               'Year', 'Value']].to_csv('outputs/LPI_Outliers.csv', index=False)
print("Saved: outputs/LPI_Outliers.csv")
print("\nDone — run next: python 03_forecasting.py (with linear model for Jordan)")