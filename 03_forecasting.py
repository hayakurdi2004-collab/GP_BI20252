import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings

warnings.filterwarnings("ignore")

DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Load data
df = pd.read_csv(DATA_DIR / "LPI_interpolated.csv")

cluster_path = OUTPUT_DIR / "LPI_Clusters.csv"
if not cluster_path.exists():
    cluster_path = DATA_DIR / "LPI_Clusters.csv"

df_cluster = pd.read_csv(cluster_path)

df_score = df[
    (df["Indicator Code"] == "LP.LPI.OVRL.XQ") &
    (df["Value"].notna())
].copy().sort_values(["Country Code", "Year"])

df_score = df_score.merge(
    df_cluster[["Country Code", "Cluster Label"]],
    on="Country Code",
    how="left"
)

country_counts = df_score.groupby("Country Code")["Year"].count()
valid_countries = country_counts[country_counts >= 4].index
df_score = df_score[df_score["Country Code"].isin(valid_countries)]

print("Max Year:", df_score["Year"].max())
print(f"Countries with 4+ data points: {len(valid_countries)}")


def compute_weights(years):
    years = np.array(years)
    recency = (years - years.min()) / (years.max() - years.min() + 1e-9)
    gaps = np.diff(years, prepend=years[0])
    gap_boost = gaps / (gaps.max() + 1e-9)
    weights = recency + 0.5 * gap_boost
    return weights / weights.sum()


def forecast_country(df_score, country_code, forecast_years):
    data = (
        df_score[df_score["Country Code"] == country_code]
        .dropna(subset=["Value"])
        .sort_values("Year")
    )

    if len(data) < 4:
        return None

    years = data["Year"].values
    y = data["Value"].values

    # Updated logic: train up to 2022, test on 2023
    train_mask = years <= 2022
    test_mask = years == 2023

    # Fallback if 2023 is missing
    if train_mask.sum() < 2 or test_mask.sum() == 0:
        train_mask = np.array([True] * (len(years) - 1) + [False])
        test_mask = np.array([False] * (len(years) - 1) + [True])

    X_train = years[train_mask].reshape(-1, 1)
    y_train = y[train_mask]
    X_test = years[test_mask].reshape(-1, 1)
    y_test = y[test_mask]

    w_train = compute_weights(years[train_mask])

    # Linear model
    m_lin = LinearRegression()
    m_lin.fit(X_train, y_train, sample_weight=w_train)

    # Polynomial model
    poly = PolynomialFeatures(degree=2)
    X_tr_p = poly.fit_transform(X_train)
    X_te_p = poly.transform(X_test)

    m_poly = LinearRegression()
    m_poly.fit(X_tr_p, y_train, sample_weight=w_train)

    err_lin = abs(m_lin.predict(X_test)[0] - y_test[0])
    err_poly = abs(m_poly.predict(X_te_p)[0] - y_test[0])

    trend = y[-1] - y[0]
    use_linear = (err_lin <= err_poly) or (trend < -0.1)

    if use_linear:
        model_name = "Linear"
        X_future = np.array(forecast_years).reshape(-1, 1)
        preds = m_lin.predict(X_future)
        y_hat_train = m_lin.predict(X_train)
        y_hat_all = m_lin.predict(years.reshape(-1, 1))
        test_pred = m_lin.predict(X_test)[0]
    else:
        model_name = "Polynomial"
        X_future = poly.transform(np.array(forecast_years).reshape(-1, 1))
        preds = m_poly.predict(X_future)
        y_hat_train = m_poly.predict(X_tr_p)
        y_hat_all = m_poly.predict(poly.transform(years.reshape(-1, 1)))
        test_pred = m_poly.predict(X_te_p)[0]

    preds = np.clip(preds, 1.0, 5.0)

    r2 = r2_score(y_train, y_hat_train, sample_weight=w_train)
    rmse = np.sqrt(mean_squared_error(y_train, y_hat_train))
    mae = mean_absolute_error(y_train, y_hat_train)
    test_error = abs(test_pred - y_test[0])

    residuals = y_train - y_hat_train
    ci = 1.5 * np.std(residuals)

    return {
        "preds": preds,
        "r2": round(r2, 3),
        "rmse": round(rmse, 3),
        "mae": round(mae, 3),
        "test_error": round(float(test_error), 3),
        "test_actual": round(float(y_test[0]), 3),
        "test_pred": round(float(test_pred), 3),
        "ci": round(float(ci), 3),
        "model": model_name,
        "data": data,
        "y_hat": y_hat_all,
        "train_mask": train_mask,
        "test_mask": test_mask,
    }


COUNTRIES = ["JOR", "SAU", "ARE", "EGY", "DEU", "SGP", "CHN", "USA"]
FORECAST_YEARS = [2024, 2025, 2026]

results = []
eval_results = []
residual_records = []

print(f"\n{'Country':<25} {'Model':<12} {'R2':>6} {'RMSE':>7} {'MAE':>7} "
      f"{'Test Actual':>12} {'Test Pred':>10} {'Test Err':>10}")
print("-" * 95)

fig, axes = plt.subplots(2, 4, figsize=(22, 11))
axes = axes.flatten()

for idx, code in enumerate(COUNTRIES):
    res = forecast_country(df_score, code, FORECAST_YEARS)
    if res is None:
        print(f"Skipped {code}")
        continue

    data = res["data"]
    name = data["Country Name"].iloc[0]
    cluster = data["Cluster Label"].iloc[0]
    years = data["Year"].values
    train_mask = res["train_mask"]
    test_mask = res["test_mask"]
    preds = res["preds"]
    ci = res["ci"]

    print(f"{name:<25} {res['model']:<12} {res['r2']:>6} {res['rmse']:>7} "
          f"{res['mae']:>7} {res['test_actual']:>12} {res['test_pred']:>10} "
          f"{res['test_error']:>10}")

    train_actual = data["Value"].values[train_mask]
    train_predicted = res["y_hat"][train_mask]
    train_years = years[train_mask]

    for yr, actual, pred in zip(train_years, train_actual, train_predicted):
        residual_records.append({
            "Country Code": code,
            "Country Name": name,
            "Year": int(yr),
            "Actual": round(float(actual), 3),
            "Predicted": round(float(pred), 3),
            "Residual": round(float(actual - pred), 3),
            "Model Used": res["model"],
        })

    ax = axes[idx]
    ax.scatter(years[train_mask], data["Value"].values[train_mask], label="Train data")
    ax.scatter(years[test_mask], data["Value"].values[test_mask], color="black", marker="D", label="Test 2023")
    ax.plot(years, res["y_hat"], "--", label=f'{res["model"]} fit')
    ax.plot(FORECAST_YEARS, preds, "s-", color="black", label="Forecast")
    ax.fill_between(
        FORECAST_YEARS,
        np.clip(preds - ci, 1.0, 5.0),
        np.clip(preds + ci, 1.0, 5.0),
        alpha=0.15,
        color="black",
        label=f"CI +/-{ci:.2f}",
    )

    ax.axvline(x=2022, linestyle=":", alpha=0.4, label="Train end")
    ax.axvline(x=2023, color="black", linestyle=":", alpha=0.4)
    ax.set_title(f"{name}\n{cluster} | {res['model']} | TestErr={res['test_error']}")
    ax.set_ylim(1, 5.4)
    ax.set_xlabel("Year")
    ax.set_ylabel("Score (1-5)")
    ax.legend(fontsize=6)
    ax.grid(True, alpha=0.3)

    for yr, pr in zip(FORECAST_YEARS, preds):
        results.append({
            "Country Code": code,
            "Country Name": name,
            "Cluster Label": cluster,
            "Model Used": res["model"],
            "Year": yr,
            "Predicted LPI Score": round(float(pr), 3),
            "CI Lower": round(float(np.clip(pr - ci, 1.0, 5.0)), 3),
            "CI Upper": round(float(np.clip(pr + ci, 1.0, 5.0)), 3),
            "R2 Train": res["r2"],
            "RMSE Train": res["rmse"],
            "MAE Train": res["mae"],
            "Test Error": res["test_error"],
        })

    eval_results.append({
        "Country Code": code,
        "Country Name": name,
        "Cluster": cluster,
        "Model Used": res["model"],
        "R2 Train": res["r2"],
        "RMSE Train": res["rmse"],
        "MAE Train": res["mae"],
        "Test Actual": res["test_actual"],
        "Test Pred": res["test_pred"],
        "Test Error": res["test_error"],
        "CI": ci,
    })

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "LPI_Forecast.png", dpi=150, bbox_inches="tight")
plt.close()

df_results = pd.DataFrame(results)
df_eval = pd.DataFrame(eval_results)
df_residuals = pd.DataFrame(residual_records)

# Save to outputs
df_results.to_csv(OUTPUT_DIR / "LPI_Forecast_Results.csv", index=False)
df_eval.to_csv(OUTPUT_DIR / "LPI_Evaluation.csv", index=False)
df_residuals.to_csv(OUTPUT_DIR / "LPI_Residuals.csv", index=False)

# Save also to data for Streamlit
df_results.to_csv(DATA_DIR / "LPI_Forecast_Results.csv", index=False)
df_eval.to_csv(DATA_DIR / "LPI_Evaluation.csv", index=False)
df_residuals.to_csv(DATA_DIR / "LPI_Residuals.csv", index=False)

print("\nSaved:")
print("outputs/LPI_Forecast_Results.csv")
print("outputs/LPI_Evaluation.csv")
print("data/LPI_Forecast_Results.csv")
print("data/LPI_Evaluation.csv")

print("\nForecast Summary:")
print(df_results.pivot_table(
    index="Country Name",
    columns="Year",
    values="Predicted LPI Score",
    aggfunc="mean"
).to_string())

print("\nEvaluation Summary:")
print(df_eval[[
    "Country Name", "Model Used", "R2 Train",
    "RMSE Train", "Test Actual", "Test Pred", "Test Error"
]].to_string(index=False))

print("\nDone.")