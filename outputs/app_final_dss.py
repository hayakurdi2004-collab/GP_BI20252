import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
    return pd.read_csv("LPI_clean.csv")


df = load_data()

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
df = df.dropna(subset=["Year", "Value"]).copy()
df["Year"] = df["Year"].astype(int)

# ============================================================
# Constants
# ============================================================
JORDAN = "Jordan"
MENA = "Middle East & North Africa"
INCOME_GROUP = "Lower middle income"

# Dynamic years from the actual dataset
YEARS = sorted(df["Year"].dropna().astype(int).unique().tolist())
DEFAULT_YEAR = max(YEARS)

MAIN_INDICATORS = [
    "Customs Score",
    "Infrastructure Score",
    "Tracking Score",
    "Logistics Quality Score",
    "Int. Shipments Score",
    "Timeliness Score"
]

PLOTLY_TEMPLATE = "plotly_dark"

# ============================================================
# Helper functions
# ============================================================
def score_data(data, year=None):
    temp = data[data["Indicator Type"].eq("Score")].copy()
    if year is not None:
        temp = temp[temp["Year"].eq(year)]
    return temp.dropna(subset=["Value"])


def main_score_data(data, year=None):
    temp = score_data(data, year)
    return temp[temp["Indicator Short"].isin(MAIN_INDICATORS)].copy()


def jordan_indicator_scores(data, year):
    temp = main_score_data(data, year)
    temp = temp[temp["Country Name"].eq(JORDAN)]
    return (
        temp.groupby("Indicator Short", as_index=False)["Value"]
        .mean()
        .rename(columns={"Indicator Short": "Indicator", "Value": "Jordan Score"})
    )


def country_indicator_matrix(data, year):
    temp = main_score_data(data, year)
    matrix = temp.pivot_table(
        index=["Country Name", "Region", "Income Group"],
        columns="Indicator Short",
        values="Value",
        aggfunc="mean"
    )

    matrix = matrix.dropna(subset=MAIN_INDICATORS, how="any").reset_index()
    matrix["Overall Proxy Score"] = matrix[MAIN_INDICATORS].mean(axis=1)
    matrix["Rank"] = matrix["Overall Proxy Score"].rank(
        ascending=False,
        method="min"
    ).astype(int)

    return matrix


def get_rank(matrix, country_name=JORDAN):
    row = matrix[matrix["Country Name"].eq(country_name)]
    if row.empty:
        return np.nan
    return int(row["Rank"].iloc[0])


def simulated_rank(matrix, new_score):
    if matrix.empty:
        return np.nan

    scores = matrix["Overall Proxy Score"].dropna()
    better_or_equal = (scores >= new_score).sum()
    return int(better_or_equal + 1)


def rank_gain_for_score(matrix, current_rank, new_score):
    new_rank = simulated_rank(matrix, new_score)
    if pd.isna(current_rank) or pd.isna(new_rank):
        return 0
    return max(int(current_rank - new_rank), 0)


def mena_averages(data, year):
    temp = main_score_data(data, year)
    temp = temp[temp["Region"].eq(MENA)]
    return (
        temp.groupby("Indicator Short", as_index=False)["Value"]
        .mean()
        .rename(columns={"Indicator Short": "Indicator", "Value": "MENA Average"})
    )


def rank_trend(data):
    rows = []
    for year in YEARS:
        matrix = country_indicator_matrix(data, year)
        if not matrix.empty:
            rows.append({
                "Year": year,
                "Jordan Rank": get_rank(matrix, JORDAN)
            })
    return pd.DataFrame(rows).dropna()


def indicator_impact_table(matrix, jordan_scores):
    current_rank = get_rank(matrix)

    rows = []
    for indicator in MAIN_INDICATORS:
        current_value = float(
            jordan_scores.loc[jordan_scores["Indicator"].eq(indicator), "Jordan Score"].iloc[0]
        )

        improved_scores = jordan_scores.copy()
        improved_scores.loc[
            improved_scores["Indicator"].eq(indicator),
            "Jordan Score"
        ] = min(current_value + 0.1, 5.0)

        new_score = float(improved_scores["Jordan Score"].mean())
        gain = rank_gain_for_score(matrix, current_rank, new_score)

        rows.append({
            "Indicator": indicator,
            "Rank Gain per 0.1 Increase": gain,
            "Current Score": current_value
        })

    return pd.DataFrame(rows).sort_values("Rank Gain per 0.1 Increase", ascending=False)


def styled_priority_table(dataframe):
    return dataframe.style.background_gradient(
        subset=["Expected Rank Gain"],
        cmap="Greens"
    ).format({
        "Current Score": "{:.2f}",
        "Target Score": "{:.2f}",
        "Expected Rank Gain": "{:.0f}"
    })


def policy_goal_targets(goal, matrix, jordan_scores, mena_df):
    current_proxy = float(jordan_scores["Jordan Score"].mean())
    current_rank = get_rank(matrix)

    if goal == "Improve Overall LPI Rank by 10 positions":
        target_rank = max(current_rank - 10, 1)
        target_score = matrix.loc[
            matrix["Rank"].eq(target_rank),
            "Overall Proxy Score"
        ].max()

        if pd.isna(target_score):
            target_score = current_proxy + 0.3

        required_total = max(float(target_score) - current_proxy + 0.01, 0)

        targets = jordan_scores.copy()
        targets["Target Score"] = np.minimum(
            targets["Jordan Score"] + required_total,
            5.0
        )

    elif goal == "Reach top 50 globally":
        target_score = matrix.loc[
            matrix["Rank"].le(50),
            "Overall Proxy Score"
        ].min()

        if pd.isna(target_score):
            target_score = current_proxy + 0.5

        required_total = max(float(target_score) - current_proxy + 0.01, 0)

        targets = jordan_scores.copy()
        targets["Target Score"] = np.minimum(
            targets["Jordan Score"] + required_total,
            5.0
        )

    else:
        targets = jordan_scores.merge(mena_df, on="Indicator", how="left")
        targets["Target Score"] = np.maximum(
            targets["Jordan Score"],
            targets["MENA Average"].fillna(targets["Jordan Score"])
        )

    return targets[["Indicator", "Jordan Score", "Target Score"]]


def build_action_plan(goal, matrix, jordan_scores, mena_df):
    impacts = indicator_impact_table(matrix, jordan_scores)
    targets = policy_goal_targets(goal, matrix, jordan_scores, mena_df)

    plan = targets.merge(impacts, on="Indicator", how="left")
    plan["Expected Rank Gain"] = plan["Rank Gain per 0.1 Increase"] * (
        ((plan["Target Score"] - plan["Jordan Score"]).clip(lower=0)) / 0.1
    )

    plan = plan.sort_values(
        ["Expected Rank Gain", "Rank Gain per 0.1 Increase"],
        ascending=False
    ).reset_index(drop=True)

    plan["Priority"] = np.arange(1, len(plan) + 1)

    return plan.rename(columns={"Jordan Score": "Current Score"})[
        ["Priority", "Indicator", "Current Score", "Target Score", "Expected Rank Gain"]
    ]


def empty_warning(message):
    st.warning(message)
    st.stop()


# ============================================================
# Sidebar controls
# ============================================================
st.sidebar.title("🚚 LPI DSS Controls")

selected_year = st.sidebar.selectbox(
    "Analysis year",
    YEARS,
    index=YEARS.index(DEFAULT_YEAR)
)

st.sidebar.markdown("---")
policy_goal = st.sidebar.selectbox(
    "🎯 Policy Goal",
    [
        "Improve Overall LPI Rank by 10 positions",
        "Reach top 50 globally",
        "Outperform MENA average in all indicators"
    ]
)

st.sidebar.markdown("---")
selected_indicators = st.sidebar.multiselect(
    "Indicators shown in overview",
    MAIN_INDICATORS,
    default=MAIN_INDICATORS
)

# ============================================================
# Base analytical data
# ============================================================
year_matrix = country_indicator_matrix(df, selected_year)
jordan_scores = jordan_indicator_scores(df, selected_year)
mena_scores = mena_averages(df, selected_year)

if year_matrix.empty or jordan_scores.empty:
    empty_warning("Required Jordan LPI score data was not found for the selected year.")

jordan_current_proxy = float(jordan_scores["Jordan Score"].mean())
jordan_current_rank = get_rank(year_matrix)
latest_year = DEFAULT_YEAR

latest_jordan_scores = jordan_indicator_scores(df, latest_year)
latest_matrix = country_indicator_matrix(df, latest_year)
latest_proxy = float(latest_jordan_scores["Jordan Score"].mean())
latest_rank = get_rank(latest_matrix)

# ============================================================
# Header
# ============================================================
st.markdown(
    "<div class='main-title'>Jordan Logistics Performance Intelligence Platform</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='subtitle'>Interactive decision-support system for LPI monitoring, benchmarking, scenario simulation, and policy prioritization.</div>",
    unsafe_allow_html=True
)

# ============================================================
# KPI cards
# ============================================================
k1, k2, k3, k4 = st.columns(4)

k1.metric("Selected Year", selected_year)
k2.metric("Jordan Proxy LPI Score", f"{jordan_current_proxy:.3f}")
k3.metric("Jordan Estimated Rank", f"{jordan_current_rank}")
k4.metric("Countries Compared", f"{year_matrix['Country Name'].nunique()}")

st.divider()

# ============================================================
# Tabs
# ============================================================
tabs = st.tabs([
    "📊 Overview",
    "📉 Gap Analysis",
    "🧪 What-If Rank Simulator",
    "🌍 Peer Benchmarking",
    "🚨 Trend Alerts",
    "🎯 Smart Recommendations",
    "📋 Technical Logic"
])

# ============================================================
# Tab 1: Overview
# ============================================================
with tabs[0]:
    st.subheader("Jordan LPI Overview")

    c1, c2 = st.columns(2)

    with c1:
        trend_rows = []
        for year in YEARS:
            scores = jordan_indicator_scores(df, year)
            if not scores.empty:
                trend_rows.append({
                    "Year": year,
                    "Overall Proxy Score": scores["Jordan Score"].mean()
                })

        trend_df = pd.DataFrame(trend_rows)

        fig = px.line(
            trend_df,
            x="Year",
            y="Overall Proxy Score",
            markers=True,
            title="Jordan Overall LPI Proxy Trend",
            template=PLOTLY_TEMPLATE
        )
        fig.update_yaxes(range=[1, 5])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        visible_scores = jordan_scores[
            jordan_scores["Indicator"].isin(selected_indicators)
        ].sort_values("Jordan Score")

        fig = px.bar(
            visible_scores,
            x="Jordan Score",
            y="Indicator",
            orientation="h",
            title=f"Jordan Indicator Scores ({selected_year})",
            template=PLOTLY_TEMPLATE,
            text="Jordan Score",
            color_discrete_sequence=["#8B1E3F"]
        )
        fig.update_xaxes(range=[1, 5])
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    priority_table = jordan_scores.copy()
    priority_table["Priority Status"] = priority_table["Jordan Score"].apply(
        lambda x: "High Priority" if x < 2.6 else "Needs Improvement" if x < 3.1 else "Strength"
    )

    st.subheader("Indicator Priority Summary")
    st.dataframe(
        priority_table.sort_values("Jordan Score").round(3),
        use_container_width=True
    )

# ============================================================
# Feature 1: Gap Analysis Dashboard
# ============================================================
with tabs[1]:
    st.subheader("Gap Analysis Dashboard")

    gap_df = jordan_scores.merge(mena_scores, on="Indicator", how="left")
    gap_df["Gap"] = gap_df["Jordan Score"] - gap_df["MENA Average"]
    gap_df["Status"] = np.where(gap_df["Gap"] >= 0, "Above MENA", "Below MENA")

    if gap_df["MENA Average"].isna().all():
        st.warning("MENA averages could not be calculated for this year.")
    else:
        plot_df = gap_df.melt(
            id_vars=["Indicator", "Gap", "Status"],
            value_vars=["Jordan Score", "MENA Average"],
            var_name="Series",
            value_name="Score"
        )

        fig = px.bar(
            plot_df,
            x="Score",
            y="Indicator",
            color="Series",
            barmode="group",
            orientation="h",
            title=f"Jordan vs MENA Average by Indicator ({selected_year})",
            template=PLOTLY_TEMPLATE,
            text="Score",
            color_discrete_map={
                "Jordan Score": "#2ecc71",
                "MENA Average": "#e74c3c"
            }
        )
        fig.update_xaxes(range=[1, 5])
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        weakest = gap_df.sort_values("Gap").iloc[0]
        st.info(
            f"Jordan's weakest indicator vs MENA peers is "
            f"**{weakest['Indicator']}** with a gap of "
            f"**{abs(weakest['Gap']):.2f}** points."
        )

        st.dataframe(gap_df.round(3), use_container_width=True)

# ============================================================
# Feature 2: What-If Rank Simulator
# ============================================================
with tabs[2]:
    st.subheader("What-If Rank Simulator")

    slider_values = {}

    slider_cols = st.columns(2)
    for idx, row in jordan_scores.iterrows():
        indicator = row["Indicator"]
        current_value = float(row["Jordan Score"])

        with slider_cols[idx % 2]:
            slider_values[indicator] = st.slider(
                indicator,
                min_value=float(current_value),
                max_value=5.0,
                value=float(current_value),
                step=0.05
            )

    simulated_score = float(np.mean(list(slider_values.values())))
    simulated_rank_value = simulated_rank(year_matrix, simulated_score)
    positions_gained = max(jordan_current_rank - simulated_rank_value, 0)

    m1, m2, m3 = st.columns(3)
    m1.metric("Current Rank", jordan_current_rank)
    m2.metric("Simulated Rank", simulated_rank_value)
    m3.metric("Positions Gained", positions_gained)

    improvement_rows = []

    for indicator in MAIN_INDICATORS:
        base_value = float(
            jordan_scores.loc[
                jordan_scores["Indicator"].eq(indicator),
                "Jordan Score"
            ].iloc[0]
        )

        new_values = jordan_scores.set_index("Indicator")["Jordan Score"].to_dict()
        new_values[indicator] = min(base_value + 0.1, 5.0)

        test_score = float(np.mean(list(new_values.values())))
        gain = rank_gain_for_score(year_matrix, jordan_current_rank, test_score)

        improvement_rows.append({
            "Indicator": indicator,
            "Rank Improvement per 0.1 Score Increase": gain
        })

    improvement_df = pd.DataFrame(improvement_rows).sort_values(
        "Rank Improvement per 0.1 Score Increase",
        ascending=False
    )

    fig = px.bar(
        improvement_df,
        x="Rank Improvement per 0.1 Score Increase",
        y="Indicator",
        orientation="h",
        title="Rank Improvement per Unit of Effort",
        template=PLOTLY_TEMPLATE,
        color="Rank Improvement per 0.1 Score Increase",
        color_continuous_scale="Greens"
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# Feature 3: Peer Benchmarking
# ============================================================
with tabs[3]:
    st.subheader('Peer Benchmarking — "Learn from Similar Countries"')

    peer_pool = year_matrix[
        (
            year_matrix["Income Group"].eq(INCOME_GROUP)
            | year_matrix["Region"].eq(MENA)
        )
        & ~year_matrix["Country Name"].eq(JORDAN)
    ].copy()

    jordan_vector = year_matrix[
        year_matrix["Country Name"].eq(JORDAN)
    ][MAIN_INDICATORS]

    if peer_pool.empty or jordan_vector.empty:
        st.warning("Peer benchmarking data is unavailable for this year.")
    else:
        jordan_vector = jordan_vector.iloc[0].astype(float).values

        peer_pool["Distance"] = peer_pool[MAIN_INDICATORS].apply(
            lambda row: np.linalg.norm(row.astype(float).values - jordan_vector),
            axis=1
        )

        top_peers = peer_pool.nsmallest(3, "Distance")
        radar_countries = pd.concat([
            year_matrix[year_matrix["Country Name"].eq(JORDAN)],
            top_peers
        ])

        fig = go.Figure()

        for _, row in radar_countries.iterrows():
            values = [row[ind] for ind in MAIN_INDICATORS]
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=MAIN_INDICATORS + [MAIN_INDICATORS[0]],
                fill="toself",
                name=row["Country Name"]
            ))

        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            title="Jordan vs Closest Peer Countries",
            polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        peer_name = top_peers.iloc[0]["Country Name"]
        peer_row = top_peers.iloc[0]

        comparison_rows = []
        for indicator in MAIN_INDICATORS:
            jordan_value = float(
                year_matrix.loc[
                    year_matrix["Country Name"].eq(JORDAN),
                    indicator
                ].iloc[0]
            )
            peer_value = float(peer_row[indicator])

            comparison_rows.append({
                "Indicator": indicator,
                "Jordan Score": jordan_value,
                f"{peer_name} Score": peer_value,
                "Gap": peer_value - jordan_value
            })

        comparison_df = pd.DataFrame(comparison_rows)
        st.dataframe(comparison_df.round(3), use_container_width=True)

        strongest_gap = comparison_df.sort_values("Gap", ascending=False).iloc[0]
        st.success(
            f"{peer_name} outperforms Jordan most in "
            f"**{strongest_gap['Indicator']}** by "
            f"**{strongest_gap['Gap']:.2f}** points."
        )

# ============================================================
# Feature 4: Trend Alert
# ============================================================
with tabs[4]:
    st.subheader("Trend Alert — Improvement & Decline Tracker")

    start_year = 2016 if 2016 in YEARS else min(YEARS)
    end_year = DEFAULT_YEAR

    scores_start = jordan_indicator_scores(df, start_year).rename(
        columns={"Jordan Score": f"Score {start_year}"}
    )
    scores_end = jordan_indicator_scores(df, end_year).rename(
        columns={"Jordan Score": f"Score {end_year}"}
    )

    trend_compare = scores_start.merge(scores_end, on="Indicator", how="inner")
    trend_compare["Change"] = trend_compare[f"Score {end_year}"] - trend_compare[f"Score {start_year}"]
    trend_compare["% Change"] = np.where(
        trend_compare[f"Score {start_year}"] != 0,
        trend_compare["Change"] / trend_compare[f"Score {start_year}"] * 100,
        np.nan
    )
    trend_compare["Direction"] = np.where(
        trend_compare["Change"] >= 0,
        "Improved",
        "Declined"
    )

    fig = px.bar(
        trend_compare.sort_values("Change"),
        x="Change",
        y="Indicator",
        orientation="h",
        color="Direction",
        title=f"Jordan Indicator Change: {start_year} to {end_year}",
        template=PLOTLY_TEMPLATE,
        text="% Change",
        color_discrete_map={
            "Improved": "#2ecc71",
            "Declined": "#e74c3c"
        }
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="white")
    st.plotly_chart(fig, use_container_width=True)

    declined = trend_compare[trend_compare["Change"] < 0].sort_values("% Change")

    if declined.empty:
        st.success(f"No indicator declined between {start_year} and {end_year}.")
    else:
        worst_decline = declined.iloc[0]
        st.error(
            f"⚠️ {worst_decline['Indicator']} declined by "
            f"{abs(worst_decline['% Change']):.1f}% — requires immediate attention."
        )

    st.dataframe(trend_compare.round(3), use_container_width=True)

    rank_df = rank_trend(df)

    fig_rank = px.line(
        rank_df,
        x="Year",
        y="Jordan Rank",
        markers=True,
        title="Jordan Overall Rank Trend",
        template=PLOTLY_TEMPLATE
    )
    fig_rank.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_rank, use_container_width=True)

# ============================================================
# Feature 5: Smart Recommendation Engine
# ============================================================
with tabs[5]:
    st.subheader("DSS Smart Recommendation Engine")

    action_plan = build_action_plan(
        policy_goal,
        year_matrix,
        jordan_scores,
        mena_scores
    )

    st.markdown(f"### Selected Policy Goal: {policy_goal}")

    st.dataframe(
        styled_priority_table(action_plan),
        use_container_width=True
    )

    top_action = action_plan.iloc[0]
    improved_score = min(
        float(
            jordan_scores.loc[
                jordan_scores["Indicator"].eq(top_action["Indicator"]),
                "Jordan Score"
            ].iloc[0]
        ) + 0.5,
        5.0
    )

    test_scores = jordan_scores.copy()
    test_scores.loc[
        test_scores["Indicator"].eq(top_action["Indicator"]),
        "Jordan Score"
    ] = improved_score

    new_proxy_score = float(test_scores["Jordan Score"].mean())
    gain_from_half_point = rank_gain_for_score(
        year_matrix,
        jordan_current_rank,
        new_proxy_score
    )

    st.success(
        f"To achieve **{policy_goal}**, focus first on "
        f"**{top_action['Indicator']}** — a 0.5 point improvement could move "
        f"Jordan up **{gain_from_half_point}** positions."
    )

    fig = px.bar(
        action_plan,
        x="Expected Rank Gain",
        y="Indicator",
        orientation="h",
        color="Expected Rank Gain",
        title="Prioritized Reform Impact",
        template=PLOTLY_TEMPLATE,
        color_continuous_scale="Greens"
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# Technical Logic
# ============================================================
with tabs[6]:
    st.subheader("Simulation Methodology")

    st.write(
        """
        This DSS uses the six LPI score indicators as a proxy for Jordan's Overall LPI Score.
        The proxy score is calculated as the simple average of the six indicators.
        Simulated ranks are estimated by comparing Jordan's simulated proxy score against
        other countries' proxy scores in the selected year.
        """
    )

    st.code(
        """
Overall Proxy Score = average(
    Customs Score,
    Infrastructure Score,
    Tracking Score,
    Logistics Quality Score,
    Int. Shipments Score,
    Timeliness Score
)

Simulated Rank = 1 + count(countries with Overall Proxy Score >= Jordan simulated score)
        """
    )

    st.subheader("Data Notes")

    st.write(
        f"""
        - Dataset file used: `LPI_clean.csv`
        - Jordan's country name is expected to be exactly `Jordan`.
        - Missing values are dropped before calculations.
        - Available analysis years are loaded dynamically from the dataset: {YEARS}
        - If interpolated years exist in the dataset, they are included automatically.
        - Countries missing any of the six score indicators in a selected year are excluded from rank simulation.
        - Rank simulation is an analytical proxy, not the official World Bank LPI ranking formula.
        """
    )

# ============================================================
# Footer
# ============================================================
st.divider()
st.caption(
    "Jordan Logistics Performance Intelligence Platform | Streamlit Decision-Support System"
)