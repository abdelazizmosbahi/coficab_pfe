# Authentication — Low-Level Use Case Decomposition

## Scope

This diagram decomposes the **Authentication** functional area into top-level actor-facing use cases and low-level system-internal behaviors. Relationships are validated against `auth_helpers.py` (970 lines).

## Mapping to General Diagram

| General UC | Title | Sub-Diagram UC |
|---|---|---|
| UC01 | Authenticate | UCA1 Log In |
| UC02 | Logout | UCA2 Log Out |

## Low-Level Use Cases

### UCA3 — Validate Credentials
*`<<include>>` by UCA1 (mandatory)*

| | |
|---|---|
| **Goal** | Verify that the provided User ID and password match the stored hash in `model_schema.users` |
| **Implementation** | Calls `verify_password()` which re-hashes the candidate password with the stored 16-byte salt via PBKDF2-HMAC-SHA256 (120,000 iterations), then compares using `hmac.compare_digest` (`auth_helpers.py:451-455`) |
| **Validation** | Returns `(False, "Invalid user ID or password.")` if no match. Also checks `IsActive=1` and `ApprovalStatus='approved'` before returning success (`auth_helpers.py:528-575`) |
| **Reuse** | Called ONLY by UCA1. No other use case in the system validates credentials. |

### UCA4 — Build & Persist Session Token
*`<<include>>` by UCA1 (mandatory)*

| | |
|---|---|
| **Goal** | Create an HMAC-SHA256 signed session token and store it across three persistence layers |
| **Sub-steps** | 1. `_build_session_token()` creates JSON `{user_id, role, exp, nonce}` signed with HMAC-SHA256 (`auth_helpers.py:69-84`)<br>2. `_set_authenticated_session()` stores user_id, role, token, expiry, payload in `st.session_state` (`auth_helpers.py:134-151`)<br>3. `_sync_query_params_from_payload()` writes `auth_user` and `auth_token` to URL query parameters (`auth_helpers.py:158-167`)<br>4. `_sync_session_to_local_storage()` embeds a `<script>` that writes the payload to `window.localStorage` (`auth_helpers.py:202-225`) |
| **TTL** | 7 days (configurable via `AUTH_SESSION_TTL_SECONDS`) |

### UCA5 — Destroy Session Globally
*`<<include>>` by UCA2 (mandatory)*

| | |
|---|---|
| **Goal** | Remove all authentication artifacts from all storage layers |
| **Sub-steps** | 1. `_clear_authenticated_session()` removes `auth_user_id`, `auth_token`, `auth_role`, `auth_expires_at`, `authenticated`, `auth_session_payload` from session state (`auth_helpers.py:153-156`)<br>2. `clear_auth_query_params()` removes `auth_user` and `auth_token` from URL query parameters (`auth_helpers.py:169-175`)<br>3. `_sync_session_to_local_storage(None)` embeds a script that removes the payload from `window.localStorage` (`auth_helpers.py:202-225`) |

### UCA6 — Restore Session From Storage
*`<<extend>>` UCA1 (conditional — triggered when `auth_user` + `auth_token` exist in URL query parameters or localStorage)*

| | |
|---|---|
| **Goal** | Restore an authenticated session without showing the login form |
| **Trigger** | `restore_session_from_query_params()` is called at the top of every page load. If `auth_user` and `auth_token` are in `st.query_params`, the token is verified (`_verify_session_token()`), and if valid and not expired, the session is re-established via `_set_authenticated_session()` + syncs (`auth_helpers.py:594-613`) |
| **Condition** | Token must be valid HMAC-SHA256 signature AND not expired (expiry check at `auth_helpers.py:98-100`). If valid → bypass login form entirely. If invalid/expired → falls through to UCA7. |
| **Also triggered from** | `_attempt_restore_from_local_storage()` on the auth page — reads from `localStorage` and redirects with auth query params appended (`auth_helpers.py:227-293`) |

### UCA7 — Reject Authentication
*`<<extend>>` UCA1 (conditional — triggered on invalid credentials or disabled account)*

| | |
|---|---|
| **Goal** | Display an appropriate error and prevent session creation |
| **Trigger Conditions** | | 
| | • Invalid User ID or password → `st.error("Invalid user ID or password.")` at `auth_helpers.py:557` |
| | • Account disabled (`IsActive=0`) → `st.error("This account is disabled.")` at `auth_helpers.py:551` |
| | • Operator not yet approved (`ApprovalStatus='pending'`) → `st.error("Your account is pending approval...")` at `auth_helpers.py:569` |
| **Result** | UCA4 (Build & Persist Session) is NOT invoked. The Analyst stays on the login page. |

## Relationship Justification

### UCA1 → UCA3 <<include>> (Validate Credentials)
**Must be invoked.** UML 2.5 §16.3.5 states `<<include>>` "designates that the behavior of the included use case is inserted into the behavior of the including use case." Authentication cannot succeed without credential validation — there is no valid execution path where `authenticate_user()` skips `verify_password()`. The include is mandatory.

### UCA1 → UCA4 <<include>> (Build & Persist Session)
**Must be invoked.** After validation, the session must be created and persisted. `sign_in_user()` always calls `_set_authenticated_session()`, `_sync_query_params_from_payload()`, and `_sync_session_to_local_storage()` in sequence (`auth_helpers.py:581-584`). Without these, the user cannot navigate to protected pages.

### UCA2 → UCA5 <<include>> (Destroy Session Globally)
**Must be invoked.** Logout (`sign_out_user()`) always calls `_clear_authenticated_session()`, `clear_auth_query_params()`, and `_sync_session_to_local_storage(None)` in sequence (`auth_helpers.py:588-591`). Partial cleanup would leave stale tokens.

### UCA6 → UCA1 <<extend>> (Restore Session)
**Conditional.** The extension fires when `st.query_params` contains valid `auth_user` + `auth_token`. This is an **optional** alternative entry path — the Analyst may arrive at the auth page with a bookmark containing auth params, or `localStorage` may have a persisted session. The base UC (login form) remains complete without it. The extension point is at `auth_helpers.py:594` inside `restore_session_from_query_params()`.

### UCA7 → UCA1 <<extend>> (Reject Authentication)
**Conditional.** This extension fires when credentials are invalid or the account is disabled. It is an **optional** alternative outcome — the base UC (display login form → validate → succeed) is the happy path. The rejection is conditional on verification failure. The extension point is within `authenticate_user()` at `auth_helpers.py:549-575`.

## Key Implementation Details

| Aspect | Detail |
|---|---|
| **Password Hashing** | PBKDF2-HMAC-SHA256, 120,000 iterations, random 16-byte salt |
| **Token Signing** | HMAC-SHA256 with secret from env (`AUTH_SESSION_SECRET`) |
| **Session TTL** | 7 days (604,800 seconds) |
| **Persistence Layers** | 3: `st.session_state` → URL query params → `window.localStorage` |
| **Restore Priority** | Query params → `localStorage` → fresh login form |
| **Default Analyst** | Auto-seeded as `admin` / `Coficab2025!` if none exists |
| **Source File** | `cable_maintenance_ai/app/auth_helpers.py:1-970` |
