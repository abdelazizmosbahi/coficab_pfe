# Report Updates — Delete User Feature

> Copy the sections below into the appropriate locations in `UPDATED_COFICAB_PFE_REPORT.md`.

---

## Section 2.2 – User Profiles (Update Analyst row only)

In the Analyst role description, append ", **permanently delete operator accounts**" to the relevant sentence:

```
| **Analyst** | Quality engineers and data analysts responsible for managing the system. Analysts configure machines, select monitoring and recipe parameters, generate reference datasheets, train quality models, and investigate quality correlations. Additionally, Analysts serve as system administrators: they approve or decline operator registration requests, view all registered users, manage per-operator page-level access permissions via the Admin Panel, and permanently delete operator accounts. Analysts have unrestricted access to all system pages. |
```

---

## Section 2.3 – Functional Requirements (Append after FR42)

| ID | Requirement | Role |
|----|-------------|------|
| FR43 | Delete User: Analysts permanently delete operator accounts from the Admin Panel, removing the user record entirely from the database | Analyst |

---

## Section 2.5 – Use Case Diagrams (Update Analyst description)

**Analyst Use Case Diagram** (append to Figure 2.3 description):

```
In addition to all Operator use cases, Analysts have exclusive access to the Admin Panel for user management. This includes: reviewing pending operator registrations, approving or declining new accounts, listing all registered users with their metadata, managing per-operator page-level permissions through a checkbox-based interface with a "Grant Full Access" option, and permanently deleting operator accounts.
```

---

## Chapter 3 – Conception: Use Case Diagrams

### 3.2.1.6 Operator Account Management — Add New Use Case Table

**TABLE 3.Z – Delete Operator Account — Use Case Textual Description**

| Element | Description |
|---------|-------------|
| **Use Case Name** | Delete Operator Account |
| **Actor** | Analyst |
| **Description** | Analyst permanently removes an operator account from the database |
| **Precondition** | Analyst is authenticated. Target operator exists in the system. |
| **Postcondition** | Operator record is permanently deleted from `model_schema.users`. |
| **Main Flow** | 1. Analyst navigates to Admin Panel → "Manage Page Access" section. 2. System displays all operator users in expandable sections. 3. Analyst expands the target operator. 4. Analyst clicks the "🗑️ Delete" button. 5. System calls `delete_user(user_id)`. 6. System executes `DELETE FROM [model_schema].[users] WHERE UserId = :uid`. 7. System displays a success toast notification and reruns to refresh the list. |
| **Alternative Flow** | If the user ID does not exist, system returns `(False, "No user found")`. If a database error occurs, system displays an error message and does not delete any records. |

---

### 3.2.3 Sequence Diagrams — Add New

#### 3.2.3.8 Delete User — Sequence Diagram (NEW)

**Figure 3.X – Delete User Sequence Diagram**

**Flow:**
1. Analyst navigates to Admin Panel → "Manage Page Access" section
2. System displays all operator users in expandable sections, each with a "🗑️ Delete" button
3. Analyst expands an operator and clicks Delete
4. Admin Panel calls `delete_user(user_id)` from `auth_helpers.py`
5. `auth_helpers.py` executes `DELETE FROM [model_schema].[users] WHERE UserId = :uid` via a transactional connection
6. Database returns affected row count (1 if deleted, 0 if not found)
7. `auth_helpers.py` returns `(True, message)` or `(False, error_message)`
8. Admin Panel stores a `user_deleted_toast` flag in `st.session_state` and calls `st.rerun()`
9. UI displays `st.toast("User deleted successfully!", icon="🗑️")`
10. The page re-renders with the user removed from the list

---

### 3.2.4 Activity Diagrams — Add New

#### 3.2.4.7 Delete User Account — Activity Diagram (NEW)

**Figure 3.X – Delete User Account Activity Diagram**

**Flow:**
1. Analyst navigates to Admin Panel
2. System displays all operators in Manage Page Access section
3. Analyst expands an operator section
4. Analyst clicks "🗑️ Delete"
5. System calls `delete_user(user_id)`
6. [User exists in database] → System executes `DELETE` query → Record permanently removed → Success toast displayed → List refreshed via `st.rerun()`
7. [User not found] → System displays error: "No user found with User ID '...'"
8. [Database error] → System displays generic error message

---

## Chapter 4 – Realization: Implementation

### 4.2.6 Admin Panel (`admin_page.py` — 344 lines)

Add the following bullet point to the **Manage Page Access Section** list:

- **Delete User**: Each operator expandable section includes a "🗑️ Delete" button (`use_container_width=True`) in the rightmost column of a four-column layout (Save Permissions | gap | Disable/Activate | Delete). Clicking Delete immediately calls `delete_user(user_id)` — there is no confirmation dialog. On success, a toast notification (`st.toast("User deleted successfully!", icon="🗑️")`) is displayed and `st.rerun()` refreshes the user list. On failure, `st.error()` shows the error message.

### 4.2.7 Page Access Management System (`auth_helpers.py` — 970 lines)

Add the following entry to the function list (after `set_user_active_status`):

- **`delete_user(user_id)`** (lines 785–797): Permanently deletes a user record from `model_schema.users`. Executes a raw SQL `DELETE` statement within a transactional context (`get_engine().begin()`). Returns `(True, "User '...' has been deleted.")` on success, `(False, "No user found with User ID '...'.")` if the user does not exist, or `(False, "Error deleting user: ...")` on database errors. No cascading effects exist — no foreign key relationships in any other table reference `model_schema.users.UserId`.

### Database Schema — No Change

The delete user feature requires no schema modifications. The existing `model_schema.users` table structure is sufficient — deletion simply removes a row via its primary key (`UserId`).

---

## 4.3 User Interface — Update Figure 4.8 Description

Update the **Manage Page Access Section** bullet in the **Figure 4.8 – Admin Panel Interface Screenshot** description:

```
- Manage Page Access Section: Expandable panels for each operator containing:
  - User metadata (User ID, Status, Active flag)
  - "Grant Full Access" checkbox — enables all pages for the operator
  - Individual page checkboxes for Configuration and Analysis pages (disabled when full access is granted)
  - "Save Permissions" button with success/error feedback
  - "🚫 Disable" / "✅ Activate" toggle button to enable or disable the operator account
  - "🗑️ Delete" button to permanently remove the operator account from the system (no confirmation dialog; success toast shown after deletion)
```

---

## Conclusion — Update

Under **Results** (page 1181), append:

```
- Permanently deleting operator accounts from the Admin Panel interface
```

Under **Future perspectives** (page 1195), append:

```
- Adding confirmation dialogs before destructive actions such as user deletion
- Implementing soft-delete (IsActive flag) instead of hard-delete to preserve audit trails
```
