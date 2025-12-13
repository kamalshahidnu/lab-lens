# BigQuery Setup for MIMIC-III Access

This guide explains how to access MIMIC-III data from the `physionet-data` project via BigQuery for model development.

## Prerequisites

1. **PhysioNet MIMIC-III Access**
  - Complete CITI training at https://physionet.org/
  - Request MIMIC-III dataset access
  - Link your Google account at https://physionet.org/settings/cloud/
  - Wait for approval (1-3 business days)
  - **Note**: The Google account linked to PhysioNet can be different from your Git/GitHub email - that's fine!

2. **Google Cloud SDK**
  - Install gcloud CLI: https://cloud.google.com/sdk/docs/install
  - Verify installation: `gcloud --version`

## Quick Start

### Step 1: Authenticate with Google Cloud

Run the setup script:

```bash
./scripts/setup_gcp_auth.sh
```

This will:
- Authenticate with gcloud
- Set up Application Default Credentials (ADC)
- Test connection to physionet-data project

**Alternative (Manual):**

```bash
# Authenticate with gcloud
gcloud auth login

# Set up Application Default Credentials
gcloud auth application-default login
```

### Step 2: Test Connection

```bash
python scripts/acquire_mimic3_bigquery.py --test
```

Expected output:
```
 Connection successful! Found 58,976 admissions in MIMIC-III
 Found 4 MIMIC-III datasets:
  - mimiciii_clinical
  - mimiciii_derived
  - mimiciii_notes
  - mimiciii_notes_derived
```

### Step 3: Fetch Data

**Fetch a sample (1000 records):**
```bash
python scripts/acquire_mimic3_bigquery.py --limit 1000
```

**Fetch all discharge summaries:**
```bash
python scripts/acquire_mimic3_bigquery.py
```

**Custom output location:**
```bash
python scripts/acquire_mimic3_bigquery.py --limit 5000 --output data/my_data.csv
```

**Save as Parquet (faster, smaller):**
```bash
python scripts/acquire_mimic3_bigquery.py --format parquet --output data/mimic3.parquet
```

## Available Datasets

The script can access these MIMIC-III datasets in `physionet-data`:

1. **mimiciii_clinical** - Clinical data (admissions, patients, lab events, etc.)
2. **mimiciii_derived** - Derived/processed tables
3. **mimiciii_notes** - Clinical notes (discharge summaries, etc.)
4. **mimiciii_notes_derived** - Derived note tables

## Data Acquisition Script

### Usage

```bash
python scripts/acquire_mimic3_bigquery.py [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--limit N` | Maximum number of records | All records |
| `--output PATH` | Output file path | `data_pipeline/data/raw/mimic_discharge_labs.csv` |
| `--format FORMAT` | Output format (`csv` or `parquet`) | `csv` |
| `--no-demographics` | Exclude patient demographics | Include |
| `--no-labs` | Exclude lab results | Include |
| `--no-diagnoses` | Exclude diagnosis codes | Include |
| `--test` | Test connection only | - |
| `--list-datasets` | List available datasets | - |
| `--list-tables DATASET` | List tables in dataset | - |
| `--project-id ID` | GCP project ID | `physionet-data` |

### Examples

**List all tables in mimiciii_clinical:**
```bash
python scripts/acquire_mimic3_bigquery.py --list-tables mimiciii_clinical
```

**Fetch discharge summaries only (no demographics/labs):**
```bash
python scripts/acquire_mimic3_bigquery.py --no-demographics --no-labs --no-diagnoses
```

**Fetch with custom project:**
```bash
python scripts/acquire_mimic3_bigquery.py --project-id my-project-id
```

## What Data is Fetched?

The script fetches discharge summaries with the following joins:

### Core Data
- **Discharge summaries** from `mimiciii_notes.noteevents`
- Text cleaned (removes de-identification markers like `[** ... **]`)
- Text length statistics

### Demographics (if `--no-demographics` not used)
- Gender
- Ethnicity
- Age at admission
- Insurance type
- Language
- Admission type

### Lab Results (if `--no-labs` not used)
- Lab summary (top 20 recent labs)
- Total lab count
- Abnormal lab count

### Diagnoses (if `--no-diagnoses` not used)
- Diagnosis count
- Top 10 ICD-9 codes

## Integration with Pipeline

The fetched data is saved to `data_pipeline/data/raw/mimic_discharge_labs.csv` by default, which is the expected input for the preprocessing pipeline:

```bash
# 1. Fetch data from BigQuery
python scripts/acquire_mimic3_bigquery.py --limit 5000

# 2. Run preprocessing
python data_pipeline/scripts/preprocessing.py

# 3. Run full pipeline
python data_pipeline/scripts/main_pipeline.py
```

## Troubleshooting

### Error: "No credentials found"

**Solution:**
```bash
gcloud auth application-default login
```

### Error: "403 Forbidden - Access Denied"

**Possible causes:**
1. Google account not linked to PhysioNet
  - Go to https://physionet.org/settings/cloud/
  - Link your Google account
  - Wait for approval

2. MIMIC-III access not approved
  - Check your PhysioNet account status
  - Complete CITI training if not done

3. Wrong project ID
  - The project must be `physionet-data` (not your own GCP project)
  - Verify: `gcloud config get-value project`

### Error: "ModuleNotFoundError: No module named 'google.cloud.bigquery'"

**Solution:**
```bash
pip install google-cloud-bigquery db-dtypes
```

### Error: "BigQuery quota exceeded"

**Solution:**
- BigQuery has free tier limits
- Use `--limit` to fetch smaller batches
- Wait and retry later

### Slow queries

**Tips:**
- Use `--limit` to fetch smaller samples for testing
- Use `--format parquet` for faster I/O
- Exclude unnecessary joins (`--no-labs`, `--no-diagnoses`)

## Authentication Methods

### Method 1: Application Default Credentials (Recommended)

```bash
gcloud auth application-default login
```

**Important**: When prompted, authenticate with the **Google account that is linked to PhysioNet** (this can be different from your Git email - that's perfectly fine!).

This is the easiest method. Credentials are stored locally and automatically used by Python scripts.

### Method 2: Service Account (For Production)

1. Create a service account in GCP
2. Grant BigQuery access
3. Download JSON key
4. Set environment variable:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
  ```

### Method 3: OAuth 2.0 (For Notebooks)

See `data_pipeline/notebooks/data_acquisition.ipynb` for OAuth flow.

## Cost Considerations

- **BigQuery Free Tier**: 1 TB query processing per month
- **Storage**: Free for queries (data stays in BigQuery)
- **Export**: Free to download results
- **Recommendation**: Use `--limit` for development/testing

## Security Notes

- **Never commit credentials** to git
- Application Default Credentials are stored in `~/.config/gcloud/`
- Service account keys should be in `.gitignore`
- The script uses read-only queries (no data modification)

## Next Steps

After fetching data:

1. **Preprocess data:**
  ```bash
  python data_pipeline/scripts/preprocessing.py
  ```

2. **Train model:**
  ```bash
  python src/training/train_gemini.py
  ```

3. **Run inference:**
  ```bash
  python src/training/example_usage.py
  ```

## Additional Resources

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [MIMIC-III Documentation](https://mimic.mit.edu/)
- [PhysioNet Cloud Access](https://physionet.org/settings/cloud/)

