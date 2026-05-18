# System Functional Overview

This document explains how the system works, with a focus on the OPC UA Realtime page, Parameter Traceability, and Manual Prediction. It is written as a step-by-step guide for operators and analysts.

## 1. Data Foundations (Shared by All Pages)

1. The system connects to the MySQL database using credentials from the .env file.
2. Core tables are read from MySQL:
   - model_schema.recipe_parameters (with ValueMin/ValueMean/ValueMax)
   - recipe_initial (base recipe definitions)
   - ProductionRun (run metadata)
   - MachineTagValue (OPC UA time-series events)
3. The app uses cached loaders to avoid repeated heavy queries.
4. If data is missing, the page shows warnings instead of crashing.

## 2. OPC UA Realtime Page (Live Monitoring)

This page shows live quality monitoring using OPC UA signals and the trained model.

Step-by-step flow:

1. Page boots and applies the Coficab theme and navigation bar.
2. The system loads model artifacts:
   - xgboost_model.pkl
   - scaler.pkl
   - feature_names.pkl
3. It loads parameter definitions from model_schema.recipe_parameters to build the data sheet and expected ranges.
4. The OPC UA client is configured with the endpoint and namespace from .env.
5. When live monitoring starts:
   - The client connects to the OPC UA server.
   - It subscribes to the mapped nodes (OpcNodeId).
   - Incoming values are buffered in memory with timestamps.
6. The system aggregates incoming values into features (mean, min, max, std) per parameter.
7. The feature vector is normalized and fed to the XGBoost classifier.
8. The page displays:
   - Live KPI tiles (status, confidence, run count)
   - A prediction gauge (OK / NOT OK)
   - Parameter cards with current value vs expected range
9. If a parameter is out of range:
   - The parameter is highlighted in red.
   - The risk summary explains which parameters drove the result.
10. The monitoring loop continues with periodic refresh and updated predictions.

## 3. Parameter Traceability Page (Root Cause Analysis)

This page shows how any parameter evolved across a selected production run.

Step-by-step flow:

1. Page loads the Coficab theme and navigation bar.
2. It loads:
   - model_schema.recipe_parameters for limits and metadata
   - MachineTagValue for the time-series trace
   - ProductionRun for run selection
3. The user selects a machine and a production run.
4. The system finds all OpcNodeId values that exist for the chosen run.
5. The user selects a parameter, then a trace is loaded:
   - The system queries MachineTagValue for the run and OpcNodeId.
   - The time-series is converted to timestamps and sorted.
6. The page builds the trace plot:
   - Historical OK band (ValueMin/ValueMax)
   - Actual sensor values over time
7. The system highlights out-of-spec points and provides a short diagnosis:
   - Below minimum: potential under-processing
   - Above maximum: potential overheating or overspeed
8. Optional multi-run comparison can be used to compare the same parameter across runs.

## 4. Manual Prediction Page (Human-In-The-Loop)

This page lets the user enter manual values for parameters and get a quality prediction.

Step-by-step flow:

1. Page loads the Coficab theme and navigation bar.
2. It loads:
   - model_schema.recipe_parameters (Min/Mean/Max)
   - recipe_initial (recipe list)
   - ProductionRun (machine list)
3. The user selects a machine and a recipe.
4. The system lists all parameters available for that machine.
5. The user selects parameters to monitor.
6. For each selected parameter, the page shows:
   - Range: [Min - Max]
   - Mean
7. The user enters custom values.
8. The system evaluates each parameter:
   - OPTIMAL if near the mean
   - ACCEPTABLE if within range but far from mean
   - TOO_LOW or TOO_HIGH if outside range
9. The system aggregates all parameters into an overall OK/NOT OK prediction.
10. The page reports:
    - Overall prediction and confidence
    - Parameter-level status table
    - Recommendations to adjust problematic parameters
11. If severe deviations exist, the system can request a Mistral explanation for root cause guidance.

## 5. Summary of Outputs

- Live monitoring: real-time prediction with OPC UA input.
- Traceability: detailed parameter history and root cause hints.
- Manual prediction: manual input simulation with per-parameter feedback.

## 6. Common Notes

- All parameter ranges are sourced from model_schema.recipe_parameters.
- If a page shows empty lists, verify the MySQL schema and data population.
- The system favors safety: missing data triggers warnings rather than silent failures.
