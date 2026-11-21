Data Directory

This directory contains datasets used throughout the Customer Funnel Analysis project.

Directory Structure
text
data/
├── raw/          # Original datasets
├── processed/    # Cleaned and transformed datasets
└── README.md     # Data documentation

Raw Data

Place original datasets in data/raw/.

Raw data should:

Remain unchanged after collection.
Retain its original structure and format.
Be obtained from authorized sources.
Never contain exposed credentials or unauthorized personal information.
Processed Data

Processed datasets are stored in data/processed/.

These datasets are generated through the project's data processing pipeline.

Data Sources
Dataset	Source	Format	Description
To be updated	To be updated	CSV	Customer funnel data
Data Availability

Raw and processed datasets are excluded from Git tracking by default.

Users must obtain the datasets from their authorized sources and place them in the appropriate directories before executing the analysis.

Important

Do not commit confidential, proprietary, or personally identifiable customer information to the repository.