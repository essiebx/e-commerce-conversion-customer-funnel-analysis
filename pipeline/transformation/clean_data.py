import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "ecommerce_funnel_events_clean.csv"
REQUIRED_COLUMNS = {
    "event_id", "user_id", "session_id", "event_timestamp", "campaign",
    "channel", "device", "stage", "cart_value", "revenue",
}
VALID_STAGES = {"landing", "product_view", "cart", "checkout", "purchase"}


def clean_funnel_data(source_path: Path, output_path: Path = DEFAULT_OUTPUT) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(source_path)
    missing_columns = sorted(REQUIRED_COLUMNS - set(raw.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    clean = raw.drop_duplicates().copy()
    clean["event_timestamp"] = pd.to_datetime(clean["event_timestamp"], utc=True, errors="coerce")
    clean = clean.loc[clean["event_timestamp"].notna()].copy()
    clean = clean.loc[clean["stage"].isin(VALID_STAGES)].copy()

    for column in ("event_id", "user_id", "session_id", "campaign", "channel", "device", "stage"):
        clean[column] = clean[column].astype(str).str.strip()

    clean = clean.drop_duplicates(subset=["event_id"])
    clean = clean.sort_values(["user_id", "event_timestamp", "stage"])

    quality = pd.DataFrame([{
        "raw_rows": len(raw),
        "exact_duplicate_rows": int(raw.duplicated().sum()),
        "duplicate_event_ids": int(raw["event_id"].duplicated().sum()),
        "invalid_timestamps": int(pd.to_datetime(raw["event_timestamp"], utc=True, errors="coerce").isna().sum()),
        "invalid_stages": int((~raw["stage"].isin(VALID_STAGES)).sum()),
        "clean_rows": len(clean),
        "excluded_rows": len(raw) - len(clean),
    }])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output_path, index=False)
    quality_path = output_path.parent / "data_quality_summary.csv"
    quality.to_csv(quality_path, index=False)
    return clean, quality


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean normalized funnel data")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    clean, quality = clean_funnel_data(args.source, args.output)
    print(f"Clean rows: {len(clean):,}")
    print(quality.to_string(index=False))


if __name__ == "__main__":
    main()
