# Figure 3.10 — Real-Time Monitoring Sequence Diagram

**Location:** Chapter 3 — Conception / §3.2.3.3  
**Type:** UML Sequence Diagram  

---

## Purpose

Real-time monitoring loop. The **Analyst** selects a configuration, the system loads the datasheet, and a 1-second loop fetches live values, compares specs, computes quality, and renders cards.

---

## Lifelines

| Lifeline | Type |
|----------|------|
| **Analyst** | Actor |
| **Model Page** | Boundary |
| **auth_helpers** | Controller |
| **db_helpers** | Controller |
| **dbo.MachineTagValue** | Entity |
| **model_schema.machine_configuration** | Entity |
| **model_schema.analysis_results_[MACHINE]** | Entity |
| **Mistral AI** | External System |

---

## Flow: Initial Load

1. **Analyst** → **Model Page**: Navigates to Realtime page
2. **Model Page** → **auth_helpers**: `ensure_page_authentication('model_page')`
3. **auth_helpers**: Verifies session → access granted
4. **Model Page** → **db_helpers**: `get_all_configurations()` (cached TTL 300s)
5. **db_helpers** → **model_schema.machine_configuration**: Returns config list
6. **Model Page** → **Analyst**: Shows config dropdown

---

## Flow: Config Selection

7. **Analyst** → **Model Page**: Selects configuration
8. **Model Page** → **db_helpers**: `load_latest_analysis_results(configId)` (cached TTL 600s)
9. **db_helpers** → **model_schema.analysis_results_[MACHINE]**: Returns reference datasheet
10. **Model Page** → **db_helpers**: `get_machine_status_by_linespeed(machineCode)` (cached TTL 10s)
11. **db_helpers** → **dbo.MachineTagValue**: Returns Working/Standby status (LineSpeed check)
12. **Model Page** → **Analyst**: Shows metrics + recipe cards

---

## Flow: Monitoring Loop (every 1 second — dual fragments)

Two `@st.fragment(run_every=1)` functions run concurrently, sharing data via `st.session_state`:

### Fragment A — `render_monitoring_values()` — fetch + compute

```
loop [every 1 second — @st.fragment A]
```

13. **Model Page** → **db_helpers**: `load_current_machine_values(machineCode, params)`
14. **db_helpers** → **dbo.MachineTagValue**: Queries latest values by OpcNodeIds
15. **dbo.MachineTagValue** → **db_helpers**: Returns current values
16. **Model Page**: For each param: `target=(min+max)/2`, `spread=(max-min)/2`, `score=max(0, 100-|deviation|/spread*50)`
17. **Model Page**: Computes overall quality = `mean(all param scores)`
18. **Model Page**: Stores `merged_readings` in `st.session_state`

```
end loop
```

### Fragment B — `render_parameter_cards()`

```
loop [every 1 second — @st.fragment B]
```

19. **Model Page**: Reads `merged_readings` from `st.session_state`
20. **Model Page**: Renders color-coded parameter cards (STABLE / NEAR MIN / NEAR MAX / OUT OF RANGE)

```
opt [any parameter out of range]
```
21. **Model Page**: Shows violation badges with deviation details

```
opt [quality < 50% or button click]
```
22. **Model Page** → **db_helpers**: `call_mistral_ai(outOfSpecParams, context)`
23. **db_helpers** → **Mistral AI**: HTTP POST with prompt
24. **Mistral AI** → **db_helpers**: Returns analysis
25. **db_helpers** → **Model Page**: Returns root cause, actions, preventions
26. **Model Page** → **Analyst**: Displays Mistral analysis dialog

```
end loop
```

---

## Flow: Traceability Charts

25. **Analyst** → **Model Page**: Expands charts section
26. **Model Page** → **db_helpers**: `get_sensor_trace(machineCode, params)`
27. **db_helpers** → **dbo.MachineTagValue**: Returns time-series data
28. **Model Page**: Renders Plotly chart with spec overlays
29. **Model Page** → **Analyst**: Shows 3-second + full timeline charts

---

## Notes for Diagram Generation

- Lifelines: **Analyst**, **Model Page**, **auth_helpers**, **db_helpers**, **dbo.MachineTagValue**, **model_schema.machine_configuration**, **model_schema.analysis_results_[MACHINE]**, **Mistral AI**.
- Use **two** `loop` blocks labeled `"Every 1 second (@st.fragment A)"` and `"Every 1 second (@st.fragment B)"` for the dual-fragment architecture.
- Fragment A fetches values and computes quality. Fragment B reads from session_state and renders cards + triggers alerts.
- Use `opt` for violation badges and Mistral trigger.
- Show initial page load with `ensure_page_authentication()` as the first call.
- Add note: `"Per param: target=(min+max)/2, spread=(max-min)/2, score=max(0, 100-|deviation|/spread*50). Final = mean(all param scores)"`.

---

## PlantUML Code

```plantuml
@startuml
actor Analyst
participant "Model Page" as ModelPage
participant "auth_helpers" as Auth
participant "db_helpers" as DBH
database "dbo.\nMachineTagValue" as MTV
database "model_schema.\nmachine_configuration" as MC
database "model_schema.\nanalysis_results_[MACHINE]" as AR
actor "Mistral AI" as Mistral <<External System>>

== Initial Page Load ==
Analyst -> ModelPage: Navigate to Realtime page
ModelPage -> Auth: ensure_page_authentication('model_page')
Auth --> ModelPage: Access granted
ModelPage -> DBH: get_all_configurations() {cached 300s}
DBH -> MC: Query active configs
MC --> DBH: config list
ModelPage --> Analyst: Show config dropdown

== Configuration Selection ==
Analyst -> ModelPage: Select configuration
ModelPage -> DBH: load_latest_analysis(configId) {cached 600s}
DBH -> AR: Query reference datasheet
AR --> DBH: Min, Max, Mean, StdDev
ModelPage -> DBH: get_machine_status(machineCode) {cached 10s}
DBH -> MTV: Query LineSpeed
MTV --> DBH: Working/Standby
ModelPage --> Analyst: Show metrics + recipe cards

== Monitoring Loop (Fragment A — fetch + compute) ==
loop Every 1 second (@st.fragment A)
  ModelPage -> DBH: load_current_values(machineCode, params)
  DBH -> MTV: Query latest values by OpcNodeIds
  MTV --> DBH: current values
  ModelPage -> ModelPage: Compare each value vs Min/Max
  note right of ModelPage: Per param: target=(min+max)/2,\nspread=(max-min)/2,\nscore=max(0, 100-|deviation|/spread*50)\nFinal = mean(all param scores)
  ModelPage -> ModelPage: Compute quality probability
  ModelPage -> ModelPage: Store merged_readings\nin st.session_state
end

== Monitoring Loop (Fragment B — render + alerts) ==
loop Every 1 second (@st.fragment B)
  ModelPage -> ModelPage: Read merged_readings\nfrom session_state
  ModelPage -> ModelPage: Render color-coded cards
  opt Parameter out of range
    ModelPage -> ModelPage: Show violation badges
  end
  opt quality < 50% or manual click
    ModelPage -> DBH: call_mistral_ai(outOfSpecParams, context)
    DBH -> Mistral: POST /v1/chat/completions
    Mistral --> DBH: root cause analysis
    DBH --> ModelPage: rootCause, actions, preventions
    ModelPage --> Analyst: Display Mistral analysis dialog
  end
end
  opt quality < 50%
    ModelPage -> DBH: call_mistral_ai(outOfSpecParams, context)
    DBH -> Mistral: POST /v1/chat/completions
    Mistral --> DBH: root cause analysis
    DBH --> ModelPage: rootCause, actions, preventions
    ModelPage --> Analyst: Display Mistral analysis dialog
  end
end

== Traceability Charts ==
Analyst -> ModelPage: Expand charts section
ModelPage -> DBH: get_sensor_trace(machineCode, params) {cached 60s}
DBH -> MTV: Query recent history by OpcNodeIds
MTV --> DBH: time-series data
ModelPage -> ModelPage: Render Plotly chart
ModelPage --> Analyst: Show 3-sec sliding + full timeline charts

@enduml
```
