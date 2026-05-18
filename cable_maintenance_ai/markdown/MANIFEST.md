# Project Manifest test

This manifest lists the maintained parts of the current system.

## Top-Level Runtime Files

- `db_connection.py`: shared SQLAlchemy engine factory used by the inner application
- `cable_maintenance_ai/requirements.txt`: Python dependencies
- `cable_maintenance_ai/README.md`: main project guide

## Streamlit App

Located in `cable_maintenance_ai/app/`.

- `app.py`: Streamlit entrypoint / home page
- `db_helpers.py`: shared MySQL data-loading helpers

### Maintained Pages

- `pages/prediction_page.py`
- `pages/manual_prediction_page.py`
- `pages/recipe_parameter_sets_page.py`
- `pages/opcua_realtime_page.py`
- `pages/opcua_parameter_testing_page.py`
- `pages/parameter_traceability_page.py`

### Legacy / Non-Canonical Pages

- `pages/realtime_demo_page.py`
- `pages/prediction_page_backup.py`

These files remain in the repository but are not part of the primary documented workflow.

## Data and Database Surface

### MySQL tables used by the app

- `recipe_parameters`
- `recipe_initial`
- `tags_mapping`
- `productionrun`
- `MachineTagValue`

### Local folders still present in the repo

- `data/`: auxiliary datasets and notebook inputs
- `feature_extraction/`: extracted recipe-related outputs
- `models/`: trained model artifacts
- `outputs/`: generated reports / derived files
- `notebooks/`: analysis and model-building notebooks

## Key Notebooks

- `notebooks/opcua_quality_prediction_model.ipynb`
- `notebooks/comprehensive_opc_data_analysis.ipynb`
- `notebooks/manual_parameter_prediction.ipynb`
- `notebooks/recipe_parameter_sets.ipynb`
- `notebooks/extract_recipe_files.ipynb`

## Primary Documentation Set

- `README.md`
- `START_HERE.md`
- `PROJECT_SUMMARY.md`
- `SYSTEM_ARCHITECTURE.md`
- `OPC_UA_QUICK_START.md`
- `docs/OPCUA_PARAMETER_TESTING_GUIDE.md`
- `QUICK_START_NOTEBOOK.md`

Historical change logs, duplicate markdown mirrors, and migration notes have been removed from the maintained documentation surface.
