import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

df = pd.read_csv("data/LPI_interpolated.csv")

indicators = {
    "LP.LPI.CUST.XQ": "Customs",
    "LP.LPI.INFR.XQ": "Infrastructure",
    "LP.LPI.ITRN.XQ": "International_Shipments",
    "LP.LPI.LOGS.XQ": "Logistics_Quality",
    "LP.LPI.TRAC.XQ": "Tracking_Tracing",
    "LP.LPI.TIME.XQ": "Timeliness"
}

future_years = np.array([2024, 2025, 2026]).reshape(-1, 1)
results = []

for code, name in indicators.items():
    temp = df[
        (df["Country Code"] == "JOR") &
        (df["Indicator Code"] == code)
    ].dropna(subset=["Value"]).sort_values("Year")

    train = temp[temp["Year"] <= 2023]

    X = train["Year"].values.reshape(-1, 1)
    y = train["Value"].values

    model = LinearRegression()
    model.fit(X, y)

    preds = model.predict(future_years)
    preds = np.clip(preds, 1.0, 5.0)

    for year, pred in zip([2024, 2025, 2026], preds):
        results.append({
            "Year": year,
            "Indicator": name,
            "Predicted Score": round(float(pred), 3)
        })

out = pd.DataFrame(results)
pivot = out.pivot(index="Year", columns="Indicator", values="Predicted Score").reset_index()

pivot.to_csv("data/LPI_Jordan_Indicators_Forecast.csv", index=False)

print("Saved: data/LPI_Jordan_Indicators_Forecast.csv")
print(pivot)