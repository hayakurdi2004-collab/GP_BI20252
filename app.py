import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Jordan LPI Decision Support Tool",
    layout="wide"
)

st.title("Jordan Logistics Performance — Decision Support Tool")
st.write(
    "Interactive Business Intelligence tool to analyze Jordan’s logistics performance, "
    "simulate improvement scenarios, and generate strategic recommendations."
)

# ============================================================
# Load data
# ============================================================
@st.cache_data
def load_data():
    return pd.read_csv("outputs/LPI_interpolated.csv")

@st.cache_data
def load_gdp():
    try:
        return pd.read_excel("data/GDP_Final.csv.xlsx")
    except Exception:
        return None

df = load_data()
gdp_df = load_gdp()

country_code = "JOR"
overall_code = "LP.LPI.OVRL.XQ"

indicator_names = {
    "LP.LPI.CUST.XQ": "Customs",
    "LP.LPI.INFR.XQ": "Infrastructure",
    "LP.LPI.ITRN.XQ": "International Shipments",
    "LP.LPI.LOGS.XQ": "Logistics Quality",
    "LP.LPI.TRAC.XQ": "Tracking & Tracing",
    "LP.LPI.TIME.XQ": "Timeliness"
}

# ============================================================
# Jordan data
# ============================================================
jordan_overall = df[
    (df["Country Code"] == country_code) &
    (df["Indicator Code"] == overall_code)
].dropna(subset=["Value"]).sort_values("Year")

latest_baseline = jordan_overall["Value"].iloc[-1]

indicator_df = df[
    (df["Country Code"] == country_code) &
    (df["Indicator Code"].isin(indicator_names.keys()))
].dropna(subset=["Value"]).copy()

latest_year = indicator_df["Year"].max()

latest_indicators = indicator_df[indicator_df["Year"] == latest_year].copy()
latest_indicators["Indicator"] = latest_indicators["Indicator Code"].map(indicator_names)

indicator_ranking = latest_indicators[
    ["Indicator", "Value"]
].sort_values("Value")

# ============================================================
# Correlations
# ============================================================
corrs = {}

for code, name in indicator_names.items():
    temp = df[
        (df["Country Code"] == country_code) &
        (df["Indicator Code"].isin([overall_code, code]))
    ].dropna(subset=["Value"])

    pivot = temp.pivot_table(
        index="Year",
        columns="Indicator Code",
        values="Value"
    ).dropna()

    if len(pivot) >= 3:
        corrs[name] = pivot[overall_code].corr(pivot[code])
    else:
        corrs[name] = 0.5

# ============================================================
# Sidebar inputs
# ============================================================
st.sidebar.header("What-if Inputs")

customs_improvement = st.sidebar.slider(
    "Customs improvement",
    0.0, 0.7, 0.25, 0.05
)

shipments_improvement = st.sidebar.slider(
    "International Shipments improvement",
    0.0, 0.7, 0.35, 0.05
)

impact_weight = st.sidebar.slider(
    "Impact weight",
    0.1, 0.7, 0.4, 0.05,
    help="Conservative multiplier translating indicator improvement into Overall LPI impact."
)

# ============================================================
# What-if calculation
# ============================================================
customs_impact = customs_improvement * corrs["Customs"] * impact_weight
shipments_impact = shipments_improvement * corrs["International Shipments"] * impact_weight

new_lpi = latest_baseline + customs_impact + shipments_impact
new_lpi = min(max(new_lpi, 1), 5)

change = new_lpi - latest_baseline

# ============================================================
# KPI cards
# ============================================================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Current / Baseline LPI", round(latest_baseline, 3))
col2.metric("Simulated LPI", round(new_lpi, 3), delta=round(change, 3))
col3.metric("Customs Impact", round(customs_impact, 3))
col4.metric("Shipments Impact", round(shipments_impact, 3))

st.divider()

# ============================================================
# Smart Recommendation Engine
# ============================================================
st.subheader("Smart Recommendation Engine")

recommendations = []

if customs_improvement >= 0.45:
    recommendations.append({
        "Priority": "High",
        "Area": "Customs",
        "Recommendation": "Aggressive Customs Digital Transformation",
        "Expected Impact": "Strong border efficiency improvement and faster logistics processing."
    })
elif customs_improvement >= 0.25:
    recommendations.append({
        "Priority": "Medium",
        "Area": "Customs",
        "Recommendation": "Partial customs automation and paperwork reduction",
        "Expected Impact": "Moderate customs efficiency improvement."
    })
else:
    recommendations.append({
        "Priority": "Low",
        "Area": "Customs",
        "Recommendation": "Current customs reforms may be insufficient",
        "Expected Impact": "Limited logistics improvement expected."
    })

if shipments_improvement >= 0.45:
    recommendations.append({
        "Priority": "High",
        "Area": "International Shipments",
        "Recommendation": "Major shipment facilitation reforms and logistics coordination upgrades",
        "Expected Impact": "Strong international logistics competitiveness improvement."
    })
elif shipments_improvement >= 0.25:
    recommendations.append({
        "Priority": "Medium",
        "Area": "International Shipments",
        "Recommendation": "Moderate shipment process optimization",
        "Expected Impact": "Noticeable shipment efficiency improvement."
    })
else:
    recommendations.append({
        "Priority": "Low",
        "Area": "International Shipments",
        "Recommendation": "Shipment improvements remain limited",
        "Expected Impact": "Minor logistics impact expected."
    })

if change >= 0.15:
    st.success(
        "High-impact scenario detected: combined logistics reforms may significantly improve Jordan’s logistics competitiveness."
    )
elif change >= 0.08:
    st.info(
        "Moderate-impact scenario detected: selected reforms may improve Jordan’s LPI gradually over time."
    )
else:
    st.warning(
        "Low-impact scenario detected: broader logistics reforms may still be required."
    )

if customs_impact > shipments_impact:
    st.write("Strategic Insight: Customs reform appears more influential than shipment facilitation alone.")
else:
    st.write("Strategic Insight: Shipment facilitation contributes strongly to projected logistics improvement.")

st.dataframe(pd.DataFrame(recommendations), width="stretch")

st.divider()

# ============================================================
# Explanation
# ============================================================
st.subheader("How the Simulation Works")

st.write(
    """
    This simulator does not change the official LPI calculation.
    It estimates how improvements in Jordan’s weak indicators may affect the Overall LPI score.
    """
)

st.code("Estimated Impact = Improvement Amount × Correlation with Overall LPI × Impact Weight")

# ============================================================
# Charts
# ============================================================
left, right = st.columns(2)

with left:
    st.subheader("Jordan Historical LPI + What-if Scenario")

    future_years = np.array([2024, 2025, 2026])

    baseline = np.array([
        latest_baseline,
        latest_baseline + 0.002,
        latest_baseline + 0.004
    ])

    scenario = baseline + np.linspace(change * 0.5, change, 3)
    decline = baseline - np.array([0.10, 0.18, 0.25])

    scenario = np.clip(scenario, 1, 5)
    decline = np.clip(decline, 1, 5)

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(jordan_overall["Year"], jordan_overall["Value"], "o-", linewidth=2, label="Historical LPI")
    ax.plot(future_years, baseline, "o--", linewidth=2, label="Baseline")
    ax.plot(future_years, scenario, "o-", linewidth=2, label="What-if Scenario")
    ax.plot(future_years, decline, "o-", linewidth=2, label="Decline Scenario")

    ax.set_title("Jordan LPI Scenario Simulation")
    ax.set_xlabel("Year")
    ax.set_ylabel("LPI Score")
    ax.set_ylim(1, 5)
    ax.grid(True, alpha=0.3)
    ax.legend()

    st.pyplot(fig)

with right:
    st.subheader(f"Jordan Weakest Indicators ({int(latest_year)})")

    fig2, ax2 = plt.subplots(figsize=(9, 5))

    ax2.barh(indicator_ranking["Indicator"], indicator_ranking["Value"])
    ax2.set_xlabel("Score")
    ax2.set_ylabel("Indicator")
    ax2.set_xlim(1, 5)
    ax2.set_title("Weakest LPI Indicators")
    ax2.grid(True, axis="x", alpha=0.3)

    for i, v in enumerate(indicator_ranking["Value"]):
        ax2.text(v + 0.03, i, f"{v:.2f}", va="center")

    st.pyplot(fig2)

# ============================================================
# Indicator impact table
# ============================================================
st.subheader("Indicator Impact Details")

impact_table = pd.DataFrame({
    "Indicator": ["Customs", "International Shipments"],
    "Assumed Improvement": [customs_improvement, shipments_improvement],
    "Correlation with Overall LPI": [
        corrs["Customs"],
        corrs["International Shipments"]
    ],
    "Estimated Impact": [
        customs_impact,
        shipments_impact
    ]
})

st.dataframe(impact_table.round(3), width="stretch")

# ============================================================
# Key insight
# ============================================================
st.subheader("Key Insight")

st.write(
    """
    Jordan’s weakest indicators are **International Shipments** and **Customs**.
    Customs has a stronger relationship with the Overall LPI score, meaning customs reform may produce
    stronger improvement effects than shipment improvements alone.
    """
)

# ============================================================
# GDP Economic Context
# ============================================================
st.divider()

st.subheader("GDP Economic Context")

if gdp_df is not None:
    jordan_gdp = gdp_df[gdp_df["Country Code"] == "JOR"].copy()

    jordan_gdp["Year"] = pd.to_numeric(jordan_gdp["Year"], errors="coerce")
    jordan_gdp["GDP"] = pd.to_numeric(jordan_gdp["GDP"], errors="coerce")

    jordan_gdp = jordan_gdp.dropna(subset=["Year", "GDP"]).sort_values("Year")

    st.write(
        """
        GDP was added as a secondary economic context dataset.
        It was not used as a forecasting feature, but it helps explain the broader economic environment
        that may support logistics development.
        """
    )

    fig3, ax3 = plt.subplots(figsize=(10, 5))

    ax3.plot(
        jordan_gdp["Year"],
        jordan_gdp["GDP"] / 1e9,
        marker="o",
        linewidth=2
    )

    ax3.set_title("Jordan GDP Trend")
    ax3.set_xlabel("Year")
    ax3.set_ylabel("GDP (Billion USD)")
    ax3.grid(True, alpha=0.3)

    st.pyplot(fig3)

    latest_gdp = jordan_gdp["GDP"].iloc[-1] / 1e9

    st.metric("Latest Jordan GDP (Billion USD)", round(latest_gdp, 2))

    st.info(
        "GDP provides economic context only. It is not treated as a direct cause of LPI improvement."
    )

else:
    st.warning("GDP dataset not found.")