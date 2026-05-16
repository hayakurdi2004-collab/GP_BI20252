import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# Load data
# ============================================================
file_path = 'outputs/LPI_interpolated.csv'

if not os.path.exists(file_path):
    file_path = 'outputs/LPI_clean.csv'

df = pd.read_csv(file_path)
print(f"Loaded file: {file_path}")

# ============================================================
# Settings
# ============================================================
country_code = 'JOR'
overall_indicator = 'LP.LPI.OVRL.XQ'

score_indicators = [
    'LP.LPI.CUST.XQ',
    'LP.LPI.INFR.XQ',
    'LP.LPI.ITRN.XQ',
    'LP.LPI.LOGS.XQ',
    'LP.LPI.TRAC.XQ',
    'LP.LPI.TIME.XQ'
]

indicator_names = {
    'LP.LPI.CUST.XQ': 'Customs',
    'LP.LPI.INFR.XQ': 'Infrastructure',
    'LP.LPI.ITRN.XQ': 'International Shipments',
    'LP.LPI.LOGS.XQ': 'Logistics Quality',
    'LP.LPI.TRAC.XQ': 'Tracking & Tracing',
    'LP.LPI.TIME.XQ': 'Timeliness'
}

# ============================================================
# Jordan overall LPI
# ============================================================
jordan_overall = df[
    (df['Country Code'] == country_code) &
    (df['Indicator Code'] == overall_indicator)
].dropna(subset=['Value']).sort_values('Year')

print("\nJordan Overall LPI:")
print(jordan_overall[['Year', 'Value']])

if len(jordan_overall) < 3:
    raise ValueError("Not enough Jordan overall LPI data.")

# ============================================================
# Use historical trend for baseline
# ============================================================
X = jordan_overall['Year'].values
y = jordan_overall['Value'].values

slope, intercept = np.polyfit(X, y, 1)

years_future = np.array([2024, 2025, 2026])
baseline = intercept + slope * years_future
baseline = np.clip(baseline, 1, 5)

# ============================================================
# Jordan indicator analysis
# ============================================================
jordan_indicators = df[
    (df['Country Code'] == country_code) &
    (df['Indicator Code'].isin(score_indicators))
].dropna(subset=['Value']).copy()

latest_year = jordan_indicators['Year'].max()

latest_indicators = jordan_indicators[
    jordan_indicators['Year'] == latest_year
].copy()

latest_indicators['Indicator Name'] = latest_indicators['Indicator Code'].map(indicator_names)

indicator_ranking = latest_indicators[
    ['Indicator Code', 'Indicator Name', 'Value']
].sort_values('Value')

print("\nJordan Indicator Ranking — Worst to Best:")
print(indicator_ranking.to_string(index=False))

worst_1 = indicator_ranking.iloc[0]
worst_2 = indicator_ranking.iloc[1]

worst_1_name = worst_1['Indicator Name']
worst_2_name = worst_2['Indicator Name']

print("\nWeakest indicators:")
print(f"1) {worst_1_name}: {worst_1['Value']:.3f}")
print(f"2) {worst_2_name}: {worst_2['Value']:.3f}")

# ============================================================
# Estimate indicator impact using correlation with Overall LPI
# ============================================================
impact_results = []

for ind in score_indicators:
    temp = df[
        (df['Country Code'] == country_code) &
        (df['Indicator Code'].isin([overall_indicator, ind]))
    ].dropna(subset=['Value'])

    pivot = temp.pivot_table(
        index='Year',
        columns='Indicator Code',
        values='Value'
    ).dropna()

    if len(pivot) >= 3:
        corr = pivot[overall_indicator].corr(pivot[ind])
    else:
        corr = 0.5

    impact_results.append({
        'Indicator Code': ind,
        'Indicator Name': indicator_names[ind],
        'Correlation with Overall': corr
    })

impact_df = pd.DataFrame(impact_results)

print("\nIndicator Impact Estimate:")
print(impact_df.to_string(index=False))

corr_1 = impact_df.loc[
    impact_df['Indicator Code'] == worst_1['Indicator Code'],
    'Correlation with Overall'
].iloc[0]

corr_2 = impact_df.loc[
    impact_df['Indicator Code'] == worst_2['Indicator Code'],
    'Correlation with Overall'
].iloc[0]

# ============================================================
# What-if assumptions
# ============================================================
# improvement_amount = how much the weak indicator improves
# impact_weight = conservative weight translating indicator improvement to overall LPI
# Example:
# if Customs improves by 0.30 and correlation is 0.80,
# overall impact = 0.30 * 0.80 * 0.40 = 0.096
# ============================================================

impact_weight = 0.40

improve_worst_1 = np.array([0.15, 0.25, 0.35])
improve_worst_2 = np.array([0.10, 0.18, 0.25])

impact_worst_1 = improve_worst_1 * corr_1 * impact_weight
impact_worst_2 = improve_worst_2 * corr_2 * impact_weight

scenario_worst_1 = baseline + impact_worst_1
scenario_worst_2 = baseline + impact_worst_2
scenario_combined = baseline + impact_worst_1 + impact_worst_2

# Decline scenario
decline = baseline - np.array([0.10, 0.18, 0.25])

scenario_worst_1 = np.clip(scenario_worst_1, 1, 5)
scenario_worst_2 = np.clip(scenario_worst_2, 1, 5)
scenario_combined = np.clip(scenario_combined, 1, 5)
decline = np.clip(decline, 1, 5)

# ============================================================
# Results table
# ============================================================
results = pd.DataFrame({
    'Year': years_future,
    'Baseline': np.round(baseline, 3),
    f'Improve {worst_1_name}': np.round(scenario_worst_1, 3),
    f'Improve {worst_2_name}': np.round(scenario_worst_2, 3),
    f'Improve {worst_1_name} + {worst_2_name}': np.round(scenario_combined, 3),
    'Decline Scenario': np.round(decline, 3)
})

print("\nWhat-if Results:")
print(results.to_string(index=False))

# ============================================================
# Plot 1 — Indicator ranking
# ============================================================
plt.figure(figsize=(10, 5))

plt.barh(
    indicator_ranking['Indicator Name'],
    indicator_ranking['Value']
)

plt.title(f'Jordan Weakest LPI Indicators ({int(latest_year)})')
plt.xlabel('Score')
plt.ylabel('Indicator')
plt.xlim(1, 5)
plt.grid(True, axis='x', alpha=0.3)

for i, v in enumerate(indicator_ranking['Value']):
    plt.text(v + 0.03, i, f'{v:.2f}', va='center')

plt.tight_layout()
plt.savefig('outputs/LPI_Jordan_Weakest_Indicators.png', dpi=150)
plt.show()

# ============================================================
# Plot 2 — What-if scenarios
# ============================================================
plt.figure(figsize=(11, 6))

plt.plot(
    jordan_overall['Year'],
    jordan_overall['Value'],
    'o-',
    linewidth=2,
    label='Historical Overall LPI'
)

plt.plot(years_future, baseline, 'o--', linewidth=2, label='Baseline')
plt.plot(years_future, scenario_worst_1, 'o-', linewidth=2, label=f'Improve {worst_1_name}')
plt.plot(years_future, scenario_worst_2, 'o-', linewidth=2, label=f'Improve {worst_2_name}')
plt.plot(years_future, scenario_combined, 'o-', linewidth=2, label=f'Improve Both')
plt.plot(years_future, decline, 'o-', linewidth=2, label='Decline Scenario')

plt.axvline(x=2023, linestyle='--', alpha=0.6, label='Scenario Start')

plt.title('Jordan What-if Analysis Based on Weakest LPI Indicators')
plt.xlabel('Year')
plt.ylabel('LPI Overall Score')
plt.ylim(1, 5)
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('outputs/LPI_WhatIf_Jordan_Indicators.png', dpi=150)
plt.show()

# ============================================================
# Save outputs
# ============================================================
results.to_csv('outputs/LPI_WhatIf_Jordan_Indicators.csv', index=False)
indicator_ranking.to_csv('outputs/LPI_Jordan_Indicator_Ranking.csv', index=False)
impact_df.to_csv('outputs/LPI_Jordan_Indicator_Impact.csv', index=False)

print("\nSaved:")
print("outputs/LPI_Jordan_Weakest_Indicators.png")
print("outputs/LPI_WhatIf_Jordan_Indicators.png")
print("outputs/LPI_WhatIf_Jordan_Indicators.csv")
print("outputs/LPI_Jordan_Indicator_Ranking.csv")
print("outputs/LPI_Jordan_Indicator_Impact.csv")

print("\nDONE ✅ Indicator-based What-if analysis completed")
# What-if analysis based on weakest LPI indicators
# Not a prediction model — scenario simulation