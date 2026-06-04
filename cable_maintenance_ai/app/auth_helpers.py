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


# ── Coficab Logo (base64) ───────────────────────────────────────────────────────

COFICAB_LOGO_B64 = "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"

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
