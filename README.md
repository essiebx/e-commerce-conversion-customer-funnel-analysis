# Customer Funnel Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Project at a Glance

- **Problem solved:** Identifies where online shoppers drop between viewing products, adding items to a cart, and purchasing. The project calculates stage conversion, drop-off, segment completion, and estimated revenue recovery opportunities.
- **Data and tools:** Public, anonymized **Retailrocket e-commerce event data** (views, add-to-cart actions, and transactions) when `--source retailrocket` is used. Python 3.10+, Pandas, and Matplotlib power the pipeline and reports.
- **What was built/found:** A reproducible pipeline that normalizes events, deduplicates users by funnel stage, and produces `reports/funnel_summary.csv`, `reports/segment_summary.csv`, `reports/revenue_opportunity.csv`, and `reports/funnel_conversion.png`.
- **Run or view:** Run `python pipeline/orchestration/run_pipeline.py --source retailrocket` with an available Retailrocket archive/source, or run `python pipeline/orchestration/run_pipeline.py --source synthetic` for a deterministic local demo.
- **Synthetic data:** A seeded workflow generates plausible demo events with campaign, channel, device, cart, and revenue fields. The generator uses 5,000 users and seed 42 by default.
- **Unfinished work:** Raw data is not committed. Generated reports and screenshots are not currently included; a live BI dashboard and BI-tool dashboard definition are not yet available. The `bi/` directory is reserved for future dashboard assets.

## Project Overview

This project analyzes the customer journey for an e-commerce experience and measures movement through five stages:

`landing → product_view → cart → checkout → purchase`

The pipeline supports two reproducible entry paths: ingesting public Retailrocket events or generating seeded synthetic events. Retailrocket `view`, `addtocart`, and `transaction` events are mapped to `product_view`, `cart`, and `purchase`; campaign, channel, and device fields are currently recorded as `unknown`. Synthetic data provides the richer segment fields used for demonstration and testing.

## Repository Structure

```text
config/                 Default source, stage, and synthetic-data settings
data/                   Raw and processed data locations; generated datasets are excluded
generator/              Seeded synthetic event generator
notebooks/              Exploration, quality, funnel, conversion, and business-insight notebooks
pipeline/               Source extraction, validation, cleaning, transformation, and orchestration
reports/                Generated CSV summaries and the funnel chart
scripts/                Standalone ingestion, generation, and analysis utilities
sql/                    Table schema and SQL funnel/segment queries
bi/                     Reserved for BI extracts and dashboard definitions
tests/                  Funnel logic and pipeline module tests
```

### Pipeline Flow

1. **Extract:** `pipeline/orchestration/run_pipeline.py --source retailrocket` downloads the Retailrocket archive or accepts an existing `events.csv` file with `--events-file`.
2. **Validate:** `pipeline/ingestion/validate_source.py` checks required Retailrocket columns and supported event types.
3. **Transform:** `pipeline/transformation/transform_data.py` normalizes events into the common funnel schema.
4. **Clean:** `pipeline/transformation/clean_data.py` removes exact duplicates, invalid timestamps, invalid stages, and duplicate event IDs.
5. **Generate:** `scripts/analyze_funnel.py` calculates funnel and segment summaries and writes reports.

Retailrocket extraction and transformation are also available through the standalone `scripts/ingest_retailrocket.py` utility.

## Data and Funnel Schema

Normalized event data contains:

| Column | Description |
|---|---|
| `event_id` | Unique event identifier |
| `user_id` | Visitor or synthetic user identifier |
| `session_id` | Session identifier |
| `event_timestamp` | UTC event timestamp |
| `campaign` | Campaign name, or `unknown` for Retailrocket |
| `channel` | Acquisition channel, or `unknown` for Retailrocket |
| `device` | Device category, or `unknown` for Retailrocket |
| `stage` | `landing`, `product_view`, `cart`, `checkout`, or `purchase` |
| `cart_value` | Cart value associated with the event |
| `revenue` | Revenue associated with a purchase |

The SQL table definition is in [`sql/schema.sql`](sql/schema.sql), while [`sql/funnel_analysis.sql`](sql/funnel_analysis.sql) contains stage counts, conversion, drop-off, and segment-performance queries.

## Setup

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Run the Project

### Seeded synthetic demo

```bash
python pipeline/orchestration/run_pipeline.py --source synthetic
python scripts/analyze_funnel.py
```

This writes the normalized and cleaned datasets under `data/` and creates the analysis outputs under `reports/`.

A standalone synthetic generator is also available:

```bash
python scripts/generate_sample_data.py
python scripts/analyze_funnel.py
```

### Retailrocket data

The pipeline can download the configured public archive automatically:

```bash
python pipeline/orchestration/run_pipeline.py --source retailrocket
python scripts/analyze_funnel.py
```

To use an existing `events.csv` file:

```bash
python pipeline/orchestration/run_pipeline.py --source retailrocket --events-file /path/to/events.csv
python scripts/analyze_funnel.py
```

Alternatively, run the standalone ingestion utility:

```bash
python scripts/ingest_retailrocket.py --events-file /path/to/events.csv
python scripts/analyze_funnel.py
```

Raw and processed data are intentionally excluded from Git; obtain Retailrocket data from an authorized source and keep it out of version control.

## Outputs

After analysis, `reports/` contains:

- `funnel_summary.csv` — unique users, step conversion, overall conversion, drop-off users, and drop-off rate for each stage
- `segment_summary.csv` — unique users by campaign, channel, device, and stage
- `revenue_opportunity.csv` — estimated abandoned users and revenue opportunity between adjacent stages
- `funnel_conversion.png` — line chart of unique users across funnel stages

Running the pipeline produces normalized and cleaned datasets in:

- `data/ecommerce_funnel_events.csv`
- `data/processed/ecommerce_funnel_events_clean.csv`
- `data/processed/data_quality_summary.csv`

## Tests

Run the unit tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests cover funnel conversion and revenue-opportunity calculations, Retailrocket source validation, and data-cleaning behavior.

## Current Limitations

- Retailrocket conversion is not a complete landing or checkout journey: the source events map directly to `product_view`, `cart`, and `purchase`.
- Retailrocket campaign, channel, and device attribution is unavailable and is stored as `unknown`.
- Purchase value in the Retailrocket adapter is represented as a unit value of `1.00` rather than a true item or order amount.
- Synthetic values are for pipeline demonstration and should not be interpreted as observed business performance.
- Notebooks and SQL scripts are available, but the repository does not yet commit generated reports or BI dashboard definitions.

## License

This project is licensed under the [MIT License](LICENSE).
