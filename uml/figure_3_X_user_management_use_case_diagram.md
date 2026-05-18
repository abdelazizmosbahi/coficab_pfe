# Figure 3.X — User Management Use Case Diagram

**Location:** Chapter 3 — Conception / §3.2.1.6  
**Type:** UML Use Case Diagram  

---

## Purpose

Administration subsystem. The Analyst manages operator accounts: views the user list, approves or declines registrations, manages page-level permissions, and deletes accounts.

---

## Actors

| Actor | Description |
|-------|-------------|
| **Analyst** | System administrator with full control over user accounts. Must be authenticated. |
| **Operator** | End user whose account is managed by the Analyst. Can register but requires approval for activation. |

---

## Use Cases

| # | Use Case | Description |
|---|----------|-------------|
| UC1 | View All Users | Display a dataframe of all registered users with UserId, Role, IsActive, ApprovalStatus, CreatedAt, LastLoginAt, and PagePermissions. |
| UC2 | Approve Operator Registration | Set an operator's ApprovalStatus from "pending" to "approved", enabling login access. |
| UC3 | Decline Operator Registration | Set an operator's ApprovalStatus to "declined" and deactivate the account. |
| UC4 | Manage Page Permissions | Configure page-level access for operators: grant full access or select individual pages (configuration_page, analysis_page). |
| UC5 | Delete User | Permanently remove a user record from the `model_schema.users` table. |

---

## Relationships

No `<<include>>` or `<<extend>>` relationships among administration use cases. Authentication is a system-level precondition.

---

## Notes for Diagram Generation

- **2 actors**: Analyst and Operator outside the system boundary.
- System boundary: **"User Management"**.
- Analyst connects to all five use cases.
- Operator connects to UC2 and UC3 to represent the registration approval lifecycle.

---

## PlantUML Code

```plantuml
@startuml
left to right direction

actor "Analyst" as Analyst
actor "Operator" as Operator

usecase (View All Users) as UC1
usecase (Approve Operator\nRegistration) as UC2
usecase (Decline Operator\nRegistration) as UC3
usecase (Manage Page\nPermissions) as UC4
usecase (Delete User) as UC5

Analyst --> UC1
Analyst --> UC2
Analyst --> UC3
Analyst --> UC4
Analyst --> UC5

Operator --> UC2
Operator --> UC3

rectangle "User Management" {
  UC1
  UC2
  UC3
  UC4
  UC5
}

@enduml
```
