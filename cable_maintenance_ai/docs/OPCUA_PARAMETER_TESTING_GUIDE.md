# OPC UA Parameter Testing Guide

## Overview

The OPC UA Parameter Testing page validates live machine parameters against reference ranges and model artifacts.
It combines:

- live OPC UA reads
- MySQL-backed recipe reference data
- saved model artifacts in `models/`
- optional Mistral-generated root cause analysis

## What the page uses

### Live source

- OPC UA server endpoint from `.env`

### Reference source

- MySQL `recipe_parameters` loaded through `app/db_helpers.py`

### Model artifacts

- `models/opcua_quality_xgboost.pkl`
- `models/feature_scaler.pkl`
- `models/feature_columns.pkl`
- `models/opcua_anomaly_detector.pkl`

## Typical workflow

1. Connect to a live OPC UA source
2. Open the OPC UA Parameter Testing page in Streamlit
3. Connect to the OPC UA endpoint
4. Select machine and recipe context
5. Refresh or auto-refresh parameter values
6. Review overall quality prediction, parameter statuses, and root cause analysis

## Parameter assessment output

The page classifies parameters into statuses such as:

- `OPTIMAL`
- `ACCEPTABLE`
- `TOO_LOW`
- `TOO_HIGH`
- `UNKNOWN`

## Exports

The page can export:

- detailed parameter assessment CSV output
- summary text reports for review / traceability

## Required configuration

```env
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=...

OPC_SERVER_URL=opc.tcp://localhost:4840/freeopcua/server/
OPC_NAMESPACE_URI=http://examples.freeopcua.github.io
MISTRAL_API_KEY=...
MISTRAL_MODEL=mistral-small-latest
```

## Troubleshooting

### Connection fails

- verify the OPC UA endpoint
- ensure the OPC UA server is running
- verify `asyncua` is installed

### Models cannot load

- check the expected files exist in `models/`
- rerun the notebook workflow if artifacts are missing or stale

### Reference data is empty

- verify MySQL connectivity
- verify `recipe_parameters` contains rows for the selected machine / recipe

### AI analysis is unavailable

- verify `MISTRAL_API_KEY`
- note that parameter assessment can still run without AI explanations
