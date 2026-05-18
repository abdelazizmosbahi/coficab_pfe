# Figure 3.4 — Analysis & Datasheet Generation Use Case Diagram

**Location:** Chapter 3 — Conception / §3.2.1.4 Analysis & Datasheet Generation  
**Type:** UML Use Case Diagram  

---

## Purpose

Detail the analysis subsystem where the Analyst generates statistical reference datasheets from historical production runs. The workflow follows a sequential six-step process.

---

## Actors

| Actor | Description |
|-------|-------------|
| **Analyst** | Sole user of the analysis subsystem. Generates reference datasheets, views history, and exports data. Must be authenticated. |

---

## Use Cases

| # | Use Case | Description |
|---|----------|-------------|
| UC1 | Select Machine | Choose a production machine from the dropdown to analyze its historical data. |
| UC2 | Select Recipe Parameters | Choose OpcNodeIds that define the recipe for filtering production runs. |
| UC3 | Load Production Runs | System retrieves the last 10 production runs for the selected machine from the `productionrun` table. |
| UC4 | Discover Run Parameters | System identifies all unique OpcNodeIds recorded during the selected run's time window. |
| UC5 | Select Sample Runs | Choose 1–10 production runs for statistical sample collection. |
| UC6 | Generate Reference Datasheet | Collect up to 5,000 samples per parameter per run, compute Min/Optimal/Max/Mean/StdDev, correlate with quality labels (IsOk), and save to `parameter_reference_datasheet`. |
| UC7 | View Analysis History | Browse previously generated datasheets with statistical summaries. |
| UC8 | Export Datasheet CSV | Download a generated datasheet as a CSV file. |

---

## Table 3.3 — Generate Datasheet — Use Case Textual Description

| Element | Description |
|---------|-------------|
| **Use Case Name** | Generate Datasheet |
| **Actor** | Analyst |
| **Description** | Analyst selects a machine, picks recipe parameters, chooses production runs, and generates a statistical reference datasheet. |
| **Precondition** | Analyst is authenticated. Machine has production runs with recorded data. |
| **Postcondition** | Reference datasheet is saved to `parameter_reference_datasheet` table. Analysis history is stored in `analysis_results_[MACHINE]` table. |
| **Main Flow** | 1. Analyst navigates to Analysis page. 2. System displays step-by-step workflow. 3. Analyst selects machine. 4. Analyst selects recipe parameters. 5. System loads recent production runs. 6. Analyst selects a run. 7. System discovers parameters in run's time window. 8. Analyst selects sample runs. 9. System collects samples. 10. System computes statistics. 11. System correlates with quality labels. 12. System saves datasheet. |
| **Alternative Flow** | If ProductionRunQuality has no matching records, all samples are labeled IsOk=0. If no production runs exist, system displays informational message. |

---

## Relationships

No `<<include>>` or `<<extend>>` relationships. The workflow is a sequential user-driven process. Authentication is a system-level precondition.

---

## Notes for Diagram Generation

- **1 actor**: Analyst outside the system boundary.
- System boundary: **"Analysis & Datasheet Generation"**.
- Group UC1–UC6 as the datasheet generation workflow, UC7 and UC8 as post-generation features.
- The sequential flow can be represented by ordering the use cases left to right or top to bottom.

---

## PlantUML Code

```plantuml
@startuml
left to right direction

actor "Analyst" as Analyst

usecase (Select Machine) as UC1
usecase (Select Recipe\nParameters) as UC2
usecase (Load Production\nRuns) as UC3
usecase (Discover Run\nParameters) as UC4
usecase (Select Sample\nRuns) as UC5
usecase (Generate Reference\nDatasheet) as UC6
usecase (View Analysis\nHistory) as UC7
usecase (Export Datasheet\nCSV) as UC8

Analyst --> UC1
Analyst --> UC2
Analyst --> UC3
Analyst --> UC4
Analyst --> UC5
Analyst --> UC6
Analyst --> UC7
Analyst --> UC8

rectangle "Datasheet Generation Workflow" {
  UC1
  UC2
  UC3
  UC4
  UC5
  UC6
}
rectangle "Post-Generation" {
  UC7
  UC8
}

@enduml
```
