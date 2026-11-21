import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generator.generate_data import generate_data
from pipeline.ingestion.extract import extract_source
from pipeline.ingestion.validate_source import validate_source_file
from pipeline.transformation.clean_data import clean_funnel_data
from pipeline.transformation.transform_data import transform_retailrocket


def run_retailrocket(events_file: Path | None = None, raw_dir: Path = ROOT / "data" / "raw") -> tuple:
    source = extract_source(events_file, raw_dir)
    source_summary = validate_source_file(source)
    normalized_path = ROOT / "data" / "ecommerce_funnel_events.csv"
    normalized = transform_retailrocket(source, normalized_path)
    clean, quality = clean_funnel_data(normalized_path)
    return normalized, clean, quality, source_summary


def run_synthetic(users: int = 5000, seed: int = 42) -> tuple:
    normalized_path = ROOT / "data" / "ecommerce_funnel_events.csv"
    generate_data(normalized_path, users=users, seed=seed)
    clean, quality = clean_funnel_data(normalized_path)
    return clean, quality


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the customer funnel pipeline")
    parser.add_argument("--source", choices=("retailrocket", "synthetic"), default="retailrocket")
    parser.add_argument("--events-file", type=Path)
    parser.add_argument("--users", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.source == "synthetic":
        _, quality = run_synthetic(args.users, args.seed)
        print(quality.to_string(index=False))
        print("Synthetic pipeline complete")
    else:
        _, _, quality, source_summary = run_retailrocket(args.events_file)
        print("Source summary:", source_summary)
        print(quality.to_string(index=False))
        print("Retailrocket pipeline complete")


if __name__ == "__main__":
    main()
