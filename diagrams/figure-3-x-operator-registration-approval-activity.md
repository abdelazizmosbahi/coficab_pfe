# Figure 3.X — Operator Registration & Approval Activity Diagram (NEW)

> Complete flow: operator registers → pending → analyst approves/declines → operator can log in.

```mermaid
flowchart TD
    START(["New user navigates to
        Register tab"])
    ENTER_DETAILS["Enter User ID
        and password"]
    CHECK_EXISTS{"User ID
        already exists?"}
    EXISTS["Show error:
        'User ID already exists'"]
    CREATE_USER["Create user:
        • Role = 'operator'
        • ApprovalStatus = 'pending'
        • IsActive = 1"]
    SAVE_DB["INSERT INTO
        model_schema.users"]
    PENDING_MSG["Show message:
        'Registration submitted.
        Awaiting analyst approval.'"]

    START --> ENTER_DETAILS
    ENTER_DETAILS --> CHECK_EXISTS
    CHECK_EXISTS -->|Exists| EXISTS
    EXISTS --> ENTER_DETAILS
    CHECK_EXISTS -->|New| CREATE_USER
    CREATE_USER --> SAVE_DB
    SAVE_DB --> PENDING_MSG

    subgraph AnalystAction["Analyst reviews in Admin Panel"]
        LOAD_PENDING["Navigate to Admin Panel
            View pending registrations"]
        REVIEW["Review operator details
            (User ID, timestamp)"]
        DECIDE{"Approve or
            Decline?"}
        APPROVE["Approve:
            ApprovalStatus = 'approved'
            IsActive = 1"]
        DECLINE["Decline:
            ApprovalStatus = 'declined'
            IsActive = 0"]
        CONFIRM["Show confirmation
            Refresh pending list"]
    end

    PENDING_MSG -.-> LOAD_PENDING
    LOAD_PENDING --> REVIEW
    REVIEW --> DECIDE
    DECIDE -->|Approve| APPROVE
    DECIDE -->|Decline| DECLINE
    APPROVE --> CONFIRM
    DECLINE --> CONFIRM

    subgraph OperatorLogin["Operator logs in"]
        ATTEMPT["Operator enters
            User ID + password"]
        CHECK_APPROVED{"ApprovalStatus
            = approved?"}
        GRANT["Login successful
            Redirect to Home"]
        DENY["Login denied
            'Account not yet approved'"]
    end

    CONFIRM -.-> ATTEMPT
    ATTEMPT --> CHECK_APPROVED
    CHECK_APPROVED -->|Yes| GRANT
    CHECK_APPROVED -->|No| DENY

    classDef start fill:#e8f0fe,stroke:#1a73e8,stroke-width:2px;
    classDef decision fill:#fef7e0,stroke:#f9ab00,stroke-width:1px;
    classDef process fill:#e6f4ea,stroke:#34a853,stroke-width:1px;
    classDef alert fill:#fce8e6,stroke:#ea4335,stroke-width:1px;
    classDef adminfill fill:#f3e8fd,stroke:#9334ea,stroke-width:1px;
    class START start;
    class CHECK_EXISTS,DECIDE,CHECK_APPROVED decision;
    class ENTER_DETAILS,CREATE_USER,SAVE_DB,PENDING_MSG,CONFIRM,ATTEMPT process;
    class EXISTS,EXISTS,alert;
    class LOAD_PENDING,REVIEW,APPROVE,DECLINE adminfill;
    class GRANT,DENY term;
```
