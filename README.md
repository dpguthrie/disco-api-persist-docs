# DBT Column Description Inheritance

This tool solves a limitation in dbt's `persist_docs` functionality by persisting inherited column descriptions to BigQuery tables. While dbt's built-in `persist_docs` feature can persist manually written column descriptions, it doesn't handle descriptions that are inherited from upstream columns.

## Overview

When using dbt's column description inheritance (using `description:` in your `.yml` files), the descriptions are visible in dbt docs but don't get persisted to the actual BigQuery tables. This script:

1. Queries the dbt Cloud Metadata API to get all models in your environment
2. Identifies columns that have inherited descriptions from upstream columns
3. Updates the BigQuery table schemas to include these inherited descriptions

## Prerequisites

- A dbt Cloud account with API access
- Google Cloud credentials with BigQuery access
- Python 3.x

## Setup

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
DBT_CLOUD_SERVICE_TOKEN=
DBT_CLOUD_HOST=
DBT_CLOUD_ACCOUNT_ID=
DBT_CLOUD_ENVIRONMENT_ID=
```

3. Place your Google Cloud service account JSON key in the root directory as `service_account.json`

## Usage

Run the script:
```bash
python main.py
```

The script will:
- Fetch all models from your dbt Cloud environment
- Identify columns with inherited descriptions
- Update BigQuery table schemas for affected tables
- Print confirmation messages for each updated table

## How It Works

1. The script uses the dbt Cloud Metadata API to query information about your models, including column descriptions and their origins
2. For each model, it checks if any columns have inherited descriptions (indicated by `descriptionOriginColumnName`)
3. If inherited descriptions are found, it updates the BigQuery table schema to include these descriptions
4. The updates are made using the BigQuery API, ensuring the descriptions persist even after future dbt runs

## Limitations

- Only works with BigQuery
- Requires dbt Cloud (not compatible with dbt Core)
- Updates are made directly to BigQuery tables, outside of dbt's normal workflow
- Descriptions will be overwritten by subsequent dbt runs, so this script should either:
  - Be configured as a webhook to run after dbt Cloud job completion
  - Be scheduled to run periodically after your dbt jobs complete
  - Be integrated into your dbt job orchestration workflow

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements or bug fixes.
