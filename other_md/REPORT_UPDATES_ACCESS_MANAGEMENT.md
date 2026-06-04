# Report Updates — Operator Page Access Management

> Copy the sections below into the appropriate locations in `UPDATED_COFICAB_PFE_REPORT.md`.

---

## Section 2.2 – User Profiles (Replace)

```
| Role | Description |
|------|-------------|
| **Operator** | Shop-floor personnel responsible for monitoring live production parameters. Operators view real-time data, detect out-of-spec conditions, and respond to alerts. They do not modify machine configurations or generate datasheets. Access to restricted pages (Configuration, Analysis, Admin) is granted explicitly by an Analyst on a per-user basis. New operator registrations require approval from an Analyst before the account becomes active. |
| **Analyst** | Quality engineers and data analysts responsible for managing the system. Analysts configure machines, select monitoring and recipe parameters, generate reference datasheets, train quality models, and investigate quality correlations. Additionally, Analysts serve as system administrators: they approve or decline operator registration requests, view all registered users, and manage per-operator page-level access permissions via the Admin Panel. Analysts have unrestricted access to all system pages. |
```

---

## Section 2.3 – Functional Requirements (Append before existing FR1–FR34)

Add the following new requirements after the existing FR34, renumbering as needed:

| ID | Requirement | Role |
|----|-------------|------|
| FR35 | Approve Operators: Analysts view pending operator registration requests and approve or decline them | Analyst |
| FR36 | List All Users: Analysts view all registered users with their role, approval status, active flag, page permissions, creation date, and last login | Analyst |
| FR37 | Manage Page Permissions: Analysts grant or revoke page-level access for each operator via checkboxes in the Admin Panel | Analyst |
| FR38 | Grant Full Access: Analysts enable a "Grant Full Access" toggle to give an operator access to all available pages at once | Analyst |
| FR39 | Select Individual Pages: Analysts individually check which restricted pages (Configuration, Analysis) each operator may access | Analyst |
| FR40 | Restrict Page Access: Operators without explicit permission for a restricted page receive an access-denied message and are blocked from viewing it | Analyst |
| FR41 | Role-Based Navigation: The navigation bar dynamically shows or hides links based on the user's role and page permissions | Both |
| FR42 | Default Page Access: All authenticated operators have access to the Home page and the Realtime Monitoring page by default, without requiring explicit permission | Both |

---

## Section 2.5 – Use Case Diagrams (Update Operator & Analyst descriptions)

**Operator Use Case Diagram** (append to Figure 2.2 description):

```
Operator capabilities are further governed by page-level permissions granted by Analysts. Operators can only access pages (Configuration, Analysis) for which they have been explicitly authorized via the Admin Panel. Unauthorized page access attempts result in a clear access-denied message.
```

**Analyst Use Case Diagram** (append to Figure 2.3 description):

```
In addition to all Operator use cases, Analysts have exclusive access to the Admin Panel for user management. This includes: reviewing pending operator registrations, approving or declining new accounts, listing all registered users with their metadata, and managing per-operator page-level permissions through a checkbox-based interface with a "Grant Full Access" option.
```

---

## Chapter 3 – Conception: Use Case Diagrams

### 3.2.1.6 Operator Account Management — Use Case Diagram (NEW)

**Figure 3.X – Operator Account Management Use Case Diagram**

**TABLE 3.X – Manage Operators — Use Case Textual Description**

| Element | Description |
|---------|-------------|
| **Use Case Name** | Manage Operators |
| **Actor** | Analyst |
| **Description** | Analyst reviews pending operator registrations and approves or declines them |
| **Precondition** | Analyst is authenticated. At least one operator registration exists with `ApprovalStatus = 'pending'`. |
| **Postcondition** | Operator's `ApprovalStatus` is updated to `'approved'` or `'declined'`. Declined operators are deactivated (`IsActive = 0`). |
| **Main Flow** | 1. Analyst navigates to Admin Panel. 2. System loads all pending operator registrations with registration timestamps. 3. Analyst reviews each pending operator. 4. Analyst clicks "Approve" or "Decline". 5. System updates the user record. 6. System refreshes the pending list. |
| **Alternative Flow** | If no pending registrations exist, system displays an informational message. If a database error occurs, system displays an error message. |

**TABLE 3.Y – Manage Page Permissions — Use Case Textual Description**

| Element | Description |
|---------|-------------|
| **Use Case Name** | Manage Page Permissions |
| **Actor** | Analyst |
| **Description** | Analyst grants or revokes page-level access permissions for each operator using a checkbox-based interface |
| **Precondition** | Analyst is authenticated. At least one operator user exists in the system. |
| **Postcondition** | Operator's `PagePermissions` column is updated with the selected page list (`NULL` for full access, JSON array for restricted access). |
| **Main Flow** | 1. Analyst navigates to Admin Panel → "Manage Page Access" section. 2. System displays all operator users in expandable sections. 3. Analyst expands a user. 4. Analyst selects "Grant Full Access" checkbox or individually checks desired pages (Configuration, Analysis). 5. Analyst clicks "Save Permissions". 6. System persists the permission changes to the database. 7. System confirms success. |
| **Alternative Flow** | If "Grant Full Access" is checked, individual page checkboxes are disabled. If the operator's `PagePermissions` is set to `NULL`, the operator has default access (Home + Realtime only). |

---

### 3.2.2 Class Diagram — Update User Entity

In **Figure 3.6 – Class Diagram — System Entities**, update the **User** entity as follows (additions in bold):

**User:**
- UserId (PK)
- PasswordHash, PasswordSalt
- CreatedAt, LastLoginAt
- IsActive
- **Role (NVARCHAR(20) — values: 'operator' | 'analyst')**
- **ApprovalStatus (NVARCHAR(20) — values: 'pending' | 'approved' | 'declined')**
- **PagePermissions (NVARCHAR(MAX) — NULL = default access, JSON array for explicit pages)**
- Methods: authenticate(), register()

---

### 3.2.3 Sequence Diagrams — Add New

#### 3.2.3.6 Operator Approval — Sequence Diagram (NEW)

**Figure 3.X – Operator Approval Sequence Diagram**

**Flow:**
1. Operator submits registration request on the Authentication page
2. System creates user record with `Role = 'operator'` and `ApprovalStatus = 'pending'`
3. Operator sees "Registration submitted. Awaiting approval." message
4. Analyst navigates to Admin Panel
5. Admin Panel calls `get_pending_operators()` from `auth_helpers.py`
6. `auth_helpers.py` queries `model_schema.users` for operators with `ApprovalStatus = 'pending'`
7. System displays pending registrations with timestamps
8. Analyst clicks "Approve" or "Decline"
9. System calls `approve_operator()` or `decline_operator()` which updates the user record
10. System confirms the action and refreshes the pending list

#### 3.2.3.7 Page Permission Management — Sequence Diagram (NEW)

**Figure 3.X – Page Permission Management Sequence Diagram**

**Flow:**
1. Analyst navigates to Admin Panel → "Manage Page Access" section
2. Admin Panel calls `get_all_users()` to retrieve all registered users
3. System displays each operator with their current page permissions
4. Analyst selects an operator from the expandable list
5. System calls `get_user_page_permissions()` to load the operator's current `PagePermissions`
6. Analyst modifies permissions (checks/unchecks pages or toggles "Grant Full Access")
7. Analyst clicks "Save Permissions"
8. System calls `set_user_page_permissions()` with the selected page list (or `NULL` for full access)
9. System updates the `PagePermissions` column in `model_schema.users`
10. System confirms the update and refreshes the interface

---

### 3.2.4 Activity Diagrams — Add New

#### 3.2.4.5 Operator Registration & Approval — Activity Diagram (NEW)

**Figure 3.X – Operator Registration & Approval Activity Diagram**

**Flow:**
1. New user navigates to Registration tab on Authentication page
2. User enters User ID and password
3. System checks if User ID already exists
4. [Exists] → System displays error → User retries
5. [New] → System creates user record with `Role = 'operator'` and `ApprovalStatus = 'pending'`
6. System displays "Registration submitted. Awaiting analyst approval."
7. Analyst logs in and navigates to Admin Panel
8. System loads pending operator registrations
9. Analyst reviews registration details
10. [Approve] → System sets `ApprovalStatus = 'approved'`
11. [Decline] → System sets `ApprovalStatus = 'declined'` and `IsActive = 0`
12. Operator can now log in (if approved)

#### 3.2.4.6 Page Access Control — Activity Diagram (NEW)

**Figure 3.X – Page Access Control Activity Diagram**

**Flow:**
1. User navigates to a Streamlit page
2. Page calls `ensure_page_authentication()`
3. System checks if user is authenticated
4. [Not authenticated] → Redirect to login page
5. [Authenticated] → System calls `check_page_access(page_id)`
6. [Role = 'analyst'] → Access granted (Analysts bypass all permission checks)
7. [Page is default (Home, Realtime)] → Access granted
8. [Page is restricted] → System queries operator's `PagePermissions`
9. [PagePermissions is NULL] → Access denied (no explicit permissions)
10. [Page ID is in PagePermissions list] → Access granted
11. [Page ID not in PagePermissions list] → Access denied; error message displayed

---

## Chapter 4 – Realization: Implementation

### 4.2.6 Admin Panel (`admin_page.py` — 241 lines)

The Admin Panel provides Analysts with user management and page-level permission control:

- **Pending Approvals Section**: Lists all operator registrations with `ApprovalStatus = 'pending'`. Each entry shows the User ID, registration timestamp, and Approve/Decline buttons. Approved operators gain the ability to log in; declined operators are automatically deactivated.
- **All Users Section**: Displays a dataframe of all registered users with columns: User ID, Role, Approval Status, Active flag, Page Access summary, Created date, and Last Login date. The Page Access column shows a human-readable summary (e.g., "All pages (analyst)", "Default (Realtime only)", or "Configuration, Analysis").
- **Manage Page Access Section**: For each operator, an expandable section provides:
  - A "Grant Full Access" checkbox — when checked, the operator can access all available pages (Configuration + Analysis + Realtime)
  - Individual checkboxes for each restricted page from `PAGE_REGISTRY` (`configuration_page` and `analysis_page`)
  - Checkboxes are automatically disabled when "Grant Full Access" is enabled
  - A "Save Permissions" button that persists changes via `set_user_page_permissions()`
- **Access Control**: The page calls `ensure_page_authentication()` and `is_current_user_analyst()` — non-Analyst users see an "Access denied" error and execution is stopped.
- **Styling**: COFICAB-themed custom CSS with navy gradients, orange accents, and Manrope/Space Grotesk fonts.

### 4.2.7 Page Access Management System (`auth_helpers.py` — 929 lines)

The authentication module was extended with a comprehensive page-level access control system:

- **Page Registry** (`PAGE_REGISTRY`): A dictionary mapping internal page identifiers to human-readable labels. Currently tracks `configuration_page` (Configuration) and `analysis_page` (Analysis) as restrictable pages. Pages not in this registry (Home `app.py`, Realtime `model_page`) are default-accessible to all authenticated operators.
- **`get_user_page_permissions(user_id)`**: Retrieves an operator's explicitly granted pages from the `PagePermissions` column. Returns `None` if no explicit permissions exist (default access only), or a list of allowed page identifiers.
- **`set_user_page_permissions(user_id, permissions)`**: Persists page permissions. Setting permissions to `None` grants only default pages; setting a list of page identifiers grants explicit access to those pages. Returns success status and a descriptive message.
- **`check_page_access(page_id)`**: Enforces page-level authorization. Rules: (1) Analysts always have access; (2) Default pages (`app.py`, `model_page`) are always accessible; (3) Restricted pages require the operator to have an explicit permission entry; (4) `NULL` PagePermissions means only default pages are accessible.
- **`ensure_page_authentication(current_page_path)`**: Extended to perform page-level access checks after authentication using `_PAGE_PATH_MAP` to resolve page paths to identifiers. Unauthorized operators see an access-denied message and cannot proceed past the page.
- **`render_nav_bar()`**: Dynamically filters navigation links through `check_page_access()` and only shows the "Admin" link to Analyst users. This ensures operators never see links to pages they cannot access.
- **User Registration**: New operator registrations are created with `Role = 'operator'` and `ApprovalStatus = 'pending'`, requiring Analyst approval before the first login.

### Database Schema Update — `model_schema.users`

The `users` table was extended with three additional columns (added via migration logic that detects and adds missing columns to existing tables):

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `UserId` | `NVARCHAR(100)` PK | — | Unique user identifier |
| `PasswordHash` | `NVARCHAR(255)` | — | PBKDF2-HMAC-SHA256 hash (120,000 iterations) |
| `PasswordSalt` | `NVARCHAR(255)` | — | Random 16-byte salt, base64-encoded |
| `Role` | `NVARCHAR(20)` | `'operator'` | User role: `'operator'` or `'analyst'` |
| `ApprovalStatus` | `NVARCHAR(20)` | `'approved'` | Registration status: `'pending'`, `'approved'`, or `'declined'` |
| `PagePermissions` | `NVARCHAR(MAX)` | `NULL` | JSON array of allowed page identifiers, or `NULL` for default-only access |
| `CreatedAt` | `DATETIME` | `GETDATE()` | Account creation timestamp |
| `LastLoginAt` | `DATETIME` | `NULL` | Last successful login timestamp |
| `IsActive` | `BIT` | `1` | Whether the account is active |

A default Analyst account is seeded automatically on first run if no Analyst exists (`UserId: 'admin'`, password configurable via `DEFAULT_ANALYST_PASSWORD` environment variable).

---

## 4.3 User Interface — Add New

**Figure 4.8 – Admin Panel Interface Screenshot (NEW)**

The Admin Panel interface features:
- **COFICAB-themed header**: Navy gradient hero section with "ADMIN PANEL" eyebrow label and "User Management" title
- **Pending Approvals Section**: Lists operator registrations awaiting approval with User ID, registration timestamp, and Approve/Decline action buttons. Shows an info message when no pending registrations exist.
- **All Users Table**: A full-width dataframe displaying all registered users with columns for User ID, Role, Approval Status, Active flag, Page Access summary, Creation date, and Last Login. The Page Access column shows a readable summary (e.g., "All pages (analyst)", "Default (Realtime only)", "Configuration, Analysis").
- **Manage Page Access Section**: Expandable panels for each operator containing:
  - User metadata (User ID, Status, Active flag)
  - "Grant Full Access" checkbox — enables all pages for the operator
  - Individual page checkboxes for Configuration and Analysis pages (disabled when full access is granted)
  - "Save Permissions" button with success/error feedback
- **Navigation**: The top navigation bar dynamically shows the "Admin" link only for Analyst users. All navigation links are filtered by `check_page_access()`.

---

## Conclusion — Update

In the **Conclusion Générale**, under the Chapter IV recap (page 1179), update to:

```
- **Chapter IV** covered implementation, UI design, and deployment of the platform. The implementation includes five Streamlit pages (Authentication, Home, Configuration, Real-Time Monitoring, Analysis, and Admin Panel), 2,300+ lines of database helper code, a 900+ line authentication and authorization module with role-based page-level access control, 13 trained machine-learning models, and Mistral AI integration for intelligent root cause analysis.
```

Under **Results** (page 1181), append:

```
- Enforcing role-based page-level access control with default and restricted pages
- Managing operator registrations through an approval workflow
- Configuring per-operator page permissions via a checkbox-based Admin Panel interface
```

Under **Future perspectives** (page 1195), append:

```
- Extending the permission system with granular feature-level (rather than page-level) access control
- Implementing role-based audit logging for all admin actions
- Adding self-service password reset and account recovery workflows
```
