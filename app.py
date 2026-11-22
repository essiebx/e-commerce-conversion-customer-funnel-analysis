from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
REPORTS_PATH = ROOT / "reports"

STAGE_COLORS = {
    "product_view": "#00B4D8",
    "cart": "#FF9F1C",
    "purchase": "#06D6A0",
}


@st.cache_data(ttl=300)
def load_report(filename: str, mtime: float) -> pd.DataFrame:
    del mtime
    return pd.read_csv(REPORTS_PATH / filename)


def report_mtime(filename: str) -> float:
    path = REPORTS_PATH / filename
    return path.stat().st_mtime if path.exists() else 0.0


st.set_page_config(page_title="Customer Funnel Analytics", page_icon="📈", layout="wide")
st.title("Customer Funnel Analytics")
st.caption("A decision-support dashboard for Retailrocket e-commerce behavior")

required_reports = [
    "funnel_summary.csv",
    "segment_summary.csv",
    "revenue_opportunity.csv",
]
missing_reports = [name for name in required_reports if not (REPORTS_PATH / name).exists()]

if missing_reports:
    st.error("The dashboard reports are missing.")
    st.write("Missing files:")
    for name in missing_reports:
        st.write(f"- `reports/{name}`")
    st.info("Commit generated report CSV files to the repository, or regenerate them locally before deployment.")
    st.code("python scripts/analyze_funnel.py")
    st.stop()

try:
    funnel = load_report("funnel_summary.csv", report_mtime("funnel_summary.csv"))
    segment = load_report("segment_summary.csv", report_mtime("segment_summary.csv"))
    opportunity = load_report("revenue_opportunity.csv", report_mtime("revenue_opportunity.csv"))
except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
    st.error("A report could not be loaded.")
    st.exception(error)
    st.stop()

manifest_path = REPORTS_PATH / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None

first_stage = funnel.iloc[0] if not funnel.empty else None
purchase_row = funnel.loc[funnel["stage"] == "purchase"] if "purchase" in funnel["stage"].values else pd.DataFrame()
purchasers = int(purchase_row["users"].iloc[0]) if not purchase_row.empty else 0
first_users = int(first_stage["users"]) if first_stage is not None else 0
overall_conversion = purchasers / first_users if first_users else 0.0

largest_dropoff = None
if len(funnel) > 1:
    dropoffs = funnel.iloc[1:]
    if not dropoffs.empty:
        largest_dropoff = dropoffs.loc[dropoffs["drop_off_users"].idxmax()]

st.sidebar.header("Dashboard Filters")
segment_options = segment.copy()
available_segments = []

for dimension in ("campaign", "channel", "device"):
    if dimension in segment_options:
        values = sorted(segment_options[dimension].dropna().astype(str).unique().tolist())
        if values:
            selected = st.sidebar.multiselect(dimension.title(), values, default=[])
            if selected:
                segment_options = segment_options[segment_options[dimension].astype(str).isin(selected)]
            available_segments.append((dimension, values, selected))

if st.sidebar.button("Reset segment filters", width="stretch"):
    st.rerun()

st.sidebar.caption("Filters affect the segment summary when the source provides these dimensions.")

overview, funnel_tab, segment_tab, opportunity_tab, methodology_tab = st.tabs([
    "Overview",
    "Funnel performance",
    "Segments",
    "Opportunities",
    "Methodology",
])

with overview:
    st.subheader("Business Problem")
    st.write(
        "Identify where customers abandon the e-commerce journey, quantify the size of those losses, "
        "and prioritize experiments that improve conversion from product discovery to purchase."
    )

    objective_left, objective_right = st.columns(2)
    with objective_left:
        st.markdown("**Primary objective**")
        st.write("Measure stage-to-stage and overall conversion using chronological event progression.")
    with objective_right:
        st.markdown("**Current scope**")
        st.write("Product view → cart → purchase. Retailrocket does not provide real attribution or transaction values.")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("First-stage users", f"{first_users:,}" )
    kpi2.metric("Purchasers", f"{purchasers:,}")
    kpi3.metric("First-stage-to-purchase", f"{overall_conversion:.2%}")
    kpi4.metric("Largest drop-off", largest_dropoff["stage"] if largest_dropoff is not None else "Unavailable")

    if largest_dropoff is not None:
        st.info(
            f"{largest_dropoff['stage']} lost {int(largest_dropoff['drop_off_users']):,} users "
            f"({largest_dropoff['drop_off_rate']:.2%})."
        )

with funnel_tab:
    st.subheader("Funnel progression")
    chart = px.bar(
        funnel,
        x="stage",
        y="users",
        text="users",
        color="stage",
        color_discrete_map=STAGE_COLORS,
        title="Unique users by funnel stage",
    )
    chart.update_layout(showlegend=False)
    st.plotly_chart(chart, width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("Stage metrics")
        st.dataframe(funnel, width="stretch", hide_index=True)
    with right:
        st.subheader("Drop-off insight")
        if largest_dropoff is not None:
            st.metric(
                str(largest_dropoff["stage"]),
                f"{int(largest_dropoff['drop_off_users']):,} lost",
                f"{largest_dropoff['drop_off_rate']:.2%}",
            )
        st.write("Drop-off is calculated against the immediately preceding stage.")

with segment_tab:
    st.subheader("Segment summary")
    if segment_options.empty:
        st.info("No segment rows match the selected filters.")
    else:
        st.dataframe(segment_options, width="stretch", hide_index=True)

with opportunity_tab:
    st.subheader("Normalized purchase opportunity")
    st.write("This is a normalized opportunity count, not real currency revenue.")

    opportunity_view = opportunity.rename(columns={
        "estimated_avg_purchase": "normalized_purchase_indicator",
        "estimated_recovery_opportunity": "normalized_purchase_opportunity",
    })
    st.dataframe(opportunity_view, width="stretch", hide_index=True)

    chart = px.bar(
        opportunity,
        x="from_stage",
        y="abandoned_users",
        text="abandoned_users",
        color="from_stage",
        title="Abandoned users by transition",
    )
    chart.update_layout(showlegend=False)
    st.plotly_chart(chart, width="stretch")

with methodology_tab:
    st.subheader("Data and Methodology")

    left, right = st.columns(2)
    with left:
        st.markdown("**Stage mapping**")
        st.markdown("- `view` → `product_view`\n- `addtocart` → `cart`\n- `transaction` → `purchase`")
    with right:
        st.markdown("**Data flow**")
        st.markdown("1. Raw Retailrocket CSV or archive\n2. Event normalization\n3. Validation and cleaning\n4. Chronological funnel reporting")

    if manifest:
        st.markdown("**Report freshness**")
        st.json(manifest)

    quality_path = REPORTS_PATH / "data_quality_summary.csv"
    if quality_path.exists():
        st.markdown("**Latest quality summary**")
        st.dataframe(pd.read_csv(quality_path), width="stretch", hide_index=True)

    st.warning(
        "Retailrocket does not provide real basket values, revenue totals, checkout events, "
        "campaign attribution, channels, or devices. Revenue and cart values are normalized indicators."
    )
