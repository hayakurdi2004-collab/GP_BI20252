import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# Load interpolated data
# ============================================================
df = pd.read_csv("outputs/LPI_interpolated.csv")

score_codes = {
    "LP.LPI.CUST.XQ": "Customs",
    "LP.LPI.INFR.XQ": "Infrastructure",
    "LP.LPI.ITRN.XQ": "International_Shipments",
    "LP.LPI.LOGS.XQ": "Logistics_Quality",
    "LP.LPI.TRAC.XQ": "Tracking_Tracing",
    "LP.LPI.TIME.XQ": "Timeliness",
    "LP.LPI.OVRL.XQ": "LPI_Overall"
}

df_scores = df[df["Indicator Code"].isin(score_codes.keys())].copy()
df_scores["Feature"] = df_scores["Indicator Code"].map(score_codes)

df_pivot = df_scores.pivot_table(
    index=["Country Code", "Country Name", "Region", "Income Group", "Year"],
    columns="Feature",
    values="Value"
).reset_index()

features = [
    "Customs",
    "Infrastructure",
    "International_Shipments",
    "Logistics_Quality",
    "Tracking_Tracing",
    "Timeliness",
    "LPI_Overall"
]

df_pivot = df_pivot.dropna(subset=features)

# ============================================================
# Clustering per year
# ============================================================
all_year_results = []

for year in sorted(df_pivot["Year"].unique()):

    data_year = df_pivot[df_pivot["Year"] == year].copy()

    if len(data_year) < 10:
        continue

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data_year[features])

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    data_year["Cluster"] = kmeans.fit_predict(X_scaled)

    cluster_means = data_year.groupby("Cluster")["LPI_Overall"].mean().sort_values()

    label_map = {
        cluster_means.index[0]: "Low Performers",
        cluster_means.index[1]: "Mid-Low Performers",
        cluster_means.index[2]: "Mid-High Performers",
        cluster_means.index[3]: "High Performers"
    }

    data_year["Cluster Label"] = data_year["Cluster"].map(label_map)

    all_year_results.append(data_year)

df_year_clusters = pd.concat(all_year_results, ignore_index=True)

# ============================================================
# Jordan cluster over time
# ============================================================
jordan = df_year_clusters[df_year_clusters["Country Code"] == "JOR"].copy()

print("\nJordan Cluster Movement Over Time:")
print(jordan[["Year", "Country Name", "LPI_Overall", "Cluster Label"]].to_string(index=False))

# ============================================================
# Save outputs
# ============================================================
df_year_clusters.to_csv("outputs/LPI_Clusters_By_Year.csv", index=False)
jordan.to_csv("outputs/LPI_Jordan_Cluster_By_Year.csv", index=False)

print("\nSaved: outputs/LPI_Clusters_By_Year.csv")
print("Saved: outputs/LPI_Jordan_Cluster_By_Year.csv")

# ============================================================
# Plot Jordan cluster movement
# ============================================================
plt.figure(figsize=(10, 6))

plt.plot(jordan["Year"], jordan["LPI_Overall"], "o-", linewidth=2)

for _, row in jordan.iterrows():
    plt.text(
        row["Year"],
        row["LPI_Overall"] + 0.03,
        row["Cluster Label"],
        ha="center",
        fontsize=8
    )

plt.title("Jordan Cluster Movement Over Time")
plt.xlabel("Year")
plt.ylabel("LPI Overall Score")
plt.ylim(1, 5)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/LPI_Jordan_Cluster_Movement.png", dpi=150)
plt.show()

print("Saved: outputs/LPI_Jordan_Cluster_Movement.png")
print("\nDONE ✅ clustering by year completed")