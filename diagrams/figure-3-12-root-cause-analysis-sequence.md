# Figure 3.12 — Root Cause Analysis Sequence Diagram

> System detects quality probability below threshold and triggers Mistral AI for natural-language root cause analysis.

```mermaid
sequenceDiagram
    actor O as Operator
    participant ModelPage as Model Page
    participant RCA as RCA Service
    participant Mistral as Mistral AI API

    Note over ModelPage: Quality probability < 50% detected (or manual click)

    O->>ModelPage: Click "Analyze Root Cause" (optional)

    ModelPage->>ModelPage: Collect out-of-range parameters
    activate ModelPage

    ModelPage->>ModelPage: For each parameter: current_value, min, max, deviation_pct
    ModelPage->>ModelPage: Build context: machine_code, parameter_names, violation_details

    ModelPage->>RCA: analyze_parameter_anomaly(context)
    deactivate ModelPage

    activate RCA
    RCA->>RCA: Construct detailed prompt with manufacturing context
    RCA->>Mistral: POST /v1/chat/completions (mistral-small-latest / mistral-large-latest)
    activate Mistral

    Mistral-->>RCA: Raw response with analysis text
    deactivate Mistral

    RCA->>RCA: Parse structured response
    RCA-->>ModelPage: {
    Note over ModelPage: root_cause, corrective_actions[], preventive_measures[]
    }
    deactivate RCA

    ModelPage-->>O: Display analysis dialog:
    Note over ModelPage, O: (1) Most Likely Root Cause
    Note over ModelPage, O: (2) Immediate Corrective Actions
    Note over ModelPage, O: (3) Preventive Measures
```
