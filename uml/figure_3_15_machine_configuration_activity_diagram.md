# Figure 3.15 — Machine Configuration Activity Diagram

**Location:** Chapter 3 — Conception / §3.2.4.3 Machine Configuration  
**Type:** UML Activity Diagram  
**Page Reference:** 35  

---

## Purpose

Model the process of creating a machine configuration, including machine selection, parameter browsing, validation, and persistence.

---

## Swimlanes

| Lane | Responsible For |
|------|----------------|
| **Analyst** | Navigating, selecting, filling form, saving |
| **System** | Authentication check, data loading, validation, persistence |

---

## Actions & Flow

```
[Start] → Analyst navigates to Configuration page
          ↓
    System: ensure_page_authentication('configuration_page')
          ↓
         [Decision: Authenticated?]
          ↓                    ↓
       [Yes]                [No]
          ↓                    ↓
    System: check_page_    System redirects
    access('configuration_  to login page
    page')                      ↓
          ↓                  [End]
         [Decision: Access granted?]
          ↓                    ↓
       [Yes]                [No]
          ↓                    ↓
    System loads         System displays
    all machines         "Access denied.
    with LineSpeed-      Only Analysts can
    based status         access this page."
          ↓                   ↓
    System displays      [End]
    machine status
    table
          ↓
    Analyst selects a machine from dropdown
          ↓
    System loads all available parameters (OpcNodeIds)
          ↓
    Analyst enters configuration name
          ↓
    Analyst selects monitoring parameters
          ↓
    Analyst selects recipe parameters (subset)
          ↓
    Analyst enters description (optional)
          ↓
    Analyst clicks "Save Configuration"
          ↓
    System: Validate
          ↓
         [Decision: Validation checks]
          ↓                          ↓
    [Recipe params ⊆            [Invalid subset]
     Monitoring params]
          ↓                          ↓
    [Name unique per           System displays
     machine?]                 validation error
          ↓         ↓               ↓
       [Yes]     [No]          Analyst corrects
          ↓         ↓               ↓
    System saves  System       [back to parameter
    to database  displays     selection]
    INSERT INTO  "Configuration
    machine_     name already
    configuration exists for
          ↓      this machine"
    System       error
    clears       message
    cache             ↓
          ↓      Analyst
    System        corrects
    confirms           ↓
    success      [back to name
          ↓      entry]
    [End]
```

---

## Decision Nodes

| # | Decision | Branches | Description |
|---|----------|----------|-------------|
| D1 | Authenticated? | [Yes] / [No] | `ensure_page_authentication()` |
| D2 | Access granted? | [Yes] / [No] | `check_page_access()` — Analyst or explicit permission required |
| D3 | Recipe params ⊆ Monitoring params? | [Valid] / [Invalid] | Subset validation |
| D4 | Config name unique per machine? | [Yes] / [No] | Uniqueness constraint |

---

## Authentication Emphasis

- **Entry guard:** `ensure_page_authentication()` is the first action. Without a valid session, the entire configuration workflow is blocked.
- **Page access:** All authenticated users (Analysts) have unconditional access to every page. No page-level restrictions.
- **Session expiration:** If the session expires mid-configuration, `st.rerun()` triggers `ensure_page_authentication()` again and redirects to login. Unsaved form data is lost.

---

## Notes for Diagram Generation

- Use two swimlanes: **Analyst** (left) and **System** (right).
- Show the authentication and access control check at the very start (before any data loads).
- Use a **sub-activity** icon (rake symbol) for composite actions: "System loads all machines" and "System loads all parameters".
- Show validation rejection loops: invalid subset loops back to parameter selection; duplicate name loops back to name entry.
- Add a note on the "Save to database" action: "`INSERT INTO model_schema.machine_configuration`".
- Show cache clearing as a parallel action step.
- The alternative flows (Edit, Delete) are separate paths off the main flow — they can be shown as `[Edit existing config]` and `[Delete config]` branches from the initial "Analyst navigates to Configuration page" action.

---

## PlantUML Code

```plantuml
@startuml
|Analyst|
start
:navigate to Configuration page;

|System|
:ensure_page_authentication('configuration_page');
if (Authenticated?) then (yes)
  :load all machines with\nLineSpeed-based status;
  :display machine status table;
  |Analyst|
  :select a machine from dropdown;
  |System|
  :load available parameters (OpcNodeIds);
  |Analyst|
  :enter configuration name;
  :select monitoring parameters;
  :select recipe parameters (subset);
  :enter description (optional);
  :click "Save Configuration";

  |System|
  :validate inputs;
  if (Recipe params ⊆ Monitoring params?) then (yes)
    if (Name unique per machine?) then (yes)
      :INSERT INTO\nmodel_schema.machine_configuration;
      :clear cache;
      :confirm success;
      stop
    else (no)
      :display error\n"Configuration name already exists";
      |Analyst|
      :correct name;
      (N) --> |System|
    endif
  else (no)
    :display error\n"Invalid param subset";
    |Analyst|
    :correct parameter selection;
    (N) --> |System|
  endif
else (no)
  :redirect to login page;
  stop
endif
@enduml
```
