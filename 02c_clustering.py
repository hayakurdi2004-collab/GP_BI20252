import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Load clean data
# ============================================================
df = pd.read_csv('outputs/LPI_clean.csv')

score_codes = {
    'LP.LPI.CUST.XQ': 'Customs',
    'LP.LPI.INFR.XQ': 'Infrastructure',
    'LP.LPI.ITRN.XQ': 'Int_Shipments',
    'LP.LPI.LOGS.XQ': 'Logistics_Quality',
    'LP.LPI.TRAC.XQ': 'Tracking',
    'LP.LPI.TIME.XQ': 'Timeliness',
    'LP.LPI.OVRL.XQ': 'LPI_Overall'
}

df_scores         = df[df['Indicator Code'].isin(score_codes.keys())].copy()
df_scores['Feature'] = df_scores['Indicator Code'].map(score_codes)

df_pivot = df_scores.pivot_table(
    index=['Country Code', 'Country Name', 'Region', 'Income Group', 'Year'],
    columns='Feature',
    values='Value'
).reset_index()

# ============================================================
# Use latest complete year per country
# ============================================================
FEATURES = ['Customs', 'Infrastructure', 'Int_Shipments',
            'Logistics_Quality', 'Tracking', 'Timeliness', 'LPI_Overall']

df_latest = (df_pivot.sort_values('Year', ascending=False)
             .dropna(subset=FEATURES)
             .groupby('Country Code')
             .first()
             .reset_index())

print(f"Countries available for clustering: {len(df_latest)}")

# ============================================================
# Scale features — KMeans sensitive to scale
# ============================================================
scaler   = StandardScaler()
X_scaled = scaler.fit_transform(df_latest[FEATURES])

# ============================================================
# Elbow method — find optimal k
# ============================================================
inertias = []
K_range  = range(2, 8)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

# ============================================================
# Apply KMeans k=4
# Low / Mid-Low / Mid-High / High performers
# ============================================================
K      = 4
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
df_latest['Cluster'] = kmeans.fit_predict(X_scaled)

cluster_means = (df_latest.groupby('Cluster')['LPI_Overall']
                 .mean().sort_values())
label_map = {
    cluster_means.index[0]: 'Low Performers',
    cluster_means.index[1]: 'Mid-Low Performers',
    cluster_means.index[2]: 'Mid-High Performers',
    cluster_means.index[3]: 'High Performers'
}
df_latest['Cluster Label'] = df_latest['Cluster'].map(label_map)

# ============================================================
# Print cluster summary
# ============================================================
print("\nCluster Summary:")
print("-" * 50)
summary = (df_latest.groupby('Cluster Label')['LPI_Overall']
           .agg(['mean', 'count', 'min', 'max']))
summary.columns = ['Avg Score', 'Countries', 'Min', 'Max']
print(summary.round(3).to_string())

print("\nFocus countries cluster assignment:")
FOCUS = ['JOR', 'SAU', 'ARE', 'EGY', 'DEU', 'SGP', 'CHN', 'USA']
focus_df = df_latest[df_latest['Country Code'].isin(FOCUS)][
    ['Country Name', 'Cluster Label', 'LPI_Overall']
].sort_values('LPI_Overall', ascending=False)
print(focus_df.to_string(index=False))

# ============================================================
# Plot 1 — Elbow curve
# Plot 2 — PCA 2D scatter
# Plot 3 — Avg score per indicator per cluster
# Plot 4 — Focus countries highlighted in clusters
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('LPI Country Clustering — K-Means (k=4)', fontsize=14, fontweight='bold')

cluster_labels_ordered = ['Low Performers', 'Mid-Low Performers',
                          'Mid-High Performers', 'High Performers']
colors = ['tomato', 'orange', 'steelblue', 'green']

# Elbow
axes[0,0].plot(K_range, inertias, 'o-', color='steelblue', linewidth=2)
axes[0,0].axvline(x=K, color='tomato', linestyle='--',
                  alpha=0.7, label=f'Chosen k={K}')
axes[0,0].set_title('Elbow Method — Optimal k')
axes[0,0].set_xlabel('Number of Clusters (k)')
axes[0,0].set_ylabel('Inertia')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# PCA scatter
pca   = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
for i, label in enumerate(cluster_labels_ordered):
    mask = df_latest['Cluster Label'] == label
    axes[0,1].scatter(X_pca[mask, 0], X_pca[mask, 1],
                      c=colors[i], label=label, alpha=0.6, s=50)

# Highlight focus countries on PCA
for code in FOCUS:
    mask = df_latest['Country Code'] == code
    if mask.sum() > 0:
        idx  = df_latest[mask].index[0]
        pos  = df_latest.index.get_loc(idx)
        name = df_latest[mask]['Country Name'].iloc[0].split(',')[0]
        axes[0,1].scatter(X_pca[pos, 0], X_pca[pos, 1],
                          s=150, edgecolors='black', linewidths=1.5,
                          zorder=5, c='yellow')
        axes[0,1].annotate(name, (X_pca[pos, 0], X_pca[pos, 1]),
                           textcoords="offset points", xytext=(5, 5),
                           fontsize=7, fontweight='bold')

axes[0,1].set_title(f'Country Clusters — PCA 2D\n'
                    f'Variance explained: {pca.explained_variance_ratio_.sum()*100:.1f}%\n'
                    f'(yellow = focus countries)')
axes[0,1].set_xlabel('PCA Component 1')
axes[0,1].set_ylabel('PCA Component 2')
axes[0,1].legend(fontsize=8)
axes[0,1].grid(True, alpha=0.3)

# Avg score per indicator per cluster
score_features = ['Customs', 'Infrastructure', 'Int_Shipments',
                  'Logistics_Quality', 'Tracking', 'Timeliness']
cluster_avg = df_latest.groupby('Cluster Label')[score_features].mean()
x     = np.arange(len(score_features))
width = 0.2

for i, label in enumerate(cluster_labels_ordered):
    if label in cluster_avg.index:
        axes[1,0].bar(x + i * width, cluster_avg.loc[label],
                      width, label=label, color=colors[i], alpha=0.8)

axes[1,0].set_title('Average Score per Indicator by Cluster')
axes[1,0].set_xticks(x + width * 1.5)
axes[1,0].set_xticklabels(score_features, rotation=20, ha='right', fontsize=8)
axes[1,0].set_ylabel('Score (1-5)')
axes[1,0].legend(fontsize=8)
axes[1,0].grid(True, alpha=0.3)

# Focus countries bar chart colored by cluster
focus_data = df_latest[df_latest['Country Code'].isin(FOCUS)].copy()
focus_data = focus_data.sort_values('LPI_Overall', ascending=True)
bar_colors = [colors[cluster_labels_ordered.index(cl)]
              for cl in focus_data['Cluster Label']]
bars = axes[1,1].barh(focus_data['Country Name'],
                       focus_data['LPI_Overall'], color=bar_colors)
axes[1,1].set_title('Focus Countries — LPI Score & Cluster')
axes[1,1].set_xlabel('LPI Overall Score')
axes[1,1].grid(True, alpha=0.3)
for bar, val, label in zip(bars, focus_data['LPI_Overall'],
                            focus_data['Cluster Label']):
    axes[1,1].text(bar.get_width() + 0.01,
                   bar.get_y() + bar.get_height()/2,
                   f'{val:.2f} | {label}',
                   va='center', fontsize=8)

plt.tight_layout()
plt.savefig('outputs/LPI_Clustering.png', dpi=150, bbox_inches='tight')
print("\nSaved: outputs/LPI_Clustering.png")
plt.show()

# ============================================================
# Save clustering results for use in forecasting
# ============================================================
df_latest[['Country Code', 'Country Name', 'Region',
           'Income Group', 'Cluster', 'Cluster Label',
           'LPI_Overall']].to_csv('outputs/LPI_Clusters.csv', index=False)
print("Saved: outputs/LPI_Clusters.csv")
print("\nDone — run next: python 03_forecasting.py")