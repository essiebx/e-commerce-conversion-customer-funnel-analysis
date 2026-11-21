# Customer Funnel Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Project at a Glance

- **Problem solved:** Identifies where online shoppers drop between viewing products, adding items to a cart, and purchasing. The project calculates stage conversion, drop-off, segment completion, and an approximate recovery opportunity.
- **Data and tools:** Public, anonymized **Retailrocket e-commerce event data** (views, add-to-cart actions, and transactions) when `--source retailrocket` is used. Python 3.10+, Pandas, Matplotlib, SQL, Jupyter Notebook, CSV reports, and a modular ingestion/cleaning/transformation pipeline. Attribution fields unavailable in Retailrocket are recorded as `unknown`.
- **What was built/found:** A reproducible pipeline that normalizes events, deduplicates users by funnel stage, and produces `reports/funnel_summary.csv`, `reports/segment_summary.csv`, `reports/revenue_opportunity.csv`, and `reports/funnel_conversion.png`. It also includes SQL funnel queries and unit tests.
- **Run or view:** Run `python pipeline/orchestration/run_pipeline.py --source retailrocket` with an available Retailrocket archive/source, or run `python pipeline/orchestration/run_pipeline.py --source synthetic --users 5000 --seed 42` for a reproducible demo. Generate legacy reports with `python scripts/analyze_funnel.py`, and run tests with `python -m unittest discover -s tests -v`.
- **Synthetic data:** A synthetic, seeded workflow is available and generates plausible demo events with campaign, channel, device, cart, and revenue fields. Synthetic findings demonstrate the pipeline only and are **not real customer results**.
- **Unfinished work:** Raw data is not committed. Generated reports and screenshots are not currently included; a live BI dashboard and BI-tool dashboard definition are not yet available. The `bi/` directory is currently a placeholder, and production use requires real warehouse data plus checkout, attribution, channel, device, and transaction-value fields.

## Project Overview
