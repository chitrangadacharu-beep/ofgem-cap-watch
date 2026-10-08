"""
Ofgem Cap Watch — A simple dashboard for understanding the UK default
tariff cap and what a variable-tariff alternative would have meant for
the average household.

Author: Charu Chitrangada
"""

import streamlit as st
import pandas as pd
import altair as alt

# ---------- Setup ----------

st.set_page_config(
    page_title="Ofgem Cap Watch",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Ofgem Cap Watch")
st.caption(
    "Tracking the UK default tariff cap (Apr 2019 – present) and modelling "
    "what a Fuse-style variable tariff and off-peak shifting would do to a "
    "typical household bill."
)

# ---------- Data ----------

@st.cache_data
def load_cap_history() -> pd.DataFrame:
    df = pd.read_csv("data/price_cap_history.csv", parse_dates=["period_start", "period_end"])
    df["label"] = df["period_start"].dt.strftime("%b %Y")
    return df

cap = load_cap_history()
latest = cap.iloc[-1]

# ---------- KPI row ----------

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(
        "Current cap (Apr–Jun 2026)",
        f"£{int(latest['annual_typical_dualfuel_dd']):,}",
        delta=f"−£{int(cap.iloc[-2]['annual_typical_dualfuel_dd'] - latest['annual_typical_dualfuel_dd']):,} vs Q1",
        delta_color="inverse",
    )
with c2:
    peak = cap["annual_typical_dualfuel_dd"].max()
    peak_period = cap.loc[cap["annual_typical_dualfuel_dd"].idxmax(), "label"]
    st.metric("Peak cap (post-crisis)", f"£{int(peak):,}", help=f"Set in {peak_period}")
with c3:
    pct_from_peak = (latest["annual_typical_dualfuel_dd"] / peak - 1) * 100
    st.metric("Current vs peak", f"{pct_from_peak:+.0f}%")

st.divider()

# ---------- Price cap chart ----------

st.subheader("Default tariff cap — quarterly history")

events = pd.DataFrame([
    {"period_start": "2020-03-15", "label": "COVID demand collapse"},
    {"period_start": "2022-02-24", "label": "Russia invades Ukraine"},
    {"period_start": "2022-10-01", "label": "EPG introduced"},
    {"period_start": "2023-07-01", "label": "EPG ends"},
    {"period_start": "2026-04-01", "label": "Apr 2026: −7%"},
])
events["period_start"] = pd.to_datetime(events["period_start"])

base = alt.Chart(cap).encode(
    x=alt.X("period_start:T", title=None),
    y=alt.Y("annual_typical_dualfuel_dd:Q", title="Annual typical dual-fuel bill (£)"),
)

line = base.mark_line(strokeWidth=3, color="#2E75B6").encode(
    tooltip=[
        alt.Tooltip("label:N", title="Period"),
        alt.Tooltip("annual_typical_dualfuel_dd:Q", title="Cap (£)", format=",.0f"),
    ]
)
points = base.mark_point(size=60, color="#2E75B6", filled=True)

rules = alt.Chart(events).mark_rule(strokeDash=[4, 4], color="#888").encode(x="period_start:T")
text = alt.Chart(events).mark_text(
    align="left", dx=4, dy=-6, fontSize=11, color="#444"
).encode(x="period_start:T", text="label:N", y=alt.value(20))

st.altair_chart((line + points + rules + text).properties(height=380), use_container_width=True)

st.caption(
    "Source: Ofgem quarterly press releases. Figures show the published "
    "cap level; during Oct 2022 – Jun 2023, the government's Energy Price "
    "Guarantee capped consumer cost at £2,500 regardless of the headline cap."
)

st.divider()

# ---------- Variable tariff simulator ----------

st.subheader("What would a Fuse-style variable tariff have done?")

st.markdown(
    "Fuse Energy sells a variable-rate tariff designed to sit below the cap. "
    "This sim asks: if you'd been on a tariff pegged at *X%* below the cap "
    "for the last five years, what would your total bill have been versus "
    "sitting on the standard variable tariff?"
)

col_a, col_b = st.columns(2)
with col_a:
    discount_pct = st.slider(
        "Tariff discount vs cap (%)",
        min_value=0, max_value=15, value=5, step=1,
        help="Fuse's reported discount has varied; 3–7% is a realistic band.",
    )
with col_b:
    start_year = st.selectbox(
        "Compare from year",
        options=[2019, 2020, 2021, 2022, 2023, 2024, 2025],
        index=2,
    )

window = cap[cap["period_start"] >= f"{start_year}-01-01"].copy()
window["quarter_share"] = (window["period_end"] - window["period_start"]).dt.days / 365.25
window["cap_cost"] = window["annual_typical_dualfuel_dd"] * window["quarter_share"]
window["variable_cost"] = window["cap_cost"] * (1 - discount_pct / 100)

total_cap = window["cap_cost"].sum()
total_variable = window["variable_cost"].sum()
savings = total_cap - total_variable

c1, c2, c3 = st.columns(3)
c1.metric("On the cap", f"£{total_cap:,.0f}")
c2.metric(f"At {discount_pct}% below cap", f"£{total_variable:,.0f}")
c3.metric("Cumulative saving", f"£{savings:,.0f}", delta_color="off")

comp = window.melt(
    id_vars=["period_start", "label"],
    value_vars=["cap_cost", "variable_cost"],
    var_name="tariff",
    value_name="cost",
)
comp["tariff"] = comp["tariff"].map({
    "cap_cost": "On the cap",
    "variable_cost": f"{discount_pct}% below cap",
})

chart = alt.Chart(comp).mark_area(opacity=0.55).encode(
    x=alt.X("period_start:T", title=None),
    y=alt.Y("cost:Q", title="Quarterly cost (£)", stack=None),
    color=alt.Color("tariff:N", title=None,
                    scale=alt.Scale(range=["#888", "#2E75B6"])),
    tooltip=[
        alt.Tooltip("label:N", title="Period"),
        alt.Tooltip("tariff:N", title="Tariff"),
        alt.Tooltip("cost:Q", title="Cost (£)", format=",.0f"),
    ],
).properties(height=300)

st.altair_chart(chart, use_container_width=True)

st.divider()

# ---------- Off-peak shifting (Project Zero analog) ----------

st.subheader("Off-peak shifting — what's the prize?")

st.markdown(
    "Fuse's *Project Zero* rewards households for shifting flexible loads "
    "(EV charging, heat pumps, hot water) into off-peak windows. Below is a "
    "back-of-envelope of what that's worth on top of any tariff discount."
)

c1, c2 = st.columns(2)
with c1:
    flexible_kwh_per_year = st.slider(
        "Annual flexible kWh (EV + heat pump + hot water)",
        min_value=0, max_value=8000, value=3000, step=250,
        help="Typical EV: ~2,500 kWh/year. Air-source heat pump: ~3,500–6,000 kWh/year.",
    )
with c2:
    peak_offpeak_gap_pence = st.slider(
        "Peak vs off-peak unit gap (p/kWh)",
        min_value=0.0, max_value=30.0, value=15.0, step=0.5,
        help="Octopus Agile and similar ToU tariffs see swings of 10–30 p/kWh.",
    )

shift_share = st.slider(
    "Share of flexible load actually shifted",
    min_value=0, max_value=100, value=60, step=5,
    help="Real-world demand response rarely hits 100%; 50–70% is a defensible target.",
)

annual_saving = flexible_kwh_per_year * (shift_share / 100) * (peak_offpeak_gap_pence / 100)
st.metric(
    "Annual saving from shifting",
    f"£{annual_saving:,.0f}",
    help="Excludes any additional Energy Dollar / token rewards.",
)

st.caption(
    "The operational question this raises: how is the baseline set? "
    "Energy Dollar accrual against a household's own historical pattern "
    "vs. a regional average produces very different incentives — and very "
    "different customer-support conversations."
)

st.divider()

# ---------- Footer ----------

st.markdown(
    """
    ### Notes
    - Cap figures are headline annual values for a typical dual-fuel household paying by direct debit.
      Actual bills vary by region, usage, and standing charge.
    - The variable tariff sim is a linear discount on the cap. Real variable tariffs price off
      wholesale and other costs, not the cap directly — this is a back-of-envelope.
    - The off-peak sim ignores standing charges, network charges, and policy levies.
    - Data last verified: 2026-05. Update `data/price_cap_history.csv` quarterly from
      [Ofgem's press releases](https://www.ofgem.gov.uk/energy-policy-and-regulation/policy-and-regulatory-programmes/default-tariff-cap).
    """
)
