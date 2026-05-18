# Figure 2.3 — Analyst Use Case Diagram (Detailed)

**Location:** Chapter 2 — Requirements / §2.5 Use Case Diagrams  
**Type:** UML Use Case Diagram  

---

## Purpose

Detailed view of the Analyst's full capabilities across all system modules. The Analyst has unrestricted access to every feature of the system.

---

## Actors

| Actor | Description |
|-------|-------------|
| **Analyst** | Full-access user responsible for configuring machines, monitoring production, generating datasheets, analyzing root causes, and managing operator accounts. |

---

## Use Cases

| # | Use Case | Description |
|---|----------|-------------|
| UC1 | Authenticate | Login with PBKDF2 credentials. HMAC-signed 7-day session token with three-layer persistence. |
| UC2 | Manage Configurations | CRUD operations on machine configurations: create with monitoring and recipe parameters, view, edit, and delete. |
| UC3 | Select Configuration | Choose a saved configuration from the dropdown to begin monitoring. |
| UC4 | View Live Parameters | Real-time display of machine parameter values with 1-second auto-refresh from MachineTagValue. |
| UC5 | View Specification Ranges | Display Min/Optimal/Max/Mean/StdDev from the latest reference datasheet per parameter. |
| UC6 | View Traceability Charts | Visualize parameter trends with 3-second sliding window and full timeline views. |
| UC7 | Compare Parameters | Overlay two parameters on a single chart for correlation analysis. |
| UC8 | Compute Quality Probability | Rule-based quality score computed from parameter deviation magnitudes. |
| UC9 | Generate Reference Datasheet | Statistical analysis: select machine, recipe parameters, production runs, collect labeled samples, compute Min/Optimal/Max/Mean/StdDev. |
| UC10 | View Analysis History | Browse previously generated datasheets with preview. |
| UC11 | Export Datasheet CSV | Download generated datasheet as a CSV file. |
| UC12 | Analyze Root Cause | Trigger Mistral AI analysis (auto when quality < 50% or manual) to receive root cause, corrective actions, and preventive measures. |
| UC13 | View All Users | Display complete user table with role, status, activity, and permissions. |
| UC14 | Approve or Decline Operator | Review and approve or decline pending operator registration requests. |
| UC15 | Manage Page Permissions | Grant or revoke page-level access for operators (configuration, analysis pages). |
| UC16 | Delete User | Permanently remove a user account from the system. |

---

## Relationships

### `<<extend>>`

| Source | Target | Condition |
|--------|--------|-----------|
| UC4 View Live Parameters | UC8 Compute Quality Probability | `[values received]` |
| UC8 Compute Quality Probability | UC12 Analyze Root Cause | `[quality < 50%]` |
| UC4 View Live Parameters | UC6 View Traceability Charts | `[charts section expanded]` |
| UC6 View Traceability Charts | UC7 Compare Parameters | `[second parameter selected]` |

---

## Notes for Diagram Generation

- **1 actor**: Analyst connected to all use cases.
- No `<<include>>` relationships — authentication is a system-level precondition.
- Draw `<<extend>>` dashed arrows from extension source to target with guard conditions.
- Group by subsystem: **Authentication**, **Configuration**, **Monitoring**, **Analysis**, **Administration**.

---

## PlantUML Code

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Analyst" as Analyst

usecase (Authenticate) as UC1
usecase (Manage Configurations) as UC2
usecase (Select Configuration) as UC3
usecase (View Live Parameters) as UC4
usecase (View Specification\nRanges) as UC5
usecase (View Traceability\nCharts) as UC6
usecase (Compare Parameters) as UC7
usecase (Compute Quality\nProbability) as UC8
usecase (Generate Reference\nDatasheet) as UC9
usecase (View Analysis\nHistory) as UC10
usecase (Export Datasheet\nCSV) as UC11
usecase (Analyze Root Cause) as UC12
usecase (View All Users) as UC13
usecase (Approve or Decline\nOperator) as UC14
usecase (Manage Page\nPermissions) as UC15
usecase (Delete User) as UC16

Analyst --> UC1
Analyst --> UC2
Analyst --> UC3
Analyst --> UC4
Analyst --> UC5
Analyst --> UC6
Analyst --> UC7
Analyst --> UC9
Analyst --> UC10
Analyst --> UC11
Analyst --> UC12
Analyst --> UC13
Analyst --> UC14
Analyst --> UC15
Analyst --> UC16

UC4 --> UC8 : <<extend>>
note right of UC4 : [values received]
UC8 --> UC12 : <<extend>>
note right of UC8 : [quality < 50%]
UC4 --> UC6 : <<extend>>
note right of UC4 : [charts expanded]
UC6 --> UC7 : <<extend>>
note right of UC6 : [second param selected]

rectangle "Authentication" { UC1 }
rectangle "Configuration" { UC2 }
rectangle "Monitoring" { UC3 UC4 UC5 UC6 UC7 UC8 }
rectangle "Analysis" { UC9 UC10 UC11 UC12 }
rectangle "Administration" { UC13 UC14 UC15 UC16 }
@enduml
```
