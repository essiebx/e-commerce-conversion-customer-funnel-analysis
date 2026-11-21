# E-Commerce Conversion & Customer Funnel Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/) [![SQL](https://img.shields.io/badge/SQL-Analysis-336791.svg)](https://www.postgresql.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A reproducible project analyzing a public, non-synthetic e-commerce event dataset to identify funnel drop-offs and estimate commercial revenue opportunities.

## Business Objective

Measure conversion across:

`product view → cart addition → purchase`

The Retailrocket data does not provide campaign landing pages, checkout events, campaign attribution, acquisition channels, devices, or transaction values. These fields are therefore not fully available in the ingested funnel. The project retains the original schema for compatibility, but unknown attribution fields are marked as `unknown`.

The analysis helps answer:

- Where do users abandon the journey?
- How much is the approximate purchase opportunity?
- Which behavioral segments offer the strongest recovery opportunity?
- What experiments should teams prioritize first?

## Data Source

This project uses the public **Retailrocket e-commerce event dataset**.

The ingestion pipeline downloads the event archive and maps supported Retailrocket events as follows:

| Retailrocket event | Project funnel stage |
|---|---|
| `view` | `product_view` |
| `addtocart` | `cart` |
| `transaction` | `purchase` |

Download and ingest the data with:

```bash
python scripts/ingest_retailrocket.py
```

To ingest an existing `events.csv` file instead:

```bash
python scripts/ingest_retailrocket.py --events-file /path/to/events.csv
```

The default normalized output is:

```text
data/ecommerce_funnel_events.csv
```

Raw downloaded files are stored beneath `data/raw/retailrocket/`. Because the source is anonymized public event data rather than synthetic demonstration data, campaign, channel, and device values are recorded as `unknown`. Retailrocket transaction rows also do not provide monetary order values, so revenue and cart value are normalized to `1.00` as a purchase indicator—not as real currency values.

## Key Metrics

- Stage conversion rate
- Step-by-step drop-off rate
- Overall product-view-to-purchase conversion
- Estimated recoverable purchase opportunity
- Completion rate by available segment

> Revenue opportunity is a directional estimate, not a currency forecast. Retailrocket does not include order totals, campaign attribution, or landing/checkout events. The existing calculation uses a normalized revenue value of `1.00` per purchase.

## Project Structure

```text
.
├── data/
│   ├── raw/retailrocket/
│   ├── ecommerce_funnel_events.csv
│   └── README.md
├── notebooks/
│   └── funnel_analysis.ipynb
├── reports/
├── scripts/
│   ├── ingest_retailrocket.py
│   ├── generate_sample_data.py
│   └── analyze_funnel.py
├── sql/
│   ├── schema.sql
│   └── funnel_analysis.sql
├── tests/
│   └── test_funnel_logic.py
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/essiebx/e-commerce-conversion-customer-funnel-analysis.git
cd e-commerce-conversion-customer-funnel-analysis
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Ingest data and run the analysis

```bash
python scripts/ingest_retailrocket.py
python scripts/analyze_funnel.py
```

The synthetic generator remains available for reproducible demonstrations:

```bash
python scripts/generate_sample_data.py
```

Running it overwrites `data/ecommerce_funnel_events.csv`, so rerun the Retailrocket ingestion pipeline before non-synthetic analysis.

Reports are written to `reports/`:

- `funnel_summary.csv`
- `segment_summary.csv`
- `revenue_opportunity.csv`
- `funnel_conversion.png`

## Data Dictionary

| Column | Description |
|---|---|
| `event_id` | Unique normalized event identifier |
| `user_id` | Visitor identifier normalized as `VIS-...` |
| `session_id` | Current ingestion uses the visitor identifier as a session fallback |
| `event_timestamp` | ISO-8601 UTC event timestamp derived from Retailrocket milliseconds |
| `campaign` | Attribution campaign; `unknown` for Retailrocket |
| `channel` | Acquisition channel; `unknown` for Retailrocket |
| `device` | User device category; `unknown` for Retailrocket |
| `stage` | Normalized funnel stage: `product_view`, `cart`, or `purchase` |
| `cart_value` | `1.00` on purchase rows; `0.00` otherwise. This is not a real basket value. |
| `revenue` | `1.00` on purchase rows; `0.00` otherwise. This is a purchase indicator, not currency revenue. |

## Analysis Method

1. Download or load the Retailrocket event data.
2. Normalize supported events to the project funnel schema.
3. Validate required columns and normalized funnel stages.
4. Count unique visitors by funnel stage.
5. Calculate stage-to-stage and overall conversion.
6. Identify absolute and percentage drop-offs.
7. Report available segment performance and normalized recovery opportunity.

## SQL Workflow

Use `sql/schema.sql` to create a compatible analytics table, then run `sql/funnel_analysis.sql` for a SQL-native funnel query.

```bash
psql -d ecommerce -f sql/schema.sql
psql -d ecommerce -f sql/funnel_analysis.sql
```

The SQL uses conditional aggregation and deduplicates visitors by stage, making results reliable even if a session contains repeated events.

## Example Outputs

| Metric | Interpretation |
|---|---|
| Product-view users | Visitors reaching at least one product view |
| Step conversion | Percentage advancing to the next available stage |
| Drop-off count | Visitors lost between consecutive observed stages |
| Recovery opportunity | Potential purchase count or normalized value based on observed purchases |

## Use in a Spreadsheet

The CSV reports can be opened directly in Excel or Google Sheets:

1. Open `reports/funnel_summary.csv` for stage KPIs.
2. Filter `reports/segment_summary.csv` where attribution fields are available.
3. Sort `reports/revenue_opportunity.csv` from largest to smallest normalized opportunity.
4. Use a funnel or waterfall chart to visualize drop-offs.

## Testing

```bash
python -m unittest discover -s tests -v
```

## Recommended Experiments

- Analyze the largest observed transition drop-off, such as product view to cart.
- Improve product-page relevance and reduce friction before add-to-cart.
- Test cart reminders or follow-up experiences for visitors who reach the cart stage.
- Use holdout groups and compare incremental behavior rather than only conversion rate.

## Limitations

- The primary data is public anonymized Retailrocket event data, not company-owned warehouse data.
- Retailrocket does not provide campaign landing, campaign attribution, channel, device, checkout, or currency value fields.
- The ingestion pipeline normalizes purchases to a value of `1.00` because transaction totals are unavailable.
- Funnel analysis assumes one record per relevant stage per visitor journey and does not infer omitted sessions.
- Revenue recovery estimates do not account for probability uncertainty or marketing costs.
- Replace the public dataset with warehouse data and configure attribution windows before production use.

## License

MIT License. See [LICENSE](LICENSE).
