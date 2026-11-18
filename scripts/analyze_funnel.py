from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ecommerce_funnel_events.csv"
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
    return frame


def funnel_summary(frame: pd.DataFrame) -> pd.DataFrame:
    counts = frame.groupby("stage", sort=False)["user_id"].nunique().reindex(STAGES)
    rows = []
    for index, stage in enumerate(STAGES):
        users = int(counts[stage])
        previous = int(counts[STAGES[index - 1]]) if index else users
        step_conversion = users / previous if previous else 0.0
        overall_conversion = users / int(counts["landing"])
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
    purchaser_count = frame.loc[frame["stage"] == "purchase", "user_id"].nunique()
    average_purchase = purchase_revenue.sum() / purchaser_count if purchaser_count else 0.0

    rows = []
    for stage in STAGES[:-1]:
        stage_users = set(frame.loc[frame["stage"] == stage, "user_id"])
        next_stage = STAGES[STAGES.index(stage) + 1]
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
        raise FileNotFoundError("Run python scripts/generate_sample_data.py first")

    frame = load_data(DATA_PATH)
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)

    summary = funnel_summary(frame)
    segments = segment_summary(frame)
    opportunity = revenue_opportunity(frame)

    summary.to_csv(REPORTS_PATH / "funnel_summary.csv", index=False)
    segments.to_csv(REPORTS_PATH / "segment_summary.csv", index=False)
    opportunity.to_csv(REPORTS_PATH / "revenue_opportunity.csv", index=False)
    build_chart(summary)

    print("Funnel analysis complete")
    print(summary.to_string(index=False))
    print("\nEstimated recovery opportunity:")
    print(opportunity.to_string(index=False))


if __name__ == "__main__":
    main()
