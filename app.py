import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
try:
    from wb_api import fetch_jordan_latest
    WB_API_AVAILABLE = True
except Exception:
    WB_API_AVAILABLE = False

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jordan LPI Decision Support System",
    page_icon="🇯🇴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colors ────────────────────────────────────────────────────────────────────
JORDAN_RED   = "#CE1126"
JORDAN_GREEN = "#007A3D"
ACCENT_BLUE  = "#2563EB"
TEXT_DARK    = "#1F2937"
BG_CHART     = "#F8FAFC"

INDICATOR_COLORS = {
    "Customs":                 "#EF4444",
    "Infrastructure":          "#3B82F6",
    "International_Shipments": "#8B5CF6",
    "Logistics_Quality":       "#10B981",
    "Timeliness":              "#F59E0B",
    "Tracking_Tracing":        "#EC4899",
    "LPI_Overall":             "#1D4ED8",
}

INDICATOR_LABELS = {
    "Customs":                 "🛃 Customs",
    "Infrastructure":          "🏗️ Infrastructure",
    "International_Shipments": "🚢 Intl. Shipments",
    "Logistics_Quality":       "📦 Logistics Quality",
    "Timeliness":              "⏱️ Timeliness",
    "Tracking_Tracing":        "📡 Tracking & Tracing",
    "LPI_Overall":             "🏆 Overall LPI",
}

SCORE_COLS = [
    "Customs", "Infrastructure", "International_Shipments",
    "Logistics_Quality", "Timeliness", "Tracking_Tracing",
]

# ── Shared chart layout defaults ──────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor=BG_CHART,
    font=dict(family="Inter", color=TEXT_DARK, size=12),
    title_font=dict(family="Inter", color=TEXT_DARK, size=14),
    
    xaxis=dict(
        color=TEXT_DARK,
        tickfont=dict(color=TEXT_DARK),
        title_font=dict(color=TEXT_DARK),
        gridcolor="#E5E7EB",
        linecolor="#D1D5DB",
    ),
    yaxis=dict(
        color=TEXT_DARK,
        tickfont=dict(color=TEXT_DARK),
        title_font=dict(color=TEXT_DARK),
        gridcolor="#E5E7EB",
        linecolor="#D1D5DB",
    ),
)

def apply_chart_style(fig, title="", height=400, legend_y=-0.2):
    fig.update_layout(
        **CHART_LAYOUT,
        title=title,
        height=height,
        legend=dict(font=dict(color=TEXT_DARK), y=legend_y, orientation="h"),
    )
    fig.update_xaxes(tickfont=dict(color=TEXT_DARK), title_font=dict(color=TEXT_DARK))
    fig.update_yaxes(tickfont=dict(color=TEXT_DARK), title_font=dict(color=TEXT_DARK))
    return fig

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}

.app-header {
    background: linear-gradient(135deg, #CE1126 0%, #8B0000 40%, #1a1a2e 100%);
    border-radius: 16px; padding: 28px 36px; margin-bottom: 24px; color: white;
}
.app-header h1 { margin:0; font-size:2rem; font-weight:700; }
.app-header p  { margin:6px 0 0; opacity:.85; font-size:.95rem; }

.kpi-card {
    background: white; border-radius: 14px; padding: 20px 24px;
    border: 1px solid #E5E7EB; box-shadow: 0 1px 4px rgba(0,0,0,.06); text-align: center;
}
.kpi-label { font-size:.78rem; color:#6B7280; font-weight:600;
             text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px; }
.kpi-value { font-size:2rem; font-weight:700; color:#1F2937; line-height:1; }
.kpi-delta { font-size:.82rem; margin-top:4px; }
.delta-up   { color:#10B981; }
.delta-down { color:#EF4444; }
.delta-neu  { color:#6B7280; }

.section-title {
    font-size:1.25rem; font-weight:700; color:#1F2937;
    border-left:4px solid #CE1126; padding-left:12px; margin:24px 0 14px;
}

.alert-box { border-radius:10px; padding:14px 18px; margin-bottom:12px;
             font-size:.9rem; line-height:1.5; }
.alert-red    { background:#FEF2F2; border-left:4px solid #EF4444; color:#991B1B; }
.alert-green  { background:#F0FDF4; border-left:4px solid #10B981; color:#065F46; }
.alert-blue   { background:#EFF6FF; border-left:4px solid #3B82F6; color:#1E40AF; }
.alert-amber  { background:#FFFBEB; border-left:4px solid #F59E0B; color:#92400E; }

.stTabs [data-baseweb="tab-list"] {
    gap:8px; background:transparent; border-bottom:2px solid #E5E7EB;
}
.stTabs [data-baseweb="tab"] {
    background:transparent; border-radius:8px 8px 0 0;
    padding:8px 18px; font-weight:600; color:#6B7280; border:none; font-size:.88rem;
}
.stTabs [aria-selected="true"] { background:#CE1126 !important; color:white !important; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] hr { border-color:#334155; }

.cluster-badge { display:inline-block; border-radius:20px; padding:4px 14px;
                 font-weight:600; font-size:.85rem; }
.cluster-high   { background:#DCFCE7; color:#166534; }
.cluster-midhi  { background:#DBEAFE; color:#1E40AF; }
.cluster-midlo  { background:#FEF9C3; color:#92400E; }
.cluster-low    { background:#FEE2E2; color:#991B1B; }

.priority-row {
    display:flex; align-items:center; gap:12px; background:white;
    border-radius:10px; padding:12px 16px; margin-bottom:8px;
    border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,.05);
}
.priority-badge {
    background:#CE1126; color:white; border-radius:50%;
    width:28px; height:28px; display:flex; align-items:center;
    justify-content:center; font-weight:700; font-size:.85rem; flex-shrink:0;
}
</style>
""", unsafe_allow_html=True)

# ── Data loader ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=0)
def load_data():
    base = "data/"
    d = {}
    files = {
        "clusters_year":     "LPI_Clusters_By_Year.csv",
        "jordan_cluster":    "LPI_Jordan_Cluster_By_Year.csv",
        "whatif_overall":    "LPI_WhatIf_Jordan.csv",
        "evaluation":        "LPI_Evaluation.csv",
        "clusters":          "LPI_Clusters.csv",
        "whatif_results":    "LPI_WhatIf_Results.csv",
        "indicator_impact":  "LPI_Jordan_Indicator_Impact.csv",
        "indicator_ranking": "LPI_Jordan_Indicator_Ranking.csv",
        "whatif_indicators": "LPI_WhatIf_Jordan_Indicators.csv",
        "forecast":          "LPI_Forecast_Results.csv",
        "indicator_forecast": "LPI_Jordan_Indicators_Forecast.csv",
        "clean":             "LPI_clean.csv",
    }
    for key, fname in files.items():
        try:
            d[key] = pd.read_csv(base + fname)
        except Exception:
            d[key] = pd.DataFrame()
    return d

data = load_data()

@st.cache_data(ttl=0)
def build_jordan_full():
    jc   = data["jordan_cluster"].copy()
    fc_j = data["forecast"][data["forecast"]["Country Name"] == "Jordan"].copy()
    ind_fc = data["indicator_forecast"].copy()
    
    hist_rows = [
        {
            "Year": int(r["Year"]), "LPI_Overall": r["LPI_Overall"],
            "Customs": r["Customs"], "Infrastructure": r["Infrastructure"],
            "International_Shipments": r["International_Shipments"],
            "Logistics_Quality": r["Logistics_Quality"],
            "Timeliness": r["Timeliness"], "Tracking_Tracing": r["Tracking_Tracing"],
            "Cluster Label": r["Cluster Label"], "Type": "Historical",
            "CI_Lower": None, "CI_Upper": None,
        }
        for _, r in jc.iterrows()
    ]
    fore_rows = []

    for _, r in fc_j.iterrows():
        year = int(r["Year"])
        ind_row = ind_fc[ind_fc["Year"] == year]

        if not ind_row.empty:
            ind_row = ind_row.iloc[0]
            customs = ind_row.get("Customs", None)
            infrastructure = ind_row.get("Infrastructure", None)
            shipments = ind_row.get("International_Shipments", None)
            logistics = ind_row.get("Logistics_Quality", None)
            timeliness = ind_row.get("Timeliness", None)
            tracking = ind_row.get("Tracking_Tracing", None)
        else:
            customs = infrastructure = shipments = logistics = timeliness = tracking = None

        fore_rows.append({
            "Year": year,
            "LPI_Overall": r["Predicted LPI Score"],
            "Customs": customs,
            "Infrastructure": infrastructure,
            "International_Shipments": shipments,
            "Logistics_Quality": logistics,
            "Timeliness": timeliness,
            "Tracking_Tracing": tracking,
            "Cluster Label": r["Cluster Label"],
            "Type": "Forecast",
            "CI_Lower": r["CI Lower"],
            "CI_Upper": r["CI Upper"],
        })
    return pd.DataFrame(hist_rows + fore_rows).sort_values("Year").reset_index(drop=True)

jordan_full = build_jordan_full()
all_years   = sorted(jordan_full["Year"].unique().tolist())

# ── Helpers ───────────────────────────────────────────────────────────────────
def cluster_css(label):
    label = str(label).lower()
    if "mid-high" in label or "mid high" in label: return "cluster-midhi"
    if "mid-low"  in label or "mid low"  in label: return "cluster-midlo"
    if "high" in label: return "cluster-high"
    return "cluster-low"

def get_jordan_rank(year):
    clean = data["clean"]
    if clean.empty: return "N/A"
    rank_df = clean[
        (clean["Indicator Short"] == "LPI Overall Rank") &
        (clean["Country Name"] == "Jordan")
    ][["Year", "Value"]].dropna()
    if rank_df.empty: return "N/A"
    closest = min(rank_df["Year"].tolist(), key=lambda y: abs(y - year))
    val     = rank_df[rank_df["Year"] == closest]["Value"].values[0]
    suffix  = f" ({closest})" if closest != year else ""
    return f"{int(val)}{suffix}"

def closest_hist_year(sel):
    hist_years = sorted(data["clusters_year"]["Year"].unique().tolist())
    return min(hist_years, key=lambda y: abs(y - sel))

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🇯🇴 LPI Dashboard")
    st.markdown("**Decision Support System**")
    st.markdown("---")
    st.markdown("### 🔧 Global Filters")

    sel_year = st.selectbox("Reference Year", all_years, index=len(all_years) - 4)

    mena_countries = data["clusters_year"][
        data["clusters_year"]["Region"] == "Middle East & North Africa"
    ]["Country Name"].dropna().unique().tolist()
    if "Jordan" in mena_countries:
        mena_countries.remove("Jordan")

    benchmark_country = st.selectbox(
        "Benchmark Country", ["MENA Average"] + sorted(mena_countries)
    )

    st.markdown("---")
    st.markdown("### 🌐 Live Data")
    if WB_API_AVAILABLE:
        if st.button("🔄 Fetch Latest from World Bank", use_container_width=True):
            with st.spinner("Fetching live data..."):
                live = fetch_jordan_latest()
                if live:
                    st.session_state["wb_live"] = live
                    st.success("✅ Live data loaded!")
                else:
                    st.warning("⚠️ API unavailable, using local data")
    else:
        st.caption("wb_api.py not found")

    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("""
Data: World Bank LPI
Years: 2007–2022 (interpolated)
Forecast: 2024–2026
Countries: 170 | Indicators: 6
""")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>🇯🇴 Jordan Logistics Performance Index</h1>
  <p>Decision Support System for Policymakers &nbsp;|&nbsp;
     World Bank LPI Data &nbsp;|&nbsp; 2007 – 2026 Forecast</p>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
jrow  = jordan_full[jordan_full["Year"] == sel_year]
jprev = jordan_full[jordan_full["Year"] == sel_year - 1]

def delta_html(curr, prev, higher_better=True):
    if prev is None or (isinstance(prev, float) and np.isnan(prev)):
        return '<span class="delta-neu">—</span>'
    diff  = curr - prev
    arrow = "▲" if diff > 0 else "▼"
    good  = diff > 0 if higher_better else diff < 0
    css   = "delta-up" if good else "delta-down"
    return f'<span class="{css}">{arrow} {abs(diff):.3f}</span>'

if not jrow.empty:
    r     = jrow.iloc[0]
    pr    = jprev.iloc[0] if not jprev.empty else None
    rank  = get_jordan_rank(sel_year)
    is_fc = r["Type"] == "Forecast"
    fc_badge = ' <span style="font-size:.7rem;background:#EFF6FF;color:#1E40AF;padding:2px 6px;border-radius:10px">Forecast</span>' if is_fc else ''

    k1, k2, k3, k4, k5 = st.columns(5)
    for col, lbl, val, prev_val, hb in [
        (k1, "Overall LPI Score",    r["LPI_Overall"],                                      pr["LPI_Overall"]    if pr is not None else None, True),
        (k2, "Global Rank",          rank,                                                   None,                False),
        (k3, "Timeliness Score",     r["Timeliness"]    ,              pr["Timeliness"]     if pr is not None else None, True),
        (k4, "Customs Score",        r["Customs"]       ,              pr["Customs"]        if pr is not None else None, True),
        (k5, "Infrastructure Score", r["Infrastructure"] ,             pr["Infrastructure"] if pr is not None else None, True),
    ]:
        if isinstance(val, float) and not np.isnan(val):
            disp = f"{val:.3f}"
            dlt  = delta_html(val, prev_val, hb)
        elif val is None or (isinstance(val, float) and np.isnan(val)):
            disp = "—"
            dlt  = '<span class="delta-neu">Forecast year</span>'
        else:
            disp = str(val)
            dlt  = '<span class="delta-neu">—</span>'

        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{lbl}{fc_badge}</div>
          <div class="kpi-value">{disp}</div>
          <div class="kpi-delta">{dlt} vs prev year</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📍 Cluster Position", "🔍 Gap Analysis", "🔮 What-If Simulator",
    "📈 Trend & Forecast",  "🎯 DSS Recommendations", "💬 Ask the Data",
    "🌐 Live World Bank Data",
])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Jordan\'s Cluster Position Among 170 Countries</div>',
                unsafe_allow_html=True)

    ch = closest_hist_year(sel_year)
    cy_yr      = data["clusters_year"][data["clusters_year"]["Year"] == ch].copy()
    jordan_row = cy_yr[cy_yr["Country Name"] == "Jordan"]

    if not jordan_row.empty:
        jcluster = jordan_row.iloc[0]["Cluster Label"]
        note     = f" (using {ch} cluster data)" if ch != sel_year else ""
        st.markdown(
            f'<p style="color:{TEXT_DARK}">Jordan is classified as: '
            f'<span class="cluster-badge {cluster_css(jcluster)}">{jcluster}</span>'
            f'<span style="color:#9CA3AF;font-size:.8rem">{note}</span></p>',
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns([3, 2])
    with c1:
        if not cy_yr.empty:
            fig = px.scatter(
                cy_yr, x="Infrastructure", y="LPI_Overall",
                color="Cluster Label", size="Customs",
                hover_name="Country Name",
                hover_data={"Customs":":.2f","Timeliness":":.2f","Cluster Label":True},
                color_discrete_sequence=["#EF4444","#F59E0B","#3B82F6","#10B981"],
            )
            if not jordan_row.empty:
                jr = jordan_row.iloc[0]
                fig.add_trace(go.Scatter(
                    x=[jr["Infrastructure"]], y=[jr["LPI_Overall"]],
                    mode="markers+text",
                    marker=dict(color=JORDAN_RED, size=18, symbol="star",
                                line=dict(color="white", width=2)),
                    text=["Jordan"], textposition="top center",
                    textfont=dict(color=JORDAN_RED, size=13, family="Inter"),
                    name="Jordan",
                ))
            apply_chart_style(fig, f"Country Clusters — Infrastructure vs LPI Overall ({ch})", 420, -0.18)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title" style="font-size:1rem">Cluster Summary</div>',
                    unsafe_allow_html=True)
        if not cy_yr.empty:
            summary = cy_yr.groupby("Cluster Label").agg(
                Countries=("Country Name","count"), Avg_LPI=("LPI_Overall","mean"),
            ).reset_index().sort_values("Avg_LPI", ascending=False)
            for _, row in summary.iterrows():
                is_j   = (not jordan_row.empty and
                          row["Cluster Label"] == jordan_row.iloc[0]["Cluster Label"])
                border = f"border:2px solid {JORDAN_RED};" if is_j else ""
                st.markdown(f"""
                <div style="background:white;border-radius:10px;padding:12px 16px;
                            margin-bottom:8px;{border}">
                  <span class="cluster-badge {cluster_css(row['Cluster Label'])}">
                    {row['Cluster Label']}</span>
                  {'&nbsp;<b style="color:#CE1126">◀ Jordan</b>' if is_j else ''}
                  <div style="margin-top:8px;font-size:.82rem;color:#4B5563;line-height:1.8">
                    🌍 {int(row['Countries'])} countries<br>
                    📊 Avg LPI: <b>{row['Avg_LPI']:.2f}</b>
                  </div>
                </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Jordan\'s LPI Journey (2007–2026)</div>',
                unsafe_allow_html=True)
    hist = jordan_full[jordan_full["Type"] == "Historical"]
    fore = jordan_full[jordan_full["Type"] == "Forecast"]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=hist["Year"], y=hist["LPI_Overall"], mode="lines+markers",
        name="Historical", line=dict(color=JORDAN_RED, width=3),
        marker=dict(size=7, color=JORDAN_RED),
    ))
    if not fore.empty:
        last = hist.iloc[-1]
        fig2.add_trace(go.Scatter(
            x=[last["Year"]]+fore["Year"].tolist(),
            y=[last["LPI_Overall"]]+fore["LPI_Overall"].tolist(),
            mode="lines+markers", name="Forecast",
            line=dict(color=JORDAN_RED, width=2, dash="dash"),
            marker=dict(size=8, color=JORDAN_RED, symbol="diamond"),
        ))
        fig2.add_trace(go.Scatter(
            x=list(fore["Year"])+list(fore["Year"])[::-1],
            y=list(fore["CI_Upper"])+list(fore["CI_Lower"])[::-1],
            fill="toself", fillcolor="rgba(206,17,38,0.08)",
            line=dict(color="rgba(0,0,0,0)"), name="95% CI",
        ))
    fig2.add_vline(x=2022, line_dash="dash", line_color="#9CA3AF",
                   annotation_text="Last Actual", annotation_position="top right",
                   annotation_font_color=TEXT_DARK)
    apply_chart_style(fig2, "Jordan LPI Score: 2007–2022 Historical + 2024–2026 Forecast", 400, -0.22)
    fig2.update_layout(yaxis_title="LPI Score", xaxis_title="Year")
    st.plotly_chart(fig2, use_container_width=True)


# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Gap Analysis: Jordan vs Peers</div>',
                unsafe_allow_html=True)

    ch    = closest_hist_year(sel_year)
    cy_yr = data["clusters_year"][data["clusters_year"]["Year"] == ch].copy()
    if ch != sel_year:
        st.info(f"ℹ️ Showing {ch} data (closest historical year to {sel_year})")

    jordan_scores = cy_yr[cy_yr["Country Name"] == "Jordan"][SCORE_COLS]
    if not jordan_scores.empty:
        jvals = jordan_scores.iloc[0]

        if benchmark_country == "MENA Average":
            bench_vals  = cy_yr[cy_yr["Region"]=="Middle East & North Africa"][SCORE_COLS].mean()
            bench_label = "MENA Average"
        else:
            br          = cy_yr[cy_yr["Country Name"]==benchmark_country][SCORE_COLS]
            bench_vals  = br.iloc[0] if not br.empty else pd.Series()
            bench_label = benchmark_country

        c1, c2 = st.columns([3, 2])
        with c1:
            cats  = [INDICATOR_LABELS.get(c, c) for c in SCORE_COLS]
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(
                r=list(jvals)+[jvals.iloc[0]], theta=cats+[cats[0]],
                fill="toself", fillcolor="rgba(206,17,38,0.15)",
                line=dict(color=JORDAN_RED, width=2.5), name="Jordan",
            ))
            if not bench_vals.empty:
                fig_r.add_trace(go.Scatterpolar(
                    r=list(bench_vals)+[bench_vals.iloc[0]], theta=cats+[cats[0]],
                    fill="toself", fillcolor="rgba(37,99,235,0.10)",
                    line=dict(color=ACCENT_BLUE, width=2, dash="dot"), name=bench_label,
                ))
            fig_r.update_layout(
                paper_bgcolor="white",
                font=dict(family="Inter", color=TEXT_DARK, size=12),
                title=dict(text=f"Jordan vs {bench_label} ({ch})", font=dict(color=TEXT_DARK, size=14)),
                polar=dict(
                    bgcolor=BG_CHART,
                    radialaxis=dict(visible=True, range=[0,5],
                                   tickfont=dict(color=TEXT_DARK),
                                   gridcolor="#D1D5DB"),
                    angularaxis=dict(tickfont=dict(color=TEXT_DARK, size=11),
                                     gridcolor="#D1D5DB"),
                ),
                showlegend=True,
                legend=dict(font=dict(color=TEXT_DARK), orientation="h", y=-0.12),
                height=420,
            )
            st.plotly_chart(fig_r, use_container_width=True)

        with c2:
            st.markdown(f'<div class="section-title" style="font-size:1rem">'
                        f'Gap vs {bench_label}</div>', unsafe_allow_html=True)
            if not bench_vals.empty:
                worst_gap, worst_ind = 0, ""
                for ind in SCORE_COLS:
                    gap  = jvals[ind] - bench_vals[ind]
                    sign = "+" if gap >= 0 else ""
                    if gap < worst_gap:
                        worst_gap, worst_ind = gap, INDICATOR_LABELS.get(ind, ind)
                    st.markdown(f"""
                    <div style="background:white;border-radius:8px;padding:10px 14px;
                                margin-bottom:6px;border:1px solid #E5E7EB;
                                display:flex;justify-content:space-between;align-items:center">
                      <span style="font-weight:600;font-size:.88rem;color:#1F2937">
                        {INDICATOR_LABELS.get(ind,ind)}</span>
                      <span style="font-size:.85rem;font-weight:700;
                                   color:{'#10B981' if gap>=0 else '#EF4444'}">
                        {sign}{gap:.3f}</span>
                    </div>""", unsafe_allow_html=True)
                if worst_ind:
                    st.markdown(
                        f'<div class="alert-box alert-red">⚠️ Biggest gap: '
                        f'<b>{worst_ind}</b> is <b>{abs(worst_gap):.3f}</b> '
                        f'points below {bench_label}</div>', unsafe_allow_html=True)

        if not bench_vals.empty:
            bar_df = pd.DataFrame({
                "Indicator": [INDICATOR_LABELS.get(c,c) for c in SCORE_COLS],
                "Jordan":    [jvals[c] for c in SCORE_COLS],
                bench_label: [bench_vals[c] for c in SCORE_COLS],
            })
            fig_b = go.Figure()
            fig_b.add_trace(go.Bar(
                name="Jordan", y=bar_df["Indicator"], x=bar_df["Jordan"],
                orientation="h", marker_color=JORDAN_RED,
                text=[f"{v:.2f}" for v in bar_df["Jordan"]],
                textposition="outside", textfont=dict(color=TEXT_DARK, size=11),
            ))
            fig_b.add_trace(go.Bar(
                name=bench_label, y=bar_df["Indicator"], x=bar_df[bench_label],
                orientation="h", marker_color=ACCENT_BLUE,
                text=[f"{v:.2f}" for v in bar_df[bench_label]],
                textposition="outside", textfont=dict(color=TEXT_DARK, size=11),
            ))
            apply_chart_style(fig_b, f"Jordan vs {bench_label} ({ch})", 400, -0.18)
            fig_b.update_layout(
                barmode="group",
                xaxis=dict(range=[0, 5.8], title="Score (1–5)",
                           tickfont=dict(color=TEXT_DARK),
                           title_font=dict(color=TEXT_DARK),
                           gridcolor="#E5E7EB"),
                yaxis=dict(tickfont=dict(color=TEXT_DARK),
                           title_font=dict(color=TEXT_DARK)),
            )
            st.plotly_chart(fig_b, use_container_width=True)


# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">🔮 What-If Scenario Simulator</div>',
                unsafe_allow_html=True)

    ch    = closest_hist_year(sel_year)
    cy_yr = data["clusters_year"][data["clusters_year"]["Year"] == ch].copy()
    jordan_scores = cy_yr[cy_yr["Country Name"] == "Jordan"][SCORE_COLS + ["LPI_Overall"]]
    if ch != sel_year:
        st.info(f"ℹ️ Using {ch} baseline scores")

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Adjust indicator scores:**")
        sim_scores = {}
        if not jordan_scores.empty:
            jvals = jordan_scores.iloc[0]
            for ind in SCORE_COLS:
                sim_scores[ind] = st.slider(
                    INDICATOR_LABELS.get(ind, ind), 1.0, 5.0,
                    float(round(jvals[ind], 2)), 0.05, key=f"sl_{ind}",
                )
        else:
            for ind in SCORE_COLS:
                sim_scores[ind] = st.slider(
                    INDICATOR_LABELS.get(ind,ind), 1.0, 5.0, 2.5, 0.05, key=f"sl_{ind}"
                )

    with c2:
        if not jordan_scores.empty:
            jvals         = jordan_scores.iloc[0]
            current_score = float(jvals["LPI_Overall"])
            sim_overall   = float(np.mean(list(sim_scores.values())))
            improvement   = sim_overall - current_score
            all_sc        = cy_yr["LPI_Overall"].dropna()
            current_rank  = int((all_sc > current_score).sum()) + 1
            sim_rank      = int((all_sc > sim_overall).sum()) + 1
            rank_gain     = current_rank - sim_rank

            m1, m2, m3 = st.columns(3)
            for col, lbl, val, color in [
                (m1, "Current Score",   f"{current_score:.3f}", "#6B7280"),
                (m2, "Simulated Score", f"{sim_overall:.3f}",
                 "#10B981" if improvement>=0 else "#EF4444"),
                (m3, "Rank Change",
                 f"{'▲' if rank_gain>0 else '▼'}{abs(rank_gain)} positions",
                 "#10B981" if rank_gain>0 else "#EF4444"),
            ]:
                col.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-label">{lbl}</div>
                  <div class="kpi-value" style="color:{color}">{val}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            compare_df = pd.DataFrame({
                "Indicator": [INDICATOR_LABELS.get(c,c) for c in SCORE_COLS],
                "Current":   [float(jvals[c]) for c in SCORE_COLS],
                "Simulated": [sim_scores[c]   for c in SCORE_COLS],
            })
            fig_wa = go.Figure()
            fig_wa.add_trace(go.Bar(
                name="Current", y=compare_df["Indicator"], x=compare_df["Current"],
                orientation="h", marker_color="#94A3B8",
                text=[f"{v:.2f}" for v in compare_df["Current"]],
                textposition="outside", textfont=dict(color=TEXT_DARK, size=11),
            ))
            fig_wa.add_trace(go.Bar(
                name="Simulated", y=compare_df["Indicator"], x=compare_df["Simulated"],
                orientation="h",
                marker_color=[
                    "#10B981" if sim_scores[c]>float(jvals[c])
                    else "#EF4444" if sim_scores[c]<float(jvals[c])
                    else "#94A3B8" for c in SCORE_COLS
                ],
                text=[f"{v:.2f}" for v in compare_df["Simulated"]],
                textposition="outside", textfont=dict(color=TEXT_DARK, size=11),
            ))
            apply_chart_style(fig_wa, "Current vs Simulated Scores", 370, -0.2)
            fig_wa.update_layout(
                barmode="group",
                xaxis=dict(range=[0, 5.8], tickfont=dict(color=TEXT_DARK),
                           gridcolor="#E5E7EB"),
                yaxis=dict(tickfont=dict(color=TEXT_DARK)),
            )
            st.plotly_chart(fig_wa, use_container_width=True)

    st.markdown('<div class="section-title">Pre-Built Policy Scenarios</div>',
                unsafe_allow_html=True)
    wr = data["whatif_results"]
    if not wr.empty:
        cols_s = st.columns(len(wr))
        for i, (_, row) in enumerate(wr.iterrows()):
            imp = float(row["Improvement"])
            cols_s[i].markdown(f"""
            <div style="background:white;border-radius:12px;padding:16px;
                        border:1px solid #E5E7EB;text-align:center">
              <div style="font-size:.72rem;font-weight:700;text-transform:uppercase;
                          color:#6B7280;margin-bottom:8px">{row['Scenario']}</div>
              <div style="font-size:1.5rem;font-weight:700;
                          color:{'#10B981' if imp>0 else '#EF4444'}">+{imp:.3f}</div>
              <div style="font-size:.78rem;color:#9CA3AF;margin-top:4px">improvement</div>
              <div style="font-size:1rem;font-weight:700;color:#1D4ED8;margin-top:6px">
                → {row['New Score']:.3f}</div>
            </div>""", unsafe_allow_html=True)


# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Jordan\'s LPI Trend & Forecast (2007–2026)</div>',
                unsafe_allow_html=True)

    wi_ind = data["whatif_indicators"].copy()
    fc_j   = data["forecast"][data["forecast"]["Country Name"]=="Jordan"].copy()
    hist   = jordan_full[jordan_full["Type"]=="Historical"]
    fore   = jordan_full[jordan_full["Type"]=="Forecast"]

    c1, c2 = st.columns([3, 2])
    with c1:
        fig_f = go.Figure()
        fig_f.add_trace(go.Scatter(
            x=hist["Year"], y=hist["LPI_Overall"], mode="lines+markers",
            name="Historical LPI", line=dict(color=JORDAN_RED, width=3),
            marker=dict(size=7, color=JORDAN_RED),
        ))
        if not fore.empty:
            last = hist.iloc[-1]
            fig_f.add_trace(go.Scatter(
                x=[last["Year"]]+fore["Year"].tolist(),
                y=[last["LPI_Overall"]]+fore["LPI_Overall"].tolist(),
                mode="lines+markers", name="Forecast (Baseline)",
                line=dict(color=JORDAN_RED, width=2, dash="dash"),
                marker=dict(size=8, color=JORDAN_RED, symbol="diamond"),
            ))
            fig_f.add_trace(go.Scatter(
                x=list(fore["Year"])+list(fore["Year"])[::-1],
                y=list(fore["CI_Upper"])+list(fore["CI_Lower"])[::-1],
                fill="toself", fillcolor="rgba(206,17,38,0.08)",
                line=dict(color="rgba(0,0,0,0)"), name="95% CI",
            ))
        if not wi_ind.empty:
            fig_f.add_trace(go.Scatter(
                x=wi_ind["Year"],
                y=wi_ind["Improve International Shipments + Customs"],
                mode="lines+markers", name="Improvement Scenario",
                line=dict(color=JORDAN_GREEN, width=2, dash="dot"),
                marker=dict(size=7, color=JORDAN_GREEN, symbol="triangle-up"),
            ))
            fig_f.add_trace(go.Scatter(
                x=wi_ind["Year"], y=wi_ind["Decline Scenario"],
                mode="lines+markers", name="Decline Scenario",
                line=dict(color="#EF4444", width=2, dash="dot"),
                marker=dict(size=7, color="#EF4444", symbol="triangle-down"),
            ))
        fig_f.add_vline(x=2022, line_dash="dash", line_color="#9CA3AF",
                        annotation_text="Last Actual", annotation_position="top right",
                        annotation_font_color=TEXT_DARK)
        apply_chart_style(fig_f, "Jordan LPI: Historical + 3-Year Forecast with Scenarios", 430, -0.24)
        fig_f.update_layout(yaxis_title="LPI Score", xaxis_title="Year")
        st.plotly_chart(fig_f, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title" style="font-size:1rem">Forecast Details</div>',
                    unsafe_allow_html=True)
        ev = data["evaluation"]
        if not ev.empty:
            er = ev[ev["Country Name"]=="Jordan"]
            if not er.empty:
                er = er.iloc[0]
                st.markdown(f"""
                <div class="alert-box alert-blue">
                  📊 <b>Forecast Model</b><br>
                  Model: {er['Model Used']}<br>
                  R²: {er['R2 Train']:.3f} &nbsp;|&nbsp; RMSE: {er['RMSE Train']:.3f}
                </div>""", unsafe_allow_html=True)
        for _, row in fc_j.iterrows():
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:12px 16px;
                        margin-bottom:8px;border:1px solid #E5E7EB">
              <div style="font-weight:700;color:#1F2937">{int(row['Year'])}</div>
              <div style="font-size:1.4rem;font-weight:700;color:{JORDAN_RED}">
                {row['Predicted LPI Score']:.3f}</div>
              <div style="font-size:.78rem;color:#6B7280">
                CI: [{row['CI Lower']:.3f} – {row['CI Upper']:.3f}]</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Indicator Trends Over Time</div>',
                unsafe_allow_html=True)
    sel_inds = st.multiselect(
        "Select indicators", SCORE_COLS,
        default=["Customs","Infrastructure","Timeliness"],
        format_func=lambda x: INDICATOR_LABELS.get(x,x),
    )
    if sel_inds:
        fig_ind = go.Figure()
        for ind in sel_inds:
            col_data = hist[["Year",ind]].dropna()
            fig_ind.add_trace(go.Scatter(
                x=col_data["Year"], y=col_data[ind], mode="lines+markers",
                name=INDICATOR_LABELS.get(ind,ind),
                line=dict(color=INDICATOR_COLORS.get(ind,"#888"), width=2.5),
                marker=dict(size=6),
            ))
        apply_chart_style(fig_ind, "Jordan — Indicator Score Trends (2007–2022)", 380, -0.22)
        fig_ind.update_layout(
            yaxis=dict(range=[1.5, 4.5], title="Score",
                       tickfont=dict(color=TEXT_DARK),
                       title_font=dict(color=TEXT_DARK)),
            xaxis=dict(title="Year", tickfont=dict(color=TEXT_DARK),
                       title_font=dict(color=TEXT_DARK)),
        )
        st.plotly_chart(fig_ind, use_container_width=True)


# ── TAB 5 ─────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">🎯 Policy Recommendation Engine</div>',
                unsafe_allow_html=True)

    impact  = data["indicator_impact"].copy()
    ranking = data["indicator_ranking"].copy()
    ch      = closest_hist_year(sel_year)
    cy_yr   = data["clusters_year"][data["clusters_year"]["Year"] == ch].copy()

    goal = st.selectbox("Select your policy goal:", [
        "🏆 Improve Overall LPI Rank by 10 positions",
        "📈 Outperform MENA Average in all indicators",
        "🚀 Reach Mid-High Performers cluster level",
        "🎯 Maximize high-impact indicators first",
    ])

    if not impact.empty and not ranking.empty:
        merged = ranking.merge(
            impact[["Indicator Name","Correlation with Overall"]],
            on="Indicator Name", how="left",
        ).rename(columns={"Value":"Current Score",
                           "Correlation with Overall":"Impact Score"})
        merged["Impact Score"]   = merged["Impact Score"].fillna(0)
        merged["Priority Score"] = (1 - merged["Current Score"]/5) * merged["Impact Score"]

        col_map = {
            "Customs":"Customs","Infrastructure":"Infrastructure",
            "International Shipments":"International_Shipments",
            "Logistics Quality":"Logistics_Quality",
            "Timeliness":"Timeliness","Tracking & Tracing":"Tracking_Tracing",
        }
        if "Mid-High" in goal:
            midhi      = cy_yr[cy_yr["Cluster Label"]=="Mid-High Performers"][SCORE_COLS].mean()
            get_target = lambda n: float(midhi[col_map[n]]) if n in col_map and col_map[n] in midhi else None
        else:
            get_target = lambda n: None

        merged = merged.sort_values("Priority Score", ascending=False).reset_index(drop=True)
        c1, c2 = st.columns([3, 2])

        with c1:
            st.markdown("#### 📋 Prioritized Action Plan")
            for i, row in merged.iterrows():
                target  = get_target(row["Indicator Name"])
                gap     = (target - row["Current Score"]) if target else None
                gap_str = f"→ Target: {target:.2f} (gap: +{gap:.2f})" if gap and gap>0 else \
                          "✅ At target" if gap and gap<=0 else ""
                bw = int(row["Priority Score"]*100/merged["Priority Score"].max())
                st.markdown(f"""
                <div class="priority-row">
                  <div class="priority-badge">{i+1}</div>
                  <div style="flex:1">
                    <div style="font-weight:600;color:#1F2937;font-size:.9rem">
                      {row['Indicator Name']}</div>
                    <div style="font-size:.8rem;color:#6B7280;margin-top:2px">
                      Current: {row['Current Score']:.3f} &nbsp;|&nbsp;
                      Impact: {row['Impact Score']:.3f}
                      {'&nbsp;|&nbsp;'+gap_str if gap_str else ''}</div>
                    <div style="background:#F3F4F6;border-radius:4px;height:6px;margin-top:6px">
                      <div style="background:#CE1126;width:{bw}%;height:6px;border-radius:4px">
                      </div></div>
                  </div>
                </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown("#### 💡 Key Insights")
            top    = merged.iloc[0]
            quick  = merged.loc[merged["Current Score"].idxmin()]
            strong = merged.loc[merged["Current Score"].idxmax()]
            st.markdown(f"""
            <div class="alert-box alert-red">
              🎯 <b>Top Priority:</b> {top['Indicator Name']}<br>
              High impact ({top['Impact Score']:.3f}) + low score ({top['Current Score']:.3f})
              = highest leverage point.
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="alert-box alert-amber">
              ⚡ <b>Most Room to Improve:</b> {quick['Indicator Name']}<br>
              Lowest score at <b>{quick['Current Score']:.3f}</b> — potential quick win.
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="alert-box alert-green">
              💪 <b>Strongest Indicator:</b> {strong['Indicator Name']}<br>
              Score of <b>{strong['Current Score']:.3f}</b> — competitive advantage.
            </div>""", unsafe_allow_html=True)

            fig_imp = px.scatter(
                merged, x="Current Score", y="Impact Score",
                size="Priority Score", color="Indicator Name",
                text="Indicator Name",
                color_discrete_sequence=list(INDICATOR_COLORS.values()),
            )
            fig_imp.update_traces(
                textposition="top center",
                textfont=dict(color=TEXT_DARK, size=9, family="Inter"),
            )
            fig_imp.add_vline(x=merged["Current Score"].mean(), line_dash="dash",
                              line_color="#9CA3AF",
                              annotation_font_color=TEXT_DARK)
            fig_imp.add_hline(y=merged["Impact Score"].mean(), line_dash="dash",
                              line_color="#9CA3AF",
                              annotation_font_color=TEXT_DARK)
            apply_chart_style(fig_imp, "Impact vs Current Score Matrix", 340, -0.15)
            fig_imp.update_layout(
                showlegend=False,
                xaxis=dict(title="Current Score", tickfont=dict(color=TEXT_DARK),
                           title_font=dict(color=TEXT_DARK), gridcolor="#E5E7EB"),
                yaxis=dict(title="Correlation with Overall LPI",
                           tickfont=dict(color=TEXT_DARK),
                           title_font=dict(color=TEXT_DARK), gridcolor="#E5E7EB"),
            )
            st.plotly_chart(fig_imp, use_container_width=True)

    st.markdown('<div class="section-title">📊 Forecast Model Evaluation</div>',
                unsafe_allow_html=True)
    ev = data["evaluation"]
    if not ev.empty:
        disp = ev[["Country Name","Cluster","Model Used","R2 Train","RMSE Train","Test Error"]].copy()
        disp.columns = ["Country","Cluster","Model","R²","RMSE","Test Error"]
        st.dataframe(disp, use_container_width=True, hide_index=True)


# ── TAB 6: Ask the Data Chatbot ───────────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-title">💬 Ask the Data</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#6B7280;margin-bottom:16px">Ask questions about Jordan\'s LPI '
        'in English or Arabic — no AI required, answers come directly from the data.</p>',
        unsafe_allow_html=True,
    )

    # ── Example questions ─────────────────────────────────────────────────────
    st.markdown("**💡 Try asking:**")
    example_cols = st.columns(3)
    examples = [
        "What is Jordan's LPI score in 2018?",
        "Which indicator is weakest?",
        "How does Jordan compare to MENA?",
        "What is the forecast for 2026?",
        "Which year was Jordan's best?",
        "What is Jordan's global rank?",
    ]
    for i, ex in enumerate(examples):
        if example_cols[i % 3].button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state["chat_input_val"] = ex

    st.markdown("---")

    # ── Chat history ──────────────────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "chat_input_val" not in st.session_state:
        st.session_state["chat_input_val"] = ""

    # ── Chatbot engine ────────────────────────────────────────────────────────
    def build_knowledge():
        """Pre-compute facts from data for fast lookup."""
        kb = {}
        jc = data["jordan_cluster"]
        fc = data["forecast"][data["forecast"]["Country Name"] == "Jordan"]
        ir = data["indicator_ranking"]
        ii = data["indicator_impact"]
        cl = data["clean"]
        wr = data["whatif_results"]
        cy = data["clusters_year"]

        # Jordan scores by year
        kb["scores_by_year"] = {
            int(r["Year"]): {
                "overall": round(r["LPI_Overall"], 3),
                "customs": round(r["Customs"], 3),
                "infrastructure": round(r["Infrastructure"], 3),
                "shipments": round(r["International_Shipments"], 3),
                "logistics": round(r["Logistics_Quality"], 3),
                "timeliness": round(r["Timeliness"], 3),
                "tracking": round(r["Tracking_Tracing"], 3),
                "cluster": r["Cluster Label"],
            }
            for _, r in jc.iterrows()
        }

        # Forecast
        kb["forecast"] = {
            int(r["Year"]): {
                "score": round(r["Predicted LPI Score"], 3),
                "ci_lower": round(r["CI Lower"], 3),
                "ci_upper": round(r["CI Upper"], 3),
            }
            for _, r in fc.iterrows()
        }

        # Indicator ranking (weakest/strongest)
        if not ir.empty:
            kb["weakest"]  = ir.loc[ir["Value"].idxmin(), "Indicator Name"]
            kb["strongest"]= ir.loc[ir["Value"].idxmax(), "Indicator Name"]
            kb["rankings"] = ir.set_index("Indicator Name")["Value"].to_dict()

        # Impact (most impactful)
        if not ii.empty:
            kb["most_impactful"] = ii.loc[ii["Correlation with Overall"].idxmax(), "Indicator Name"]
            kb["impacts"]        = ii.set_index("Indicator Name")["Correlation with Overall"].to_dict()

        # Best/worst year
        if kb["scores_by_year"]:
            kb["best_year"]  = max(kb["scores_by_year"], key=lambda y: kb["scores_by_year"][y]["overall"])
            kb["worst_year"] = min(kb["scores_by_year"], key=lambda y: kb["scores_by_year"][y]["overall"])

        # MENA average (latest year)
        latest_hist = max(cy["Year"].unique())
        cy_latest   = cy[cy["Year"] == latest_hist]
        mena        = cy_latest[cy_latest["Region"] == "Middle East & North Africa"]
        kb["mena_avg"] = {
            "year": int(latest_hist),
            "overall": round(mena["LPI_Overall"].mean(), 3),
            "customs": round(mena["Customs"].mean(), 3),
            "infrastructure": round(mena["Infrastructure"].mean(), 3),
            "shipments": round(mena["International_Shipments"].mean(), 3),
            "logistics": round(mena["Logistics_Quality"].mean(), 3),
            "timeliness": round(mena["Timeliness"].mean(), 3),
            "tracking": round(mena["Tracking_Tracing"].mean(), 3),
        }

        # Jordan MENA gap
        jlatest = kb["scores_by_year"].get(latest_hist, {})
        if jlatest:
            kb["mena_gap"] = round(jlatest["overall"] - kb["mena_avg"]["overall"], 3)

        # Global rank
        if not cl.empty:
            rank_df = cl[
                (cl["Indicator Short"] == "LPI Overall Rank") &
                (cl["Country Name"] == "Jordan")
            ][["Year","Value"]].dropna()
            kb["ranks"] = {int(r["Year"]): int(r["Value"]) for _, r in rank_df.iterrows()}

        # Whatif scenarios
        if not wr.empty:
            kb["scenarios"] = wr[["Scenario","New Score","Improvement"]].to_dict("records")

        return kb

    @st.cache_data
    def get_kb():
        return build_knowledge()

    kb = get_kb()

    def answer(q: str) -> str:
        q_low = q.lower().strip()

        # ── Year-specific score ───────────────────────────────────────────────
        for year in kb["scores_by_year"]:
            if str(year) in q:
                s = kb["scores_by_year"][year]
                if any(w in q_low for w in ["custom","جمارك"]):
                    return f"🛃 Jordan's **Customs** score in {year} was **{s['customs']}** out of 5."
                if any(w in q_low for w in ["infra","بنية"]):
                    return f"🏗️ Jordan's **Infrastructure** score in {year} was **{s['infrastructure']}** out of 5."
                if any(w in q_low for w in ["shipment","شحن"]):
                    return f"🚢 Jordan's **Int. Shipments** score in {year} was **{s['shipments']}** out of 5."
                if any(w in q_low for w in ["logistic","لوجستي"]):
                    return f"📦 Jordan's **Logistics Quality** score in {year} was **{s['logistics']}** out of 5."
                if any(w in q_low for w in ["timeliness","توقيت"]):
                    return f"⏱️ Jordan's **Timeliness** score in {year} was **{s['timeliness']}** out of 5."
                if any(w in q_low for w in ["track","تتبع"]):
                    return f"📡 Jordan's **Tracking** score in {year} was **{s['tracking']}** out of 5."
                if any(w in q_low for w in ["rank","رتبة","مرتبة"]):
                    rank = kb.get("ranks", {}).get(year, "N/A")
                    return f"🏆 Jordan's **global rank** in {year} was **#{rank}**."
                return (
                    f"📊 Jordan's LPI in **{year}**:\n\n"
                    f"| Indicator | Score |\n|---|---|\n"
                    f"| 🏆 Overall | **{s['overall']}** |\n"
                    f"| 🛃 Customs | {s['customs']} |\n"
                    f"| 🏗️ Infrastructure | {s['infrastructure']} |\n"
                    f"| 🚢 Intl. Shipments | {s['shipments']} |\n"
                    f"| 📦 Logistics Quality | {s['logistics']} |\n"
                    f"| ⏱️ Timeliness | {s['timeliness']} |\n"
                    f"| 📡 Tracking | {s['tracking']} |\n"
                    f"| 🏷️ Cluster | {s['cluster']} |"
                )

        # ── Forecast ──────────────────────────────────────────────────────────
        if any(w in q_low for w in ["forecast","predict","2024","2025","2026","توقع","مستقبل"]):
            lines = ["📈 Jordan's LPI **Forecast**:\n\n| Year | Score | 95% CI |", "|---|---|---|"]
            for yr, f in kb["forecast"].items():
                lines.append(f"| {yr} | **{f['score']}** | [{f['ci_lower']} – {f['ci_upper']}] |")
            return "\n".join(lines)

        # ── Weakest ───────────────────────────────────────────────────────────
        if any(w in q_low for w in ["weak","worst","lowest","أضعف","أسوأ","أدنى"]):
            w = kb.get("weakest","N/A")
            s = kb.get("rankings",{}).get(w,"N/A")
            return f"⚠️ Jordan's **weakest indicator** is **{w}** with a score of **{s:.3f}**.\n\nThis is the area with the most room for improvement."

        # ── Strongest ─────────────────────────────────────────────────────────
        if any(w in q_low for w in ["strong","best","highest","أقوى","أفضل","أعلى"]):
            s  = kb.get("strongest","N/A")
            sc = kb.get("rankings",{}).get(s,"N/A")
            return f"💪 Jordan's **strongest indicator** is **{s}** with a score of **{sc:.3f}**.\n\nThis is Jordan's competitive advantage in logistics."

        # ── MENA comparison ───────────────────────────────────────────────────
        if any(w in q_low for w in ["mena","compare","region","منطقة","مقارنة","الشرق"]):
            m   = kb["mena_avg"]
            gap = kb.get("mena_gap", 0)
            jyr = kb["scores_by_year"].get(m["year"], {})
            pos = "above ✅" if gap >= 0 else "below ⚠️"
            return (
                f"🌍 Jordan vs **MENA Average** ({m['year']}):\n\n"
                f"| Indicator | Jordan | MENA Avg | Gap |\n|---|---|---|---|\n"
                f"| 🏆 Overall | {jyr.get('overall','N/A')} | {m['overall']} | "
                f"{'▲' if gap>=0 else '▼'} {abs(gap):.3f} |\n"
                f"| 🛃 Customs | {jyr.get('customs','N/A')} | {m['customs']} | "
                f"{'▲' if jyr.get('customs',0)>=m['customs'] else '▼'} {abs(jyr.get('customs',0)-m['customs']):.3f} |\n"
                f"| 🏗️ Infrastructure | {jyr.get('infrastructure','N/A')} | {m['infrastructure']} | "
                f"{'▲' if jyr.get('infrastructure',0)>=m['infrastructure'] else '▼'} {abs(jyr.get('infrastructure',0)-m['infrastructure']):.3f} |\n"
                f"| ⏱️ Timeliness | {jyr.get('timeliness','N/A')} | {m['timeliness']} | "
                f"{'▲' if jyr.get('timeliness',0)>=m['timeliness'] else '▼'} {abs(jyr.get('timeliness',0)-m['timeliness']):.3f} |\n\n"
                f"Jordan is **{abs(gap):.3f} points {pos}** the MENA average overall."
            )

        # ── Best/worst year ───────────────────────────────────────────────────
        if any(w in q_low for w in ["best year","أفضل سنة","top year"]):
            yr = kb.get("best_year")
            sc = kb["scores_by_year"][yr]["overall"] if yr else "N/A"
            return f"🏆 Jordan's **best year** was **{yr}** with an overall LPI score of **{sc}**."

        if any(w in q_low for w in ["worst year","أسوأ سنة","lowest year"]):
            yr = kb.get("worst_year")
            sc = kb["scores_by_year"][yr]["overall"] if yr else "N/A"
            return f"📉 Jordan's **worst year** was **{yr}** with an overall LPI score of **{sc}**."

        # ── Global rank ───────────────────────────────────────────────────────
        if any(w in q_low for w in ["rank","رتبة","مرتبة","position"]):
            ranks = kb.get("ranks", {})
            if ranks:
                latest_rank_yr = max(ranks)
                lines = ["🏆 Jordan's **Global LPI Rank**:\n\n| Year | Rank |\n|---|---|"]
                for yr in sorted(ranks):
                    lines.append(f"| {yr} | #{ranks[yr]} |")
                return "\n".join(lines)

        # ── Impact / most important indicator ─────────────────────────────────
        if any(w in q_low for w in ["impact","important","priority","أهم","تأثير","أولوية"]):
            mi = kb.get("most_impactful","N/A")
            ic = kb.get("impacts",{}).get(mi,"N/A")
            return (
                f"🎯 The **most impactful** indicator for Jordan's overall LPI is "
                f"**{mi}** (correlation: {ic:.3f}).\n\n"
                f"Improving this indicator will have the biggest effect on Jordan's overall score."
            )

        # ── Cluster ───────────────────────────────────────────────────────────
        if any(w in q_low for w in ["cluster","group","category","مجموعة","تصنيف"]):
            latest_yr = max(kb["scores_by_year"])
            cl = kb["scores_by_year"][latest_yr]["cluster"]
            return (
                f"🏷️ Jordan is currently classified as: **{cl}**\n\n"
                f"This is based on clustering analysis of 170 countries using all 6 LPI indicators."
            )

        # ── Scenarios ─────────────────────────────────────────────────────────
        if any(w in q_low for w in ["scenario","improve","what if","ماذا لو","سيناريو","تحسين"]):
            sc = kb.get("scenarios", [])
            if sc:
                lines = ["🔮 **Policy Improvement Scenarios**:\n\n| Scenario | New Score | Improvement |\n|---|---|---|"]
                for s in sc:
                    lines.append(f"| {s['Scenario']} | {s['New Score']:.3f} | +{s['Improvement']:.3f} |")
                return "\n".join(lines)

        # ── All indicators summary ─────────────────────────────────────────────
        if any(w in q_low for w in ["all indicator","كل المؤشرات","all score","summary","ملخص"]):
            rnk = kb.get("rankings", {})
            imp = kb.get("impacts", {})
            lines = ["📊 **Jordan's LPI Indicators Summary**:\n\n| Indicator | Score | Impact |\n|---|---|---|"]
            for ind, sc in sorted(rnk.items(), key=lambda x: x[1]):
                ic = imp.get(ind, 0)
                lines.append(f"| {ind} | {sc:.3f} | {ic:.3f} |")
            return "\n".join(lines)

        # ── Fallback ──────────────────────────────────────────────────────────
        return (
            "🤔 I didn't find an exact match for your question. Try asking about:\n\n"
            "- **Scores**: *'What is Jordan's score in 2018?'*\n"
            "- **Indicators**: *'Which indicator is weakest?'*\n"
            "- **Comparison**: *'How does Jordan compare to MENA?'*\n"
            "- **Forecast**: *'What is the forecast for 2026?'*\n"
            "- **Rank**: *'What is Jordan's global rank?'*\n"
            "- **Scenarios**: *'What are the improvement scenarios?'*"
        )

    # ── Chat UI ───────────────────────────────────────────────────────────────
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"],
                                  avatar="🇯🇴" if msg["role"]=="assistant" else "👤"):
                st.markdown(msg["content"])

    user_input = st.chat_input("Ask about Jordan's LPI data...",
                                key="chat_main")

    # Handle example button click
    if st.session_state.get("chat_input_val"):
        user_input = st.session_state["chat_input_val"]
        st.session_state["chat_input_val"] = ""

    if user_input:
        st.session_state["chat_history"].append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        bot_reply = answer(user_input)
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": bot_reply}
        )
        with st.chat_message("assistant", avatar="🇯🇴"):
            st.markdown(bot_reply)

    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear chat", key="clear_chat"):
            st.session_state["chat_history"] = []
            st.rerun()


# ── TAB 7: Live World Bank Data ───────────────────────────────────────────────
with tab7:
    st.markdown('<div class="section-title">🌐 Live Data from World Bank API</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-box alert-blue">
      🌐 <b>World Bank Open Data API</b> — Free, no API key required.<br>
      Click the button in the sidebar to fetch the latest LPI data directly
      from the World Bank database.
    </div>""", unsafe_allow_html=True)

    live = st.session_state.get("wb_live", {})

    if live:
        st.markdown('<div class="section-title" style="font-size:1rem">'
                    'Jordan Latest LPI — Live from World Bank</div>',
                    unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (name, info) in enumerate(live.items()):
            cols[i % 3].markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">{name}</div>
              <div class="kpi-value" style="font-size:1.5rem">{info['value']:.3f}</div>
              <div class="kpi-delta delta-neu">Year: {info['year']}</div>
            </div><br>""", unsafe_allow_html=True)

        # Compare live vs local CSV
        st.markdown('<div class="section-title" style="font-size:1rem">'
                    'Live vs Local CSV Comparison</div>', unsafe_allow_html=True)

        clean = data["clean"]
        rows  = []
        for name, info in live.items():
            local_row = clean[
                (clean["Indicator Short"] == name) &
                (clean["Country Name"] == "Jordan") &
                (clean["Year"] == info["year"])
            ]["Value"]
            local_val = float(local_row.values[0]) if not local_row.empty else None
            diff      = round(info["value"] - local_val, 4) if local_val else None
            rows.append({
                "Indicator":   name,
                "Year":        info["year"],
                "Live (API)":  info["value"],
                "Local (CSV)": local_val if local_val else "N/A",
                "Difference":  diff if diff is not None else "N/A",
            })

        df_compare = pd.DataFrame(rows)
        st.dataframe(df_compare, use_container_width=True, hide_index=True)

        # Bar chart comparison
        df_scores_only = df_compare[
            df_compare["Indicator"].str.contains("Score") &
            df_compare["Live (API)"].notna() &
            df_compare["Local (CSV)"].apply(lambda x: x != "N/A")
        ].copy()

        if not df_scores_only.empty:
            fig_live = go.Figure()
            fig_live.add_trace(go.Bar(
                name="Live (API)",
                x=df_scores_only["Indicator"],
                y=df_scores_only["Live (API)"],
                marker_color=JORDAN_RED,
                text=[f"{v:.3f}" for v in df_scores_only["Live (API)"]],
                textposition="outside",
                textfont=dict(color=TEXT_DARK),
            ))
            fig_live.add_trace(go.Bar(
                name="Local (CSV)",
                x=df_scores_only["Indicator"],
                y=df_scores_only["Local (CSV)"],
                marker_color=ACCENT_BLUE,
                text=[f"{v:.3f}" for v in df_scores_only["Local (CSV)"]],
                textposition="outside",
                textfont=dict(color=TEXT_DARK),
            ))
            apply_chart_style(fig_live, "Jordan LPI: Live API vs Local CSV", 400, -0.2)
            fig_live.update_layout(
                barmode="group",
                xaxis=dict(tickangle=-20, tickfont=dict(color=TEXT_DARK, size=10)),
                yaxis=dict(range=[0, 5.5], title="Score"),
            )
            st.plotly_chart(fig_live, use_container_width=True)

    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#9CA3AF">
          <div style="font-size:3rem">🌐</div>
          <div style="font-size:1.1rem;font-weight:600;margin-top:12px">
            No live data loaded yet</div>
          <div style="font-size:.9rem;margin-top:8px">
            Click <b>"🔄 Fetch Latest from World Bank"</b> in the sidebar</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:.8rem;color:#9CA3AF">
      📡 <b>API Source:</b>
      <a href="https://api.worldbank.org/v2" target="_blank"
         style="color:#3B82F6">api.worldbank.org</a> &nbsp;|&nbsp;
      Free & open access &nbsp;|&nbsp; No authentication required &nbsp;|&nbsp;
      Data updated by World Bank annually
    </div>""", unsafe_allow_html=True)