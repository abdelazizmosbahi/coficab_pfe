# User Administration — Low-Level Use Case Decomposition

## Scope

This diagram decomposes the **User Administration** functional area, accessible exclusively to the Analyst via the Admin page. The Analyst manages operator accounts including registrations, page-level permissions, and account status. Source: `admin_page.py` (344 lines) + `auth_helpers.py` (970 lines).

## Mapping to General Diagram

| General UC | Title | Sub-Diagram UC |
|---|---|---|
| UC15 | Manage Operator Registrations | UCU2 View Pending Registrations |
| UC16 | Manage Page Permissions | UCU3 Manage Page Permissions |
| UC17 | Manage User Accounts | UCU4 Manage Account Status |
| UC18 | View All Users | UCU1 View All Users |

*Note: UCU2 (formerly part of UC15) is renamed to "View Pending Registrations" to reflect that the base behavior is viewing — approving and declining are conditional extensions. UCU4 (formerly UC17) is renamed to "Manage Account Status" to clarify that it encompasses activate, disable, and delete operations.*

## Low-Level Use Cases

### UCU5 — Query All Users
*`<<include>>` by UCU1 (mandatory)*

| | |
|---|---|
| **Goal** | Retrieve all registered users from `model_schema.users` |
| **Implementation** | `get_all_users()` — `SELECT UserId, Role, ApprovalStatus, IsActive, CreatedAt, LastLoginAt FROM model_schema.users ORDER BY CreatedAt DESC` (`auth_helpers.py:702-728`) |
| **Output** | List of dicts: `{user_id, role, approval_status, is_active, created_at, last_login_at}` |

### UCU6 — Query Pending Operators
*`<<include>>` by UCU2 (mandatory)*

| | |
|---|---|
| **Goal** | Retrieve all operator registrations with `ApprovalStatus='pending'` |
| **Implementation** | `get_pending_operators()` — `SELECT UserId, CreatedAt FROM model_schema.users WHERE Role='operator' AND ApprovalStatus='pending'` (`auth_helpers.py:680-700`) |
| **Output** | List of `{user_id, created_at}` dicts |

### UCU7 — Approve Operator
*`<<extend>>` UCU2 (conditional — Analyst clicks ✅ Approve)*

| | |
|---|---|
| **Goal** | Set an operator's `ApprovalStatus` to `'approved'`, enabling login |
| **Implementation** | `approve_operator(uid)` — `UPDATE model_schema.users SET ApprovalStatus='approved' WHERE UserId=:uid` (`auth_helpers.py:730-746`) |
| **Post-action** | `st.toast("User approved successfully!", icon="✅")` + `st.rerun()` |
| **Precondition** | Operator must have `ApprovalStatus='pending'` |

### UCU8 — Decline Operator
*`<<extend>>` UCU2 (conditional — Analyst clicks ❌ Decline)*

| | |
|---|---|
| **Goal** | Reject an operator's registration: set status to `'declined'` and deactivate |
| **Implementation** | `decline_operator(uid)` — `UPDATE model_schema.users SET ApprovalStatus='declined', IsActive=0 WHERE UserId=:uid` (`auth_helpers.py:748-764`) |
| **Post-action** | `st.toast("User declined!", icon="⚠️")` + `st.rerun()` |
| **Result** | Operator cannot log in. They may re-register (the system treats re-registration of a declined user as an update). |

### UCU9 — Load Permissions from DB
*`<<include>>` by UCU1, UCU3 (mandatory for both)*

| | |
|---|---|
| **Goal** | Read the `PagePermissions` JSON column for a specified user |
| **Implementation** | `get_user_page_permissions(uid)` — `SELECT PagePermissions FROM model_schema.users WHERE UserId=:uid`. Returns `None` (full access / analyst) or a `list[str]` of allowed page IDs (`auth_helpers.py:812-838`) |
| **Used By** | UCU1: to display the "Page Access" summary column in the user table. UCU3: to pre-populate the permission checkboxes in the expander. |
| **Reuse** | This is the ONLY shared low-level use case in User Administration — called by two different top-level use cases. |

### UCU10 — Save Permissions to DB
*`<<include>>` by UCU3 (mandatory)*

| | |
|---|---|
| **Goal** | Persist the Analyst's permission configuration for an operator |
| **Implementation** | `set_user_page_permissions(uid, permissions)` — `UPDATE model_schema.users SET PagePermissions=:perms WHERE UserId=:uid`. Saves `NULL` (full access) or a JSON list `["configuration_page", "analysis_page"]` (`auth_helpers.py:840-867`) |
| **UI Flow** | Analyst checks "Grant Full Access" (stores `NULL`) or toggles individual page checkboxes (stores JSON list). The `PAGE_REGISTRY` maps `{"configuration_page": "Configuration (machine config)", "analysis_page": "Analysis (datasheets)"}`. |

### UCU11 — Toggle Active Status
*`<<extend>>` UCU4 (conditional — Analyst clicks Activate or Disable button)*

| | |
|---|---|
| **Goal** | Set a user's `IsActive` flag to 1 (enable) or 0 (disable) |
| **Implementation** | `set_user_active_status(uid, is_active)` — `UPDATE model_schema.users SET IsActive=:active WHERE UserId=:uid` (`auth_helpers.py:766-783`) |
| **Button Label** | Dynamic: shows "🚫 Disable" when user is active, "✅ Activate" when user is disabled |
| **Effect** | Disabled users cannot log in (checked at `authenticate_user()` line `auth_helpers.py:551`: `if not user["IsActive"]: return False, "This account is disabled."`) |

### UCU12 — Delete Account Permanently
*`<<extend>>` UCU4 (conditional — Analyst clicks Delete button)*

| | |
|---|---|
| **Goal** | Permanently remove a user from the system |
| **Implementation** | `delete_user(uid)` — `DELETE FROM model_schema.users WHERE UserId=:uid` (`auth_helpers.py:785-798`) |
| **Irreversible** | No confirmation dialog in the UI. The Analyst must be deliberate. There is no undo. |
| **Post-action** | `st.toast("User deleted successfully!", icon="🗑️")` + `st.rerun()` |

## Relationship Justification

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCU1 | UCU5 | `<<include>>` | View All Users REQUIRES querying the DB for all users |
| UCU1 | UCU9 | `<<include>>` | View All Users REQUIRES loading each user's page permissions to display the "Page Access" column |
| UCU2 | UCU6 | `<<include>>` | View Pending Registrations REQUIRES querying pending operators from DB |
| UCU3 | UCU9 | `<<include>>` | Manage Permissions REQUIRES loading current permissions to pre-populate the form |
| UCU3 | UCU10 | `<<include>>` | Manage Permissions REQUIRES saving the updated permissions to DB |
| UCU7 | UCU2 | `<<extend>>` | **Approve is a conditional action** within the "View Pending Registrations" base use case. The base (viewing the list) is complete without approving anyone. The extension fires only when the Analyst clicks ✅ on a specific operator. |
| UCU8 | UCU2 | `<<extend>>` | **Decline is also conditional** — same logic as UCU7, but an alternative outcome. Both UCU7 and UCU8 are extensions of the same base (UCU2), selected by which button the Analyst clicks. |
| UCU11 | UCU4 | `<<extend>>` | **Toggle Active Status is conditional.** The analyst can view the account management panel without toggling any status. The Activate/Disable button is an optional action within the panel. |
| UCU12 | UCU4 | `<<extend>>` | **Delete is conditional.** Same pattern — viewing the panel is the base; deletion is an optional, irreversible action. |

### Shared Behavior Analysis

UCU9 (Load Permissions from DB) is the only low-level use case shared by multiple top-level use cases (UCU1 and UCU3). All other low-level use cases are exclusive to their parent.

### Page Layout Context

The Admin page (`admin_page.py`) composes these independent use cases on a single dashboard:

```
┌─────────────────────────────────────────────┐
│           Admin Dashboard                   │
├─────────────────────────────────────────────┤
│ UCU2: Pending Approvals section             │
│   ├─ Operator 1:  [✅ Approve] [❌ Decline]  │
│   └─ Operator 2:  [✅ Approve] [❌ Decline]  │
├─────────────────────────────────────────────┤
│ UCU1: All Users table                       │
│ ┌─────────────────────────────────────────┐ │
│ │ User ID │ Role │ Active │ Page Access  │ │
│ ├─────────────────────────────────────────┤ │
│ │ admin   │analyst│  ✅   │ All pages    │ │
│ │ op1     │operat.│  ✅   │ Default      │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ UCU3 + UCU4: Per-operator expanders         │
│   └─ ✏️ op1                                 │
│       ├─ Permissions: [ ] Full Access       │
│       │    [ ] Configuration                 │
│       │    [ ] Analysis                      │
│       │    [💾 Save Permissions]             │
│       ├─ [🚫 Disable] [🗑️ Delete]           │
└─────────────────────────────────────────────┘
```

This is a **UI composition** pattern — co-located but functionally independent.

## Authentication Prerequisite

All top-level use cases in this diagram `<<include>>` the **Authenticate** use case (UCAUTH) as a mandatory prerequisite. The Analyst must be authenticated before accessing any administration functionality. The system enforces this via a two-layer check: first, `ensure_page_authentication()` at the top of `admin_page.py:168` verifies a valid session; second, `is_current_user_analyst()` at `admin_page.py:170` verifies the user has the `analyst` role. If either check fails, the user is redirected to the Authentication page or shown an error.

### Relationship Detail

| Source | Target | Type | Rationale |
|---|---|---|---|
| UCU1–UCU4 | UCAUTH | `<<include>>` | All user administration operations require authentication. Without a valid session, the Analyst cannot view the Admin page at all. Additionally, the role check (`is_current_user_analyst()`) ensures only Analyst-role users can perform these operations — operators are blocked even if authenticated. |

## Key Implementation Details

| Aspect | Detail |
|---|---|
| **Source Table** | `model_schema.users` |
| **User Columns** | UserId, PasswordHash, PasswordSalt, Role, ApprovalStatus, IsActive, PagePermissions, CreatedAt, LastLoginAt |
| **Page Registry** | `PAGE_REGISTRY = {"configuration_page": "Configuration", "analysis_page": "Analysis"}` |
| **Default Pages** | `_DEFAULT_PAGES = {"app.py", "model_page"}` — always accessible to operators |
| **Permission Storage** | `PagePermissions: NULL` = full access, JSON list = specific pages |
| **Access Check** | `check_page_access(page_id)` in `auth_helpers.py:869` |
| **Source File (Page)** | `cable_maintenance_ai/app/pages/admin_page.py` (344 lines) |
| **Source File (Auth)** | `cable_maintenance_ai/app/auth_helpers.py` (970 lines) |
