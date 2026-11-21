import argparse
import zipfile
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RETAILROCKET_URL = "https://raw.githubusercontent.com/benfred/recommenders/master/data/ecommerce-events.zip"


def download_archive(destination: Path, url: str = RETAILROCKET_URL) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"Download failed with HTTP status {response.status}")
        destination.write_bytes(response.read())
    return destination


def extract_events_archive(archive_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        event_members = [name for name in archive.namelist() if name.endswith("events.csv")]
        if not event_members:
            raise ValueError("Archive does not contain an events.csv file")
        archive.extract(event_members[0], destination_dir)
        return destination_dir / event_members[0]


def extract_source(events_file: Path | None = None, raw_dir: Path = RAW_DIR) -> Path:
    if events_file:
        source = Path(events_file)
        if not source.exists():
            raise FileNotFoundError(f"Source CSV not found: {source}")
        return source

    archive_path = raw_dir / "retailrocket" / "ecommerce-events.zip"
    download_archive(archive_path)
    return extract_events_archive(archive_path, raw_dir / "retailrocket")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Retailrocket source events")
    parser.add_argument("--events-file", type=Path)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    args = parser.parse_args()
    source = extract_source(args.events_file, args.raw_dir)
    print(f"Extracted source events: {source}")


if __name__ == "__main__":
    main()
