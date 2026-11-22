from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "ecommerce_funnel_events_clean.csv"
REPORTS_PATH = ROOT / "reports"
STAGES = ["landing", "product_view", "cart", "checkout", "purchase"]


def load_data(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"user_id", "campaign", "channel", "device", "stage", "cart_value", "revenue"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    unknown = set(frame["stage"]) - set(STAGES)
    if unknown:
        raise ValueError(f"Unknown funnel stages: {sorted(unknown)}")

    if "event_timestamp" in frame:
        frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True, errors="coerce")
    return frame


def funnel_summary(frame: pd.DataFrame) -> pd.DataFrame:
    stages = [stage for stage in STAGES if stage in set(frame["stage"])]

    if "event_timestamp" in frame.columns:
        chronological = frame.dropna(subset=["event_timestamp"])
        first_stage_times = (
            chronological.groupby(["user_id", "stage"])["event_timestamp"]
            .min()
            .unstack("stage")
        )

        counts = {}
        for stage_index, stage in enumerate(stages):
            eligible = pd.Series(True, index=first_stage_times.index)
            for previous_stage in stages[:stage_index]:
                eligible &= first_stage_times[previous_stage].notna() if previous_stage in first_stage_times else pd.Series(False, index=first_stage_times.index)
                if previous_stage in first_stage_times:
                    eligible &= first_stage_times[previous_stage] <= first_stage_times[stage]
            counts[stage] = int((eligible & first_stage_times[stage].notna()).sum()) if stage in first_stage_times else 0
    else:
        counts = frame.groupby("stage")["user_id"].nunique().reindex(stages).fillna(0).to_dict()

    rows = []
    for index, stage in enumerate(stages):
        users = int(counts[stage])
        previous = int(counts[stages[index - 1]]) if index else users
        step_conversion = users / previous if previous else 0.0
        denominator = int(counts[stages[0]])
        overall_conversion = users / denominator if denominator else 0.0
        drop_off = previous - users if index else 0
        rows.append({
            "stage": stage,
            "users": users,
            "step_conversion_rate": round(step_conversion, 4),
            "overall_conversion_rate": round(overall_conversion, 4),
            "drop_off_users": drop_off,
            "drop_off_rate": round(drop_off / previous, 4) if previous else 0,
        })
    return pd.DataFrame(rows)


def segment_summary(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.pivot_table(index=["campaign", "channel", "device", "stage"], values="user_id", aggfunc="nunique", fill_value=0)
        .reset_index()
        .rename(columns={"user_id": "users"})
    )


def revenue_opportunity(frame: pd.DataFrame) -> pd.DataFrame:
    purchase_revenue = frame.loc[frame["stage"] == "purchase", "revenue"]
    purchase_rows = len(purchase_revenue)
    average_purchase = purchase_revenue.sum() / purchase_rows if purchase_rows else 0.0

    rows = []
    stages = [stage for stage in STAGES if stage in set(frame["stage"])]
    for index, stage in enumerate(stages[:-1]):
        stage_users = set(frame.loc[frame["stage"] == stage, "user_id"])
        next_stage = stages[index + 1]
        next_users = set(frame.loc[frame["stage"] == next_stage, "user_id"])
        abandoned_users = len(stage_users - next_users)
        opportunity = abandoned_users * average_purchase
        rows.append({
            "from_stage": stage,
            "to_stage": next_stage,
            "abandoned_users": abandoned_users,
            "estimated_avg_purchase": round(average_purchase, 2),
            "estimated_recovery_opportunity": round(opportunity, 2),
        })
    return pd.DataFrame(rows)


def build_chart(summary: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))
    plt.plot(summary["stage"], summary["users"], marker="o", linewidth=2)
    plt.title("E-Commerce Customer Funnel")
    plt.xlabel("Funnel stage")
    plt.ylabel("Unique users")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(REPORTS_PATH / "funnel_conversion.png", dpi=150)
    plt.close()


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Run python pipeline/orchestration/run_pipeline.py "
            "--events-file data/raw/retailrocket/events.csv first"
        )

    frame = load_data(DATA_PATH)
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)

    summary = funnel_summary(frame)
    segments = segment_summary(frame)
    opportunity = revenue_opportunity(frame)

    summary.to_csv(REPORTS_PATH / "funnel_summary.csv", index=False)
    segments.to_csv(REPORTS_PATH / "segment_summary.csv", index=False)
    opportunity.to_csv(REPORTS_PATH / "revenue_opportunity.csv", index=False)

    pipeline_quality = DATA_PATH.parent / "data_quality_summary.csv"
    if pipeline_quality.exists():
        shutil.copy2(pipeline_quality, REPORTS_PATH / "data_quality_summary.csv")

    build_chart(summary)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": str(DATA_PATH.relative_to(ROOT)),
        "source_rows": int(len(frame)),
        "unique_users": int(frame["user_id"].nunique()),
        "stages": summary["stage"].tolist(),
        "reports": [
            "funnel_summary.csv",
            "segment_summary.csv",
            "revenue_opportunity.csv",
            "funnel_conversion.png",
        ],
    }
    (REPORTS_PATH / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Funnel analysis complete")
    print(summary.to_string(index=False))
    print("\nEstimated recovery opportunity:")
    print(opportunity.to_string(index=False))


if __name__ == "__main__":
    main()
