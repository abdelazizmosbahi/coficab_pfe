# System Architecture

## High-Level Architecture

The current system is organized into five layers:

1. Data layer: MySQL tables containing recipe definitions, run metadata, and sensor traces
2. Integration layer: OPC UA server providing live telemetry
3. Model layer: persisted ML artifacts used by prediction and validation pages
4. Application layer: Streamlit pages for prediction, monitoring, testing, and traceability
5. AI explanation layer: Mistral-powered analysis where configured

## Data Layer

### MySQL tables used directly by the application

- `recipe_parameters`
- `recipe_initial`
- `tags_mapping`
- `productionrun`
- `MachineTagValue`

`app/db_helpers.py` is the shared access layer for these tables.
It applies caching and preserves backward-compatible column aliases where older page code expects them.

## Integration Layer

OPC UA pages connect to a live OPC UA server using the endpoint configured in `.env`.

## Model Layer

Two main artifact families are present:

### Multi-scenario / manual workflows

- `xgboost_model.pkl`
- `scaler.pkl`
- `feature_names.pkl`

### OPC UA testing workflows

- `opcua_quality_xgboost.pkl`
- `feature_scaler.pkl`
- `feature_columns.pkl`
- `opcua_anomaly_detector.pkl`

## Application Layer

The Streamlit app lives in `app/`.

### Shared runtime modules

- `app.py`
- `db_helpers.py`

### Maintained user-facing pages

- `prediction_page.py`
- `manual_prediction_page.py`
- `recipe_parameter_sets_page.py`
- `opcua_realtime_page.py`
- `opcua_parameter_testing_page.py`
- `parameter_traceability_page.py`

## Traceability Architecture

The traceability page uses the same MySQL-backed recipe datasheet as the OPC UA real-time page and adds:

- single-row parameter selection from the recipe datasheet
- run-specific historical trace loading from `MachineTagValue`
- optimal / normal / not-ok visual bands
- out-of-spec root cause banner
- multi-run comparison aligned on elapsed time

## Data Flow

### Historical traceability flow

1. User selects a production run
2. App loads recipe datasheet from `recipe_parameters`
3. User selects a parameter row
4. App loads time-series data from `MachineTagValue`
5. App overlays historical spec ranges and violation analysis

### Live OPC UA flow

1. OPC UA server publishes machine and parameter values
2. Streamlit OPC UA pages connect to the server
3. Pages read live values and run model / range checks

### Offline prediction flow

1. Pages load recipe reference data from MySQL
2. Pages load model artifacts from `models/`
3. User selects scenarios or enters custom values
4. App computes predictions and explanation outputs
