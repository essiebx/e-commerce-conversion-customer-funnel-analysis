import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.ingestion.extract import extract_source
from pipeline.ingestion.validate_source import validate_source_file
from pipeline.transformation.clean_data import clean_funnel_data
from pipeline.transformation.transform_data import transform_retailrocket


def run_retailrocket(events_file: Path | None = None, raw_dir: Path = ROOT / "data" / "raw") -> tuple:
    source = extract_source(events_file, raw_dir)
    source_summary = validate_source_file(source)
    normalized_path = ROOT / "data" / "processed" / "ecommerce_funnel_events_normalized.csv"
    normalized = transform_retailrocket(source, normalized_path)
    clean, quality = clean_funnel_data(normalized_path)
    return normalized, clean, quality, source_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Retailrocket customer funnel pipeline")
    parser.add_argument("--events-file", type=Path)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data" / "raw")
    args = parser.parse_args()

    _, _, quality, source_summary = run_retailrocket(args.events_file, args.raw_dir)
    print("Source summary:", source_summary)
    print(quality.to_string(index=False))
    print("Retailrocket pipeline complete")


if __name__ == "__main__":
    main()
