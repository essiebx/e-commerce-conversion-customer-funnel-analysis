import argparse
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RETAILROCKET_URL = "https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset/download?datasetVersionNumber=1"


def download_archive(destination: Path, url: str = RETAILROCKET_URL) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "customer-funnel-analysis/1.0"})
    try:
        with urlopen(request, timeout=60) as response:
            if response.status != 200:
                raise RuntimeError(f"Download failed with HTTP status {response.status}")
            content = response.read()
    except HTTPError as exc:
        raise RuntimeError(
            f"Remote archive returned HTTP {exc.code}. Use an existing local CSV with "
            "--events-file or place the Kaggle archive beneath data/raw/."
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach the remote archive: {exc.reason}") from exc

    if not content.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        preview = content[:200].decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            "The remote response is not a ZIP archive. Kaggle may require authentication. "
            "Download the dataset manually, place it beneath data/raw/, or pass "
            f"--events-file /path/to/events.csv. Response preview: {preview[:120]}"
        )

    destination.write_bytes(content)
    return destination


def extract_events_archive(archive_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    if not zipfile.is_zipfile(archive_path):
        raise RuntimeError(
            f"File is not a valid ZIP archive: {archive_path}. Replace it with the archive "
            "downloaded from Kaggle or pass --events-file /path/to/events.csv."
        )

    with zipfile.ZipFile(archive_path) as archive:
        event_members = [name for name in archive.namelist() if name.lower().endswith("events.csv")]
        if not event_members:
            raise ValueError("Archive does not contain an events.csv file")

        archive.extractall(destination_dir)
        extracted_events = destination_dir / event_members[0]
        if not extracted_events.exists():
            raise RuntimeError(f"events.csv was not extracted correctly: {extracted_events}")
        return extracted_events


def find_local_events(raw_dir: Path) -> Path | None:
    candidates = [
        raw_dir / "events.csv",
        raw_dir / "retailrocket" / "events.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    for candidate in raw_dir.rglob("events.csv"):
        if candidate.is_file():
            return candidate
    return None


def find_local_archive(raw_dir: Path) -> Path | None:
    preferred = raw_dir / "retailrocket" / "ecommerce-events.zip"
    if preferred.exists():
        return preferred

    archives = sorted(raw_dir.rglob("*.zip"), key=lambda path: str(path))
    for archive in archives:
        if zipfile.is_zipfile(archive):
            return archive
    return None


def extract_source(events_file: Path | None = None, raw_dir: Path = RAW_DIR) -> Path:
    if events_file:
        source = Path(events_file)
        if not source.exists():
            raise FileNotFoundError(f"Source CSV not found: {source}")
        return source

    local_archive = find_local_archive(raw_dir)
    if local_archive:
        return extract_events_archive(local_archive, raw_dir / "retailrocket")

    local_source = find_local_events(raw_dir)
    if local_source:
        return local_source

    archive_path = raw_dir / "retailrocket" / "ecommerce-events.zip"
    download_archive(archive_path)
    return extract_events_archive(archive_path, raw_dir / "retailrocket")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Retailrocket source events")
    parser.add_argument("--events-file", type=Path)
    parser.add_argument("--archive", type=Path, help="Path to a local Kaggle ZIP archive")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    args = parser.parse_args()

    if args.archive:
        source = extract_events_archive(args.archive, args.raw_dir / "retailrocket")
    else:
        source = extract_source(args.events_file, args.raw_dir)
    print(f"Extracted source events: {source}")


if __name__ == "__main__":
    main()
