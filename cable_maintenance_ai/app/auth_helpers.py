"""Authentication helpers for the Streamlit app."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from urllib.parse import urlencode

import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy import text

from db_helpers import get_engine


AUTH_PAGE_PATH = "pages/authentication_page.py"
AUTH_SESSION_STORAGE_KEY = "coficab_auth_session"
AUTH_QUERY_USER_KEY = "auth_user"
AUTH_QUERY_TOKEN_KEY = "auth_token"
AUTH_QUERY_LOGOUT_KEY = "logout"
AUTH_SESSION_TTL_SECONDS = int(os.getenv("AUTH_SESSION_TTL_SECONDS", str(7 * 24 * 60 * 60)))
PASSWORD_HASH_ITERATIONS = int(os.getenv("AUTH_PASSWORD_ITERATIONS", "120000"))
AUTH_SECRET = (
    os.getenv("AUTH_SESSION_SECRET")
    or os.getenv("DB_PASSWORD")
    or "coficab-auth-secret"
)

# ── Page Access Management ───────────────────────────────────────────────────
# Pages that require explicit permission for operators (shown as checkboxes).
# Pages NOT in this list (app.py, model_page) are accessible by default.
PAGE_REGISTRY: dict[str, str] = {
    "configuration_page": "Configuration (machine config)",
    "analysis_page": "Analysis (datasheets)",
}

# Page identifiers always accessible to any authenticated operator.
_DEFAULT_PAGES: set[str] = {"app.py", "model_page"}

# Maps page paths passed to ensure_page_authentication() to page identifiers.
_PAGE_PATH_MAP: dict[str, str] = {
    "app.py": "app.py",
    "pages/configuration_page.py": "configuration_page",
    "pages/model_page.py": "model_page",
    "pages/analysis_page.py": "analysis_page",
    "pages/admin_page.py": "admin_page",
}


def _normalize_user_id(user_id: str) -> str:
    return (user_id or "").strip()


def _as_single_value(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _pad_base64(value: str) -> str:
    return value + "=" * (-len(value) % 4)


def _build_session_token(user_id: str, expires_at: int | None = None, role: str = "") -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "expires_at": expires_at or int(time.time()) + AUTH_SESSION_TTL_SECONDS,
        "nonce": secrets.token_urlsafe(16),
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload_token = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")
    signature = hmac.new(
        AUTH_SECRET.encode("utf-8"),
        payload_json.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_token}.{signature}"


def _verify_session_token(token: str, expected_user_id: str | None = None) -> dict | None:
    try:
        payload_token, signature = token.split(".", 1)
        payload_json = base64.urlsafe_b64decode(_pad_base64(payload_token)).decode("utf-8")
        expected_signature = hmac.new(
            AUTH_SECRET.encode("utf-8"),
            payload_json.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload = json.loads(payload_json)
        if not isinstance(payload, dict):
            return None
        if int(payload.get("expires_at", 0)) < int(time.time()):
            return None
        if expected_user_id and payload.get("user_id") != expected_user_id:
            return None
        return payload
    except Exception:
        return None


def _session_payload_to_dict(user_id: str, token: str) -> dict:
    payload = _verify_session_token(token, expected_user_id=user_id)
    if not payload:
        role = st.session_state.get("auth_role", "")
        payload = {
            "user_id": user_id,
            "role": role,
            "expires_at": int(time.time()) + AUTH_SESSION_TTL_SECONDS,
            "nonce": secrets.token_urlsafe(16),
        }
        token = _build_session_token(user_id, role=role, expires_at=payload["expires_at"])
        payload = _verify_session_token(token, expected_user_id=user_id) or payload
    payload["token"] = token
    return payload


def _is_authenticated() -> bool:
    user_id = st.session_state.get("auth_user_id")
    token = st.session_state.get("auth_token")
    if not user_id or not token:
        return False
    return _verify_session_token(token, expected_user_id=user_id) is not None


def _set_authenticated_session(
    user_id: str, role: str = "", token: str | None = None
) -> dict:
    user_id = _normalize_user_id(user_id)
    if role and not token:
        token = _build_session_token(user_id, role=role)
    else:
        token = token or _build_session_token(user_id)
    payload = _session_payload_to_dict(user_id, token)

    st.session_state.auth_user_id = payload["user_id"]
    st.session_state.auth_role = payload.get("role", role)
    st.session_state.auth_token = payload["token"]
    st.session_state.auth_expires_at = payload["expires_at"]
    st.session_state.authenticated = True
    st.session_state.auth_session_payload = payload
    return payload


def _clear_authenticated_session() -> None:
    for key in ("auth_user_id", "auth_token", "auth_expires_at", "authenticated", "auth_session_payload"):
        st.session_state.pop(key, None)


def _sync_query_params_from_payload(payload: dict | None) -> None:
    if not payload or not payload.get("user_id") or not payload.get("token"):
        return

    try:
        st.query_params[AUTH_QUERY_USER_KEY] = payload["user_id"]
        st.query_params[AUTH_QUERY_TOKEN_KEY] = payload["token"]
    except Exception:
        pass


def clear_auth_query_params() -> None:
    try:
        st.query_params.pop(AUTH_QUERY_USER_KEY, None)
        st.query_params.pop(AUTH_QUERY_TOKEN_KEY, None)
    except Exception:
        pass


def _page_url_path(page_path: str) -> str:
    cleaned = page_path.lstrip("/")
    return "" if cleaned == "app.py" else cleaned


def build_authenticated_href(page_path: str, payload: dict | None = None) -> str:
    payload = payload or st.session_state.get("auth_session_payload")
    base = _page_url_path(page_path)
    if not payload:
        return f"/{base}"

    query_string = urlencode(
        {
            AUTH_QUERY_USER_KEY: payload.get("user_id", ""),
            AUTH_QUERY_TOKEN_KEY: payload.get("token", ""),
        }
    )
    return f"/{base}?{query_string}"


def build_logout_href(page_path: str = "app.py") -> str:
    base = _page_url_path(page_path)
    return f"/{base}?{AUTH_QUERY_LOGOUT_KEY}=1"


def _sync_session_to_local_storage(payload: dict | None) -> None:
    payload_json = json.dumps(payload or {})
    storage_key = json.dumps(AUTH_SESSION_STORAGE_KEY)

    components.html(
        f"""
        <script>
        (function() {{
            const key = {storage_key};
            const payload = {payload_json};
            try {{
                if (payload && payload.user_id && payload.token) {{
                    window.localStorage.setItem(key, JSON.stringify(payload));
                }} else {{
                    window.localStorage.removeItem(key);
                }}
            }} catch (err) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def _attempt_restore_from_local_storage() -> None:
    storage_key = json.dumps(AUTH_SESSION_STORAGE_KEY)
    user_key = json.dumps(AUTH_QUERY_USER_KEY)
    token_key = json.dumps(AUTH_QUERY_TOKEN_KEY)

    components.html(
        f"""
        <script>
        (function() {{
            const key = {storage_key};
            let payload = null;
            try {{
                const raw = window.localStorage.getItem(key);
                if (raw) {{
                    payload = JSON.parse(raw);
                }}
            }} catch (err) {{
                payload = null;
            }}

            if (!payload || !payload.user_id || !payload.token) {{
                return;
            }}

            let currentHref = window.location.href;
            try {{
                currentHref = window.top.location.href;
            }} catch (err) {{
                try {{
                    currentHref = window.parent.location.href;
                }} catch (err2) {{}}
            }}

            const url = new URL(currentHref);
            url.searchParams.set({user_key}, payload.user_id);
            url.searchParams.set({token_key}, payload.token);

            try {{
                window.top.location.replace(url.toString());
                return;
            }} catch (err) {{}}

            try {{
                window.parent.location.href = url.toString();
                return;
            }} catch (err) {{}}

            try {{
                window.location.href = url.toString();
                return;
            }} catch (err) {{}}

            try {{
                const form = document.createElement("form");
                form.method = "GET";
                form.action = url.toString();
                form.target = "_top";
                document.body.appendChild(form);
                form.submit();
            }} catch (err) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def initialize_users_table() -> None:
    """Create the model_schema.users table if it does not exist."""
    try:
        with get_engine().connect() as connection:
            connection.execute(
                text(
                    """
                    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'model_schema')
                    BEGIN
                        EXEC('CREATE SCHEMA [model_schema]')
                    END
                    """
                )
            )
            connection.commit()

            connection.execute(
                text(
                    """
                    IF NOT EXISTS (
                        SELECT *
                        FROM sys.tables t
                        JOIN sys.schemas s ON t.schema_id = s.schema_id
                        WHERE t.name = 'users' AND s.name = 'model_schema'
                    )
                    CREATE TABLE [model_schema].[users] (
                        [UserId] NVARCHAR(100) NOT NULL PRIMARY KEY,
                        [PasswordHash] NVARCHAR(255) NOT NULL,
                        [PasswordSalt] NVARCHAR(255) NOT NULL,
                        [Role] NVARCHAR(20) NOT NULL DEFAULT 'operator',
                        [ApprovalStatus] NVARCHAR(20) NOT NULL DEFAULT 'approved',
                        [CreatedAt] DATETIME NOT NULL DEFAULT GETDATE(),
                        [LastLoginAt] DATETIME NULL,
                        [IsActive] BIT NOT NULL DEFAULT 1
                    )
                    """
                )
            )
            connection.commit()

            # Add Role column if table already exists without it
            try:
                connection.execute(
                    text(
                        """
                        IF NOT EXISTS (
                            SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = 'model_schema'
                              AND TABLE_NAME = 'users'
                              AND COLUMN_NAME = 'Role'
                        )
                        ALTER TABLE [model_schema].[users] ADD [Role] NVARCHAR(20) NOT NULL DEFAULT 'operator'
                        """
                    )
                )
                connection.commit()
            except Exception:
                try:
                    connection.rollback()
                except Exception:
                    pass

            # Add ApprovalStatus column if table already exists without it
            try:
                connection.execute(
                    text(
                        """
                        IF NOT EXISTS (
                            SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = 'model_schema'
                              AND TABLE_NAME = 'users'
                              AND COLUMN_NAME = 'ApprovalStatus'
                        )
                        ALTER TABLE [model_schema].[users]
                        ADD [ApprovalStatus] NVARCHAR(20) NOT NULL DEFAULT 'approved'
                        """
                    )
                )
                connection.commit()
            except Exception:
                try:
                    connection.rollback()
                except Exception:
                    pass

            # Add PagePermissions column if it doesn't exist
            try:
                connection.execute(
                    text(
                        """
                        IF NOT EXISTS (
                            SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = 'model_schema'
                              AND TABLE_NAME = 'users'
                              AND COLUMN_NAME = 'PagePermissions'
                        )
                        ALTER TABLE [model_schema].[users]
                        ADD [PagePermissions] NVARCHAR(MAX) NULL
                        """
                    )
                )
                connection.commit()
            except Exception:
                try:
                    connection.rollback()
                except Exception:
                    pass

            # Seed default analyst account if no analyst exists
            try:
                existing_analyst = connection.execute(
                    text(
                        "SELECT COUNT(*) as cnt FROM [model_schema].[users] WHERE [Role] = 'analyst'"
                    )
                ).fetchone()
                analyst_count = existing_analyst[0] if existing_analyst else 0
                if analyst_count == 0:
                    default_password = os.getenv(
                        "DEFAULT_ANALYST_PASSWORD", "Coficab2025!"
                    )
                    analyst_salt, analyst_hash = hash_password(default_password)
                    connection.execute(
                        text(
                            """
                            INSERT INTO [model_schema].[users]
                            (UserId, PasswordHash, PasswordSalt, Role, ApprovalStatus, IsActive)
                            VALUES (:uid, :pwd_hash, :pwd_salt, 'analyst', 'approved', 1)
                            """
                        ),
                        {
                            "uid": "admin",
                            "pwd_hash": analyst_hash,
                            "pwd_salt": analyst_salt,
                        },
                    )
                    connection.commit()
            except Exception:
                try:
                    connection.rollback()
                except Exception:
                    pass
    except Exception:
        pass


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return base64.b64encode(salt).decode("utf-8"), base64.b64encode(derived).decode("utf-8")


def verify_password(password: str, stored_salt: str, stored_hash: str) -> bool:
    try:
        salt = base64.b64decode(stored_salt.encode("utf-8"))
        _, computed_hash = hash_password(password, salt=salt)
        return hmac.compare_digest(computed_hash, stored_hash)
    except Exception:
        return False


def register_user(user_id: str, password: str) -> tuple[bool, str]:
    user_id = _normalize_user_id(user_id)
    if not user_id or not password:
        return False, "User ID and password are required."

    initialize_users_table()

    try:
        with get_engine().connect() as connection:
            existing = connection.execute(
                text(
                    "SELECT [ApprovalStatus] FROM [model_schema].[users] WHERE [UserId] = :user_id"
                ),
                {"user_id": user_id},
            ).mappings().first()
            if existing:
                status = existing.get("ApprovalStatus", "")
                if status == "pending":
                    return False, "This User ID already has a pending registration request."
                if status == "approved":
                    return False, "User ID already exists."
                # Declined users can re-register — update their record
                password_salt, password_hash = hash_password(password)
                connection.execute(
                    text(
                        """
                        UPDATE [model_schema].[users]
                        SET PasswordHash = :pwd_hash,
                            PasswordSalt = :pwd_salt,
                            Role = 'operator',
                            ApprovalStatus = 'pending',
                            IsActive = 1,
                            PagePermissions = NULL,
                            CreatedAt = GETDATE(),
                            LastLoginAt = NULL
                        WHERE UserId = :user_id
                        """
                    ),
                    {
                        "user_id": user_id,
                        "pwd_hash": password_hash,
                        "pwd_salt": password_salt,
                    },
                )
                connection.commit()
                return True, "Registration submitted! Your account is pending approval by an Analyst."

            password_salt, password_hash = hash_password(password)
            connection.execute(
                text(
                    """
                    INSERT INTO [model_schema].[users]
                    (UserId, PasswordHash, PasswordSalt, Role, ApprovalStatus, IsActive, PagePermissions)
                    VALUES (:user_id, :password_hash, :password_salt, 'operator', 'pending', 1, NULL)
                    """
                ),
                {
                    "user_id": user_id,
                    "password_hash": password_hash,
                    "password_salt": password_salt,
                },
            )
            connection.commit()
        return True, "Registration submitted! Your account is pending approval by an Analyst."
    except Exception as exc:
        return False, f"Registration failed: {exc}"


def authenticate_user(user_id: str, password: str) -> tuple[bool, str, str | None]:
    user_id = _normalize_user_id(user_id)
    if not user_id or not password:
        return False, "User ID and password are required.", None

    initialize_users_table()

    try:
        with get_engine().connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT UserId, PasswordHash, PasswordSalt, IsActive,
                           Role, ApprovalStatus
                    FROM [model_schema].[users]
                    WHERE UserId = :user_id
                    """
                ),
                {"user_id": user_id},
            ).mappings().first()

            if not row:
                return False, "Invalid user ID or password.", None
            if not row.get("IsActive", True):
                return False, "This account is disabled.", None
            if not verify_password(password, row["PasswordSalt"], row["PasswordHash"]):
                return False, "Invalid user ID or password.", None

            role = row.get("Role", "operator")
            approval_status = row.get("ApprovalStatus", "approved")

            if role == "operator" and approval_status == "pending":
                return False, "Your account is pending approval by an Analyst.", None
            if role == "operator" and approval_status == "declined":
                return False, "Your account has been declined. You may register again.", None

            connection.execute(
                text(
                    """
                    UPDATE [model_schema].[users]
                    SET LastLoginAt = GETDATE()
                    WHERE UserId = :user_id
                    """
                ),
                {"user_id": user_id},
            )
            connection.commit()

        return True, "Login successful.", role
    except Exception as exc:
        return False, f"Login failed: {exc}", None


def sign_in_user(user_id: str, role: str = "") -> dict:
    payload = _set_authenticated_session(user_id, role=role)
    _sync_query_params_from_payload(payload)
    _sync_session_to_local_storage(payload)
    return payload


def sign_out_user() -> None:
    _clear_authenticated_session()
    clear_auth_query_params()
    _sync_session_to_local_storage(None)


def restore_session_from_query_params() -> bool:
    if _as_single_value(st.query_params.get(AUTH_QUERY_LOGOUT_KEY)) in {"1", "true", "yes"}:
        sign_out_user()
        return False

    user_id = _as_single_value(st.query_params.get(AUTH_QUERY_USER_KEY))
    token = _as_single_value(st.query_params.get(AUTH_QUERY_TOKEN_KEY))
    if not user_id or not token:
        return False

    payload = _verify_session_token(token, expected_user_id=user_id)
    if not payload:
        return False

    role = payload.get("role", "")
    _set_authenticated_session(user_id, role=role, token=token)
    _sync_query_params_from_payload(st.session_state.auth_session_payload)
    _sync_session_to_local_storage(st.session_state.auth_session_payload)
    return True


def ensure_page_authentication(current_page_path: str, auth_page_path: str = AUTH_PAGE_PATH) -> bool:
    """Keep the current page protected and restore sessions from query parameters."""
    if _as_single_value(st.query_params.get(AUTH_QUERY_LOGOUT_KEY)) in {"1", "true", "yes"}:
        sign_out_user()
        st.switch_page(auth_page_path)
        return False

    if _is_authenticated():
        if "auth_session_payload" not in st.session_state:
            st.session_state.auth_session_payload = _session_payload_to_dict(
                st.session_state.auth_user_id,
                st.session_state.auth_token,
            )
        _sync_query_params_from_payload(st.session_state.auth_session_payload)
        _sync_session_to_local_storage(st.session_state.auth_session_payload)

        # Page-level access check
        page_id = _PAGE_PATH_MAP.get(current_page_path, current_page_path)
        if not check_page_access(page_id):
            st.error("⛔ **Access denied.** You do not have permission to view this page. Contact an Analyst if you need access.")
            st.stop()
            return False

        return True

    if restore_session_from_query_params():
        return True

    st.session_state.auth_next_page = current_page_path
    st.switch_page(auth_page_path)
    return False


def bootstrap_auth_page() -> bool:
    """Restore the current session if possible and keep logged-in users moving forward."""
    if _as_single_value(st.query_params.get(AUTH_QUERY_LOGOUT_KEY)) in {"1", "true", "yes"}:
        sign_out_user()

    if _is_authenticated():
        if "auth_session_payload" not in st.session_state:
            st.session_state.auth_session_payload = _session_payload_to_dict(
                st.session_state.auth_user_id,
                st.session_state.auth_token,
            )
        _sync_query_params_from_payload(st.session_state.auth_session_payload)
        _sync_session_to_local_storage(st.session_state.auth_session_payload)
        target_page = st.session_state.pop("auth_next_page", "app.py") or "app.py"
        if target_page == AUTH_PAGE_PATH:
            target_page = "app.py"
        st.switch_page(target_page)
        return True

    if restore_session_from_query_params():
        target_page = st.session_state.pop("auth_next_page", "app.py") or "app.py"
        if target_page == AUTH_PAGE_PATH:
            target_page = "app.py"
        st.switch_page(target_page)
        return True

    _attempt_restore_from_local_storage()
    return False


# ── Admin / User Management Helpers ────────────────────────────────────────────

def get_pending_operators() -> list[dict]:
    """Return list of operator registrations pending approval."""
    try:
        with get_engine().connect() as c:
            rows = c.execute(
                text(
                    """
                    SELECT UserId, CreatedAt
                    FROM [model_schema].[users]
                    WHERE Role = 'operator' AND ApprovalStatus = 'pending'
                    ORDER BY CreatedAt DESC
                    """
                )
            ).fetchall()
        return [
            {"user_id": row[0], "created_at": row[1]}
            for row in rows
        ]
    except Exception:
        return []


def get_all_users() -> list[dict]:
    """Return all users with their role and approval status."""
    try:
        with get_engine().connect() as c:
            rows = c.execute(
                text(
                    """
                    SELECT UserId, Role, ApprovalStatus, IsActive, CreatedAt, LastLoginAt
                    FROM [model_schema].[users]
                    ORDER BY CreatedAt DESC
                    """
                )
            ).fetchall()
        return [
            {
                "user_id": row[0],
                "role": row[1],
                "approval_status": row[2],
                "is_active": row[3],
                "created_at": row[4],
                "last_login_at": row[5],
            }
            for row in rows
        ]
    except Exception:
        return []


def approve_operator(user_id: str) -> tuple[bool, str]:
    """Approve a pending operator registration."""
    try:
        with get_engine().begin() as c:
            result = c.execute(
                text(
                    "UPDATE [model_schema].[users] SET ApprovalStatus = 'approved' "
                    "WHERE UserId = :uid AND Role = 'operator' AND ApprovalStatus = 'pending'"
                ),
                {"uid": user_id},
            )
            if result.rowcount == 0:
                return False, f"No pending operator found with User ID '{user_id}'."
        return True, f"Operator '{user_id}' approved successfully."
    except Exception as e:
        return False, f"Error approving user: {e}"


def decline_operator(user_id: str) -> tuple[bool, str]:
    """Decline a pending operator registration."""
    try:
        with get_engine().begin() as c:
            result = c.execute(
                text(
                    "UPDATE [model_schema].[users] SET ApprovalStatus = 'declined', IsActive = 0 "
                    "WHERE UserId = :uid AND Role = 'operator' AND ApprovalStatus = 'pending'"
                ),
                {"uid": user_id},
            )
            if result.rowcount == 0:
                return False, f"No pending operator found with User ID '{user_id}'."
        return True, f"Operator '{user_id}' declined."
    except Exception as e:
        return False, f"Error declining user: {e}"


def set_user_active_status(user_id: str, active: bool) -> tuple[bool, str]:
    """Activate or disable a user."""
    try:
        with get_engine().begin() as c:
            result = c.execute(
                text(
                    "UPDATE [model_schema].[users] SET IsActive = :active "
                    "WHERE UserId = :uid"
                ),
                {"active": 1 if active else 0, "uid": user_id},
            )
            if result.rowcount == 0:
                return False, f"No user found with User ID '{user_id}'."
            status = "activated" if active else "disabled"
            return True, f"User '{user_id}' has been {status}."
    except Exception as e:
        return False, f"Error updating user status: {e}"


def delete_user(user_id: str) -> tuple[bool, str]:
    """Permanently delete a user from the database."""
    try:
        with get_engine().begin() as c:
            result = c.execute(
                text("DELETE FROM [model_schema].[users] WHERE UserId = :uid"),
                {"uid": user_id},
            )
            if result.rowcount == 0:
                return False, f"No user found with User ID '{user_id}'."
        return True, f"User '{user_id}' has been deleted."
    except Exception as e:
        return False, f"Error deleting user: {e}"


def get_current_user_role() -> str:
    """Return the role of the currently logged-in user."""
    return st.session_state.get("auth_role", "")


def is_current_user_analyst() -> bool:
    """Check if the currently logged-in user is an Analyst."""
    return st.session_state.get("auth_role", "") == "analyst"


# ── Page Access Management ───────────────────────────────────────────────────

def get_user_page_permissions(user_id: str) -> list[str] | None:
    """
    Retrieve the list of explicitly granted pages for an operator.
    
    Returns:
        list[str] | None:
          - None  →  no explicit permissions (only default pages: Home, Realtime)
          - [...] →  list of explicitly allowed page identifiers
    """
    initialize_users_table()
    try:
        with get_engine().connect() as c:
            row = c.execute(
                text(
                    "SELECT PagePermissions FROM [model_schema].[users] WHERE UserId = :uid"
                ),
                {"uid": user_id},
            ).fetchone()
        if row is None or row[0] is None:
            return None
        perms = json.loads(row[0])
        if not isinstance(perms, list):
            return None
        return perms
    except Exception:
        return None


def set_user_page_permissions(user_id: str, permissions: list[str] | None) -> tuple[bool, str]:
    """
    Save explicit page permissions for an operator.
    
    Args:
        user_id: The operator's UserId.
        permissions: 
          - None  →  grant only default pages (Home, Realtime)
          - [...] →  list of page identifiers to explicitly allow
    
    Returns:
        (success, message)
    """
    initialize_users_table()
    try:
        value = json.dumps(permissions) if permissions is not None else None
        with get_engine().begin() as c:
            c.execute(
                text(
                    "UPDATE [model_schema].[users] SET PagePermissions = :perms WHERE UserId = :uid"
                ),
                {"perms": value, "uid": user_id},
            )
        label = "full access (all pages)" if permissions is None else f"restricted to: {', '.join(permissions)}"
        return True, f"Permissions updated for '{user_id}': {label}"
    except Exception as e:
        return False, f"Error updating permissions: {e}"


def check_page_access(page_id: str) -> bool:
    """
    Check whether the currently authenticated user can access the given page.
    
    Rules:
      - Analysts always have access.
      - Default pages (Home, Realtime) are always accessible to operators.
      - For restricted pages, the operator must have an explicit permission entry.
      - If PagePermissions is NULL → only default pages (no restricted access).
    
    Returns:
        True if access is allowed, False otherwise.
    """
    role = get_current_user_role()
    if role == "analyst":
        return True

    if page_id in _DEFAULT_PAGES:
        return True

    user_id = st.session_state.get("auth_user_id", "")
    if not user_id:
        return False

    perms = get_user_page_permissions(user_id)
    if perms is None:
        return False

    return page_id in perms


# ── Shared Navigation Bar ───────────────────────────────────────────────────────

COFICAB_NAV_STYLE = """
<style>
.cofi-nav {
    display: flex; align-items: center; justify-content: space-between; gap: 24px;
    padding: 10px 24px; margin: 0;
    background: linear-gradient(120deg, #0c1f31 0%, #133657 55%, #1f4a6f 100%);
    box-shadow: 0 14px 32px rgba(7, 18, 30, 0.2);
    position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
}
.cofi-nav__left { display: flex; align-items: center; gap: 14px; }
.cofi-nav__logo { height: 36px; width: auto; }
.cofi-nav__links { display: flex; justify-content: center; gap: 18px; flex-wrap: wrap; flex: 1; }
.cofi-nav__actions { display: flex; align-items: center; justify-content: flex-end; min-width: 120px; }
.cofi-nav__link {
    color: #ffffff; text-decoration: none; font-weight: 600; font-size: 16px; letter-spacing: 0.6px;
}
.cofi-nav__link:visited { color: #ffffff; }
.cofi-nav__link:hover { color: #ffddbf; }
.cofi-nav__link--active { color: #ffddbf !important; border-bottom: 2px solid #f57c00; }
.cofi-nav__logout {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 8px 14px; border-radius: 999px; border: 1px solid rgba(255, 221, 191, 0.35);
    background: rgba(255, 255, 255, 0.08); color: #ffffff; text-decoration: none;
    font-weight: 700; font-size: 14px;
}
.cofi-nav__logout:hover { background: rgba(255, 221, 191, 0.16); color: #ffffff; }
</style>
"""


def render_nav_bar(current_page: str = "app.py") -> None:
    """Render the shared navigation bar. Filters links based on page permissions."""

    is_analyst = is_current_user_analyst()

    nav_links = [
        ("Home", "app.py"),
        ("Configuration", "configuration_page"),
        ("Realtime", "model_page"),
        ("Analysis", "analysis_page"),
    ]

    if is_analyst:
        nav_links.append(("Admin", "admin_page"))

    st.markdown(COFICAB_NAV_STYLE, unsafe_allow_html=True)

    links_html = ""
    for label, page in nav_links:
        if not check_page_access(page):
            continue
        href = build_authenticated_href(page)
        active_class = " cofi-nav__link--active" if current_page == page else ""
        links_html += f'<a class="cofi-nav__link{active_class}" href="{href}" target="_self">{label}</a>'

    logout_href = build_logout_href(current_page)

    st.markdown(
        f"""
        <nav class="cofi-nav">
            <div class="cofi-nav__left"></div>
            <div class="cofi-nav__links">{links_html}</div>
            <div class="cofi-nav__actions">
                <a class="cofi-nav__logout" href="{logout_href}" target="_self">Logout</a>
            </div>
        </nav>
        """,
        unsafe_allow_html=True,
    )
