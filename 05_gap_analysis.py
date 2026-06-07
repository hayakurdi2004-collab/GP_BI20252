import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/LPI_interpolated_FINAL.csv")

indicator_map = {
    "LP.LPI.CUST.XQ": "Customs",
    "LP.LPI.INFR.XQ": "Infrastructure",
    "LP.LPI.ITRN.XQ": "International Shipments",
    "LP.LPI.LOGS.XQ": "Logistics Quality",
    "LP.LPI.TRAC.XQ": "Tracking & Tracing",
    "LP.LPI.TIME.XQ": "Timeliness"
}

df = df[
    (df["Indicator Code"].isin(indicator_map.keys())) &
    (df["Value"].notna())
].copy()

df["Indicator"] = df["Indicator Code"].map(indicator_map)

# آخر سنة متوفرة للأردن
jordan_years = df[df["Country Code"] == "JOR"]["Year"].unique()
latest_year = max(jordan_years)

print("Latest available year for Jordan:", latest_year)

df_gap = df[df["Year"] == latest_year].copy()

jordan = df_gap[df_gap["Country Code"] == "JOR"][
    ["Indicator", "Value"]
].rename(columns={"Value": "Jordan Score"})

mena = df_gap[df_gap["Region"] == "Middle East & North Africa"]

mena_avg = mena.groupby("Indicator")["Value"].mean().reset_index()
mena_avg = mena_avg.rename(columns={"Value": "MENA Average"})

gap = jordan.merge(mena_avg, on="Indicator", how="left")
gap["Gap"] = gap["Jordan Score"] - gap["MENA Average"]
gap = gap.sort_values("Gap")

gap.to_csv("outputs/LPI_Gap_Analysis.csv", index=False)

print("\nJordan vs MENA Gap Analysis")
print(gap.round(3).to_string(index=False))

plt.figure(figsize=(10, 6))
plt.barh(gap["Indicator"], gap["Gap"])
plt.axvline(0, color="black", linewidth=1)
plt.title(f"Jordan vs MENA Average Gap Analysis ({latest_year})")
plt.xlabel("Gap = Jordan Score - MENA Average")
plt.ylabel("Indicator")
plt.grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/LPI_Gap_Analysis.png", dpi=150, bbox_inches="tight")
plt.show()

print("\nSaved:")
print("outputs/LPI_Gap_Analysis.csv")
print("outputs/LPI_Gap_Analysis.png")