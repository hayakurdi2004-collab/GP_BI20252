import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Page configuration
# ============================================================
st.set_page_config(
    page_title="Jordan LPI Intelligence Platform",
    page_icon="🚚",
    layout="wide"
)

# ============================================================
# Custom UI styling
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0f10 0%, #171717 55%, #20151a 100%);
        color: #f5f5f5;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #cfcfcf;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .section-card {
        background-color: rgba(30, 30, 30, 0.92);
        border: 1px solid #4a2532;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.25);
    }

    .small-note {
        color: #bbbbbb;
        font-size: 0.9rem;
    }

    .metric-label {
        color: #c7c7c7;
        font-size: 0.86rem;
        margin-bottom: 0.25rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.75rem;
        font-weight: 800;
    }

    .metric-delta {
        color: #ff4d6d;
        font-size: 0.9rem;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 1.8rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #cfcfcf;
    }

    div[data-testid="stSidebar"] {
        background: #111111;
        border-right: 1px solid #3b1e2a;
    }

    .stSlider > div > div > div {
        color: #ff4d6d;
    }

    hr {
        border-color: #3a2029;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# Data loading
# ============================================================
@st.cache_data
def load_data():
    return pd.read_csv("outputs/LPI_interpolated.csv")


df = load_data()

# Ensure numeric columns are safe
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
df = df.dropna(subset=["Year", "Value"]).copy()
df["Year"] = df["Year"].astype(int)

# ============================================================
# Project constants
# ============================================================
COUNTRY_CODE = "JOR"
OVERALL_CODE = "LP.LPI.OVRL.XQ"

INDICATOR_NAMES = {
    "LP.LPI.CUST.XQ": "Customs",
    "LP.LPI.INFR.XQ": "Infrastructure",
    "LP.LPI.ITRN.XQ": "International Shipments",
    "LP.LPI.LOGS.XQ": "Logistics Quality",
    "LP.LPI.TRAC.XQ": "Tracking & Tracing",
    "LP.LPI.TIME.XQ": "Timeliness"
}

INDICATOR_DESCRIPTIONS = {
    "Customs": "Efficiency of customs clearance and border procedures.",
    "Infrastructure": "Quality of trade and transport infrastructure.",
    "International Shipments": "Ease of arranging competitively priced shipments.",
    "Logistics Quality": "Competence and quality of logistics services.",
    "Tracking & Tracing": "Ability to track and trace consignments.",
    "Timeliness": "Frequency with which shipments reach destination on time."
}

# ============================================================
# Helper functions
# ============================================================
def get_jordan_overall(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data[
            (data["Country Code"] == COUNTRY_CODE)
            & (data["Indicator Code"] == OVERALL_CODE)
        ]
        .dropna(subset=["Value"])
        .sort_values("Year")
    )


def get_indicator_data(data: pd.DataFrame) -> pd.DataFrame:
    indicator_df = data[
        (data["Country Code"] == COUNTRY_CODE)
        & (data["Indicator Code"].isin(INDICATOR_NAMES.keys()))
    ].dropna(subset=["Value"]).copy()

    indicator_df["Indicator"] = indicator_df["Indicator Code"].map(INDICATOR_NAMES)
    return indicator_df


def calculate_correlations(data: pd.DataFrame) -> dict:
    corrs = {}

    for code, name in INDICATOR_NAMES.items():
        temp = data[
            (data["Country Code"] == COUNTRY_CODE)
            & (data["Indicator Code"].isin([OVERALL_CODE, code]))
        ].dropna(subset=["Value"])

        pivot = temp.pivot_table(
            index="Year",
            columns="Indicator Code",
            values="Value"
        ).dropna()

        if len(pivot) >= 3 and pivot[overall_code_safe()].std() > 0 and pivot[code].std() > 0:
            corrs[name] = float(pivot[overall_code_safe()].corr(pivot[code]))
        else:
            # Conservative fallback if correlation cannot be calculated safely
            corrs[name] = 0.50

        # Avoid negative or unstable correlations in decision simulation
        if pd.isna(corrs[name]) or corrs[name] < 0:
            corrs[name] = 0.50

    return corrs


def overall_code_safe():
    return OVERALL_CODE


def priority_level(score: float) -> tuple[str, str]:
    if score >= 75:
        return "High", "High-priority reform scenario detected."
    if score >= 45:
        return "Medium", "Moderate-priority scenario detected."
    return "Low", "Low-priority scenario detected."


def status_from_score(score: float) -> str:
    if score < 2.6:
        return "High Priority"
    if score < 3.1:
        return "Needs Improvement"
    return "Strength"


def build_recommendations(
    latest_scores: pd.DataFrame,
    improvements: dict,
    impacts: dict,
    simulated_lpi: float,
    baseline_lpi: float
) -> pd.DataFrame:
    rows = []

    for indicator, current_score in latest_scores.set_index("Indicator")["Value"].items():
        improvement = improvements.get(indicator, 0)
        impact = impacts.get(indicator, 0)
        status = status_from_score(current_score)

        # More sensitive recommendation logic
        if current_score < 2.60 and improvement < 0.20:
            priority = "Critical"
            recommendation = f"Increase reform intensity for {indicator}"
            action = "Current improvement assumption is too low for a weak indicator."
            expected = "Limited improvement unless reform intensity increases."
        elif current_score < 2.60 and improvement >= 0.20:
            priority = "High"
            recommendation = f"Prioritize {indicator} reform"
            action = "Focus resources on this weak area because it has strong improvement potential."
            expected = "Meaningful improvement in Jordan’s logistics performance."
        elif 2.60 <= current_score < 3.10 and impact >= 0.04:
            priority = "Medium"
            recommendation = f"Maintain steady improvement in {indicator}"
            action = "Continue gradual operational improvement and monitor results."
            expected = "Moderate contribution to LPI improvement."
        elif current_score >= 3.10:
            priority = "Strength"
            recommendation = f"Protect existing strength in {indicator}"
            action = "Maintain service quality and prevent performance decline."
            expected = "Supports stability in overall logistics performance."
        else:
            priority = "Low"
            recommendation = f"Monitor {indicator}"
            action = "No urgent intervention required under the current scenario."
            expected = "Limited short-term change."

        rows.append({
            "Priority": priority,
            "Indicator": indicator,
            "Current Score": round(current_score, 2),
            "Assumed Improvement": round(improvement, 2),
            "Estimated Impact": round(impact, 3),
            "Recommendation": recommendation,
            "Strategic Action": action,
            "Expected Outcome": expected
        })

    # Overall scenario recommendation
    change = simulated_lpi - baseline_lpi
    if change >= 0.15:
        rows.append({
            "Priority": "Strategic",
            "Indicator": "Overall LPI",
            "Current Score": round(baseline_lpi, 2),
            "Assumed Improvement": "-",
            "Estimated Impact": round(change, 3),
            "Recommendation": "Scenario has strong strategic value",
            "Strategic Action": "Use this reform mix as a decision-support scenario for policy discussion.",
            "Expected Outcome": "Potential improvement in logistics competitiveness."
        })
    elif change >= 0.05:
        rows.append({
            "Priority": "Moderate",
            "Indicator": "Overall LPI",
            "Current Score": round(baseline_lpi, 2),
            "Assumed Improvement": "-",
            "Estimated Impact": round(change, 3),
            "Recommendation": "Scenario is useful but limited",
            "Strategic Action": "Increase reform assumptions or target weaker indicators more directly.",
            "Expected Outcome": "Moderate projected improvement."
        })
    else:
        rows.append({
            "Priority": "Low",
            "Indicator": "Overall LPI",
            "Current Score": round(baseline_lpi, 2),
            "Assumed Improvement": "-",
            "Estimated Impact": round(change, 3),
            "Recommendation": "Scenario impact is weak",
            "Strategic Action": "Current assumptions are not enough to create a meaningful LPI change.",
            "Expected Outcome": "Minimal improvement."
        })

    priority_order = {"Critical": 0, "High": 1, "Strategic": 2, "Medium": 3, "Moderate": 4, "Strength": 5, "Low": 6}
    rec_df = pd.DataFrame(rows)
    rec_df["Sort"] = rec_df["Priority"].map(priority_order).fillna(99)
    return rec_df.sort_values(["Sort", "Estimated Impact"], ascending=[True, False]).drop(columns=["Sort"])


# ============================================================
# Prepare analytical data
# ============================================================
jordan_overall = get_jordan_overall(df)
indicator_df = get_indicator_data(df)

if jordan_overall.empty or indicator_df.empty:
    st.error("Required LPI data was not found. Please check outputs/LPI_interpolated.csv.")
    st.stop()

latest_baseline = float(jordan_overall["Value"].iloc[-1])
latest_year = int(indicator_df["Year"].max())

latest_indicators = indicator_df[indicator_df["Year"] == latest_year].copy()
indicator_ranking = latest_indicators[["Indicator", "Value"]].sort_values("Value")

corrs = calculate_correlations(df)

# ============================================================
# Header
# ============================================================
st.markdown("<div class='main-title'>Jordan Logistics Performance Intelligence Platform</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Interactive decision-support web application for LPI monitoring, scenario simulation, forecasting, and strategic logistics recommendations.</div>",
    unsafe_allow_html=True
)

# ============================================================
# Sidebar: All indicators
# ============================================================
st.sidebar.title("🚚 LPI DSS Controls")
st.sidebar.caption("Adjust all logistics indicators to simulate improvement scenarios.")

impact_weight = st.sidebar.slider(
    "Impact weight",
    0.10, 0.70, 0.40, 0.05,
    help="Conservative multiplier translating indicator improvements into Overall LPI impact."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Indicator Improvements")

improvements = {}
for indicator in INDICATOR_NAMES.values():
    improvements[indicator] = st.sidebar.slider(
        indicator,
        0.00, 0.70, 0.20, 0.05
    )

st.sidebar.markdown("---")
selected_indicators = st.sidebar.multiselect(
    "Indicators shown in charts",
    list(INDICATOR_NAMES.values()),
    default=list(INDICATOR_NAMES.values())
)

# ============================================================
# What-if calculation
# ============================================================
impacts = {
    indicator: improvements[indicator] * corrs.get(indicator, 0.50) * impact_weight
    for indicator in INDICATOR_NAMES.values()
}

total_impact = sum(impacts.values())
simulated_lpi = min(max(latest_baseline + total_impact, 1), 5)
change = simulated_lpi - latest_baseline

priority_score = (
    np.mean([v / 0.70 for v in improvements.values()]) * 35
    + min(max(change / 0.30, 0), 1) * 45
    + min(max(len([v for v in improvements.values() if v >= 0.25]) / 6, 0), 1) * 20
)
priority_score = max(0, min(priority_score, 100))

scenario_level, scenario_message = priority_level(priority_score)
recommendation_df = build_recommendations(
    latest_scores=latest_indicators,
    improvements=improvements,
    impacts=impacts,
    simulated_lpi=simulated_lpi,
    baseline_lpi=latest_baseline
)

# ============================================================
# Popup / toast recommendation
# ============================================================
top_rec = recommendation_df.iloc[0]
try:
    if top_rec["Priority"] in ["Critical", "High"]:
        st.toast(f"High-impact DSS recommendation: {top_rec['Recommendation']}", icon="🚨")
    elif scenario_level == "High":
        st.toast("Strong scenario detected: projected LPI improvement is meaningful.", icon="✅")
except Exception:
    pass

# ============================================================
# KPI cards
# ============================================================
k1, k2, k3, k4 = st.columns(4)

k1.metric("Baseline LPI", f"{latest_baseline:.3f}")
k2.metric("Simulated LPI", f"{simulated_lpi:.3f}", delta=f"{change:.3f}")
k3.metric("Total Estimated Impact", f"{total_impact:.3f}")
k4.metric("Reform Priority Score", f"{priority_score:.0f}/100")

st.divider()

# ============================================================
# Executive DSS summary
# ============================================================
summary_col1, summary_col2 = st.columns([1, 2])

with summary_col1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("DSS Scenario Status")
    st.metric("Scenario Level", scenario_level)
    if scenario_level == "High":
        st.success(scenario_message)
    elif scenario_level == "Medium":
        st.info(scenario_message)
    else:
        st.warning(scenario_message)
    st.markdown("</div>", unsafe_allow_html=True)

with summary_col2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Strategic Interpretation")
    strongest_impact = max(impacts, key=impacts.get)
    weakest_indicator = indicator_ranking.iloc[0]["Indicator"]

    st.write(
        f"""
        The simulation estimates how improvements across logistics indicators may influence Jordan’s Overall LPI.
        The strongest projected contribution in the current scenario comes from **{strongest_impact}**,
        while the weakest latest indicator is **{weakest_indicator}**.
        """
    )

    if change >= 0.15:
        st.success("The selected scenario may create a meaningful improvement in Jordan’s logistics competitiveness.")
    elif change >= 0.05:
        st.info("The selected scenario indicates moderate improvement potential.")
    else:
        st.warning("The selected scenario has limited projected impact. Stronger or more targeted reforms may be needed.")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Tabs
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🧠 Decision Support",
    "📈 Forecast & Scenarios",
    "📋 Technical Logic"
])

# ============================================================
# Tab 1: Overview
# ============================================================
with tab1:
    st.subheader("Jordan LPI Overview")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### Historical Overall LPI")

        fig, ax = plt.subplots(figsize=(9, 4.8))
        ax.plot(
            jordan_overall["Year"],
            jordan_overall["Value"],
            marker="o",
            linewidth=2.5,
            color="#8B1E3F"
        )
        ax.set_xlabel("Year")
        ax.set_ylabel("LPI Score")
        ax.set_ylim(1, 5)
        ax.grid(True, alpha=0.25)
        ax.set_title("Jordan Overall LPI Trend")
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown(f"### Latest Indicator Scores ({latest_year})")

        visible_ranking = indicator_ranking[indicator_ranking["Indicator"].isin(selected_indicators)]
        fig2, ax2 = plt.subplots(figsize=(9, 4.8))
        ax2.barh(
            visible_ranking["Indicator"],
            visible_ranking["Value"],
            color="#8B1E3F"
        )
        ax2.set_xlim(1, 5)
        ax2.set_xlabel("Score")
        ax2.grid(True, axis="x", alpha=0.25)
        ax2.set_title("Jordan Logistics Indicator Profile")

        for i, value in enumerate(visible_ranking["Value"]):
            ax2.text(value + 0.03, i, f"{value:.2f}", va="center")

        st.pyplot(fig2)
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Indicator Priority Summary")
    priority_table = latest_indicators[["Indicator", "Value"]].copy()
    priority_table["Priority Status"] = priority_table["Value"].apply(status_from_score)
    priority_table = priority_table.sort_values("Value")
    st.dataframe(priority_table.round(3), use_container_width=True)

# ============================================================
# Tab 2: Decision Support
# ============================================================
with tab2:
    st.subheader("Recommended Alternative Solutions")

    st.write(
        """
        The DSS engine evaluates indicator weakness, selected improvement assumptions,
        estimated impact, and scenario strength to generate reform recommendations.
        """
    )

    st.dataframe(recommendation_df, use_container_width=True)

    st.subheader("Estimated Indicator Impact")

    impact_df = pd.DataFrame({
        "Indicator": list(impacts.keys()),
        "Assumed Improvement": [improvements[i] for i in impacts.keys()],
        "Correlation with Overall LPI": [corrs.get(i, 0.5) for i in impacts.keys()],
        "Estimated Impact": [impacts[i] for i in impacts.keys()]
    }).sort_values("Estimated Impact", ascending=False)

    impact_col1, impact_col2 = st.columns([1, 1])

    with impact_col1:
        st.dataframe(impact_df.round(3), use_container_width=True)

    with impact_col2:
        fig3, ax3 = plt.subplots(figsize=(8, 4.8))
        ax3.barh(impact_df["Indicator"], impact_df["Estimated Impact"], color="#A03C5A")
        ax3.set_xlabel("Estimated Impact")
        ax3.set_title("Estimated Reform Contribution")
        ax3.grid(True, axis="x", alpha=0.25)
        st.pyplot(fig3)

# ============================================================
# Tab 3: Forecast and scenarios
# ============================================================
with tab3:
    st.subheader("LPI Forecast and What-if Scenario Simulation")

    future_years = np.array([latest_year + 1, latest_year + 2, latest_year + 3])

    baseline = np.array([
        latest_baseline,
        latest_baseline + 0.002,
        latest_baseline + 0.004
    ])

    improvement_scenario = baseline + np.linspace(change * 0.50, change, 3)
    decline_scenario = baseline - np.array([0.08, 0.15, 0.22])

    baseline = np.clip(baseline, 1, 5)
    improvement_scenario = np.clip(improvement_scenario, 1, 5)
    decline_scenario = np.clip(decline_scenario, 1, 5)

    fig4, ax4 = plt.subplots(figsize=(11, 5.5))

    ax4.plot(
        jordan_overall["Year"],
        jordan_overall["Value"],
        "o-",
        linewidth=2.5,
        color="#ffffff",
        label="Historical LPI"
    )

    ax4.plot(
        future_years,
        baseline,
        "o--",
        linewidth=2,
        color="#9E9E9E",
        label="Baseline"
    )

    ax4.plot(
        future_years,
        improvement_scenario,
        "o-",
        linewidth=2.8,
        color="#FF4D6D",
        label="Improvement Scenario"
    )

    ax4.plot(
        future_years,
        decline_scenario,
        "o-",
        linewidth=2.3,
        color="#6D3148",
        label="Decline Scenario"
    )

    ax4.set_title("Jordan LPI Forecast and Scenario Comparison")
    ax4.set_xlabel("Year")
    ax4.set_ylabel("LPI Score")
    ax4.set_ylim(1, 5)
    ax4.grid(True, alpha=0.25)
    ax4.legend()

    st.pyplot(fig4)

    st.info(
        "Power BI summarizes scenario results visually, while this Streamlit application allows users to adjust assumptions and generate decision-support recommendations."
    )

# ============================================================
# Tab 4: Technical logic
# ============================================================
with tab4:
    st.subheader("Simulation Methodology")

    st.write(
        """
        The DSS does not change the official World Bank LPI calculation.
        It estimates potential improvement using conservative assumptions based on
        indicator improvement, historical correlation with Overall LPI, and an impact weight.
        """
    )

    st.code("Estimated Impact = Improvement Amount × Correlation with Overall LPI × Impact Weight")

    st.subheader("Correlation Inputs Used by DSS")

    corr_table = pd.DataFrame({
        "Indicator": list(corrs.keys()),
        "Correlation with Overall LPI": list(corrs.values())
    }).sort_values("Correlation with Overall LPI", ascending=False)

    st.dataframe(corr_table.round(3), use_container_width=True)

    st.subheader("Data Notes")

    st.write(
        """
        - The primary dataset is the World Bank Logistics Performance Index.
        - Missing annual gaps were handled before deployment using the project preprocessing pipeline.
        - The application focuses on logistics indicators and decision-support simulation.
        - Forecast values are scenario-based and intended for strategic exploration, not official prediction.
        """
    )

# ============================================================
# Footer
# ============================================================
st.divider()
st.caption(
    "Jordan Logistics Performance Intelligence Platform | BI Graduation Project | Streamlit Decision-Support Web Application"
)
