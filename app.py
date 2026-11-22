from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
REPORTS_PATH = ROOT / "reports"
DATA_PATH = ROOT / "data" / "processed" / "ecommerce_funnel_events_clean.csv"
STAGES = ["landing", "product_view", "cart", "checkout", "purchase"]

STAGE_COLORS = {
    "landing": "#6C5CE7",
    "product_view": "#00B4D8",
    "cart": "#FF9F1C",
    "checkout": "#EF476F",
    "purchase": "#06D6A0",
}
DIMENSION_COLORS = ["#635BFF", "#00B4D8", "#FF9F1C", "#EF476F", "#06D6A0"]


@st.cache_data(ttl=300)
def load_clean_data(mtime: float) -> pd.DataFrame:
    del mtime
    columns = [
        "event_id", "user_id", "session_id", "event_timestamp",
        "campaign", "channel", "device", "stage", "cart_value", "revenue",
    ]
    frame = pd.read_csv(DATA_PATH, usecols=lambda column: column in set(columns))
    frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True, errors="coerce")
    return frame


@st.cache_data(ttl=300)
def load_report(filename: str, mtime: float) -> pd.DataFrame:
    del mtime
    return pd.read_csv(REPORTS_PATH / filename)


def report_mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def chronological_funnel(frame: pd.DataFrame) -> pd.DataFrame:
    stages = [stage for stage in STAGES if stage in set(frame["stage"])]
    if not stages:
        return pd.DataFrame(columns=[
            "stage", "users", "step_conversion_rate", "overall_conversion_rate",
            "drop_off_users", "drop_off_rate",
        ])

    valid = frame.dropna(subset=["event_timestamp", "user_id", "stage"])
    first_stage_times = (
        valid.groupby(["user_id", "stage"])["event_timestamp"]
        .min()
        .unstack("stage")
    )

    counts = {}
    for stage_index, stage in enumerate(stages):
        if stage not in first_stage_times:
            counts[stage] = 0
            continue

        eligible = pd.Series(True, index=first_stage_times.index)
        for previous_stage in stages[:stage_index]:
            if previous_stage not in first_stage_times:
                eligible &= False
            else:
                eligible &= first_stage_times[previous_stage].notna()
                eligible &= first_stage_times[previous_stage] <= first_stage_times[stage]

        counts[stage] = int((eligible & first_stage_times[stage].notna()).sum())

    rows = []
    for index, stage in enumerate(stages):
        users = int(counts[stage])
        previous = int(counts[stages[index - 1]]) if index else users
        step_rate = users / previous if previous else 0.0
        first_users = int(counts[stages[0]])
        overall_rate = users / first_users if first_users else 0.0
        drop_off = previous - users if index else 0
        rows.append({
            "stage": stage,
            "users": users,
            "step_conversion_rate": round(step_rate, 4),
            "overall_conversion_rate": round(overall_rate, 4),
            "drop_off_users": max(drop_off, 0),
            "drop_off_rate": round(max(drop_off, 0) / previous, 4) if previous else 0.0,
        })
    return pd.DataFrame(rows)


def segment_performance(frame: pd.DataFrame, dimension: str) -> pd.DataFrame:
    stages = [stage for stage in STAGES if stage in set(frame["stage"])]
    if dimension not in frame or not stages:
        return pd.DataFrame()

    valid = frame.dropna(subset=["event_timestamp", "user_id", "stage", dimension])
    rows = []
    for segment, segment_frame in valid.groupby(dimension, sort=True):
        first_stage_times = (
            segment_frame.groupby(["user_id", "stage"])["event_timestamp"]
            .min()
            .unstack("stage")
        )
        if not first_stage_times.empty:
            first_stage = stages[0]
            last_stage = stages[-1]
            first_users = int(first_stage_times[first_stage].notna().sum()) if first_stage in first_stage_times else 0
            purchasers = int(first_stage_times[last_stage].notna().sum()) if last_stage in first_stage_times else 0
            rate = purchasers / first_users if first_users else 0.0
            rows.append({
                "segment": str(segment),
                "dimension": dimension,
                "first_stage_users": first_users,
                "last_stage_users": purchasers,
                "conversion_rate": round(rate, 4),
            })
    return pd.DataFrame(rows)


def reset_filters():
    st.session_state.campaign_filter = []
    st.session_state.channel_filter = []
    st.session_state.device_filter = []
    st.session_state.minimum_users = 0


st.set_page_config(page_title="Customer Funnel Analytics", page_icon="📈", layout="wide")
st.title("Customer Funnel Analytics")
st.caption("A decision-support dashboard for Retailrocket e-commerce behavior")

if not DATA_PATH.exists():
    st.error("Processed clean data was not found.")
    st.code("python pipeline/orchestration/run_pipeline.py --events-file data/raw/retailrocket/events.csv")
    st.stop()

try:
    manifest_path = REPORTS_PATH / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    frame = load_clean_data(report_mtime(DATA_PATH))
    segment_report = load_report("segment_summary.csv", report_mtime(REPORTS_PATH / "segment_summary.csv"))
except (FileNotFoundError, pd.errors.EmptyDataError):
    st.error("The dashboard could not load the processed data or report files.")
    st.stop()

frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True, errors="coerce")
frame = frame.dropna(subset=["event_timestamp"])

with st.sidebar:
    st.header("Filters")

    min_date = frame["event_timestamp"].min().date()
    max_date = frame["event_timestamp"].max().date()

    date_range = st.date_input(
        "Event date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    campaign_values = sorted(frame["campaign"].dropna().astype(str).unique().tolist())
    channel_values = sorted(frame["channel"].dropna().astype(str).unique().tolist())
    device_values = sorted(frame["device"].dropna().astype(str).unique().tolist())

    st.multiselect("Campaign", campaign_values, key="campaign_filter", default=[])
    st.multiselect("Channel", channel_values, key="channel_filter", default=[])
    st.multiselect("Device", device_values, key="device_filter", default=[])
    st.slider("Minimum segment users", 0, 10000, 0, 100, key="minimum_users")

    if st.button("Reset filters", on_click=reset_filters, width="stretch"):
        st.rerun()

filtered = frame.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    start_timestamp = pd.Timestamp(start_date).tz_localize("UTC")
    end_timestamp = pd.Timestamp(end_date).tz_localize("UTC") + pd.Timedelta(days=1)
    filtered = filtered[
        (filtered["event_timestamp"] >= start_timestamp)
        & (filtered["event_timestamp"] < end_timestamp)
    ]

for column, state_key in (
    ("campaign", "campaign_filter"),
    ("channel", "channel_filter"),
    ("device", "device_filter"),
):
    selected = st.session_state.get(state_key, [])
    if selected:
        filtered = filtered[filtered[column].astype(str).isin(selected)]

if filtered.empty:
    st.warning("No data matches the selected filters. Adjust or reset them in the sidebar.")
    st.stop()

funnel = chronological_funnel(filtered)
if funnel.empty:
    st.warning("The filtered data does not contain enough stage information.")
    st.stop()

first_stage = funnel.iloc[0]
purchase_row = funnel.loc[funnel["stage"] == "purchase"] if "purchase" in funnel["stage"].values else pd.DataFrame()
purchasers = int(purchase_row["users"].iloc[0]) if not purchase_row.empty else 0
unique_users = int(filtered["user_id"].nunique())
view_to_purchase = purchasers / int(first_stage["users"]) if int(first_stage["users"]) else 0.0

largest_dropoff_candidates = funnel.iloc[1:] if len(funnel) > 1 else funnel
largest_dropoff = (
    largest_dropoff_candidates.loc[largest_dropoff_candidates["drop_off_users"].idxmax()]
    if not largest_dropoff_candidates.empty
    else None
)

page, funnel_tab, segment_tab, opportunity_tab, methodology_tab = st.tabs([
    "Overview",
    "Funnel performance",
    "Segments",
    "Opportunities",
    "Methodology",
])

with page:
    st.subheader("Business Problem")
    st.write(
        "Identify where customers abandon the e-commerce journey, quantify the cost of those losses, "
        "and prioritize experiments that improve conversion from product discovery to purchase."
    )

    objective_left, objective_right = st.columns(2)
    with objective_left:
        st.markdown("**Primary objective**")
        st.write("Measure stage-to-stage and overall conversion using chronological event progression.")
    with objective_right:
        st.markdown("**Current scope**")
        st.write("Product view → cart → purchase. Campaign, channel, and device values are unavailable in Retailrocket.")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Unique users", f"{unique_users:,}")
    kpi2.metric("First-stage users", f"{int(first_stage['users']):,}")
    kpi3.metric("Purchasers", f"{purchasers:,}")
    kpi4.metric("First-stage to purchase", f"{view_to_purchase:.2%}")

    if largest_dropoff is not None:
        st.info(
            f"**Largest drop-off:** {largest_dropoff['stage']} — "
            f"{int(largest_dropoff['drop_off_users']):,} users "
            f"({largest_dropoff['drop_off_rate']:.2%})."
        )

    applied_filters = []
    if isinstance(date_range, tuple) and len(date_range) == 2:
        applied_filters.append(f"Date: {date_range[0]} to {date_range[1]}")
    for label, key in (("Campaign", "campaign_filter"), ("Channel", "channel_filter"), ("Device", "device_filter")):
        values = st.session_state.get(key, [])
        if values:
            applied_filters.append(f"{label}: {', '.join(values)}")
    st.caption("Applied filters: " + (" • ".join(applied_filters) if applied_filters else "None — full available range"))

with funnel_tab:
    st.subheader("Funnel progression")
    chart = px.bar(
        funnel,
        x="stage",
        y="users",
        text="users",
        color="stage",
        title="Unique users reaching each stage in valid chronological sequence",
        color_discrete_map=STAGE_COLORS,
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
    st.subheader("Segment comparison")
    minimum_users = st.session_state.get("minimum_users", 0)

    segment_frames = []
    for dimension in ("campaign", "channel", "device"):
        result = segment_performance(filtered, dimension)
        if not result.empty:
            segment_frames.append(result[result["first_stage_users"] >= minimum_users])

    if segment_frames:
        segment_table = pd.concat(segment_frames, ignore_index=True)
        st.dataframe(segment_table.sort_values(["dimension", "conversion_rate"], ascending=[True, False]), width="stretch", hide_index=True)

        known_segments = segment_table[segment_table["segment"].astype(str).str.lower() != "unknown"]
        if not known_segments.empty:
            chart = px.bar(
                known_segments,
                x="segment",
                y="conversion_rate",
                color="dimension",
                barmode="group",
                text="conversion_rate",
                title="Conversion rate by available segment",
                color_discrete_sequence=DIMENSION_COLORS,
            )
            chart.update_layout(yaxis_tickformat=".1%")
            st.plotly_chart(chart, width="stretch")
        else:
            st.info("No non-unknown segment values are available in this Retailrocket dataset.")
    else:
        st.info("No segment comparison is available for the filtered data.")

with opportunity_tab:
    st.subheader("Normalized purchase opportunity")
    st.write("This estimates abandoned users between adjacent stages using the normalized purchase indicator. It is not currency revenue.")

    opportunity_rows = []
    for index, stage in enumerate(funnel["stage"].tolist()[:-1]):
        next_stage = funnel["stage"].tolist()[index + 1]
        stage_users = set(filtered.loc[filtered["stage"] == stage, "user_id"])
        next_users = set(filtered.loc[filtered["stage"] == next_stage, "user_id"])
        abandoned = len(stage_users - next_users)
        opportunity_rows.append({
            "transition": f"{stage} → {next_stage}",
            "abandoned_users": abandoned,
            "normalized_purchase_opportunity": abandoned,
        })

    opportunity_table = pd.DataFrame(opportunity_rows)
    if not opportunity_table.empty:
        st.dataframe(opportunity_table.sort_values("abandoned_users", ascending=False), width="stretch", hide_index=True)
        chart = px.bar(opportunity_table, x="transition", y="abandoned_users", text="abandoned_users", color="transition", color_discrete_sequence=["#635BFF", "#00B4D8", "#FF9F1C", "#EF476F"])
        st.plotly_chart(chart, width="stretch")

with methodology_tab:
    st.subheader("Data and Methodology")

    method_left, method_right = st.columns(2)
    with method_left:
        st.markdown("**Stage mapping**")
        st.markdown("- `view` → `product_view`\n- `addtocart` → `cart`\n- `transaction` → `purchase`")
        st.markdown("**Funnel rule**")
        st.write("A visitor counts at a stage only when the stage occurred after each preceding stage.")
    with method_right:
        st.markdown("**Data flow**")
        st.markdown("1. Raw Retailrocket archive or CSV\n2. Event normalization\n3. Validation and cleaning\n4. Chronological funnel reporting")

    if manifest:
        st.json(manifest)

    quality_path = REPORTS_PATH / "data_quality_summary.csv"
    if quality_path.exists():
        st.markdown("**Latest quality summary**")
        st.dataframe(pd.read_csv(quality_path), width="stretch", hide_index=True)

    st.warning(
        "Retailrocket does not provide real basket values, revenue totals, landing pages, checkout events, "
        "campaign attribution, channels, or devices. Revenue and cart values are normalized indicators."
    )
