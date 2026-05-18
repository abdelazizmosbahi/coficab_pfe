# Figure 3.X (3.2.4.7) — Delete User Account Activity Diagram

**Location:** Chapter 3 — Conception / §3.2.4.7 Delete User Account (NEW — from Delete User Feature)  
**Type:** UML Activity Diagram  

---

## Purpose

Model the workflow for permanently deleting a user account from the Admin Panel. The deletion is immediate with no confirmation dialog. The user record is hard-deleted from the database.

---

## Swimlanes

| Lane | Responsible For |
|------|----------------|
| **Analyst** | Navigating the Admin Panel, clicking the Delete button |
| **System** | Authentication check, user query, database deletion, UI feedback |

---

## Actions & Flow

```
[Start] → Analyst navigates to Admin Panel
          ↓
    System: ensure_page_authentication('admin_page')
          ↓
    System: is_current_user_analyst()
          ↓
         [Decision: Is Analyst?]
          ↓                    ↓
       [Yes]                [No]
          ↓                    ↓
    System loads all
    users via get_all_users()
          ↓
    System displays
    All Users dataframe
          ↓
    System displays expandable sections
    for each user
          ↓
    Analyst expands the target user's section
          ↓
    System shows user metadata and actions:
    • User ID, Status, Active flag
    • "Delete" button
          ↓
    Analyst clicks "🗑️ Delete" button
    (No confirmation dialog — immediate action)
          ↓
    System calls delete_user(operator_id)
          ↓
    System executes DELETE FROM [model_schema].[users]
    WHERE UserId = :uid  (within transaction)
          ↓
         [Decision: Database result?]
          ↓                    ↓               ↓
    [Rowcount = 1]      [Rowcount = 0]    [Exception]
    (User found and     (User not found)  (DB error)
     deleted)                 ↓               ↓
          ↓             System returns     Transaction
    System returns      (False, "No user   auto-rollback
    (True, "User        found with User          ↓
    has been            ID '...'.")        System returns
    deleted.")               ↓             (False, "Error
          ↓             System calls       deleting user:")
    System stores       st.error(msg)           ↓
    user_deleted_toast       ↓             System calls
    = True in           [End]              st.error(msg)
    session_state                                  ↓
          ↓                                  [End]
    System calls st.rerun()
          ↓
    [On rerun:]
    Pops user_deleted_toast flag
          ↓
    System displays
    st.toast("User deleted successfully!",
             icon="🗑️")
          ↓
    System refreshes user list
    — deleted user no longer appears
          ↓
       [End]
```

---

## Decision Nodes

| # | Decision | Branches | Description |
|---|----------|----------|-------------|
| D1 | Is Analyst? | [Yes] / [No] | Role check — only Analysts can access Admin Panel |
| D2 | Database result? | [Rowcount = 1] / [Rowcount = 0] / [Exception] | Three possible outcomes of DELETE query |

---

## Database Outcomes Detail

| Outcome | Meaning | Transaction | UI Feedback |
|---------|---------|-------------|-------------|
| Rowcount = 1 | User found and deleted | Committed | Toast: "User deleted successfully!" + page refresh |
| Rowcount = 0 | No matching UserId | Committed (no-op) | Error: "No user found with User ID '...'" |
| Exception | Database error (constraint, connection, etc.) | Rolled back | Error: "Error deleting user: ..." |

---

## Authentication Emphasis

- **Double authentication gate:**
  1. `ensure_page_authentication('admin_page')` — verifies valid session
  2. `is_current_user_analyst()` — verifies Analyst role. If `False`, execution stops with `st.stop()` and the Delete button is never rendered.
- **Target:** Any user can be deleted by an Analyst (the sole role).
- **No re-authentication required** for the delete action — the existing session is sufficient.
- **No cascading effects:** Because no foreign keys reference `model_schema.users.UserId`, deleting a user has no side effects on other tables (machine_configurations, analysis_results, etc.).

---

## Notes for Diagram Generation

- Use two swimlanes: **Analyst** (left) and **System** (right).
- Show the double authentication gate at the top: first `ensure_page_authentication()`, then the D1 `[Is Analyst?]` decision.
- Use `opt` to show the three database outcomes as branches from D2.
- Show `st.rerun()` as an action that triggers the post-delete refresh.
- Add a prominent note: `"No confirmation dialog — deletion is immediate and irreversible."`
- Add another note: `"Hard-delete (not soft-delete). The row is permanently removed. No foreign key cascading effects."`
- The error paths (rowcount=0 and exception) can be merged into a single `st.error(msg)` action if desired.

---

## PlantUML Code

```plantuml
@startuml
|Analyst|
start
:navigate to Admin Panel;

|System|
:ensure_page_authentication('admin_page');
:is_current_user_analyst();
if (Is Analyst?) then (yes)
  :get_all_users()\nload all user records;
  :display All Users dataframe;
  :display expandable section\nfor each user;
  |Analyst|
  :expand target user's section;
  |System|
  :show user metadata;
  |Analyst|
  :click "Delete" button\n(no confirmation);

  |System|
  :call delete_user(userId);
  :BEGIN TRANSACTION;
  :DELETE FROM model_schema.users\nWHERE UserId = :uid;

  if (Database result?) then (rowcount = 1)
    :COMMIT;
    :set user_deleted_toast = True;
    :st.rerun();
    :display toast\n"User deleted successfully!";
    :refresh user list\n(deleted user removed);
    stop
  else (rowcount = 0)
    :COMMIT (no-op);
    :display error\n"No user found";
    stop
  else (exception)
    :ROLLBACK;
    :display error\n"Error deleting user";
    stop
  endif
else (no)
  :display "Access denied.\nOnly Analysts can view this page.";
  :st.stop();
  stop
endif
@enduml
```
