# E-Commerce Conversion & Customer Funnel Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/) [![SQL](https://img.shields.io/badge/SQL-Analysis-336791.svg)](https://www.postgresql.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A reproducible portfolio project analyzing a multi-stage e-commerce journey to identify funnel drop-offs, estimate lost revenue, and prioritize commercial experiments.

## Business Objective

Measure conversion across:

`campaign landing → product view → cart addition → checkout → purchase`

The analysis helps answer:

- Where do users abandon the journey?
- Which campaigns, channels, and devices perform best?
- How much revenue is lost at each funnel stage?
- Which segments offer the strongest recovery opportunity?
- What experiments should teams prioritize first?

## Key Metrics

- Stage conversion rate
- Step-by-step drop-off rate
- Overall landing-to-purchase conversion
- Revenue by campaign, channel, and device
- Estimated recoverable revenue
- Completion rate by segment

> Revenue opportunity is a directional estimate, not a guaranteed forecast. It assumes that users who abandon a stage could convert at the next segment's observed purchase or progression rate.

## Project Structure

```text
.
├── data/
│   └── ecommerce_funnel_events.csv
├── notebooks/
│   └── funnel_analysis.ipynb
├── reports/
├── scripts/
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

### 4. Generate data and run the analysis

```bash
python scripts/generate_sample_data.py
python scripts/analyze_funnel.py
```

Reports are written to `reports/`:

- `funnel_summary.csv`
- `segment_summary.csv`
- `revenue_opportunity.csv`
- `funnel_conversion.png`

## Data Dictionary

| Column | Description |
|---|---|
| `event_id` | Unique event identifier |
| `user_id` | Unique customer identifier |
| `session_id` | User session identifier |
| `event_timestamp` | Event timestamp in ISO-8601 format |
| `campaign` | Attribution campaign |
| `channel` | Acquisition channel |
| `device` | User device category |
| `stage` | Funnel stage |
| `cart_value` | Basket value at the cart or checkout stage |
| `revenue` | Recognized revenue at purchase; otherwise 0 |

The included synthetic dataset represents sample data for demonstration and contains no real customer information.

## Analysis Method

1. Generate or load event-level journey data.
2. Validate required columns and event stages.
3. Count unique users by funnel stage.
4. Calculate stage-to-stage and overall conversion.
5. Identify absolute and percentage drop-offs.
6. Compare campaign, channel, and device segments.
7. Estimate revenue opportunity by comparing purchase revenue with the potential value of abandoned journeys.

## SQL Workflow

Use `sql/schema.sql` to create a compatible analytics table, then run `sql/funnel_analysis.sql` for a SQL-native funnel query.

```bash
psql -d ecommerce -f sql/schema.sql
psql -d ecommerce -f sql/funnel_analysis.sql
```

The SQL uses conditional aggregation and deduplicates users by stage, making results reliable even if a session contains repeated events.

## Example Outputs

| Metric | Interpretation |
|---|---|
| Landing users | Total users entering the campaign funnel |
| Step conversion | Percentage of users advancing to the next stage |
| Drop-off count | Users lost between consecutive stages |
| Revenue opportunity | Potential recovery value based on observed segment performance |

Run the Python analysis to generate current values from the deterministic sample dataset.

## Use in a Spreadsheet

The CSV reports can be opened directly in Excel or Google Sheets:

1. Open `reports/funnel_summary.csv` for stage KPIs.
2. Filter `reports/segment_summary.csv` by campaign or device.
3. Sort `reports/revenue_opportunity.csv` from largest to smallest opportunity.
4. Use a funnel or waterfall chart to visualize drop-offs.

## Testing

```bash
python -m unittest discover -s tests -v
```

## Recommended Experiments

- Optimize the largest campaign or device drop-off segment before the entire funnel.
- Add cart reminders or checkout reassurance at the highest-loss transition.
- Test faster checkout, delivery cost visibility, and payment method coverage.
- Use holdout groups and compare incremental revenue, not only conversion rate.

## Limitations

- The initial dataset is synthetic and intended for reproducibility.
- Funnel analysis assumes one event record per stage per user journey.
- Revenue recovery estimates do not account for probability uncertainty or marketing costs.
- Replace sample data with warehouse data and configure attribution windows before production use.

## License

MIT License. See [LICENSE](LICENSE).
