# Notebook Quick Start

This guide covers the current notebook workflow used to produce or refresh model artifacts.

## Primary notebook

Use:

`notebooks/opcua_quality_prediction_model.ipynb`

This is the most relevant end-to-end notebook for the current OPC UA-oriented workflow.

## What it produces

Depending on the notebook cells you run, it can generate or refresh:

- recipe extraction outputs in `feature_extraction/`
- parameter intervals derived from historical runs
- model artifacts in `models/`
- metadata / reports in `outputs/`

## Recommended run order

1. Open Jupyter

```bash
jupyter notebook
```

2. Open `notebooks/opcua_quality_prediction_model.ipynb`

3. Run cells in order to:

- load recipe and historical data
- build feature tables
- train / evaluate models
- save artifacts to `models/`

## Other notebooks

- `comprehensive_opc_data_analysis.ipynb`: exploratory analysis
- `extract_recipe_files.ipynb`: recipe extraction support
- `manual_parameter_prediction.ipynb`: manual prediction experiments
- `recipe_parameter_sets.ipynb`: recipe testing workflow support
- `parameter_extraction_and_prediction.ipynb`: older pipeline retained for reference

## Expected artifacts used by the app

### Prediction pages

- `models/xgboost_model.pkl`
- `models/scaler.pkl`
- `models/feature_names.pkl`

### OPC UA testing pages

- `models/opcua_quality_xgboost.pkl`
- `models/feature_scaler.pkl`
- `models/feature_columns.pkl`
- `models/opcua_anomaly_detector.pkl`

## Before running notebooks

- ensure dependencies are installed
- ensure `.env` is present if notebook cells use database access
- verify the expected input files / tables exist

## Practical guidance

- If Streamlit reports missing model artifacts, run the relevant notebook workflow first.
- If you only need the app and the required models already exist, you do not need to rerun notebooks.
