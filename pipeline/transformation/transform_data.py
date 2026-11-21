import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "ecommerce_funnel_events.csv"
EVENT_STAGE_MAP = {"view": "product_view", "addtocart": "cart", "transaction": "purchase"}


def transform_retailrocket(events_path: Path, output_path: Path = DEFAULT_OUTPUT) -> pd.DataFrame:
    frame = pd.read_csv(events_path)
    required = {"timestamp", "visitorid", "event", "itemid"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required Retailrocket columns: {sorted(missing)}")

    frame = frame.loc[frame["event"].isin(EVENT_STAGE_MAP)].copy()
    if frame.empty:
        raise ValueError("No supported view, addtocart, or transaction events found")

    frame["event_timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    frame["stage"] = frame["event"].map(EVENT_STAGE_MAP)

    rows = []
    for event_id, row in enumerate(frame.itertuples(index=False), start=1):
        purchase = row.stage == "purchase"
        rows.append({
            "event_id": f"EVT-{event_id:07d}",
            "user_id": f"VIS-{int(row.visitorid):08d}",
            "session_id": f"SES-{int(row.visitorid):08d}",
            "event_timestamp": row.event_timestamp,
            "campaign": "unknown",
            "channel": "unknown",
            "device": "unknown",
            "stage": row.stage,
            "cart_value": "1.00" if purchase else "0.00",
            "revenue": "1.00" if purchase else "0.00",
        })

    result = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Transform Retailrocket events")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    frame = transform_retailrocket(args.source, args.output)
    print(f"Transformed {len(frame):,} events to {args.output}")


if __name__ == "__main__":
    main()
