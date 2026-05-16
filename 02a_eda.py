import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Load the clean data
# ============================================================
df = pd.read_csv('outputs/LPI_clean.csv')

df_score = df[
    (df['Indicator Code'] == 'LP.LPI.OVRL.XQ') &
    (df['Value'].notna())
].copy()

print(f"Overall LPI Score records: {df_score.shape[0]}")

# ============================================================
# Plot 1: Average LPI by Region over time
# ============================================================
region_avg = df_score.groupby(['Region', 'Year'])['Value'].mean().reset_index()

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('LPI Exploratory Data Analysis', fontsize=16, fontweight='bold')

ax1 = axes[0, 0]
for region in region_avg['Region'].dropna().unique():
    data = region_avg[region_avg['Region'] == region]
    ax1.plot(data['Year'], data['Value'], marker='o', linewidth=2, label=region)
ax1.set_title('Average LPI Score by Region over Time')
ax1.set_xlabel('Year')
ax1.set_ylabel('Score (1-5)')
ax1.legend(fontsize=7)
ax1.grid(True, alpha=0.3)

# ============================================================
# Plot 2: Top 10 countries in 2018
# ============================================================
ax2 = axes[0, 1]
top10 = (df_score[df_score['Year'] == 2018]
         .nlargest(10, 'Value')[['Country Name', 'Value']])
bars = ax2.barh(top10['Country Name'], top10['Value'], color='steelblue')
ax2.set_title('Top 10 Countries — LPI 2018')
ax2.set_xlabel('Score')
ax2.invert_yaxis()
for bar, val in zip(bars, top10['Value']):
    ax2.text(bar.get_width() - 0.05, bar.get_y() + bar.get_height()/2,
             f'{val:.2f}', va='center', ha='right', color='white', fontweight='bold')

# ============================================================
# Plot 3: LPI distribution by Income Group
# ============================================================
ax3 = axes[1, 0]
income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
income_data  = df_score[df_score['Income Group'].isin(income_order)]
sns.boxplot(data=income_data, x='Income Group', y='Value',
            order=income_order, ax=ax3, palette='Blues')
ax3.set_title('LPI Distribution by Income Group')
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=20, ha='right', fontsize=8)
ax3.set_ylabel('Score')
ax3.set_xlabel('')

# ============================================================
# Plot 4: Correlation between all Score indicators
# ============================================================
ax4 = axes[1, 1]
score_codes = [c for c in df['Indicator Code'].unique() if str(c).endswith('XQ')]
df_pivot = (df[df['Indicator Code'].isin(score_codes)]
            .pivot_table(index=['Country Code', 'Year'],
                         columns='Indicator Short',
                         values='Value')
            .reset_index())
corr_cols = [c for c in df_pivot.columns if c not in ['Country Code', 'Year']]
corr_matrix = df_pivot[corr_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='Blues',
            ax=ax4, annot_kws={'size': 7})
ax4.set_title('Correlation Between Indicators')
ax4.tick_params(axis='x', rotation=30, labelsize=7)
ax4.tick_params(axis='y', rotation=0, labelsize=7)

plt.tight_layout()
plt.savefig('outputs/LPI_EDA.png', dpi=150, bbox_inches='tight')
print("Saved: outputs/LPI_EDA.png")
plt.show()

# ============================================================
# Print summary stats
# ============================================================
print("\nGlobal average LPI Score by year:")
print(df_score.groupby('Year')['Value'].mean().round(3).to_string())

print("\nAverage LPI Score by region (latest year 2023):")
latest = df_score[df_score['Year'] == 2023]
print(latest.groupby('Region')['Value'].mean()
      .sort_values(ascending=False).round(3).to_string())

print("\nDone — run next: python 02b_clustering.py")