import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Load clean data — Overall LPI Score only
# ============================================================
df = pd.read_csv('outputs/LPI_clean.csv')

df_score = df[
    (df['Indicator Code'] == 'LP.LPI.OVRL.XQ') &
    (df['Value'].notna())
].copy().sort_values(['Country Code', 'Year'])

# ============================================================
# Pattern 1: Global trend — is the world improving?
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('LPI Historical Pattern Analysis', fontsize=14, fontweight='bold')

ax1 = axes[0, 0]
global_avg = df_score.groupby('Year')['Value'].agg(['mean', 'std']).reset_index()
ax1.plot(global_avg['Year'], global_avg['mean'], 'o-',
         color='steelblue', linewidth=2.5, markersize=8, label='Global Average')
ax1.fill_between(global_avg['Year'],
                 global_avg['mean'] - global_avg['std'],
                 global_avg['mean'] + global_avg['std'],
                 alpha=0.15, color='steelblue', label='±1 std dev')
ax1.axvspan(2018, 2023, alpha=0.08, color='orange', label='5-yr gap')

# Annotate gap size between each year
years = global_avg['Year'].values
for i in range(1, len(years)):
    gap   = years[i] - years[i-1]
    mid_x = (years[i] + years[i-1]) / 2
    mid_y = global_avg['mean'].values[i-1] + 0.05
    ax1.annotate(f'+{gap}yr', (mid_x, mid_y),
                 ha='center', fontsize=8, color='gray')

ax1.set_title('Global Average LPI Score over Time')
ax1.set_xlabel('Year')
ax1.set_ylabel('Score (1-5)')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# ============================================================
# Pattern 2: Trend direction per region
# ============================================================
ax2 = axes[0, 1]
region_trend = []
for region, grp in df_score.groupby('Region'):
    avg = grp.groupby('Year')['Value'].mean()
    if len(avg) >= 2:
        trend = avg.iloc[-1] - avg.iloc[0]
        region_trend.append({'Region': region, 'Trend': round(trend, 3)})

df_trend = pd.DataFrame(region_trend).sort_values('Trend', ascending=True)
colors   = ['tomato' if t < 0 else 'steelblue' for t in df_trend['Trend']]
bars     = ax2.barh(df_trend['Region'], df_trend['Trend'], color=colors)
ax2.axvline(x=0, color='black', linewidth=0.8)
ax2.set_title('LPI Trend by Region (first vs last year)')
ax2.set_xlabel('Score Change')
ax2.grid(True, alpha=0.3)
for bar, val in zip(bars, df_trend['Trend']):
    ax2.text(val + 0.005 if val >= 0 else val - 0.005,
             bar.get_y() + bar.get_height()/2,
             f'{val:+.3f}', va='center',
             ha='left' if val >= 0 else 'right', fontsize=8)

# ============================================================
# Pattern 3: Score change 2018 vs 2023 — impact of 5-yr gap
# ============================================================
ax3 = axes[1, 0]
df_2018 = df_score[df_score['Year'] == 2018].set_index('Country Code')['Value']
df_2023 = df_score[df_score['Year'] == 2023].set_index('Country Code')['Value']
df_change = (df_2023 - df_2018).dropna().reset_index()
df_change.columns = ['Country Code', 'Change']

improvers = df_change[df_change['Change'] > 0]
decliners = df_change[df_change['Change'] < 0]

ax3.hist(df_change['Change'], bins=20, color='steelblue',
         edgecolor='white', linewidth=0.5)
ax3.axvline(x=0, color='tomato', linewidth=1.5, linestyle='--')
ax3.axvline(x=df_change['Change'].mean(), color='green',
            linewidth=1.5, linestyle='--', label=f"Mean: {df_change['Change'].mean():+.3f}")
ax3.set_title(f'Score Change: 2018 → 2023\n'
              f'Improved: {len(improvers)} countries | Declined: {len(decliners)} countries')
ax3.set_xlabel('Score Change')
ax3.set_ylabel('Number of Countries')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# ============================================================
# Pattern 4: Selected countries trend — your focus countries
# ============================================================
ax4 = axes[1, 1]
FOCUS_COUNTRIES = ['JOR', 'SAU', 'ARE', 'EGY', 'DEU', 'SGP', 'CHN', 'USA']
colors_fc = ['steelblue', 'tomato', 'green', 'orange',
             'purple', 'brown', 'pink', 'gray']

for code, color in zip(FOCUS_COUNTRIES, colors_fc):
    data = df_score[df_score['Country Code'] == code].sort_values('Year')
    if len(data) == 0:
        continue
    name = data['Country Name'].iloc[0]
    ax4.plot(data['Year'], data['Value'], 'o-',
             color=color, linewidth=2, markersize=5, label=name)

ax4.axvspan(2018, 2023, alpha=0.08, color='orange')
ax4.set_title('LPI Trend — Focus Countries')
ax4.set_xlabel('Year')
ax4.set_ylabel('Score (1-5)')
ax4.legend(fontsize=7)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/LPI_Pattern.png', dpi=150, bbox_inches='tight')
print("Saved: outputs/LPI_Pattern.png")
plt.show()

# ============================================================
# Print pattern summary
# ============================================================
print("\nGlobal LPI Score by year:")
print(global_avg.set_index('Year')[['mean']].round(3).to_string())

print(f"\nScore change 2018 to 2023:")
print(f"  Countries improved: {len(improvers)}")
print(f"  Countries declined: {len(decliners)}")
print(f"  Average change:     {df_change['Change'].mean():+.3f}")

print("\nFocus countries trend (first to last year):")
for code in FOCUS_COUNTRIES:
    data = df_score[df_score['Country Code'] == code].sort_values('Year')
    if len(data) >= 2:
        name  = data['Country Name'].iloc[0]
        trend = data['Value'].iloc[-1] - data['Value'].iloc[0]
        first = data['Value'].iloc[0]
        last  = data['Value'].iloc[-1]
        print(f"  {name}: {first:.2f} → {last:.2f} ({trend:+.3f})")

print("\nDone — run next: python 02b_clustering.py")