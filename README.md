# E-Commerce Conversion & Customer Funnel Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.24+-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI Tests](https://github.com/essiebx/e-commerce-conversion-customer-funnel-analysis/actions/workflows/tests.yml/badge.svg)](.github/workflows/tests.yml)

An end-to-end e-commerce customer conversion and funnel analysis framework built on **2.75M+ real-world Retailrocket interaction events**. This project provides a modular ETL data pipeline, chronological stage-to-stage conversion analysis, SQL analytical queries, Jupyter research notebooks, and an interactive decision-support **Streamlit dashboard**.

---

## Table of Contents

- [Project at a Glance](#project-at-a-glance)
- [Key Findings & Funnel Metrics](#key-findings--funnel-metrics)
- [Funnel Methodology](#funnel-methodology)
- [Interactive Streamlit Dashboard](#interactive-streamlit-dashboard)
- [Repository Structure](#repository-structure)
- [Data Pipeline & Architecture](#data-pipeline--architecture)
- [Data Schema & SQL Analytics](#data-schema--sql-analytics)
- [Exploratory Notebooks](#exploratory-notebooks)
- [Installation & Setup](#installation-setup)
- [How to Run the Project](#how-to-run-the-project)
- [Testing](#testing)
- [Automation & CI/CD](#automation--cicd)
- [Data Limitations & Caveats](#data-limitations--caveats)
- [Production Deployment](#production-deployment)
- [License](#license)

---

## Project at a Glance

- **Problem Statement:** Identifies exact drop-off points in the e-commerce customer journey, quantifies visitor abandonment between product discovery and final purchase, and isolates conversion bottlenecks to guide UX/merchandising interventions.
- **Dataset:** Anonymized, real-world **Retailrocket e-commerce event log** containing 2,756,101 recorded interactions (`view`, `addtocart`, and `transaction`) across 1,407,580 unique visitors.
- **Pipeline Architecture:** Modular Python pipeline with automated extraction/download, source validation, event normalization into a standardized funnel schema, timestamp validation, and data cleaning with quality reporting.
- **Chronological Funnel Engine:** Calculates conversion rates requiring strict chronological event progression ($T_{\text{view}} \le T_{\text{cart}} \le T_{\text{purchase}}$), preventing false stage skips.
- **Interactive Dashboard:** Full-featured **Streamlit web application** (`app.py`) featuring 5 analytical tabs, KPI metrics, dynamic Plotly visualizations, segment filtering, and data quality inspection.
- **Production-Ready & Lightweight:** Report summaries (`reports/`) are pre-generated and tracked, allowing instant local launch and zero-data-leak cloud deployment without uploading the 286 MB raw dataset.

---

## Key Findings & Funnel Metrics

From the analysis of 2,756,101 cleaned events from the Retailrocket dataset, the chronological funnel reveals:

| Funnel Stage | Unique Users | Step Conversion Rate | Overall Conversion Rate | Drop-Off Users | Stage Drop-Off Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`product_view`** | **1,404,179** | 100.00% | 100.00% | — | — |
| **`cart`** | **32,272** | 2.30% | 2.30% | 1,371,907 | **97.70%** |
| **`purchase`** | **9,956** | **30.85%** | **0.71%** | 22,316 | 69.15% |

### Core Insights:

1. **The Primary Bottleneck is Discovery-to-Cart (97.70% Drop-Off):**
   - Out of 1.4M visitors viewing products, only 2.30% add an item to their shopping cart.
   - **Action Item:** Focus optimization on product detail page (PDP) usability, social proof/reviews, transparent pricing/shipping expectations, search relevancy, and prominent "Add to Cart" CTAs.
2. **High Cart-to-Purchase Intent (30.85% Step Conversion):**
   - Once a shopper commits an item to the cart, nearly 1 in 3 (30.85%) converts to a completed purchase.
   - **Action Item:** Protect this conversion channel with streamlined checkout flows, guest checkout options, abandoned cart email notifications, and automated recovery reminders.
3. **End-to-End Conversion:**
   - Overall conversion rate from initial product view to completed purchase stands at **0.71%**, typical of large-scale open browse e-commerce catalogs.

---

## Funnel Methodology

### Stage Definitions

The project supports a generalized 5-stage e-commerce funnel schema:

$$\text{landing} \longrightarrow \text{product\_view} \longrightarrow \text{cart} \longrightarrow \text{checkout} \longrightarrow \text{purchase}$$

### Retailrocket Mapping

Because the Retailrocket dataset captures product-level browsing and purchasing events without web server access logs or checkout form steps, events are mapped as follows:

| Retailrocket Event | Funnel Stage | Description |
| :--- | :--- | :--- |
| `view` | `product_view` | User viewed a product detail page |
| `addtocart` | `cart` | User added a product to their shopping cart |
| `transaction` | `purchase` | User completed an order transaction |

*Note: For Retailrocket data, `landing` and `checkout` stages are absent, and marketing attributes (`campaign`, `channel`, `device`) default to `unknown`.*

### Chronological Funnel Progression

Unlike naive funnel models that count distinct users per stage independently, this framework computes chronological conversion:
- A user is only credited with reaching `cart` if they have a recorded `product_view` timestamp at or before the `cart` timestamp.
- A user is only credited with reaching `purchase` if they have recorded prior stages chronologically ($T_{\text{view}} \le T_{\text{cart}} \le T_{\text{purchase}}$).
- This mirrors genuine user sessions and prevents out-of-order anomalies.

---

## Interactive Streamlit Dashboard

The Streamlit web application (`app.py`) provides an intuitive decision-support tool for business stakeholders and analysts.

```bash
streamlit run app.py
```

### Dashboard Tabs & Features

1. **Overview:**
   - Top-level KPI cards: First-stage users (1,404,179), Purchasers (9,956), Overall conversion rate (0.71%), and Largest drop-off stage identification.
   - Business objective summary and analytical scope indicators.
2. **Funnel Performance:**
   - Interactive Plotly bar chart depicting unique users at each stage.
   - Comprehensive stage metrics table with step conversion, overall conversion, and drop-off user counts.
   - Dynamic drop-off insight callout highlighting the highest-loss stage.
3. **Segments:**
   - Multi-dimensional breakdown by campaign, channel, device, and stage.
   - Sidebar multi-select filters to drill down into specific segments when attribution data is available.
4. **Opportunities:**
   - Abandoned user counts per transition stage.
   - Opportunity indicator table and interactive transition drop-off chart.
5. **Methodology:**
   - Visual data pipeline flow and event stage mapping documentation.
   - **Report Freshness:** Embedded JSON inspector for `reports/manifest.json`.
   - **Data Quality Summary:** Live table rendering of `reports/data_quality_summary.csv` showing row counts, deduplications, and cleaning statistics.

---

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       ├── refresh-reports.yml       # Scheduled & manual GitHub Actions report refresh
│       └── tests.yml                 # Automated CI unit tests
├── .streamlit/
│   └── config.toml                   # Streamlit UI theme and server configuration
├── bi/
│   └── README.md                     # BI dashboard asset guidelines
├── config/
│   ├── pipeline.yaml                 # Pipeline data sources, paths, and valid stages
│   └── README.md                     # Configuration documentation
├── data/
│   ├── raw/                          # Raw event data (excluded from Git)
│   ├── processed/                    # Normalized and cleaned datasets (excluded from Git)
│   └── README.md                     # Data directory structure & security guidelines
├── notebooks/
│   ├── 01_data_exploration.ipynb     # Initial exploratory analysis on Retailrocket data
│   ├── 02_data_quality_analysis.ipynb# Missingness, duplicates, and timestamp integrity
│   ├── 03_customer_funnel_analysis.ipynb # Chronological funnel metrics & calculations
│   ├── 04_conversion_analysis.ipynb  # Stage-to-stage transition & drop-off analysis
│   ├── 05_business_insights.ipynb    # Executive insights, recommendations & visualizations
│   └── funnel_analysis.ipynb         # Standalone funnel prototype notebook
├── pipeline/
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── extract.py                # Source archive download and extraction
│   │   └── validate_source.py        # Schema and column verification
│   ├── transformation/
│   │   ├── __init__.py
│   │   ├── clean_data.py             # Deduplication, timestamp parsing & quality audit
│   │   └── transform_data.py         # Normalization into common funnel schema
│   └── orchestration/
│       ├── __init__.py
│       └── run_pipeline.py           # End-to-end pipeline execution entry point
├── reports/
│   ├── data_quality_summary.csv      # Metrics on raw vs. clean rows and anomalies
│   ├── funnel_conversion.png         # Exported conversion line chart
│   ├── funnel_summary.csv            # Funnel stages, conversion, and drop-off rates
│   ├── manifest.json                 # Metadata: source rows, users, and generation time
│   ├── README.md                     # Reports directory documentation
│   ├── revenue_opportunity.csv       # Transition abandonment and opportunity indicators
│   └── segment_summary.csv           # Segment-level stage aggregations
├── scripts/
│   ├── analyze_funnel.py             # Generates all reports from cleaned data
│   ├── generate_sample_data.py       # Helper utility for Retailrocket events ingestion
│   └── ingest_retailrocket.py        # Standalone archive download & ingestion script
├── sql/
│   ├── analysis/
│   │   ├── funnel_conversion.sql     # Stage conversion and drop-off rate SQL
│   │   └── segment_conversion.sql    # Conversion rate by segment dimensions
│   ├── staging/
│   │   └── normalize_funnel_events.sql# SQL staging normalization
│   ├── transformations/
│   │   └── funnel_stage_counts.sql   # SQL LAG window functions for user drop-off
│   ├── funnel_analysis.sql           # Unified SQL script for funnel & drop-off analysis
│   └── schema.sql                    # Table DDL and indexing schema
├── tests/
│   ├── test_funnel_logic.py          # Unit tests for funnel & chronological ordering
│   └── test_pipeline_modules.py      # Unit tests for ingestion validation & cleaning
├── .gitignore                        # Git exclusion rules (raw/processed data, caches)
├── app.py                            # Streamlit analytics dashboard application
├── LICENSE                           # MIT License
├── README.md                         # Project documentation
└── requirements.txt                  # Python dependencies
```

---

## Data Pipeline & Architecture

The pipeline processes event logs through five modular stages:

```
┌─────────────────┐      ┌─────────────────────────┐      ┌──────────────────────────┐
│   Raw Source    │ ───> │ Ingestion & Validation  │ ───> │ Normalization & Schema   │
│  (events.csv /  │      │  (extract.py,           │      │  Mapping                 │
│   archive.zip)  │      │   validate_source.py)   │      │  (transform_data.py)     │
└─────────────────┘      └─────────────────────────┘      └──────────────────────────┘
                                                                        │
                                                                        ▼
┌─────────────────┐      ┌─────────────────────────┐      ┌──────────────────────────┐
│ Streamlit App & │ <─── │ Analysis & Reports      │ <─── │ Cleaning & Quality Audit │
│ SQL Analytics   │      │ (analyze_funnel.py)     │      │ (clean_data.py)          │
└─────────────────┘      └─────────────────────────┘      └──────────────────────────┘
```

1. **Extraction (`pipeline/ingestion/extract.py`):**
   - Automatically searches for existing `events.csv` or archive `.zip` files in `data/raw/`.
   - Downloads the public Retailrocket dataset archive if no local source is found.
2. **Source Validation (`pipeline/ingestion/validate_source.py`):**
   - Confirms that required source columns (`timestamp`, `visitorid`, `event`, `itemid`) exist and verifies that supported events (`view`, `addtocart`, `transaction`) are present.
3. **Transformation (`pipeline/transformation/transform_data.py`):**
   - Maps raw event names to standardized funnel stages.
   - Formats UNIX timestamps in milliseconds to ISO 8601 UTC strings.
   - Assigns formatted IDs (`EVT-0000001`, `VIS-00000001`, `SES-00000001`).
   - Normalizes indicators (`cart_value` and `revenue`).
4. **Cleaning & Quality Audit (`pipeline/transformation/clean_data.py`):**
   - Eliminates exact duplicate records and duplicate `event_id` occurrences.
   - Parses and verifies timestamp integrity, discarding non-date rows.
   - Restricts events to approved funnel stages (`landing`, `product_view`, `cart`, `checkout`, `purchase`).
   - Outputs both the validated dataset (`ecommerce_funnel_events_clean.csv`) and a summary audit (`data_quality_summary.csv`).
5. **Reporting & Analysis (`scripts/analyze_funnel.py`):**
   - Calculates chronological stage counts, conversion rates, and user drop-offs.
   - Aggregates segment breakdowns and estimates transition abandonment.
   - Generates summary CSVs, Plotly/Matplotlib charts, and updates `reports/manifest.json`.

---

## Data Schema & SQL Analytics

### Normalized Funnel Schema

The normalized event data model conforms to the following schema:

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `event_id` | `VARCHAR(50)` | `PRIMARY KEY` | Unique event identifier (e.g., `EVT-0000001`) |
| `user_id` | `VARCHAR(50)` | `NOT NULL` | Standardized visitor identifier (e.g., `VIS-00000001`) |
| `session_id` | `VARCHAR(50)` | `NOT NULL` | Session identifier |
| `event_timestamp` | `TIMESTAMP` | `NOT NULL` | UTC event timestamp in ISO 8601 format |
| `campaign` | `VARCHAR(100)` | `NOT NULL` | Marketing campaign name (`unknown` if unavailable) |
| `channel` | `VARCHAR(100)` | `NOT NULL` | Traffic channel (`unknown` if unavailable) |
| `device` | `VARCHAR(50)` | `NOT NULL` | Device category (`unknown` if unavailable) |
| `stage` | `VARCHAR(50)` | `NOT NULL` | Funnel stage: `landing`, `product_view`, `cart`, `checkout`, `purchase` |
| `cart_value` | `NUMERIC(12, 2)` | `DEFAULT 0` | Associated cart value indicator |
| `revenue` | `NUMERIC(12, 2)` | `DEFAULT 0` | Associated purchase revenue indicator |

### SQL Analytics Library

The `sql/` directory contains standard SQL queries compatible with PostgreSQL, DuckDB, and other modern SQL engines:

- [`sql/schema.sql`](sql/schema.sql): DDL for table creation and composite index on `(user_id, stage)`.
- [`sql/funnel_analysis.sql`](sql/funnel_analysis.sql): Full query calculating users per stage, step conversion percentage, and `LAG` window drop-off metrics.
- [`sql/staging/normalize_funnel_events.sql`](sql/staging/normalize_funnel_events.sql): Staging query casting types and filtering valid stages.
- [`sql/transformations/funnel_stage_counts.sql`](sql/transformations/funnel_stage_counts.sql): Aggregation CTE using window functions for stage-to-stage delta tracking.
- [`sql/analysis/funnel_conversion.sql`](sql/analysis/funnel_conversion.sql): Granular conversion percentages across each transition.
- [`sql/analysis/segment_conversion.sql`](sql/analysis/segment_conversion.sql): Cross-dimensional conversion metrics grouped by campaign, channel, and device.

---

## Exploratory Notebooks

Detailed analytical workflows and visualizations are provided in `notebooks/`:

1. **`01_data_exploration.ipynb`:** Initial exploration of raw Retailrocket events, event distribution (`view`: 96.6%, `addtocart`: 2.5%, `transaction`: 0.8%), and user activity distributions.
2. **`02_data_quality_analysis.ipynb`:** Verification of timestamp boundaries, ID formatting, missing value rates, and data cleaning validation.
3. **`03_customer_funnel_analysis.ipynb`:** Implementation and verification of chronological funnel counting versus independent unique counts.
4. **`04_conversion_analysis.ipynb`:** In-depth transition modeling, drop-off rate calculations, and velocity analysis.
5. **`05_business_insights.ipynb`:** Scenario analysis, recovery potential estimations, executive charts, and strategic merchandising recommendations.

---

## Installation & Setup

### Prerequisites

- **Python:** Version 3.10 or newer (tested on Python 3.10, 3.11, and 3.12).
- **Git**

### 1. Clone the repository

```bash
git clone https://github.com/essiebx/e-commerce-conversion-customer-funnel-analysis.git
cd e-commerce-conversion-customer-funnel-analysis
```

### 2. Create and activate a virtual environment

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## How to Run the Project

### Option A: Launch the Streamlit Dashboard (Instant)

Because the project includes pre-computed report datasets in `reports/`, you can launch the interactive dashboard immediately:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

### Option B: Run the Complete Data Pipeline

To process a new or updated Retailrocket dataset from scratch:

1. **Run the ingestion and cleaning pipeline:**
   ```bash
   # If you have a local events.csv file:
   python pipeline/orchestration/run_pipeline.py --events-file data/raw/retailrocket/events.csv

   # Or let the pipeline automatically find or download the source archive:
   python pipeline/orchestration/run_pipeline.py
   ```

2. **Generate reports and summaries:**
   ```bash
   python scripts/analyze_funnel.py
   ```

   This generates or updates:
   - `reports/funnel_summary.csv`
   - `reports/segment_summary.csv`
   - `reports/revenue_opportunity.csv`
   - `reports/funnel_conversion.png`
   - `reports/manifest.json`

3. **Launch the dashboard to inspect the fresh results:**
   ```bash
   streamlit run app.py
   ```

### Standalone Utilities

- **Standalone Retailrocket Ingestion:**
  ```bash
  python scripts/ingest_retailrocket.py --events-file /path/to/events.csv
  ```

---

## Testing

A comprehensive unit test suite is included to guarantee funnel calculation accuracy, chronological integrity, and pipeline robustness.

Run the tests using Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

### Test Coverage

- [`tests/test_funnel_logic.py`](tests/test_funnel_logic.py):
  - Validates overall and step conversion calculations against known control data.
  - Verifies that all expected funnel stage transitions are present in the revenue opportunity report.
  - Enforces chronological sequence logic: confirms that a purchase event recorded before a cart event is excluded from valid funnel progression.
- [`tests/test_pipeline_modules.py`](tests/test_pipeline_modules.py):
  - Tests Retailrocket source validation (checking required columns and supported event counts).
  - Tests data cleaning logic (asserting that exact duplicate rows and invalid timestamps are discarded while valid rows are retained).

---

## Automation & CI/CD

Continuous integration workflows are configured in `.github/workflows/`:

- **[`tests.yml`](.github/workflows/tests.yml):** Automatically triggers on every push and pull request. Sets up Python 3.12, installs dependencies from `requirements.txt`, and executes the complete test suite.
- **[`refresh-reports.yml`](.github/workflows/refresh-reports.yml):** Scheduled daily cron job (and manual `workflow_dispatch`) that runs the pipeline on updated source data, regenerates reports, runs tests, and automatically commits refreshed report artifacts.

---

## Data Limitations & Caveats

When interpreting analysis results, consider the structural characteristics of the Retailrocket dataset:

- **Attribution Absence:** Retailrocket data does not capture acquisition channels (organic, paid search, social), campaign names, or client devices (mobile, desktop). In all reports, these attributes are recorded as `unknown`.
- **Unit Value Indicators:** Raw Retailrocket transactions do not record order monetary amounts or product prices. In normalized data, `cart_value` and `revenue` are unit indicators (`1.00`), serving as transaction count metrics rather than total currency figures.
- **Top-of-Funnel Visibility:** The raw event stream records interaction on product pages (`view`), additions to cart (`addtocart`), and checkout completions (`transaction`). It does not record top-level homepage or category landing visits, nor mid-checkout form fields.

---

## Production Deployment

### Streamlit Community Cloud (Recommended)

The dashboard is fully compatible with free hosting on **Streamlit Community Cloud**:

1. **Commit Generated Reports:** Ensure the lightweight files under `reports/` (`funnel_summary.csv`, `segment_summary.csv`, `revenue_opportunity.csv`, `data_quality_summary.csv`, `manifest.json`) are committed to your GitHub repository.
2. **Keep Large Data Excluded:** Verify that `data/raw/` and `data/processed/` remain ignored by `.gitignore`.
3. **Deploy via Streamlit:**
   - Connect your GitHub account to [share.streamlit.io](https://share.streamlit.io/).
   - Select your repository and branch (`master`).
   - Set the Main file path to `app.py`.
   - Click **Deploy**.

---

## License

This project is licensed under the [MIT License](LICENSE).
