"""
dashboard.py
------------
Master Streamlit dashboard for Vietnam SDG indicator data.
Run with:  streamlit run dashboard.py

Spreadsheet inventory (all in the same directory):
  gdp.xlsx         – SDG 8.1.1  Annual growth rate of real GDP per capita (%)
  unempl.xlsx      – SDG 8.5.2  Unemployment rate, by sex and age (%)
  neet.xlsx        – SDG 8.6.1  Youth not in education, employment or training (%)
  propb50.xlsx     – SDG 10.2.1 Proportion of people below 50% of median income (%)
  propteach.xlsx   – SDG 4.c.1  Proportion of teachers with minimum qualifications (%)
  partrateedu.xlsx – SDG 4.3.1  Participation rate in education and training (%)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Vietnam SDG Dashboard",
    page_icon="🇻🇳",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent

SEX_COLORS  = {"BOTHSEX": "#1565c0", "FEMALE": "#c2185b", "MALE": "#2e7d32"}
SEX_LABELS  = {"BOTHSEX": "Both Sexes", "FEMALE": "Female", "MALE": "Male"}
SEX_STYLES  = {"BOTHSEX": "-", "FEMALE": "--", "MALE": "-."}

LEVEL_ORDER  = ["PREPRI", "PRIMAR", "LOWSEC", "SECOND", "UPPSEC"]
LEVEL_LABELS = {
    "PREPRI": "Pre-primary",
    "PRIMAR": "Primary",
    "LOWSEC": "Lower Secondary",
    "SECOND": "Secondary",
    "UPPSEC": "Upper Secondary",
}
LEVEL_COLORS = ["#1565c0", "#2e7d32", "#f57f17", "#6a1b9a", "#c62828"]

# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------
@st.cache_data
def load(filename: str, sheet: str = "Record format") -> pd.DataFrame:
    return pd.read_excel(DATA_DIR / filename, sheet_name=sheet)


def gdp_series() -> pd.DataFrame:
    df = load("gdp.xlsx")[["TimePeriod", "Value"]].dropna()
    df["TimePeriod"] = df["TimePeriod"].astype(int)
    return df.sort_values("TimePeriod").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------
def _style_ax(ax, title: str, xlabel: str = "Year", ylabel: str = ""):
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(axis="y", linestyle=":", linewidth=0.7, alpha=0.6, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _add_covid_band(ax):
    """Shade the 2020-2021 COVID disruption period."""
    ax.axvspan(2019.5, 2021.5, alpha=0.08, color="#e53935", zorder=1)
    ax.text(2020.5, ax.get_ylim()[1] * 0.97, "COVID",
            ha="center", va="top", fontsize=7.5, color="#e53935", style="italic")


# ---------------------------------------------------------------------------
# Chart 1 – GDP growth rate
# ---------------------------------------------------------------------------
def chart_gdp() -> plt.Figure:
    data = gdp_series()
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.bar(
        data["TimePeriod"], data["Value"],
        color=["#d32f2f" if v < 0 else "#1565c0" for v in data["Value"]],
        edgecolor="white", linewidth=0.5, zorder=3,
    )
    ax.plot(data["TimePeriod"], data["Value"], color="#ffa000",
            linewidth=1.8, marker="o", markersize=4, zorder=4, label="Annual growth rate")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--", zorder=2)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax.set_xticks(data["TimePeriod"])
    ax.set_xticklabels(data["TimePeriod"], rotation=45, ha="right", fontsize=9)
    _add_covid_band(ax)
    _style_ax(ax,
              "Annual Growth Rate of Real GDP per Capita  (SDG 8.1.1)",
              ylabel="Growth Rate (%)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Chart 2 – GDP vs below-50%-median-income (dual axis)
# ---------------------------------------------------------------------------
def chart_gdp_vs_inequality() -> plt.Figure:
    gdp  = gdp_series()
    b50  = load("propb50.xlsx")[["TimePeriod", "Value"]].dropna()
    b50["TimePeriod"] = b50["TimePeriod"].astype(int)
    b50  = b50.sort_values("TimePeriod").reset_index(drop=True)

    fig, ax1 = plt.subplots(figsize=(12, 4))
    ax2 = ax1.twinx()

    ax1.bar(gdp["TimePeriod"], gdp["Value"],
            color=["#d32f2f" if v < 0 else "#bbdefb" for v in gdp["Value"]],
            alpha=0.7, label="GDP Growth Rate (%)", zorder=2)
    ax1.plot(gdp["TimePeriod"], gdp["Value"],
             color="#1565c0", linewidth=1.5, marker="o", markersize=3, zorder=3)

    ax2.plot(b50["TimePeriod"], b50["Value"],
             color="#e65100", linewidth=2.2, marker="s", markersize=6,
             zorder=4, label="Below 50% Median Income (%)")
    ax2.fill_between(b50["TimePeriod"], b50["Value"],
                     alpha=0.12, color="#e65100")

    ax1.set_ylabel("GDP Growth Rate (%)", color="#1565c0", fontsize=10)
    ax2.set_ylabel("Population Below 50% Median Income (%)", color="#e65100", fontsize=10)
    ax1.tick_params(axis="y", labelcolor="#1565c0")
    ax2.tick_params(axis="y", labelcolor="#e65100")

    all_years = sorted(set(gdp["TimePeriod"].tolist() + b50["TimePeriod"].tolist()))
    ax1.set_xticks(all_years)
    ax1.set_xticklabels(all_years, rotation=45, ha="right", fontsize=8)
    ax1.grid(axis="y", linestyle=":", alpha=0.35)
    ax1.spines["top"].set_visible(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper left")
    ax1.set_title(
        "GDP Growth vs. Population Below 50% of Median Income  (SDG 8.1.1 × 10.2.1)",
        fontsize=12, fontweight="bold", pad=12,
    )
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Chart 3 – Unemployment rate by sex (age 15+)
# ---------------------------------------------------------------------------
def chart_unemployment_by_sex() -> plt.Figure:
    df = load("unempl.xlsx")
    subset = df[(df["Age"] == "15+") & df["Sex"].isin(SEX_COLORS)]

    fig, ax = plt.subplots(figsize=(12, 4))
    for sex in ["BOTHSEX", "FEMALE", "MALE"]:
        s = subset[subset["Sex"] == sex].sort_values("TimePeriod")
        ax.plot(s["TimePeriod"], s["Value"],
                color=SEX_COLORS[sex], linestyle=SEX_STYLES[sex],
                linewidth=2, marker="o", markersize=5, label=SEX_LABELS[sex])

    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax.set_xticks(sorted(subset["TimePeriod"].unique()))
    ax.set_xticklabels(sorted(subset["TimePeriod"].unique()), rotation=45, ha="right", fontsize=9)
    _add_covid_band(ax)
    _style_ax(ax, "Unemployment Rate by Sex, Age 15+  (SDG 8.5.2)", ylabel="Unemployment Rate (%)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Chart 4 – Youth NEET rate by sex
# ---------------------------------------------------------------------------
def chart_neet_by_sex() -> plt.Figure:
    df = load("neet.xlsx")

    fig, ax = plt.subplots(figsize=(12, 4))
    for sex in ["BOTHSEX", "FEMALE", "MALE"]:
        s = df[df["Sex"] == sex].sort_values("TimePeriod")
        ax.plot(s["TimePeriod"], s["Value"],
                color=SEX_COLORS[sex], linestyle=SEX_STYLES[sex],
                linewidth=2, marker="o", markersize=5, label=SEX_LABELS[sex])
        ax.fill_between(s["TimePeriod"], s["Value"], alpha=0.07, color=SEX_COLORS[sex])

    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax.set_xticks(sorted(df["TimePeriod"].unique()))
    ax.set_xticklabels(sorted(df["TimePeriod"].unique()), rotation=45, ha="right", fontsize=9)
    _add_covid_band(ax)
    _style_ax(ax, "Youth NEET Rate by Sex, Age 15-24  (SDG 8.6.1)", ylabel="NEET Rate (%)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Chart 5 – Qualified teachers by education level over time (both sexes)
# ---------------------------------------------------------------------------
def chart_teachers_by_level() -> plt.Figure:
    df = load("propteach.xlsx")
    # Only levels with multi-year time series
    ts_levels = ["PREPRI", "PRIMAR", "LOWSEC"]
    subset = df[(df["Sex"] == "BOTHSEX") & df["Education level"].isin(ts_levels)]

    fig, ax = plt.subplots(figsize=(12, 4))
    for level, color in zip(ts_levels, LEVEL_COLORS):
        s = subset[subset["Education level"] == level].sort_values("TimePeriod")
        ax.plot(s["TimePeriod"], s["Value"],
                color=color, linewidth=2, marker="o", markersize=4,
                label=LEVEL_LABELS[level])

    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.set_ylim(0, 108)
    _add_covid_band(ax)
    _style_ax(ax,
              "Proportion of Qualified Teachers by Education Level  (SDG 4.c.1)",
              ylabel="% with Min. Qualifications")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Chart 6 – Gender gap in teacher qualifications (latest-year snapshot)
# ---------------------------------------------------------------------------
def chart_teachers_gender_gap() -> plt.Figure:
    df = load("propteach.xlsx")
    latest = (df[df["Sex"].isin(["FEMALE", "MALE"])]
              .sort_values("TimePeriod")
              .groupby(["Education level", "Sex"])
              .last()
              .reset_index())

    def val(level, sex):
        row = latest[(latest["Education level"] == level) & (latest["Sex"] == sex)]
        return row["Value"].values[0] if len(row) else 0

    female_vals = [val(l, "FEMALE") for l in LEVEL_ORDER]
    male_vals   = [val(l, "MALE")   for l in LEVEL_ORDER]

    x = range(len(LEVEL_ORDER))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 4))
    bars_f = ax.bar([i - w / 2 for i in x], female_vals, w,
                    label="Female", color=SEX_COLORS["FEMALE"], alpha=0.85)
    bars_m = ax.bar([i + w / 2 for i in x], male_vals, w,
                    label="Male", color=SEX_COLORS["MALE"], alpha=0.85)

    for bar in list(bars_f) + list(bars_m):
        if bar.get_height() > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                    f"{bar.get_height():.0f}%",
                    ha="center", va="bottom", fontsize=8)

    ax.set_xticks(list(x))
    ax.set_xticklabels([LEVEL_LABELS[l] for l in LEVEL_ORDER], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.set_ylim(0, 112)
    _style_ax(ax,
              "Qualified Teachers by Sex and Education Level — Most Recent Year  (SDG 4.c.1)",
              ylabel="% with Min. Qualifications")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Chart 7 – Education participation by age group (both sexes)
# ---------------------------------------------------------------------------
def chart_edu_participation_by_age() -> plt.Figure:
    df = load("partrateedu.xlsx")
    subset = df[df["Sex"] == "BOTHSEX"]

    age_groups = {"15-24": "Youth (15-24)", "15-64": "Working-age (15-64)",
                  "25-54": "Prime-age (25-54)", "55-64": "Older adults (55-64)"}

    fig, ax = plt.subplots(figsize=(12, 4))
    for (age, label), color in zip(age_groups.items(), LEVEL_COLORS):
        s = subset[subset["Age"] == age].sort_values("TimePeriod")
        if not s.empty:
            ax.plot(s["TimePeriod"], s["Value"],
                    color=color, linewidth=2, marker="o", markersize=4, label=label)

    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    _add_covid_band(ax)
    _style_ax(ax,
              "Education & Training Participation Rate by Age Group  (SDG 4.3.1)",
              ylabel="Participation Rate (%)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Chart 8 – Education participation by sex, working-age adults (15-64)
# ---------------------------------------------------------------------------
def chart_edu_participation_by_sex(age: str = "15-64") -> plt.Figure:
    df = load("partrateedu.xlsx")
    subset = df[df["Age"] == age]

    fig, ax = plt.subplots(figsize=(12, 4))
    for sex in ["BOTHSEX", "FEMALE", "MALE"]:
        s = subset[subset["Sex"] == sex].sort_values("TimePeriod")
        if not s.empty:
            ax.plot(s["TimePeriod"], s["Value"],
                    color=SEX_COLORS[sex], linestyle=SEX_STYLES[sex],
                    linewidth=2, marker="o", markersize=5, label=SEX_LABELS[sex])

    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    _add_covid_band(ax)
    _style_ax(ax,
              f"Education & Training Participation by Sex, Age {age}  (SDG 4.3.1)",
              ylabel="Participation Rate (%)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ===========================================================================
# Layout
# ===========================================================================
st.title("🇻🇳 Vietnam SDG Indicators Dashboard")
st.caption(
    "Data source: UN SDG global monitoring extracts · Geography: Viet Nam (GeoAreaCode 704)"
)
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Economic Growth",
    "⚖️ Inclusive Growth",
    "👷 Labor Market",
    "🎓 Education",
])

# ---------------------------------------------------------------------------
# Tab 1 – Economic Growth
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("SDG 8.1.1 — Annual Growth Rate of Real GDP per Capita")
    st.markdown(
        "Vietnam sustained one of the world's highest GDP growth rates throughout 2000–2023. "
        "The COVID-19 disruption (shaded) caused a sharp contraction in 2020 followed by a "
        "near-immediate rebound, demonstrating the economy's resilience."
    )
    st.pyplot(chart_gdp())

    with st.expander("Raw data"):
        st.dataframe(gdp_series(), use_container_width=True)

# ---------------------------------------------------------------------------
# Tab 2 – Inclusive Growth
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("SDG 8.1.1 × 10.2.1 — Does Growth Reach the Bottom Half?")
    st.markdown(
        "Vietnam's GDP growth has been robust, yet the share of the population living below "
        "50% of median income has not declined consistently — rising from 8% in 2002 to a "
        "peak near 14% in 2016 before easing slightly. This suggests that while the economy "
        "expands, the gains are not automatically reaching those at the bottom, pointing to "
        "a distributional challenge alongside the growth success story."
    )
    st.pyplot(chart_gdp_vs_inequality())

    with st.expander("Raw data"):
        col1, col2 = st.columns(2)
        with col1:
            st.caption("GDP Growth Rate (annual, 2000–2023)")
            st.dataframe(gdp_series(), use_container_width=True)
        with col2:
            st.caption("Below 50% Median Income (2002–2022, even years)")
            b50 = load("propb50.xlsx")[["TimePeriod", "Value"]].dropna().sort_values("TimePeriod")
            st.dataframe(b50, use_container_width=True)

# ---------------------------------------------------------------------------
# Tab 3 – Labor Market
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("SDG 8.5.2 — Unemployment Rate by Sex, Age 15+")
    st.markdown(
        "Vietnam's overall unemployment rate has stayed low (under 3%), but female unemployment "
        "persistently runs higher than male — a sign that women face structural barriers to "
        "labor market entry. The COVID period produced a visible, temporary spike."
    )
    st.pyplot(chart_unemployment_by_sex())

    st.subheader("SDG 8.6.1 — Youth NEET Rate by Sex, Age 15-24")
    st.markdown(
        "The NEET rate (youth not in education, employment, or training) fell from ~10.7% in "
        "2007 to ~6% by 2019, then spiked back up during COVID. Notably, **female youth are "
        "consistently more likely to be NEET than males**, suggesting they are more vulnerable "
        "to disengagement from both education and the labor market."
    )
    st.pyplot(chart_neet_by_sex())

    with st.expander("Raw data"):
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Unemployment Rate (Age 15+)")
            unempl = load("unempl.xlsx")[["TimePeriod", "Sex", "Age", "Value"]]
            st.dataframe(
                unempl[unempl["Age"] == "15+"].sort_values(["TimePeriod", "Sex"]),
                use_container_width=True,
            )
        with col2:
            st.caption("Youth NEET Rate (Age 15-24)")
            neet = load("neet.xlsx")[["TimePeriod", "Sex", "Value"]]
            st.dataframe(neet.sort_values(["TimePeriod", "Sex"]), use_container_width=True)

# ---------------------------------------------------------------------------
# Tab 4 – Education
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("SDG 4.c.1 — Qualified Teachers Over Time by Education Level")
    st.markdown(
        "Vietnam made rapid gains in teacher qualifications from 2000 onward, with primary and "
        "lower-secondary coverage reaching near-100% by the early 2010s. The sharp dip in 2021 "
        "reflects COVID-19 disruption to teacher certification processes, with a recovery "
        "trajectory visible through 2024. Pre-primary consistently lags the other levels."
    )
    st.pyplot(chart_teachers_by_level())

    st.subheader("SDG 4.c.1 — Gender Gap in Teacher Qualifications (Latest Year)")
    st.markdown(
        "An unexpected finding: **male pre-primary teachers are significantly less likely to hold "
        "minimum qualifications than their female counterparts** (71% vs. 91%). This gap narrows "
        "at higher education levels. The pre-primary gap may reflect the feminization of early "
        "childhood education, where male entrants are fewer and less credentialed on average."
    )
    st.pyplot(chart_teachers_gender_gap())

    st.subheader("SDG 4.3.1 — Education Participation by Age Group")
    st.markdown(
        "Youth (15–24) dominate participation in education and training, as expected. However, "
        "the upward trend in the working-age (15–64) and prime-age (25–54) cohorts indicates "
        "Vietnam is increasingly investing in adult learning — a key ingredient for sustaining "
        "economic growth as the country moves up the value chain."
    )
    st.pyplot(chart_edu_participation_by_age())

    st.subheader("SDG 4.3.1 — Education Participation by Sex, Working-age Adults (15-64)")
    st.markdown(
        "Male and female working-age participation in education and training track very closely, "
        "suggesting broadly equitable access to learning opportunities for adults. This contrasts "
        "with the labor market picture, where gender gaps are more pronounced."
    )
    st.pyplot(chart_edu_participation_by_sex("15-64"))

    with st.expander("Raw data"):
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Qualified Teachers")
            teach = load("propteach.xlsx")[["TimePeriod", "Education level", "Sex", "Value"]]
            st.dataframe(teach.sort_values(["Education level", "TimePeriod"]), use_container_width=True)
        with col2:
            st.caption("Education Participation Rate")
            edu = load("partrateedu.xlsx")[["TimePeriod", "Age", "Sex", "Value"]]
            st.dataframe(edu.sort_values(["Age", "TimePeriod"]), use_container_width=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption("Vietnam SDG Dashboard · ISS_SDG project")
