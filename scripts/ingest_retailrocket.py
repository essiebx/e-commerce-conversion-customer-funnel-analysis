import argparse
import csv
import io
import zipfile
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT = DATA_DIR / "processed" / "ecommerce_funnel_events_normalized.csv"
RETAILROCKET_URL = "https://raw.githubusercontent.com/benfred/recommenders/master/data/ecommerce-events.zip"

EVENT_STAGE_MAP = {
    "view": "product_view",
    "addtocart": "cart",
    "transaction": "purchase",
}


def download_retailrocket_archive(destination: Path, url: str = RETAILROCKET_URL) -> Path:
    """Download the Kaggle-ready Retailrocket event archive."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"Download failed with HTTP status {response.status}")
        destination.write_bytes(response.read())
    return destination


def ingest_retailrocket_events(events_path: Path, output_path: Path = DEFAULT_OUTPUT) -> pd.DataFrame:
    """Convert Retailrocket events.csv rows into the project's funnel schema."""
    frame = pd.read_csv(events_path)
    required = {"timestamp", "visitorid", "event", "itemid"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required Retailrocket columns: {sorted(missing)}")

    frame = frame.loc[frame["event"].isin(EVENT_STAGE_MAP)].copy()
    if frame.empty:
        raise ValueError("No supported view, addtocart, or transaction events found")

    frame["event_timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    frame["stage"] = frame["event"].map(EVENT_STAGE_MAP)

    transactions = frame.loc[frame["event"] == "transaction", ["visitorid", "itemid"]]
    transaction_items = set(map(tuple, transactions.to_numpy()))

    rows = []
    for event_id, row in enumerate(frame.itertuples(index=False), start=1):
        stage = getattr(row, "stage")
        cart_value = 0.0
        revenue = 0.0
        if stage == "purchase":
            revenue = 1.0
            cart_value = 1.0

        rows.append({
            "event_id": f"EVT-{event_id:07d}",
            "user_id": f"VIS-{int(row.visitorid):08d}",
            "session_id": f"SES-{int(row.visitorid):08d}",
            "event_timestamp": row.event_timestamp,
            "campaign": "unknown",
            "channel": "unknown",
            "device": "unknown",
            "stage": stage,
            "cart_value": f"{cart_value:.2f}",
            "revenue": f"{revenue:.2f}",
        })

    result = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def extract_events_from_archive(archive_path: Path, raw_dir: Path) -> Path:
    """Extract events.csv from the downloaded archive."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        event_members = [name for name in archive.namelist() if name.endswith("events.csv")]
        if not event_members:
            raise ValueError("Archive does not contain an events.csv file")
        archive.extract(event_members[0], raw_dir)
        return raw_dir / event_members[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and normalize Retailrocket ecommerce events")
    parser.add_argument("--events-file", type=Path, help="Existing Retailrocket events.csv path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--raw-dir", type=Path, default=DATA_DIR / "raw" / "retailrocket")
    args = parser.parse_args()

    if args.events_file:
        events_path = args.events_file
    else:
        archive_path = args.raw_dir / "ecommerce-events.zip"
        download_retailrocket_archive(archive_path)
        events_path = extract_events_from_archive(archive_path, args.raw_dir)

    frame = ingest_retailrocket_events(events_path, args.output)
    print(f"Ingested {len(frame):,} supported events")
    print(f"Normalized data written to {args.output}")


if __name__ == "__main__":
    main()
