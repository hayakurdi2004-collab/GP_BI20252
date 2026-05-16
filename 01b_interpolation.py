import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# ============================================================
# Load data
# ============================================================
df = pd.read_csv('outputs/LPI_clean.csv')

FILL_YEARS = list(range(2007, 2024))
interpolated = []

groups = df.groupby([
    'Country Code', 'Country Name', 'Region',
    'Income Group', 'Indicator Code', 'Indicator Short', 'Indicator Type'
])

# ============================================================
# MAIN LOOP
# ============================================================
for (cc, cn, reg, inc, ic, ish, it), grp in groups:

    grp_sorted = grp.sort_values('Year').dropna(subset=['Value'])

    if len(grp_sorted) < 2:
        continue

    known_years  = grp_sorted['Year'].values.astype(float)
    known_values = grp_sorted['Value'].values.astype(float)

    # Keep original data
    for _, row in grp_sorted.iterrows():
        interpolated.append({
            'Country Code': cc,
            'Country Name': cn,
            'Region': reg,
            'Income Group': inc,
            'Indicator Code': ic,
            'Indicator Short': ish,
            'Indicator Type': it,
            'Year': int(row['Year']),
            'Value': row['Value'],
            'Interpolated': False
        })

    # ===============================
    # TRAIN MODELS (<= 2018)
    # ===============================
    train_mask = known_years <= 2018

    if train_mask.sum() >= 3:

        X_train = known_years[train_mask].reshape(-1, 1)
        y_train = known_values[train_mask]

        lin_model = LinearRegression().fit(X_train, y_train)
        poly_model = make_pipeline(
            PolynomialFeatures(2),
            LinearRegression()
        ).fit(X_train, y_train)

        # residuals for CI
        residuals = y_train - lin_model.predict(X_train)
        std_resid = np.std(residuals)

    else:
        lin_model = None
        poly_model = None

    # ===============================
    # FILL YEARS
    # ===============================
    for year in FILL_YEARS:

        if year in known_years:
            continue

        before = known_years[known_years < year]
        after  = known_years[known_years > year]

        # --------------------------------
        # Small gaps → Interpolation
        # --------------------------------
        if len(before) > 0 and len(after) > 0:

            y_before = before.max()
            y_after  = after.min()

            if (y_after - y_before) <= 4:

                v_before = known_values[known_years == y_before][0]
                v_after  = known_values[known_years == y_after][0]

                ratio = (year - y_before) / (y_after - y_before)
                value = v_before + ratio * (v_after - v_before)

                interpolated.append({
                    'Country Code': cc,
                    'Country Name': cn,
                    'Region': reg,
                    'Income Group': inc,
                    'Indicator Code': ic,
                    'Indicator Short': ish,
                    'Indicator Type': it,
                    'Year': year,
                    'Value': round(value, 4),
                    'Interpolated': True
                })
                continue

        # --------------------------------
        # Big gap → Improved Hybrid
        # --------------------------------
        if 2018 < year < 2023 and lin_model is not None:

            pred_lin  = lin_model.predict(np.array([[year]]))[0]
            pred_poly = poly_model.predict(np.array([[year]]))[0]

            # 🔥 improved weights
            pred = 0.85 * pred_lin + 0.15 * pred_poly
            pred = np.clip(pred, 1.0, 5.0)

            # 🔥 tighter CI (80%)
            ci = 1.28 * std_resid

            interpolated.append({
                'Country Code': cc,
                'Country Name': cn,
                'Region': reg,
                'Income Group': inc,
                'Indicator Code': ic,
                'Indicator Short': ish,
                'Indicator Type': it,
                'Year': year,
                'Value': round(pred, 4),
                'Interpolated': True,
                'CI_lower': round(pred - ci, 4),
                'CI_upper': round(pred + ci, 4)
            })

# ============================================================
# FINAL DATA
# ============================================================
df_interp = pd.DataFrame(interpolated).sort_values(
    ['Country Code', 'Indicator Code', 'Year']
)

# ============================================================
# PLOT (Jordan)
# ============================================================
country = 'JOR'

orig = df[(df['Country Code']==country) &
          (df['Indicator Code']=='LP.LPI.OVRL.XQ')].dropna()

train = orig[orig['Year'] <= 2018]

X = train['Year'].values.reshape(-1,1)
y = train['Value'].values

lin_model = LinearRegression().fit(X,y)
poly_model = make_pipeline(PolynomialFeatures(2), LinearRegression()).fit(X,y)

years = np.arange(2007, 2024).reshape(-1,1)

lin_pred = lin_model.predict(years)
poly_pred = poly_model.predict(years)

# 🔥 tighter CI
residuals = y - lin_model.predict(X)
std = np.std(residuals)

ci_upper = lin_pred + 1.28*std
ci_lower = lin_pred - 1.28*std

plt.figure(figsize=(10,6))

plt.scatter(orig['Year'], orig['Value'], s=80, label='Real Data')
plt.plot(years, lin_pred, '--', label='Linear')
plt.plot(years, poly_pred, '-.', label='Polynomial')

plt.fill_between(years.flatten(), ci_lower, ci_upper,
                 alpha=0.2, label='Confidence Interval (80%)')

plt.axvspan(2018, 2023, alpha=0.1, label='Big Gap')

plt.title('Final Model (Improved Hybrid + CI)')
plt.xlabel('Year')
plt.ylabel('LPI')
plt.legend()
plt.grid()

plt.show()

# ============================================================
# SAVE
# ============================================================
df_interp.to_csv('outputs/LPI_interpolated.csv', index=False)
df_interp.to_csv('outputs/LPI_FINAL_A_PLUS.csv', index=False)

print("Saved: outputs/LPI_interpolated.csv")
print("Saved: outputs/LPI_FINAL_A_PLUS.csv")

print("DONE ✅ ")