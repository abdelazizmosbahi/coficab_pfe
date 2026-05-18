# Figure 3.X — Page Access Control Activity Diagram (NEW)

> Page-level access enforcement flow: authentication check, role-based bypass, default vs. restricted page logic.

```mermaid
flowchart TD
    START(["User navigates to
        a Streamlit page"])
    CALL_ENSURE["Page calls
        ensure_page_authentication()"]
    CHECK_AUTH{"User is
        authenticated?"}
    REDIRECT_AUTH["Redirect to
        Authentication page"]
    MAP_PAGE["Map page path to
        page identifier
        (_PAGE_PATH_MAP)"]
    CHECK_ROLE{"User role
        = analyst?"}
    GRANT["✅ Access granted
        (Analyst has full access)"]
    CHECK_DEFAULT{"Page is default?
        (app.py or model_page)"}
    GRANT_DEFAULT["✅ Access granted
        (Default page)"]
    LOAD_PERMS["Load operator's
        PagePermissions"]
    CHECK_NULL{"PagePermissions
        = NULL?"}
    CHECK_IN_LIST{"Page ID in
        PagePermissions list?"}
    GRANT_PERM["✅ Access granted
        (Explicit permission)"]
    DENY["⛔ Access denied
        Show error message
        'Contact an Analyst'"]
    STOP(["Execution stopped
        (st.stop())"])

    START --> CALL_ENSURE
    CALL_ENSURE --> CHECK_AUTH
    CHECK_AUTH -->|No| REDIRECT_AUTH
    REDIRECT_AUTH --> STOP
    CHECK_AUTH -->|Yes| MAP_PAGE
    MAP_PAGE --> CHECK_ROLE
    CHECK_ROLE -->|Yes| GRANT
    CHECK_ROLE -->|No (operator)| CHECK_DEFAULT
    CHECK_DEFAULT -->|Yes| GRANT_DEFAULT
    CHECK_DEFAULT -->|No (restricted)| LOAD_PERMS
    LOAD_PERMS --> CHECK_NULL
    CHECK_NULL -->|Yes| DENY
    CHECK_NULL -->|No| CHECK_IN_LIST
    CHECK_IN_LIST -->|Yes| GRANT_PERM
    CHECK_IN_LIST -->|No| DENY
    DENY --> STOP

    classDef start fill:#e8f0fe,stroke:#1a73e8,stroke-width:2px;
    classDef decision fill:#fef7e0,stroke:#f9ab00,stroke-width:1px;
    classDef process fill:#e6f4ea,stroke:#34a853,stroke-width:1px;
    classDef grant fill:#e6f4ea,stroke:#34a853,stroke-width:2px;
    classDef deny fill:#fce8e6,stroke:#ea4335,stroke-width:2px;
    class START start;
    class CHECK_AUTH,CHECK_ROLE,CHECK_DEFAULT,CHECK_NULL,CHECK_IN_LIST decision;
    class CALL_ENSURE,REDIRECT_AUTH,MAP_PAGE,LOAD_PERMS process;
    class GRANT,GRANT_DEFAULT,GRANT_PERM grant;
    class DENY,STOP deny;
```
