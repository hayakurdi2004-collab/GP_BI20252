import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Load evaluation results from forecasting step
# ============================================================
df_eval    = pd.read_csv('outputs/LPI_Evaluation.csv')
df_forecast = pd.read_csv('outputs/LPI_Forecast_Results.csv')

print("=" * 65)
print("Model Evaluation Report")
print("=" * 65)

# ============================================================
# Section 1: Train metrics
# ============================================================
print("\nSection 1 — Train Set Metrics (2007-2018)")
print("-" * 65)
print(f"{'Country':<25} {'Model':<12} {'R2':>6} {'RMSE':>8} {'MAE':>8}")
print("-" * 65)

for _, row in df_eval.iterrows():
    print(f"{row['Country Name']:<25} {row['Model Used']:<12} "
          f"{row['R2 Train']:>6} {row['RMSE Train']:>8} {row['MAE Train']:>8}")

print(f"\nAverage R2  (train): {df_eval['R2 Train'].mean():.3f}")
print(f"Average RMSE (train): {df_eval['RMSE Train'].mean():.3f}")
print(f"Average MAE  (train): {df_eval['MAE Train'].mean():.3f}")

# ============================================================
# Section 2: Test metrics (2023)
# ============================================================
print("\nSection 2 — Test Set Metrics (2023 holdout)")
print("-" * 65)
print(f"{'Country':<25} {'Actual':>8} {'Predicted':>10} {'Error':>8} {'Quality':>12}")
print("-" * 65)

for _, row in df_eval.iterrows():
    error = row['Test Error']
    if error < 0.1:
        quality = 'Excellent'
    elif error < 0.2:
        quality = 'Good'
    elif error < 0.35:
        quality = 'Acceptable'
    else:
        quality = 'Weak'

    print(f"{row['Country Name']:<25} {row['Test Actual']:>8} "
          f"{row['Test Pred']:>10} {row['Test Error']:>8} {quality:>12}")

print(f"\nAverage Test Error: {df_eval['Test Error'].mean():.3f}")
best  = df_eval.loc[df_eval['Test Error'].idxmin(), 'Country Name']
worst = df_eval.loc[df_eval['Test Error'].idxmax(), 'Country Name']
print(f"Best forecast:  {best}")
print(f"Worst forecast: {worst}")

# ============================================================
# Section 3: Forecast reliability per country
# ============================================================
print("\nSection 3 — Forecast Reliability (CI width)")
print("-" * 65)

df_ci = df_forecast.copy()
df_ci['CI Width'] = df_ci['CI Upper'] - df_ci['CI Lower']

ci_summary = (df_ci.groupby('Country Name')['CI Width']
              .mean().sort_values().reset_index())
ci_summary.columns = ['Country', 'Avg CI Width']

print(f"{'Country':<25} {'Avg CI Width':>14} {'Reliability':>14}")
print("-" * 55)
for _, row in ci_summary.iterrows():
    reliability = 'High' if row['Avg CI Width'] < 0.3 else \
                  'Medium' if row['Avg CI Width'] < 0.5 else 'Low'
    print(f"{row['Country']:<25} {row['Avg CI Width']:>14.3f} {reliability:>14}")

# ============================================================
# Section 4: Overall project quality score
# ============================================================
print("\nSection 4 — Overall Model Quality")
print("-" * 65)

avg_r2         = df_eval['R2 Train'].mean()
avg_test_error = df_eval['Test Error'].mean()
avg_ci_width   = ci_summary['Avg CI Width'].mean()

print(f"Average R2 (train):     {avg_r2:.3f} — "
      f"{'Good' if avg_r2 > 0.5 else 'Moderate'}")
print(f"Average Test Error:     {avg_test_error:.3f} — "
      f"{'Good' if avg_test_error < 0.25 else 'Moderate'}")
print(f"Average CI Width:       {avg_ci_width:.3f} — "
      f"{'Tight' if avg_ci_width < 0.3 else 'Wide'}")

# ============================================================
# Plots
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Model Evaluation Report — LPI Forecasting',
             fontsize=13, fontweight='bold')

# R2 per country
colors_r2 = ['green' if r > 0.6 else 'orange' if r > 0.3 else 'tomato'
              for r in df_eval['R2 Train']]
axes[0].barh(df_eval['Country Name'], df_eval['R2 Train'], color=colors_r2)
axes[0].axvline(x=0.5, color='black', linestyle='--',
                linewidth=1, label='R2=0.5 threshold')
axes[0].set_title('R2 Score — Train Set\n(green > 0.6, orange > 0.3, red < 0.3)')
axes[0].set_xlabel('R2')
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3)
for i, (name, val) in enumerate(zip(df_eval['Country Name'], df_eval['R2 Train'])):
    axes[0].text(val + 0.01, i, f'{val:.3f}', va='center', fontsize=8)

# Test error per country
colors_te = ['green' if e < 0.1 else 'orange' if e < 0.35 else 'tomato'
             for e in df_eval['Test Error']]
axes[1].barh(df_eval['Country Name'], df_eval['Test Error'], color=colors_te)
axes[1].axvline(x=0.2, color='black', linestyle='--',
                linewidth=1, label='Error=0.2 threshold')
axes[1].set_title('Test Error — 2023 Holdout\n(green < 0.1, orange < 0.35, red > 0.35)')
axes[1].set_xlabel('Absolute Error')
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.3)
for i, (name, val) in enumerate(zip(df_eval['Country Name'], df_eval['Test Error'])):
    axes[1].text(val + 0.005, i, f'{val:.3f}', va='center', fontsize=8)

# Actual vs Predicted 2023
axes[2].scatter(df_eval['Test Actual'], df_eval['Test Pred'],
                s=100, color='steelblue', zorder=3)
min_val = min(df_eval['Test Actual'].min(), df_eval['Test Pred'].min()) - 0.1
max_val = max(df_eval['Test Actual'].max(), df_eval['Test Pred'].max()) + 0.1
axes[2].plot([min_val, max_val], [min_val, max_val],
             'k--', linewidth=1, label='Perfect prediction')
for _, row in df_eval.iterrows():
    axes[2].annotate(row['Country Name'].split(',')[0],
                     (row['Test Actual'], row['Test Pred']),
                     textcoords="offset points", xytext=(5, 5), fontsize=7)
axes[2].set_title('Actual vs Predicted — 2023\n(closer to diagonal = better)')
axes[2].set_xlabel('Actual 2023 Score')
axes[2].set_ylabel('Predicted 2023 Score')
axes[2].legend(fontsize=8)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/LPI_Evaluation.png', dpi=150, bbox_inches='tight')
print("\nSaved: outputs/LPI_Evaluation.png")
plt.show()

print("\nDone — run next: python 04_whatif.py")