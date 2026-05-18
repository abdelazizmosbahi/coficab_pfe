# Figure 3.1 — System Use Case Diagram (Main)

**Location:** Chapter 3 — Conception / §3.2.1.1  
**Type:** UML Use Case Diagram  

---

## Purpose

Conception-level system diagram showing all major subsystems and how the two user roles (Analyst and Operator) interact with them. Each subsystem groups related functionalities.

---

## Actors

| Actor | Description |
|-------|-------------|
| **Analyst** | Full-access user. Can access all subsystems including configuration management, analysis, and user administration. |
| **Operator** | Restricted-access user. Can access authentication and real-time monitoring. Requires Analyst approval for account activation. |

---

## Use Cases

| # | Use Case | Subsystem | Description |
|---|----------|-----------|-------------|
| UC1 | Login | Authentication | Authenticate with credentials. Receive HMAC-signed session token. |
| UC2 | Register | Authentication | Create new Operator account (pending approval). |
| UC3 | Logout | Authentication | End session and clear all storage layers. |
| UC4 | Manage Configurations | Configuration | CRUD operations on machine monitoring configurations. |
| UC5 | Monitor Production | Monitoring | Real-time parameter monitoring with quality prediction. |
| UC6 | Generate Datasheet | Analysis | Statistical reference datasheet generation from production runs. |
| UC7 | Analyze Root Cause | Analysis | Mistral AI-powered root cause analysis (auto or manual trigger). |
| UC8 | Manage Users | Administration | User account management: approve, decline, set permissions, delete. |

---

## Relationships

### `<<extend>>`

| Source | Target | Condition |
|--------|--------|-----------|
| UC5 Monitor Production | UC7 Analyze Root Cause | `[quality probability < 50%]` |

---

## Notes for Diagram Generation

- **2 actors**: Analyst (full system access) and Operator (authentication + monitoring only).
- Draw dashed `<<extend>>` arrow from UC5 to UC7 with guard `[quality < 50%]`.
- Group use cases into subsystem rectangles: **Authentication**, **Configuration**, **Monitoring**, **Analysis**, **Administration**.

---

## PlantUML Code

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Analyst" as Analyst
actor "Operator" as Operator

usecase (Login) as UC1
usecase (Register) as UC2
usecase (Logout) as UC3
usecase (Manage Configurations) as UC4
usecase (Monitor Production) as UC5
usecase (Generate Datasheet) as UC6
usecase (Analyze Root Cause) as UC7
usecase (Manage Users) as UC8

Analyst --> UC1
Analyst --> UC2
Analyst --> UC3
Analyst --> UC4
Analyst --> UC5
Analyst --> UC6
Analyst --> UC7
Analyst --> UC8

Operator --> UC1
Operator --> UC3
Operator --> UC5
Operator --> UC7

UC5 --> UC7 : <<extend>>
note right of UC5 : [quality < 50%]

rectangle "Authentication" {
  UC1
  UC2
  UC3
}
rectangle "Configuration" {
  UC4
}
rectangle "Monitoring" {
  UC5
}
rectangle "Analysis" {
  UC6
  UC7
}
rectangle "Administration" {
  UC8
}
@enduml
```
