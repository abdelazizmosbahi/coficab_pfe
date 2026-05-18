# Cable Manufacturing AI

Cable Manufacturing AI is a Streamlit-based monitoring and prediction system for cable production.
The current system is built around MySQL-backed recipe and trace data, optional OPC UA live connectivity,
and trained ML artifacts used by the prediction pages.

## Current System

- Primary app runtime: Streamlit in `app/`
- Primary data source for app pages: MySQL tables, not local CSV files
- Live sensor source: OPC UA
- Historical traceability source: MySQL `MachineTagValue`
- AI explanations: Mistral API when configured

## Active App Pages

- `app/app.py`: home page / entrypoint
- `app/pages/prediction_page.py`: multi-scenario quality prediction
- `app/pages/manual_prediction_page.py`: manual parameter input prediction
- `app/pages/recipe_parameter_sets_page.py`: recipe-based testing
- `app/pages/opcua_realtime_page.py`: OPC UA live monitoring and datasheet view
- `app/pages/opcua_parameter_testing_page.py`: real-time parameter assessment and model validation
- `app/pages/parameter_traceability_page.py`: datasheet-driven traceability and multi-run comparison

Legacy pages such as `realtime_demo_page.py` and `prediction_page_backup.py` still exist in the repository,
but they are not the canonical workflow described by this documentation.

## Data Sources

The application now reads directly from MySQL through `app/db_helpers.py`.
The main tables used by the app are:

- `recipe_parameters`
- `recipe_initial`
- `tags_mapping`
- `productionrun`
- `MachineTagValue`

Important detail: several MySQL column names are reserved words, so SQL queries in the codebase use backticks.

## Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with the required connection settings.

Minimum database configuration:

```env
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
```

Optional AI / OPC UA settings:

```env
MISTRAL_API_KEY=...
MISTRAL_MODEL=mistral-small-latest
OPC_SERVER_URL=opc.tcp://0.0.0.0:4840/freeopcua/server/
OPC_NAMESPACE_URI=http://examples.freeopcua.github.io
```

## Run the App

From the repository root:

```bash
cd app
streamlit run app.py
```

## Notebook and Model Workflow

The repository still contains notebooks for analysis and model generation.
The main notebook guide is in `QUICK_START_NOTEBOOK.md`.

Current notebooks of interest:

- `notebooks/opcua_quality_prediction_model.ipynb`
- `notebooks/comprehensive_opc_data_analysis.ipynb`
- `notebooks/manual_parameter_prediction.ipynb`
- `notebooks/recipe_parameter_sets.ipynb`

Current model artifacts in `models/` include:

- `xgboost_model.pkl`
- `scaler.pkl`
- `feature_names.pkl`
- `opcua_quality_xgboost.pkl`
- `feature_scaler.pkl`
- `feature_columns.pkl`
- `opcua_anomaly_detector.pkl`

## Documentation Map

- `START_HERE.md`: fastest path to running the current system
- `MANIFEST.md`: curated file map of the maintained project surface
- `PROJECT_SUMMARY.md`: current project summary
- `SYSTEM_ARCHITECTURE.md`: architecture and data flow
- `OPC_UA_QUICK_START.md`: live OPC UA setup
- `docs/OPCUA_PARAMETER_TESTING_GUIDE.md`: parameter testing page guide
- `QUICK_START_NOTEBOOK.md`: notebook and model generation guide

## Notes

- The app no longer depends on the old local `data/` workflow for page-level operation.
- Some notebooks and legacy scripts still reference CSV-based experimentation; use the guides above as the current source of truth.
- If a page reports missing model artifacts, run the relevant notebook workflow first.
