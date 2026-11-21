import argparse
from pathlib import Path

import pandas as pd

REQUIRED_RETAILROCKET_COLUMNS = {"timestamp", "visitorid", "event", "itemid"}
SUPPORTED_EVENTS = {"view", "addtocart", "transaction"}


def validate_retailrocket_source(frame: pd.DataFrame) -> dict:
    missing = sorted(REQUIRED_RETAILROCKET_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required Retailrocket columns: {missing}")

    supported = frame.loc[frame["event"].isin(SUPPORTED_EVENTS)]
    if supported.empty:
        raise ValueError("No supported view, addtocart, or transaction events found")

    return {
        "rows": len(frame),
        "supported_rows": len(supported),
        "unsupported_rows": len(frame) - len(supported),
        "unique_visitors": frame["visitorid"].nunique(),
    }


def validate_source_file(source_path: Path) -> dict:
    frame = pd.read_csv(source_path)
    return validate_retailrocket_source(frame)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Retailrocket source data")
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    result = validate_source_file(args.source)
    print(result)


if __name__ == "__main__":
    main()
