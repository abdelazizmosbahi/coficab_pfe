# Figure 3.14 — User Registration Activity Diagram

> New user registration flow with User ID availability check and automatic login.

```mermaid
flowchart TD
    START(["User navigates to
        Register tab"])
    ENTER_DETAILS["Enter User ID
        and password"]
    CHECK_EXISTS{"Check if User ID
        already exists?"}
    EXISTS["Show error:
        'User ID already exists'"]
    GEN_SALT["Generate random
        16-byte salt"]
    HASH_PWD["Hash password with
        PBKDF2-HMAC-SHA256
        (120,000 iterations)"]
    SET_ROLE["Set Role = 'operator'
        ApprovalStatus = 'pending'"]
    INSERT_DB["Insert new user record
        INTO model_schema.users"]
    AUTO_LOGIN["Auto-login new user
        (create session token)"]
    REDIRECT_HOME["Redirect to Home page"]
    REDIRECT_LOGIN["Redirect to Login page
        with pending message"]

    START --> ENTER_DETAILS
    ENTER_DETAILS --> CHECK_EXISTS
    CHECK_EXISTS -->|Exists| EXISTS
    EXISTS --> ENTER_DETAILS
    CHECK_EXISTS -->|New user| GEN_SALT
    GEN_SALT --> HASH_PWD
    HASH_PWD --> SET_ROLE
    SET_ROLE --> INSERT_DB
    INSERT_DB --> REDIRECT_LOGIN

    classDef start fill:#e8f0fe,stroke:#1a73e8,stroke-width:2px;
    classDef decision fill:#fef7e0,stroke:#f9ab00,stroke-width:1px;
    classDef process fill:#e6f4ea,stroke:#34a853,stroke-width:1px;
    classDef term fill:#fce8e6,stroke:#ea4335,stroke-width:1px;
    class START start;
    class CHECK_EXISTS decision;
    class ENTER_DETAILS,GEN_SALT,HASH_PWD,SET_ROLE,INSERT_DB,AUTO_LOGIN process;
    class EXISTS,EXISTS,term;
    class REDIRECT_HOME,REDIRECT_LOGIN term;
```
