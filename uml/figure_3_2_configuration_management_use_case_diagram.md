# Figure 3.2 — Configuration Management Use Case Diagram

**Location:** Chapter 3 — Conception / §3.2.1.2 Configuration Management  
**Type:** UML Use Case Diagram  

---

## Purpose

Detail the configuration management subsystem. The Analyst creates, reads, updates, and deletes machine configurations by selecting monitoring parameters and designating recipe parameters.

---

## Actors

| Actor | Description |
|-------|-------------|
| **Analyst** | Sole user of the configuration management subsystem. Performs CRUD operations on machine configurations. Must be authenticated. |

---

## Use Cases

| # | Use Case | Description |
|---|----------|-------------|
| UC1 | Create Configuration | Define a new machine configuration: name, machine selection, monitoring parameters, recipe parameters, and description. Validates that recipe parameters are a subset of monitoring parameters. |
| UC2 | View Configurations | Browse all saved configurations by machine, with expandable detail view showing parameters. |
| UC3 | Edit Configuration | Modify an existing configuration: rename, add or remove monitoring or recipe parameters, update description. |
| UC4 | Delete Configuration | Remove a configuration with confirmation dialog to prevent accidental deletion. |

---

## Table 3.1 — Configure Machine — Use Case Textual Description

| Element | Description |
|---------|-------------|
| **Use Case Name** | Manage Configurations |
| **Actor** | Analyst |
| **Description** | Analyst creates or modifies machine configurations by selecting monitoring parameters and designating recipe parameters. |
| **Precondition** | Analyst is authenticated. At least one machine exists in the system. |
| **Postcondition** | Configuration is persisted to `model_schema.machine_configuration` table. |
| **Main Flow** | 1. Analyst navigates to Configuration page. 2. System displays machine status table. 3. Analyst fills or edits configuration form. 4. System validates inputs. 5. System saves configuration. 6. System confirms success. |
| **Alternative Flow** | If configuration name already exists for the machine, system displays error. If recipe parameters are not a subset of monitoring parameters, system displays validation error. If database deadlock occurs, system retries with exponential backoff. |

---

## Relationships

No `<<include>>` or `<<extend>>` relationships among configuration use cases. Authentication is a system-level precondition.

---

## Notes for Diagram Generation

- **1 actor**: Analyst outside the system boundary.
- System boundary: **"Configuration Management"** containing Create, View, Edit, and Delete Configuration.
- No relationship arrows between use cases — each is an independent operation.

---

## PlantUML Code

```plantuml
@startuml
left to right direction

actor "Analyst" as Analyst

usecase (Create Configuration) as UC1
usecase (View Configurations) as UC2
usecase (Edit Configuration) as UC3
usecase (Delete Configuration) as UC4

Analyst --> UC1
Analyst --> UC2
Analyst --> UC3
Analyst --> UC4

rectangle "Configuration Management" {
  UC1
  UC2
  UC3
  UC4
}

@enduml
```
