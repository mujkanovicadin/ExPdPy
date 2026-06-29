import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from scipy import stats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Convergence for Whom?",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY  = "#0F2942"
TEAL  = "#0D9488"
AMBER = "#D97706"
GRAY  = "#64748B"
CLUB_COLORS = ["#0F2942","#0D9488","#D97706","#7C3AED","#DC2626","#94A3B8"]

COUNTRY_COLORS = {
    "Slovenia":            "#0F2942",
    "Croatia":             "#0D9488",
    "Bosnia & Herzegovina":"#D97706",
    "Serbia":              "#7C3AED",
    "Montenegro":          "#DC2626",
    "North Macedonia":     "#0369A1",
    "Kosovo":              "#65A30D",
}

st.markdown(f"""
<style>
  [data-testid="stSidebar"] {{ background:#0F2942; }}
  [data-testid="stSidebar"] * {{ color:#F1F5F9 !important; }}
  [data-testid="stSidebar"] .stRadio label {{ color:#F1F5F9 !important; font-size:.95rem; }}
  [data-testid="stSidebar"] hr {{ border-color:#1E3A5F; }}
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stSlider label {{ color:#94A3B8 !important; font-size:.8rem; }}
  [data-testid="stSidebar"] h3 {{ color:#0D9488 !important; font-size:1rem; margin-bottom:0; }}
  .block-container {{ padding-top:1.5rem; max-width:1200px; }}
  h1 {{ color:#0F2942; border-bottom:3px solid #0D9488; padding-bottom:.35rem; font-size:2rem; }}
  h2 {{ color:#0F2942; margin-top:1.5rem; font-size:1.4rem; }}
  h3 {{ color:#0F2942; font-size:1.1rem; }}
  .card {{
    background:#fff; border:1px solid #E2E8F0; border-radius:10px;
    padding:1.1rem 1rem; text-align:center;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
  }}
  .card .val {{ font-size:2rem; font-weight:700; color:#0D9488; line-height:1.1; }}
  .card .lbl {{ font-size:.78rem; color:#64748B; margin-top:.25rem; }}
  .section-intro {{
    background:#F0FDFA; border-left:4px solid #0D9488;
    padding:.75rem 1rem; border-radius:0 8px 8px 0;
    font-size:.92rem; color:#0F2942; margin-bottom:1.2rem;
  }}
  .teal-bar {{
    height:4px; background:#0D9488; border-radius:2px; margin-bottom:1.2rem;
  }}
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df  = pd.read_parquet("expdpy_sample.parquet")
    geo = json.load(open("regions.geojson"))
    return df, geo

df, geo = load_data()

YEAR_COL    = "year"
ID_COL      = "region_num"
GEO_ID      = "region_id"
GDP_COL     = "ln_gdp_pc"
GDP_RAW     = "gdp_per_capita"
NAME_COL    = "region_name"
COUNTRY_COL = "country"
CLUB_COL    = next((c for c in df.columns if "club" in c.lower()), None)

years = sorted(df[YEAR_COL].unique())
N     = df[ID_COL].nunique()
y0, yT = years[0], years[-1]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Convergence for Whom?")
    st.markdown("Ex-Yugoslav Regions · 2000–2022")
    st.markdown("---")
    st.markdown("### Section")
    section = st.radio(
        "",
        ["Overview", "Descriptive Statistics", "Beta Convergence",
         "Sigma Convergence", "Club Convergence"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("### Filters")
    year_range = st.slider("Year range", int(y0), int(yT), (int(y0), int(yT)))
    countries  = sorted(df[COUNTRY_COL].unique())
    sel_countries = st.multiselect("Countries", countries, default=countries)
    st.markdown("---")
    st.markdown(
        "<small>Adin Mujkanovic · Nagoya University GSID<br>"
        "Supervised by Prof. Carlos Mendez · 2025–2027</small>",
        unsafe_allow_html=True,
    )

dff = df[
    (df[YEAR_COL] >= year_range[0]) &
    (df[YEAR_COL] <= year_range[1]) &
    (df[COUNTRY_COL].isin(sel_countries))
].copy()

# ─────────────────────────────────────────────────────────────────────────────
# OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if section == "Overview":
    st.markdown("# Convergence for Whom?")
    st.markdown(
        "**Club Formation and Persistent Inequality in the Post-Yugoslav Space**  \n"
        "Country-year exploration of subnational GDP per capita across 71 NUTS3-equivalent regions · "
        "Adin Mujkanovic · Nagoya University GSID"
    )
    st.markdown('<div class="teal-bar"></div>', unsafe_allow_html=True)

    # ── Stat cards ────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    latest = df[df[YEAR_COL] == yT]
    mean_gdp = latest[GDP_RAW].mean()
    max_gdp  = latest[GDP_RAW].max()
    min_gdp  = latest[GDP_RAW].min()

    for col, val, lbl in [
        (c1, N, "Regions"),
        (c2, len(countries), "Countries"),
        (c3, f"{y0}–{yT}", "Period"),
        (c4, f"€{mean_gdp:,.0f}", f"Mean GDP pc ({yT})"),
        (c5, f"{max_gdp/min_gdp:.1f}×", "Max/Min ratio"),
    ]:
        col.markdown(
            f'<div class="card"><div class="val">{val}</div>'
            f'<div class="lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Two-column layout: coverage + map ─────────────────────────────────────
    left, right = st.columns([1, 1.6])

    with left:
        st.markdown("### Panel coverage")
        coverage = df.groupby(YEAR_COL)[ID_COL].count().reset_index()
        coverage.columns = ["Year", "Regions"]
        fig_cov = px.area(
            coverage, x="Year", y="Regions",
            color_discrete_sequence=[TEAL],
        )
        fig_cov.update_layout(
            margin=dict(l=0,r=0,t=10,b=0),
            height=260,
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#FAFAFA",
            yaxis=dict(range=[0, N+5], gridcolor="#E2E8F0"),
            xaxis=dict(gridcolor="#E2E8F0"),
            showlegend=False,
        )
        fig_cov.update_traces(line_color=TEAL, fillcolor="rgba(13,148,136,.15)")
        st.plotly_chart(fig_cov, use_container_width=True)

        # Country breakdown table
        st.markdown("### Regions per country")
        ctry = df.groupby(COUNTRY_COL)[ID_COL].nunique().reset_index()
        ctry.columns = ["Country", "Regions"]
        ctry = ctry.sort_values("Regions", ascending=False)
        st.dataframe(ctry, use_container_width=True, hide_index=True, height=260)

    with right:
        st.markdown("### GDP per capita map")
        map_year = st.slider(
            "Map year", int(y0), int(yT), int(yT), key="map_year"
        )
        map_df = df[df[YEAR_COL] == map_year][[GEO_ID, NAME_COL, COUNTRY_COL, GDP_RAW, GDP_COL]].copy()

        fig_map = px.choropleth(
            map_df,
            geojson=geo,
            locations=GEO_ID,
            featureidkey="properties.NUTS_ID",
            color=GDP_RAW,
            hover_name=NAME_COL,
            hover_data={COUNTRY_COL: True, GDP_RAW: ":,.0f", GEO_ID: False},
            color_continuous_scale=[
                [0.0, "#CCFBF1"],
                [0.3, "#0D9488"],
                [0.7, "#0F5942"],
                [1.0, "#0F2942"],
            ],
            labels={GDP_RAW: "GDP pc (€)", COUNTRY_COL: "Country"},
        )
        fig_map.update_geos(
            fitbounds="locations",
            visible=False,
            bgcolor="#FAFAFA",
            projection_type="mercator",
            lataxis_range=[40, 47],
            lonaxis_range=[13, 23],
        )
        fig_map.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=460,
            paper_bgcolor="#FAFAFA",
            coloraxis_colorbar=dict(
                title="GDP pc (€)",
                thickness=12,
                len=0.7,
                tickformat=",.0f",
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    # ── GDP distribution over time ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### GDP per capita distribution over time")
    st.markdown(
        '<div class="section-intro">Box plots show the full cross-sectional distribution '
        'of GDP per capita across all 71 regions for each year. '
        'Narrowing boxes signal convergence.</div>',
        unsafe_allow_html=True,
    )

    box_df = dff.copy()
    fig_box = px.box(
        box_df, x=YEAR_COL, y=GDP_RAW,
        color=COUNTRY_COL,
        color_discrete_map=COUNTRY_COLORS,
        labels={GDP_RAW: "GDP per capita (€)", YEAR_COL: "Year"},
        points=False,
    )
    fig_box.update_layout(
        height=380,
        plot_bgcolor="#FAFAFA",
        paper_bgcolor="#FAFAFA",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(gridcolor="#E2E8F0"),
        xaxis=dict(gridcolor="#E2E8F0"),
        margin=dict(l=0,r=0,t=30,b=0),
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# DESCRIPTIVE STATISTICS
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Descriptive Statistics":
    st.markdown("# Descriptive Statistics")
    st.markdown('<div class="teal-bar"></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["By country", "By region"])

    with tab1:
        latest = dff[dff[YEAR_COL] == dff[YEAR_COL].max()]
        ctry_stats = (
            latest.groupby(COUNTRY_COL)[GDP_RAW]
            .agg(N="count", Mean="mean", Median="median",
                 Min="min", Max="max", Std="std")
            .round(1).reset_index()
        )
        st.dataframe(ctry_stats, use_container_width=True, hide_index=True)

        fig = px.bar(
            ctry_stats.sort_values("Mean"),
            x="Mean", y=COUNTRY_COL, orientation="h",
            color=COUNTRY_COL, color_discrete_map=COUNTRY_COLORS,
            labels={"Mean": f"Mean GDP pc ({dff[YEAR_COL].max()})", COUNTRY_COL: ""},
        )
        fig.update_layout(
            height=320, showlegend=False,
            plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA",
            xaxis=dict(gridcolor="#E2E8F0"),
            margin=dict(l=0,r=0,t=10,b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        latest2 = dff[dff[YEAR_COL] == dff[YEAR_COL].max()].sort_values(GDP_RAW, ascending=False)
        st.dataframe(
            latest2[[NAME_COL, COUNTRY_COL, GDP_RAW, GDP_COL]]
            .rename(columns={GDP_RAW:"GDP pc (€)", GDP_COL:"ln GDP pc"})
            .reset_index(drop=True),
            use_container_width=True,
            height=500,
        )

# ─────────────────────────────────────────────────────────────────────────────
# BETA CONVERGENCE
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Beta Convergence":
    st.markdown("# β-Convergence")
    st.markdown('<div class="teal-bar"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-intro">Do initially poorer regions grow faster? '
        'A negative slope (β &lt; 0) indicates unconditional β-convergence — '
        'the speed at which lagging regions catch up to leaders.</div>',
        unsafe_allow_html=True,
    )

    first = dff[dff[YEAR_COL]==dff[YEAR_COL].min()][[ID_COL, NAME_COL, COUNTRY_COL, GDP_COL]].rename(columns={GDP_COL:"y0"})
    last  = dff[dff[YEAR_COL]==dff[YEAR_COL].max()][[ID_COL, GDP_COL]].rename(columns={GDP_COL:"yT"})
    cs    = first.merge(last, on=ID_COL).dropna()
    periods = year_range[1] - year_range[0]
    cs["growth"] = (cs["yT"] - cs["y0"]) / max(periods, 1)

    slope, intercept, r, p, se = stats.linregress(cs["y0"], cs["growth"])
    lam  = -np.log(1 + slope) if slope > -1 else np.nan
    half = np.log(2) / lam if (not np.isnan(lam) and lam > 0) else np.nan

    m1, m2, m3, m4, m5 = st.columns(5)
    for col, val, lbl in [
        (m1, f"{slope:.4f}", "β (slope)"),
        (m2, f"{se:.4f}", "Std. error"),
        (m3, f"{r**2:.3f}", "R²"),
        (m4, f"{lam:.4f}" if not np.isnan(lam) else "—", "Speed λ"),
        (m5, f"{half:.1f} yrs" if not np.isnan(half) else "—", "Half-life"),
    ]:
        col.markdown(
            f'<div class="card"><div class="val">{val}</div>'
            f'<div class="lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")
    cs["color"] = cs[COUNTRY_COL].map(COUNTRY_COLORS).fillna(GRAY)
    xfit = np.linspace(cs["y0"].min(), cs["y0"].max(), 200)
    yfit = intercept + slope * xfit

    fig = go.Figure()
    for country in sorted(cs[COUNTRY_COL].unique()):
        sub = cs[cs[COUNTRY_COL]==country]
        fig.add_trace(go.Scatter(
            x=sub["y0"], y=sub["growth"],
            mode="markers",
            name=country,
            marker=dict(color=COUNTRY_COLORS.get(country, GRAY), size=9,
                        line=dict(width=0.5, color="white")),
            text=sub[NAME_COL],
            hovertemplate="<b>%{text}</b><br>Initial ln GDP: %{x:.3f}<br>Growth: %{y:.4f}<extra></extra>",
        ))
    fig.add_trace(go.Scatter(
        x=xfit, y=yfit, mode="lines",
        line=dict(color=NAVY, width=2),
        name=f"OLS fit (β={slope:.4f})",
        hoverinfo="skip",
    ))
    fig.update_layout(
        height=460,
        plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA",
        xaxis=dict(title="Initial ln GDP per capita", gridcolor="#E2E8F0"),
        yaxis=dict(title="Average annual growth", gridcolor="#E2E8F0"),
        legend=dict(orientation="v", x=1.01, y=1),
        margin=dict(l=0,r=0,t=20,b=0),
        title=dict(
            text=f"Unconditional β-convergence  (N={len(cs)}, β={slope:.4f}, SE={se:.4f}, R²={r**2:.3f})",
            font=dict(size=13, color=NAVY),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    if slope < 0 and p < 0.05:
        st.success(f"β-convergence confirmed (β = {slope:.4f}, p = {p:.2e}). Implied half-life ≈ {half:.1f} years.")
    elif slope < 0:
        st.warning(f"Negative slope (β = {slope:.4f}) but not significant at 5% (p = {p:.3f}).")
    else:
        st.error("No β-convergence detected in this sample/period.")

# ─────────────────────────────────────────────────────────────────────────────
# SIGMA CONVERGENCE
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Sigma Convergence":
    st.markdown("# σ-Convergence")
    st.markdown('<div class="teal-bar"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-intro">Does the cross-sectional dispersion of log GDP per capita '
        'shrink over time? A declining standard deviation confirms σ-convergence.</div>',
        unsafe_allow_html=True,
    )

    def gini(s):
        s = s.dropna().values
        if len(s) == 0 or s.mean() == 0: return np.nan
        return np.abs(np.subtract.outer(s,s)).sum() / (2*len(s)**2*s.mean())

    sigma = dff.groupby(YEAR_COL)[GDP_COL].agg(std="std", gini=gini).reset_index()
    slope_s, int_s, _, p_s, _ = stats.linregress(sigma[YEAR_COL], sigma["std"])
    slope_g, int_g, _, p_g, _ = stats.linregress(sigma[YEAR_COL], sigma["gini"])

    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in [
        (m1, f"{slope_s:.4f}", "Std trend / year"),
        (m2, f"{p_s:.2e}", "p-value (std)"),
        (m3, f"{slope_g:.4f}", "Gini trend / year"),
        (m4, f"{p_g:.2e}", "p-value (Gini)"),
    ]:
        col.markdown(
            f'<div class="card"><div class="val" style="font-size:1.4rem">{val}</div>'
            f'<div class="lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")
    xfit = np.array([sigma[YEAR_COL].min(), sigma[YEAR_COL].max()])

    left, right = st.columns(2)
    for col, y_col, label, color, sl, it in [
        (left,  "std",  "Std. dev. of ln GDP pc", TEAL,  slope_s, int_s),
        (right, "gini", "Gini index",              AMBER, slope_g, int_g),
    ]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sigma[YEAR_COL], y=sigma[y_col],
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=5),
            name=label,
        ))
        fig.add_trace(go.Scatter(
            x=xfit, y=it + sl*xfit,
            mode="lines", line=dict(color=NAVY, dash="dash", width=1.5),
            name=f"Trend ({sl:.4f}/yr)",
        ))
        fig.update_layout(
            height=320,
            plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA",
            xaxis=dict(title="Year", gridcolor="#E2E8F0"),
            yaxis=dict(title=label, gridcolor="#E2E8F0"),
            title=dict(text=label, font=dict(size=12, color=NAVY)),
            legend=dict(x=0, y=-0.25, orientation="h"),
            margin=dict(l=0,r=0,t=30,b=0),
        )
        col.plotly_chart(fig, use_container_width=True)

    if slope_s < 0 and p_s < 0.05:
        st.success(f"σ-convergence confirmed: dispersion fell {slope_s:.4f} per year (p = {p_s:.2e}).")
    else:
        st.warning("Dispersion trend not statistically significant at 5%.")

# ─────────────────────────────────────────────────────────────────────────────
# CLUB CONVERGENCE
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Club Convergence":
    st.markdown("# Club Convergence")
    st.markdown('<div class="teal-bar"></div>', unsafe_allow_html=True)

    if CLUB_COL is None:
        st.markdown(
            '<div class="section-intro">⚠️ No club column detected in the dataset. '
            'Merge your Stata output (<code>f_club2000</code>) into the CSV — '
            'any column containing "club" will be auto-detected.</div>',
            unsafe_allow_html=True,
        )
    else:
        annual_mean = dff.groupby(YEAR_COL)[GDP_COL].mean().rename("cross_mean")
        dff2 = dff.merge(annual_mean, on=YEAR_COL)
        dff2["rel"] = dff2[GDP_COL] / dff2["cross_mean"]
        club_paths = dff2.groupby([YEAR_COL, CLUB_COL])["rel"].mean().reset_index()
        clubs = sorted(club_paths[CLUB_COL].unique())

        fig = go.Figure()
        fig.add_hline(y=1, line_dash="dot", line_color="black", opacity=0.3)
        for i, club in enumerate(clubs):
            sub = club_paths[club_paths[CLUB_COL]==club]
            ls = "dash" if "div" in str(club).lower() or str(club) in ["6"] else "solid"
            fig.add_trace(go.Scatter(
                x=sub[YEAR_COL], y=sub["rel"],
                mode="lines+markers",
                name=str(club),
                line=dict(color=CLUB_COLORS[i % len(CLUB_COLORS)], width=2.2, dash=ls),
                marker=dict(size=4),
            ))
        fig.update_layout(
            height=420,
            plot_bgcolor="#FAFAFA", paper_bgcolor="#FAFAFA",
            xaxis=dict(title="Year", gridcolor="#E2E8F0"),
            yaxis=dict(title="Relative ln GDP pc (mean = 1)", gridcolor="#E2E8F0"),
            title=dict(text="Phillips-Sul Convergence Club Transition Paths",
                       font=dict(size=13, color=NAVY)),
            legend=dict(title="Club", x=1.01, y=1),
            margin=dict(l=0,r=0,t=40,b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Membership table + map
        st.markdown("### Club membership")
        first_y = dff[dff[YEAR_COL]==dff[YEAR_COL].min()]
        last_y  = dff[dff[YEAR_COL]==dff[YEAR_COL].max()]
        n_mem   = dff.groupby(CLUB_COL)[ID_COL].nunique().rename("N Regions")
        g_start = first_y.groupby(CLUB_COL)[GDP_COL].mean().rename(f"ln GDP pc ({y0})")
        g_end   = last_y.groupby(CLUB_COL)[GDP_COL].mean().rename(f"ln GDP pc ({yT})")
        table   = pd.concat([n_mem, g_start, g_end], axis=1).reset_index()
        table[f"ln GDP pc ({y0})"] = table[f"ln GDP pc ({y0})"].round(3)
        table[f"ln GDP pc ({yT})"] = table[f"ln GDP pc ({yT})"].round(3)
        st.dataframe(table, use_container_width=True, hide_index=True)

        st.markdown("### Club map")
        latest_club = dff[dff[YEAR_COL]==dff[YEAR_COL].max()][[GEO_ID, NAME_COL, COUNTRY_COL, CLUB_COL]].copy()
        latest_club[CLUB_COL] = latest_club[CLUB_COL].astype(str)
        club_order = sorted(latest_club[CLUB_COL].unique())
        club_color_map = {str(c): CLUB_COLORS[i % len(CLUB_COLORS)] for i, c in enumerate(club_order)}
        fig_map = px.choropleth(
            latest_club,
            geojson=geo,
            locations=GEO_ID,
            featureidkey="properties.NUTS_ID",
            color=CLUB_COL,
            hover_name=NAME_COL,
            hover_data={COUNTRY_COL: True, GEO_ID: False},
            color_discrete_map=club_color_map,
            category_orders={CLUB_COL: club_order},
            labels={CLUB_COL: "Club"},
        )
        fig_map.update_geos(
            fitbounds="locations", visible=False, bgcolor="#FAFAFA",
            projection_type="mercator",
            lataxis_range=[40, 47],
            lonaxis_range=[13, 23],
        )
        fig_map.update_layout(
            margin=dict(l=0,r=0,t=0,b=0), height=440,
            paper_bgcolor="#FAFAFA",
            legend=dict(title="Club", x=1.01, y=0.5),
        )
        st.plotly_chart(fig_map, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small>Adin Mujkanovic · Graduate School of International Development, Nagoya University · "
    "Supervised by Prof. Carlos Mendez · 2025–2027 · "
    "<a href='https://github.com/mujkanovicadin' target='_blank'>GitHub</a></small>",
    unsafe_allow_html=True,
)
