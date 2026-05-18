# Figure 2.1 — General Use Case Diagram

**Location:** Chapter 2 — Requirements / §2.5 Use Case Diagrams  
**Type:** UML Use Case Diagram  

---

## Purpose

High-level overview of the Cable Manufacturing AI system showing the two user roles and their interactions with the primary system functionalities. Authentication is a prerequisite for all operations.

---

## Actors

| Actor | Description |
|-------|-------------|
| **Analyst** | Full-access user. Manages configurations, monitors production, generates datasheets, performs root cause analysis, and administers user accounts. |
| **Operator** | Restricted-access user. Monitors live production parameters, detects out-of-spec conditions, views traceability charts, and triggers root cause analysis. |

---

## Use Cases

| # | Use Case | Description |
|---|----------|-------------|
| UC1 | Authenticate | Login with User ID and password. System issues HMAC-signed session token. Registration creates pending Operator account requiring Analyst approval. |
| UC2 | Manage Configurations | Create, view, edit, and delete machine configurations with monitoring and recipe parameters. |
| UC3 | Monitor Production | Select a configuration, view live parameter values with 1-second refresh, compare against specification ranges, and compute quality probability. |
| UC4 | Generate Datasheet | Multi-step workflow: select machine, recipe parameters, production runs, then compute statistical reference datasheet (Min, Optimal, Max, Mean, StdDev). |
| UC5 | Analyze Root Cause | Trigger Mistral AI analysis (auto-triggered when quality < 50% or manually) to receive natural-language root cause identification and corrective actions. |
| UC6 | Manage Users | View registered users, approve or decline operator registrations, manage page-level permissions, and delete user accounts. |

---

## Relationships

### `<<extend>>`

| Source | Target | Condition |
|--------|--------|-----------|
| UC3 Monitor Production | UC5 Analyze Root Cause | `[quality probability < 50%]` |

---

## Notes for Diagram Generation

- **2 actors**: Analyst (full access) and Operator (restricted access) outside the system boundary.
- Draw **Analyst** connected to UC2, UC3, UC4, UC5, UC6.
- Draw **Operator** connected to UC3, UC5.
- Both actors connect to UC1 Authenticate.
- Draw a dashed `<<extend>>` arrow from UC3 to UC5 with guard `[quality probability < 50%]`.
- Group use cases into packages: **Authentication** (UC1), **Configuration** (UC2), **Monitoring** (UC3), **Analysis** (UC4–UC5), **Administration** (UC6).

---

## PlantUML Code

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Analyst" as Analyst
actor "Operator" as Operator

usecase (Authenticate) as UC1
usecase (Manage Configurations) as UC2
usecase (Monitor Production) as UC3
usecase (Generate Datasheet) as UC4
usecase (Analyze Root Cause) as UC5
usecase (Manage Users) as UC6

Analyst --> UC1
Analyst --> UC2
Analyst --> UC3
Analyst --> UC4
Analyst --> UC5
Analyst --> UC6

Operator --> UC1
Operator --> UC3
Operator --> UC5

UC3 --> UC5 : <<extend>>
note right of UC3 : [quality probability < 50%]

rectangle "Authentication" {
  UC1
}
rectangle "Configuration" {
  UC2
}
rectangle "Monitoring" {
  UC3
}
rectangle "Analysis" {
  UC4
  UC5
}
rectangle "Administration" {
  UC6
}
@enduml
```
