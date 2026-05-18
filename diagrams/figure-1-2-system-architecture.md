# Figure 1.2 — System Architecture Diagram

> Modular Streamlit multi-page architecture organized around configuration, live monitoring, and analysis — backed by SQL Server, ML models, and Mistral AI.

```mermaid
flowchart TB
    subgraph Frontend["Streamlit Multi-Page Application"]
        CONFIG["Configuration & Setup
            ─────────────────
            • Machine selection
            • Parameter management
            • Recipe configuration
            • Session persistence
            • CRUD operations"]
        MONITOR["Live Monitoring
            ─────────────────
            • Real-time parameter cards
            • Spec violation badges
            • Quality probability
            • Traceability charts"]
        ANALYSIS["Analysis & Datasheet Gen.
            ─────────────────
            • Run selection
            • Sample collection
            • Statistics
            • Quality correlation
            • CSV export"]
    end

    subgraph Shared["Shared Database Helpers & ML Utils"]
        DB_HELP["db_helpers.py
            (queries, caching, analysis)"]
        AUTH_HELP["auth_helpers.py
            (authentication, sessions,
             page permissions)"]
    end

    subgraph Database["SQL Server Database (OpcDb)"]
        DB1["MachineTagValue | productionrun"]
        DB2["ProductionRunQuality | machine_configuration"]
        DB3["parameter_reference_datasheet | users"]
        DB4["tags_mapping | analysis_results_[MACHINE]"]
    end

    subgraph External["ML Models & Notebooks"]
        ML["XGBoost / Random Forest"]
        NB["Jupyter Notebooks via Papermill"]
        MISTRAL["Mistral AI API"]
        CHARTS["Plotly Charts"]
    end

    CONFIG --> DB_HELP
    MONITOR --> DB_HELP
    ANALYSIS --> DB_HELP
    CONFIG --> AUTH_HELP
    MONITOR --> AUTH_HELP
    ANALYSIS --> AUTH_HELP

    DB_HELP --> DB1
    DB_HELP --> DB2
    DB_HELP --> DB3
    DB_HELP --> DB4
    AUTH_HELP --> DB3

    MONITOR --> ML
    MONITOR --> MISTRAL
    ANALYSIS --> NB
    MONITOR --> CHARTS
    ANALYSIS --> CHARTS
```

**Data Flow:**

1. OPC UA sensors write data to `MachineTagValue` (time-series events)
2. Configuration page saves machine setups to `machine_configuration`
3. Analysis notebook (executed via Papermill) reads historical data, computes statistics, and stores reference datasheets
4. Model page loads reference datasheets and compares live values from `MachineTagValue` in real-time
5. Quality prediction score is computed based on parameter deviations from specification ranges
6. Out-of-spec parameters trigger Mistral AI for natural-language root-cause analysis
7. `auth_helpers.py` enforces page-level permissions on every page load
