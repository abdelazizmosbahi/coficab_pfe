# PlantUML Inputs For Grok

This file summarizes the system, components, actors, and flows for generating three diagrams:
1) System component diagram
2) General use case diagram
3) Class diagram

All details are based on the maintained Streamlit app and current docs, plus a
future production data source change to SQL Server.

## System Scope
- Product name: Cable Manufacturing AI
- Primary runtime: Streamlit app in app/
- Current data source: MySQL tables (no CSV dependency for maintained pages)
- Production data source (future): SQL Server (replace MySQL as the primary data source)
- Runtime services: OPC UA server (now used), optional Mistral API
- Model artifacts: stored in models/

## Actors (for use cases)
- Operator / Engineer: uses Streamlit pages to predict quality, test parameters, and trace history
- Data Engineer: maintains data and models
- External Systems: MySQL (current), SQL Server (future production), OPC UA Server, Mistral API

## External Systems / Interfaces
- MySQL database (tables listed below, current)
- SQL Server database (future production)
- OPC UA server endpoint (opc.tcp://...)
- Mistral API (optional AI explanations)
- Model artifacts stored on disk (models/)

## Data Stores And Tables (Current MySQL)
- recipe_parameters (main parameter ranges and metadata)
- recipe_initial (base recipe definitions)
- tags_mapping (machine and parameter mapping)
- productionrun (run metadata)
- MachineTagValue (event-based sensor values)
- model_schema.parameter_optimal_windows (learned stable windows)

## Data Stores And Tables (Future SQL Server)
- SQL Server will replace MySQL as the primary data source in production.
- Expect the same logical tables or views, even if schema or naming differs.
- The core entities should map to:
  - Recipe parameters and ranges
  - Recipe initial definitions
  - Tags mapping (machine/parameter)
  - Production runs metadata
  - Machine tag values (event-based trace data)
  - Stable window outputs (if persisted)

## Model Artifacts
- xgboost_model.pkl
- scaler.pkl
- feature_names.pkl
- opcua_quality_xgboost.pkl
- feature_scaler.pkl
- feature_columns.pkl
- opcua_anomaly_detector.pkl

## Application Components
- app/app.py: entrypoint, navigation, capability list
- app/db_helpers.py: shared MySQL access, caching, aliases
- app/pages/prediction_page.py: multi-scenario prediction
- app/pages/manual_prediction_page.py: manual parameter input prediction
- app/pages/recipe_parameter_sets_page.py: recipe-based testing
- app/pages/opcua_realtime_page.py: live OPC UA monitoring + prediction
- app/pages/opcua_parameter_testing_page.py: OPC UA parameter validation + model checks
- app/pages/parameter_traceability_page.py: datasheet + traceability view
- db_connection.py: builds SQLAlchemy engine from .env

## Configuration Inputs (.env)
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME (current MySQL)
- MISTRAL_API_KEY, MISTRAL_MODEL (optional AI explanations)
- OPC_SERVER_URL, OPC_NAMESPACE_URI

## Live Data Notes
- The app connects to a real OPC UA server for live values.

## Shared Helpers (db_helpers.py)
- get_engine(): cached SQLAlchemy engine
- load_recipe_parameters_df(): recipe parameters with Min/Mean/Max aliases
- load_recipe_initial_df(): base recipe definitions
- load_tags_mapping_df(): machine/parameter mapping
- load_production_runs_df(): run metadata
- load_distinct_run_ids(): distinct ProductionRunId
- load_sensor_trace(run_id, opc_node_id): trace for a run and parameter
- load_parameter_optimal_windows(): stable windows (model_schema)
- rebuild_step_signal(): forward-fill event data to step signal
- detect_stable_points(): stable region detection

## Page Responsibilities (Use Cases)
- Prediction Page:
  - Build multiple scenarios for a machine/recipe
  - Load recipe/parameter context from MySQL
  - Run model-based predictions
  - Optionally request Mistral explanations
- Manual Prediction Page:
  - Manual entry of parameter values
  - Evaluate values against historical ranges
  - Aggregate to OK/NOTOK prediction
  - Optionally request Mistral explanations
- Recipe Parameter Sets Page:
  - Load recipe parameters from MySQL
  - Allow editing values and assess ranges
  - Run model-based predictions
  - Optionally request Mistral explanations
- OPC UA Real-Time Page:
  - Connect to OPC UA server
  - Read live parameter values
  - Run quality model + anomaly detector
  - Optionally request Mistral explanations
- OPC UA Parameter Testing Page:
  - Connect to OPC UA server
  - Read live values for selected machine/recipe
  - Assess parameter health vs historical ranges
  - Run quality model + anomaly detector
  - Optionally request Mistral explanations
- Parameter Traceability Page:
  - View recipe parameter datasheet
  - Select a parameter and production run
  - Load trace from MachineTagValue
  - Overlay Min/Mean/Max bands and show violations
  - Show learned stable windows

## Key Data Flows (System Diagram)
- Streamlit pages -> db_helpers -> MySQL (current) or SQL Server (future)
- Prediction/Manual/Recipe pages -> model artifacts
- OPC UA pages -> OPC UA server (read live values)
- Pages -> Mistral API (optional explanation)

## Production Data Source Change (Explicit Note)
- Current system uses MySQL as the primary data source.
- In real production, the primary database is SQL Server.
- For diagrams, show MySQL as current and SQL Server as future production, or
  represent a generic "Production Database" with a note that it is SQL Server.

## Notes For Class Diagram
- Codebase is function-oriented; few concrete classes are defined.
- Concrete classes used at runtime (external libraries):
  - sqlalchemy.engine.Engine
  - asyncua.Client
  - asyncua.Server
  - mistralai.Mistral
- Modules can be modeled as components or pseudo-classes if desired.

## Suggested Diagram Boundaries
- System component diagram should include:
  - Streamlit app (pages + db_helpers)
  - MySQL database (current)
  - SQL Server database (future production)
  - OPC UA server
  - OPC UA server
  - Model artifacts
  - Mistral API (optional)
- Use case diagram should include:
  - Operator / Engineer actor
  - Data Engineer actor
  - Use cases for each maintained page
  - Optional AI explanation use case
- Class diagram can be minimal (external library classes + module dependencies)
  or expanded into a module-as-class view if desired.
