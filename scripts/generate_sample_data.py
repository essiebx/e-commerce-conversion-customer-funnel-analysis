import argparse
from pathlib import Path

from scripts.ingest_retailrocket import ingest_retailrocket_events


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize an existing RetailRocket events file")
    parser.add_argument("events_file", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/ecommerce_funnel_events_normalized.csv"),
    )
    args = parser.parse_args()

    frame = ingest_retailrocket_events(args.events_file, args.output)
    print(f"Ingested {len(frame):,} supported events")
    print(f"Normalized data written to {args.output}")


if __name__ == "__main__":
    main()
