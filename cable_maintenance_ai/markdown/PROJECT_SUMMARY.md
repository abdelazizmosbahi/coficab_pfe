# Project Summary

## Overview

Cable Manufacturing AI is a hybrid monitoring and prediction system for cable production.
Its current production-oriented workflow combines:

- MySQL-backed recipe and historical sensor data
- Streamlit pages for interactive analysis
- ML model artifacts for quality prediction
- OPC UA connectivity for live telemetry
- Optional Mistral-powered explanations

## Current Runtime Model

The app has moved away from page-level CSV loading.
Current Streamlit pages load shared data through `app/db_helpers.py`, which reads from MySQL and caches the results in-process.

The most important tables are:

- `recipe_parameters`: recipe parameter definitions and historical min/mean/max values
- `recipe_initial`: recipe baseline values used by some prediction workflows
- `tags_mapping`: machine / parameter mappings
- `productionrun`: run metadata
- `MachineTagValue`: historical sensor trace data used by traceability

## Current User Flows

### Prediction workflows

- `prediction_page.py`: multi-scenario prediction using trained model artifacts
- `manual_prediction_page.py`: manual value entry and parameter-level assessment
- `recipe_parameter_sets_page.py`: recipe-based production testing

### Live / monitoring workflows

- `opcua_realtime_page.py`: OPC UA monitoring, datasheet access, live prediction context
- `opcua_parameter_testing_page.py`: parameter health assessment and model validation
- `parameter_traceability_page.py`: datasheet selection plus run traceability and multi-run comparison

## OPC UA Integration

OPC UA pages connect to a live OPC UA server for real-time values.
Historical traceability continues to come from MySQL `MachineTagValue`.

## Models and Artifacts

The repository currently contains two related artifact sets:

### General prediction pages

- `models/xgboost_model.pkl`
- `models/scaler.pkl`
- `models/feature_names.pkl`

### OPC UA parameter testing pages

- `models/opcua_quality_xgboost.pkl`
- `models/feature_scaler.pkl`
- `models/feature_columns.pkl`
- `models/opcua_anomaly_detector.pkl`

## Current State of Documentation

The documentation has been consolidated around the current architecture.
Older update logs, migration notes, and duplicate `markdown/` copies were removed because they no longer matched the MySQL-backed runtime.

Use these files as the current source of truth:

- `README.md`
- `START_HERE.md`
- `MANIFEST.md`
- `SYSTEM_ARCHITECTURE.md`
- `OPC_UA_QUICK_START.md`
- `docs/OPCUA_PARAMETER_TESTING_GUIDE.md`
- `QUICK_START_NOTEBOOK.md`
