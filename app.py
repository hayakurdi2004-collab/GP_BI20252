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
    "Interactive tool to simulate how improving Jordan’s weakest logistics indicators "
    "could affect the Overall Logistics Performance Index (LPI)."
)

# ============================================================
# Load data
# ============================================================
@st.cache_data
def load_data():
    return pd.read_csv("outputs/LPI_interpolated.csv")

df = load_data()

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
# Jordan overall data
# ============================================================
jordan_overall = df[
    (df["Country Code"] == country_code) &
    (df["Indicator Code"] == overall_code)
].dropna(subset=["Value"]).sort_values("Year")

latest_baseline = jordan_overall["Value"].iloc[-1]

# ============================================================
# Jordan indicators latest values
# ============================================================
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
# Correlations with overall LPI
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
    min_value=0.0,
    max_value=0.7,
    value=0.25,
    step=0.05
)

shipments_improvement = st.sidebar.slider(
    "International Shipments improvement",
    min_value=0.0,
    max_value=0.7,
    value=0.35,
    step=0.05
)

impact_weight = st.sidebar.slider(
    "Impact weight",
    min_value=0.1,
    max_value=0.7,
    value=0.4,
    step=0.05,
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
# Recommendation engine
# ============================================================
st.subheader("Recommended Alternative Solutions")

recommendations = []

if customs_improvement >= 0.25:
    recommendations.append({
        "Solution": "Digital Customs Reform",
        "Action": "Automate customs clearance, reduce paperwork, and improve border processing.",
        "Expected Benefit": "Faster clearance and higher logistics efficiency."
    })

if shipments_improvement >= 0.25:
    recommendations.append({
        "Solution": "International Shipment Facilitation",
        "Action": "Improve shipment procedures, reduce delays, and strengthen logistics coordination.",
        "Expected Benefit": "Better shipment reliability and easier trade operations."
    })

if change >= 0.12:
    st.success(
        "Strong improvement scenario: the selected reforms could noticeably improve Jordan’s LPI performance."
    )
elif change >= 0.06:
    st.info(
        "Moderate improvement scenario: the selected reforms may improve Jordan’s LPI, but more reforms are needed."
    )
else:
    st.warning(
        "Limited improvement scenario: current changes may not be enough to significantly improve Jordan’s position."
    )

if recommendations:
    st.table(pd.DataFrame(recommendations))
else:
    st.write("Increase one of the improvement sliders to generate alternative solution recommendations.")

st.divider()

# ============================================================
# Explanation
# ============================================================
st.subheader("How the simulation works")

st.write(
    """
    This simulator does not change the original LPI calculation.
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

    ax.plot(
        jordan_overall["Year"],
        jordan_overall["Value"],
        "o-",
        linewidth=2,
        label="Historical LPI"
    )

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

    ax2.barh(
        indicator_ranking["Indicator"],
        indicator_ranking["Value"]
    )

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
# Final insight
# ============================================================
st.subheader("Key Insight")

st.write(
    """
    Jordan’s weakest indicators are **International Shipments** and **Customs**.
    However, Customs has a stronger relationship with the Overall LPI score, meaning that customs reform
    may produce a stronger improvement effect than shipment improvements alone.
    """
)