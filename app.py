import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Jordan Logistics Performance Intelligence Platform",
    page_icon="🚚",
    layout="wide"
)

# ============================================================
# CUSTOM UI
# ============================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0f10 0%, #171717 55%, #20151a 100%);
    color: #ffffff;
}

.main-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: white;
}

.subtitle {
    color: #cfcfcf;
    margin-bottom: 1rem;
}

div[data-testid="stSidebar"] {
    background: #111111;
}

div[data-testid="stMetricValue"] {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    return pd.read_csv("outputs/LPI_clean.csv")

df = load_data()

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

df = df.dropna(subset=["Year", "Value"]).copy()

df["Year"] = df["Year"].astype(int)

# ============================================================
# CONSTANTS
# ============================================================
JORDAN = "Jordan"
MENA = "Middle East & North Africa"

MAIN_INDICATORS = [
    "Customs Score",
    "Infrastructure Score",
    "Tracking Score",
    "Logistics Quality Score",
    "Int. Shipments Score",
    "Timeliness Score"
]

YEARS = sorted(df["Year"].unique().tolist())
DEFAULT_YEAR = max(YEARS)

PLOTLY_TEMPLATE = "plotly_dark"

# ============================================================
# HELPERS
# ============================================================
def score_df(data, year):

    temp = data[
        (data["Indicator Type"] == "Score") &
        (data["Year"] == year)
    ].copy()

    return temp


def jordan_scores(data, year):

    temp = score_df(data, year)

    temp = temp[
        (temp["Country Name"] == JORDAN) &
        (temp["Indicator Short"].isin(MAIN_INDICATORS))
    ]

    return (
        temp.groupby("Indicator Short", as_index=False)["Value"]
        .mean()
        .rename(columns={
            "Indicator Short": "Indicator",
            "Value": "Jordan Score"
        })
    )


def mena_scores(data, year):

    temp = score_df(data, year)

    temp = temp[
        (temp["Region"] == MENA) &
        (temp["Indicator Short"].isin(MAIN_INDICATORS))
    ]

    return (
        temp.groupby("Indicator Short", as_index=False)["Value"]
        .mean()
        .rename(columns={
            "Indicator Short": "Indicator",
            "Value": "MENA Average"
        })
    )


def country_matrix(data, year):

    temp = score_df(data, year)

    temp = temp[
        temp["Indicator Short"].isin(MAIN_INDICATORS)
    ]

    matrix = temp.pivot_table(
        index=["Country Name", "Region", "Income Group"],
        columns="Indicator Short",
        values="Value",
        aggfunc="mean"
    )

    matrix = matrix.dropna().reset_index()

    matrix["Overall Proxy Score"] = matrix[
        MAIN_INDICATORS
    ].mean(axis=1)

    matrix["Rank"] = matrix[
        "Overall Proxy Score"
    ].rank(
        ascending=False,
        method="min"
    ).astype(int)

    return matrix


def jordan_rank(matrix):

    row = matrix[
        matrix["Country Name"] == JORDAN
    ]

    if row.empty:
        return np.nan

    return int(row["Rank"].iloc[0])


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🚚 DSS Controls")

selected_year = st.sidebar.selectbox(
    "Select Year",
    YEARS,
    index=YEARS.index(DEFAULT_YEAR)
)

policy_goal = st.sidebar.selectbox(
    "🎯 Policy Goal",
    [
        "Improve Overall LPI Rank by 10 positions",
        "Reach top 50 globally",
        "Outperform MENA average in all indicators"
    ]
)

# ============================================================
# BASE DATA
# ============================================================
year_matrix = country_matrix(df, selected_year)

jord = jordan_scores(df, selected_year)

mena = mena_scores(df, selected_year)

current_proxy = float(jord["Jordan Score"].mean())

current_rank = jordan_rank(year_matrix)

# ============================================================
# HEADER
# ============================================================
st.markdown(
    "<div class='main-title'>Jordan Logistics Performance Intelligence Platform</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Interactive Decision Support System for Jordan's Logistics Performance</div>",
    unsafe_allow_html=True
)

# ============================================================
# KPI CARDS
# ============================================================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Selected Year", selected_year)
c2.metric("Jordan Proxy Score", round(current_proxy, 3))
c3.metric("Estimated Rank", current_rank)
c4.metric("Countries", year_matrix["Country Name"].nunique())

st.divider()

# ============================================================
# TABS
# ============================================================
tabs = st.tabs([
    "📊 Overview",
    "📉 Gap Analysis",
    "🧪 What-if Simulator",
    "🌍 Peer Benchmarking",
    "🚨 Trend Alerts",
    "🎯 Smart Recommendations",
    "📋 Methodology"
])

# ============================================================
# OVERVIEW
# ============================================================
with tabs[0]:

    st.subheader("Jordan LPI Overview")

    left, right = st.columns(2)

    with left:

        trend_rows = []

        for y in YEARS:

            temp = jordan_scores(df, y)

            if not temp.empty:

                trend_rows.append({
                    "Year": y,
                    "Overall Proxy Score":
                    temp["Jordan Score"].mean()
                })

        trend_df = pd.DataFrame(trend_rows)

        fig = px.line(
            trend_df,
            x="Year",
            y="Overall Proxy Score",
            markers=True,
            template=PLOTLY_TEMPLATE,
            title="Jordan Overall LPI Trend"
        )

        fig.update_yaxes(range=[1, 5])

        st.plotly_chart(fig, use_container_width=True)

    with right:

        fig2 = px.bar(
            jord.sort_values("Jordan Score"),
            x="Jordan Score",
            y="Indicator",
            orientation="h",
            template=PLOTLY_TEMPLATE,
            text="Jordan Score",
            color_discrete_sequence=["#8B1E3F"],
            title=f"Jordan Indicator Scores ({selected_year})"
        )

        fig2.update_xaxes(range=[1, 5])

        st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# GAP ANALYSIS
# ============================================================
with tabs[1]:

    st.subheader("Gap Analysis Dashboard")

    gap_df = jord.merge(
        mena,
        on="Indicator",
        how="left"
    )

    gap_df["Gap"] = (
        gap_df["Jordan Score"] -
        gap_df["MENA Average"]
    )

    weakest = gap_df.sort_values("Gap").iloc[0]

    plot_df = gap_df.melt(
        id_vars=["Indicator"],
        value_vars=[
            "Jordan Score",
            "MENA Average"
        ],
        var_name="Series",
        value_name="Score"
    )

    fig = px.bar(
        plot_df,
        x="Score",
        y="Indicator",
        color="Series",
        orientation="h",
        barmode="group",
        template=PLOTLY_TEMPLATE,
        text="Score",
        title="Jordan vs MENA Average"
    )

    fig.update_xaxes(range=[1, 5])

    st.plotly_chart(fig, use_container_width=True)

    st.warning(
        f"Jordan's weakest indicator vs MENA peers is "
        f"{weakest['Indicator']} with a gap of "
        f"{abs(weakest['Gap']):.2f}"
    )

# ============================================================
# WHAT IF
# ============================================================
with tabs[2]:

    st.subheader("What-if Rank Simulator")

    slider_values = {}

    col1, col2 = st.columns(2)

    for idx, row in jord.iterrows():

        with col1 if idx % 2 == 0 else col2:

            slider_values[row["Indicator"]] = st.slider(
                row["Indicator"],
                min_value=float(row["Jordan Score"]),
                max_value=5.0,
                value=float(row["Jordan Score"]),
                step=0.05
            )

    simulated_score = np.mean(
        list(slider_values.values())
    )

    simulated_rank = int(
        (year_matrix["Overall Proxy Score"] >= simulated_score).sum() + 1
    )

    gained = max(current_rank - simulated_rank, 0)

    m1, m2, m3 = st.columns(3)

    m1.metric("Current Rank", current_rank)
    m2.metric("Simulated Rank", simulated_rank)
    m3.metric("Positions Gained", gained)

# ============================================================
# PEER BENCHMARKING
# ============================================================
with tabs[3]:

    st.subheader("Peer Benchmarking")

    peer_pool = year_matrix[
        (
            (year_matrix["Income Group"] == "Lower middle income")
            |
            (year_matrix["Region"] == MENA)
        )
        &
        (year_matrix["Country Name"] != JORDAN)
    ].copy()

    jordan_vector = year_matrix[
        year_matrix["Country Name"] == JORDAN
    ][MAIN_INDICATORS].iloc[0].values

    peer_pool["Distance"] = peer_pool[
        MAIN_INDICATORS
    ].apply(
        lambda row:
        np.linalg.norm(
            row.values - jordan_vector
        ),
        axis=1
    )

    top_peers = peer_pool.nsmallest(3, "Distance")

    radar_df = pd.concat([
        year_matrix[
            year_matrix["Country Name"] == JORDAN
        ],
        top_peers
    ])

    fig = go.Figure()

    for _, row in radar_df.iterrows():

        vals = [row[ind] for ind in MAIN_INDICATORS]

        fig.add_trace(
            go.Scatterpolar(
                r=vals + [vals[0]],
                theta=MAIN_INDICATORS + [MAIN_INDICATORS[0]],
                fill="toself",
                name=row["Country Name"]
            )
        )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 5]
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TREND ALERTS
# ============================================================
with tabs[4]:

    st.subheader("Trend Alerts")

    start_year = 2016 if 2016 in YEARS else min(YEARS)

    start_scores = jordan_scores(df, start_year)
    end_scores = jordan_scores(df, DEFAULT_YEAR)

    compare = start_scores.merge(
        end_scores,
        on="Indicator",
        suffixes=(" Start", " End")
    )

    compare["Change"] = (
        compare["Jordan Score End"] -
        compare["Jordan Score Start"]
    )

    compare["Direction"] = np.where(
        compare["Change"] >= 0,
        "Improved",
        "Declined"
    )

    fig = px.bar(
        compare,
        x="Change",
        y="Indicator",
        orientation="h",
        color="Direction",
        template=PLOTLY_TEMPLATE,
        color_discrete_map={
            "Improved": "#2ecc71",
            "Declined": "#e74c3c"
        },
        title=f"Indicator Change: {start_year} to {DEFAULT_YEAR}"
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# SMART RECOMMENDATIONS
# ============================================================
with tabs[5]:

    st.subheader("Smart Recommendation Engine")

    priority_df = jord.copy()

    priority_df["Priority"] = priority_df[
        "Jordan Score"
    ].rank().astype(int)

    priority_df["Target Score"] = np.minimum(
        priority_df["Jordan Score"] + 0.5,
        5.0
    )

    priority_df["Expected Rank Gain"] = (
        6 - priority_df["Priority"]
    ) * 2

    st.dataframe(
        priority_df.sort_values("Priority"),
        use_container_width=True
    )

    top_priority = priority_df.sort_values(
        "Priority"
    ).iloc[0]

    st.success(
        f"To achieve '{policy_goal}', focus first on "
        f"{top_priority['Indicator']}."
    )

# ============================================================
# METHODOLOGY
# ============================================================
with tabs[6]:

    st.subheader("Methodology")

    st.write("""
    - Overall Proxy Score = Average of the 6 LPI indicators
    - Rank Simulation compares Jordan against all countries
    - Missing values are excluded automatically
    - Years are loaded dynamically from the dataset
    - Interpolated years are included automatically if available
    """)

# ============================================================
# FOOTER
# ============================================================
st.divider()

st.caption(
    "Jordan Logistics Performance Intelligence Platform | DSS"
)