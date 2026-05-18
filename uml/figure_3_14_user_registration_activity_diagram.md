# Figure 3.14 — User Registration Activity Diagram

**Location:** Chapter 3 — Conception / §3.2.4.2  
**Type:** UML Activity Diagram  

---

## Purpose

New user self-registration. Accounts are created with `Role = 'operator'` and `ApprovalStatus = 'pending'` — an Analyst must approve them before they can log in.

---

## Swimlanes

| Lane | Actions |
|------|---------|
| **Analyst** | Navigates to Register tab, enters credentials |
| **System** | Validation, PBKDF2 hashing, account creation |

---

## Flow

```
[Start] → Analyst navigates to Register tab
          ↓
    Analyst enters User ID + password
          ↓
    System normalizes User ID (lowercase trim)
          ↓
    System checks if User ID already exists
          ↓
         [Decision: Status?]
          ↓        ↓          ↓
      [approved] [pending] [declined or new]
          ↓        ↓          ↓
    "User ID   "Pending   "No existing
     already    approval   record"
     exists"    exists"       ↓
          ↓        ↓     System generates
    Analyst   Analyst   16-byte random salt
    retries   retries       ↓
          ↓        ↓    PBKDF2-HMAC-SHA256
          ←        ←    (password + salt,
                          120,000 iterations)
                               ↓
                         INSERT INTO model_schema.users
                         (UserId, PasswordHash, PasswordSalt,
                          Role='operator', ApprovalStatus='pending',
                          IsActive=1, CreatedAt=GETDATE())
                               ↓
                         System displays
                         "Registration submitted.
                          Your account is pending
                          analyst approval."
                               ↓
                         System shows Login form
                               ↓
                             [End]
```

---

## Decision Nodes

| # | Decision | Branches |
|---|----------|----------|
| D1 | Existing account status? | [approved] / [pending] / [declined or new] |

---

## Notes for Diagram Generation

- 2 swimlanes: **Analyst** (left), **System** (right).
- Three branches for existing user: approved (blocked), pending (blocked), declined (re-registration allowed).
- If user was declined, the existing record is updated with new hash + status set back to `pending`.
- Note on hashing: `"120,000 iterations, 16-byte salt"`.
- New account is Operator role with `ApprovalStatus='pending'` — requires Analyst approval to log in.

---

## PlantUML Code

```plantuml
@startuml
|Analyst|
start
:navigate to Register tab;
:enter User ID + password;

|System|
:normalize User ID (lowercase trim);
:check existing status for User ID;
if (Status: approved?) then (yes)
  :display error\n"User ID already exists";
  |Analyst|
  :retry with different ID;
  (N) --> |Analyst|
else (no)
  if (Status: pending?) then (yes)
    :display error\n"Already has a\npending request";
    |Analyst|
    :retry with different ID;
    (N) --> |Analyst|
  else (no)
    |System|
    :generate random 16-byte salt
    (base64-encoded);
    :PBKDF2-HMAC-SHA256
    (password + salt, 120,000 iterations);
    :INSERT INTO model_schema.users\n(UserId, PasswordHash, PasswordSalt,\n Role='operator', ApprovalStatus='pending',\n IsActive=1, CreatedAt=GETDATE());
    :display "Registration submitted.\nPending analyst approval";
    :show Login form;
    stop
  endif
endif
@enduml
```
