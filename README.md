# Customer Funnel Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Project Overview

This project analyzes customer funnel performance to understand customer behavior, identify conversion bottlenecks, and generate actionable business insights.

The analysis tracks customers through the funnel, measures stage-by-stage conversion and drop-off rates, and identifies opportunities to improve customer acquisition and retention.

## Business Objective

The default analysis measures conversion across:

```text
product view → cart addition → purchase
```

It helps answer:

- Where do users abandon the journey?
- How much is the approximate purchase opportunity?
- Which available behavioral segments offer the strongest recovery opportunity?
- Which experiments should teams prioritize first?

The Retailrocket source does not provide campaign landing pages, checkout events, campaign attribution, acquisition channels, devices, or transaction values. Unknown attribution fields are retained in the normalized schema as `unknown`, and transaction values are normalized for analysis only.

## Project Structure

```text
.
├── bi/                           # BI and dashboard definitions
├── config/                       # Pipeline configuration
├── data/
│   ├── raw/                      # Original datasets, excluded from Git
│   ├── processed/                # Normalized and cleaned datasets
│   └── README.md
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_quality_analysis.ipynb
│   ├── 03_customer_funnel_analysis.ipynb
│   ├── 04_conversion_analysis.ipynb
│   └── 05_business_insights.ipynb
├── pipeline/
│   ├── ingestion/
│   │   ├── extract.py
│   │   └── validate_source.py
│   ├── transformation/
│   │   ├── clean_data.py
│   │   └── transform_data.py
│   └── orchestration/
│       └── run_pipeline.py
├── reports/                      # Generated analysis reports
├── scripts/
│   └── analyze_funnel.py         # Existing funnel reporting entry point
├── sql/
│   ├── staging/
│   ├── transformations/
│   └── analysis/
├── tests/
├── LICENSE
├── requirements.txt
└── README.md
```

## Data Management

The project separates raw and processed datasets to maintain data integrity and reproducibility.

| Directory | Description | Git Tracking |
|---|---|---|
| `data/raw/` | Original, unmodified datasets | Excluded |
| `data/processed/` | Cleaned and transformed datasets | Excluded by default |
| `data/README.md` | Data sources, descriptions, and setup instructions | Tracked |

### Data Guidelines

- Keep original datasets in `data/raw/`.
- Never modify raw datasets directly.
- Store cleaned and transformed datasets in `data/processed/`.
- Document dataset sources, formats, and relevant data dictionaries.
- Do not commit confidential, sensitive, or personally identifiable information.
- Use scripts in `scripts/` or a future pipeline to reproduce processed datasets.

## Obtaining the Data

Raw datasets are not included in this repository. Obtain the required dataset from its authorized source and place it in `data/raw/`.

This project uses the public **Retailrocket e-commerce event dataset**. The ingestion pipeline downloads the event archive or accepts an existing `events.csv` file.

| Retailrocket event | Funnel stage |
|---|---|
| `view` | `product_view` |
| `addtocart` | `cart` |
| `transaction` | `purchase` |

Download and ingest the public dataset:

```bash
python scripts/ingest_retailrocket.py
```

To ingest an existing events file:

```bash
python scripts/ingest_retailrocket.py --events-file /path/to/events.csv
```

The normalized output is written to `data/processed/ecommerce_funnel_events_normalized.csv`. The validated final output is written to `data/processed/ecommerce_funnel_events_clean.csv`. Raw downloaded files remain beneath `data/raw/retailrocket/`.

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- SQL
- Git and GitHub
- Jupyter Notebook

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/essiebx/e-commerce-conversion-customer-funnel-analysis.git
cd e-commerce-conversion-customer-funnel-analysis
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Linux/macOS:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

Run the modular pipeline using the extracted Retailrocket events file:

```bash
python pipeline/orchestration/run_pipeline.py --events-file data/raw/retailrocket/events.csv
```

Generate dashboard reports from the cleaned processed dataset:

```bash
python scripts/analyze_funnel.py
```

Launch the dashboard:

```bash
python -m streamlit run app.py
```

## Analysis Workflow

1. Collect or download the source events.
2. Validate the required fields and funnel stages.
3. Normalize supported events.
4. Deduplicate unique visitors at each stage.
5. Calculate stage-to-stage and overall conversion.
6. Identify absolute and percentage drop-offs.
7. Report available segment performance and recovery opportunity.
8. Generate business insights and experiments.

## Key Metrics

- Stage conversion rate
- Step-by-step drop-off rate
- Overall product-view-to-purchase conversion
- Estimated recoverable purchase opportunity
- Completion rate by available segment

Reports are written to `reports/`:

- `funnel_summary.csv`
- `segment_summary.csv`
- `revenue_opportunity.csv`
- `funnel_conversion.png`

## Data Dictionary

| Column | Description |
|---|---|
| `event_id` | Unique normalized event identifier |
| `user_id` | Anonymized visitor identifier |
| `session_id` | Session identifier; currently falls back to the visitor identifier |
| `event_timestamp` | ISO-8601 UTC event timestamp |
| `campaign` | Attribution campaign; `unknown` for Retailrocket |
| `channel` | Acquisition channel; `unknown` for Retailrocket |
| `device` | User device category; `unknown` for Retailrocket |
| `stage` | Normalized funnel stage |
| `cart_value` | `1.00` on purchase rows; `0.00` otherwise |
| `revenue` | `1.00` on purchase rows; `0.00` otherwise; a purchase indicator, not actual currency |

## SQL Workflow

Create the compatible analytics table and run the SQL-native funnel query:

```bash
psql -d ecommerce -f sql/schema.sql
psql -d ecommerce -f sql/funnel_analysis.sql
```

The query uses conditional aggregation and deduplicates visitors by stage.

## Testing

```bash
python -m unittest discover -s tests -v
```

## Recommended Experiments

- Improve product-page relevance and reduce friction before add-to-cart.
- Test cart reminders or follow-up experiences for visitors who reach the cart stage.
- Analyze the largest observed transition drop-off.
- Use holdout groups and compare incremental behavior rather than conversion rate alone.

## Limitations

- Retailrocket is public anonymized event data, not company-owned warehouse data.
- It does not provide campaign landing pages, checkout events, campaign attribution, channel, device, or currency value fields.
- Purchases are normalized to `1.00` because transaction totals are unavailable.
- Revenue recovery estimates are directional and do not include probability uncertainty or marketing costs.
- Before production use, replace the public dataset with warehouse data and configure attribution windows.

## Contributing

Contributions, suggestions, and improvements are welcome. Please open an issue or submit a pull request that follows the repository's conventions.

## License

MIT License. See [LICENSE](LICENSE).

## Live Dashboard

Launch the Streamlit dashboard locally:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, normally `http://localhost:8501`.

The dashboard reads generated files from `reports/`, so run the pipeline and analysis first:

```bash
python pipeline/orchestration/run_pipeline.py --events-file data/raw/retailrocket/events.csv
python scripts/analyze_funnel.py
streamlit run app.py
```

For Streamlit Community Cloud, deploy `app.py` from the GitHub repository and set the main file path to `app.py`. Processed data is ignored by Git, so generate reports during deployment or add a small hosted dataset workflow before publishing.

## Free Production Deployment

### 1. Publish lightweight reports

Commit the generated files beneath `reports/`; do not commit `data/raw/`, `data/processed/`, or the 286 MB source-derived CSV. The dashboard requires:

- `reports/funnel_summary.csv`
- `reports/segment_summary.csv`
- `reports/revenue_opportunity.csv`
- `reports/manifest.json`

Raw and processed event data remain excluded by `.gitignore`.

### 2. Deploy Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud and select the repository.
3. Set the main file to `app.py`.
4. Deploy.

Streamlit Community Cloud is sufficient for this static or periodically refreshed report dashboard.

### 3. Refresh reports

Run reports locally after updating source data:

```bash
python pipeline/orchestration/run_pipeline.py --events-file data/raw/retailrocket/events.csv
python scripts/analyze_funnel.py
```

Commit the updated files beneath `reports/` and redeploy or let Streamlit redeploy automatically.

The repository includes GitHub Actions workflows that:

- Run unit tests on push and pull requests.
- Provide a manual or scheduled report-refresh job.

Kaggle requires authentication for the source archive, so a public GitHub Action cannot download it without source credentials or a public mirror. Keep credentials out of GitHub and do not commit the raw dataset.

### 4. Production validation checklist

- Confirm every required report exists.
- Confirm `manifest.json` contains a recent `generated_at_utc` value.
- Confirm the dashboard uses chronological funnel logic.
- Confirm no raw, processed, or personally identifiable customer data is committed.
- Run `python -m unittest discover -s tests -v` before publishing.
