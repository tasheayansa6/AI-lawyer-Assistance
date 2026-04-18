"""
Authentication module — strong hashing, session management,
password reset, OAuth2, CSRF-safe state, and role/permission system.
"""

import hashlib
import hmac
import os
import secrets
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

import streamlit as st

import db

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
PBKDF2_ITERATIONS = 600_000          # NIST SP 800-132 recommendation (2023)
PEPPER = os.getenv("PASSWORD_PEPPER", "change-me-in-production-pepper")
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
ALLOWED_DOMAINS_ENV = os.getenv("ALLOWED_URL_DOMAINS", "")          # comma-separated whitelist
ALLOWED_URL_DOMAINS = [d.strip() for d in ALLOWED_DOMAINS_ENV.split(",") if d.strip()]

# ── Roles & Permissions ────────────────────────────────────────────────────────

class UserRole:
    ADMINISTRATOR       = "administrator"
    LICENSED_LAWYER     = "licensed_lawyer"
    PARALEGAL           = "paralegal"
    GENERAL_PUBLIC      = "general_public"
    COMPLIANCE_OFFICER  = "compliance_officer"

    ALL = [ADMINISTRATOR, LICENSED_LAWYER, PARALEGAL, GENERAL_PUBLIC, COMPLIANCE_OFFICER]

    DISPLAY = {
        ADMINISTRATOR:      "Administrator",
        LICENSED_LAWYER:    "Licensed Lawyer",
        PARALEGAL:          "Paralegal",
        GENERAL_PUBLIC:     "General Public",
        COMPLIANCE_OFFICER: "Compliance Officer",
    }

    BADGE_COLOR = {
        ADMINISTRATOR:      "#e53e3e",
        LICENSED_LAWYER:    "#dd6b20",
        PARALEGAL:          "#38a169",
        GENERAL_PUBLIC:     "#2c5282",
        COMPLIANCE_OFFICER: "#805ad5",
    }


# Permission matrix — True = allowed, False = denied, int = daily limit
_PERMS: dict[str, dict] = {
    UserRole.ADMINISTRATOR: {
        "view_all_queries": True, "modify_system_settings": True,
        "access_analytics": True, "generate_compliance_reports": True,
        "reset_user_passwords": True, "manage_user_accounts": True,
        "delete_user_data": True, "access_audit_logs": True,
        "document_upload": True, "case_law_research": True,
        "jurisdiction_comparison": True, "export_pdf_reports": True,
        "access_law_library": True, "cite_check": True,
        "create_client_folders": True, "priority_api": True,
        "rate_limit": 0,          # 0 = unlimited
        "max_tokens": 1000,
    },
    UserRole.LICENSED_LAWYER: {
        "view_all_queries": True, "modify_system_settings": False,
        "access_analytics": True, "generate_compliance_reports": False,
        "reset_user_passwords": False, "manage_user_accounts": False,
        "delete_user_data": False, "access_audit_logs": False,
        "document_upload": True, "case_law_research": True,
        "jurisdiction_comparison": True, "export_pdf_reports": True,
        "access_law_library": True, "cite_check": True,
        "create_client_folders": True, "priority_api": True,
        "rate_limit": 0,
        "max_tokens": 1000,
    },
    UserRole.PARALEGAL: {
        "view_all_queries": True, "modify_system_settings": False,
        "access_analytics": False, "generate_compliance_reports": False,
        "reset_user_passwords": False, "manage_user_accounts": False,
        "delete_user_data": False, "access_audit_logs": False,
        "document_upload": True, "case_law_research": False,
        "jurisdiction_comparison": False, "export_pdf_reports": False,
        "access_law_library": True, "cite_check": False,
        "create_client_folders": False, "priority_api": False,
        "rate_limit": 50,
        "max_tokens": 600,
    },
    UserRole.GENERAL_PUBLIC: {
        "view_all_queries": False, "modify_system_settings": False,
        "access_analytics": False, "generate_compliance_reports": False,
        "reset_user_passwords": False, "manage_user_accounts": False,
        "delete_user_data": False, "access_audit_logs": False,
        "document_upload": False, "case_law_research": False,
        "jurisdiction_comparison": False, "export_pdf_reports": False,
        "access_law_library": False, "cite_check": False,
        "create_client_folders": False, "priority_api": False,
        "rate_limit": 10,
        "max_tokens": 300,
    },
    UserRole.COMPLIANCE_OFFICER: {
        "view_all_queries": True, "modify_system_settings": False,
        "access_analytics": True, "generate_compliance_reports": True,
        "reset_user_passwords": False, "manage_user_accounts": False,
        "delete_user_data": False, "access_audit_logs": True,
        "document_upload": True, "case_law_research": True,
        "jurisdiction_comparison": True, "export_pdf_reports": True,
        "access_law_library": True, "cite_check": True,
        "create_client_folders": False, "priority_api": False,
        "rate_limit": 0,
        "max_tokens": 800,
    },
}


def get_permissions(role: str) -> dict:
    return _PERMS.get(role, _PERMS[UserRole.GENERAL_PUBLIC])


def has_permission(username: str, permission: str) -> bool:
    user = db.get_user(username)
    if not user:
        return False
    perms = get_permissions(user["role"])
    val = perms.get(permission, False)
    return bool(val) if not isinstance(val, int) else val > 0


# ── Password helpers ───────────────────────────────────────────────────────────

def _hash_password(password: str, salt: str) -> str:
    """PBKDF2-HMAC-SHA256 with pepper + salt."""
    peppered = (PEPPER + password).encode()
    return hashlib.pbkdf2_hmac("sha256", peppered, salt.encode(), PBKDF2_ITERATIONS).hex()


def _verify_password(password: str, salt: str, stored_hash: str) -> bool:
    computed = _hash_password(password, salt)
    return hmac.compare_digest(computed, stored_hash)


def _validate_username(username: str) -> Tuple[bool, str]:
    if not username or not isinstance(username, str):
        return False, "Username is required"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 30:
        return False, "Username must be less than 30 characters"
    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        return False, "Username can only contain letters, numbers, _ and -"
    return True, ""


def _validate_password(password: str) -> Tuple[bool, str]:
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, ""


# ── Public auth API ────────────────────────────────────────────────────────────

def register(username: str, password: str, confirm_password: str,
             email: str = "") -> Tuple[bool, str]:
    ok, msg = _validate_username(username)
    if not ok:
        return False, msg
    ok, msg = _validate_password(password)
    if not ok:
        return False, msg
    if password != confirm_password:
        return False, "Passwords do not match"
    if db.get_user_by_username_ci(username):
        return False, "Username already exists"

    salt = secrets.token_hex(32)
    pw_hash = _hash_password(password, salt)
    created = db.create_user(username, pw_hash, salt, email=email)
    if created:
        db.audit(username, "REGISTER", f"email={email}")
        return True, "Registration successful"
    return False, "Failed to save user — username may already exist"


def login(username: str, password: str) -> Tuple[bool, str]:
    if not username or not password:
        return False, "Username and password are required"

    # Brute-force check
    locked, until = db.is_account_locked(username)
    if locked:
        return False, f"Account locked until {until}. Too many failed attempts."

    user = db.get_user_by_username_ci(username)
    if not user:
        return False, "Invalid username or password"

    if _verify_password(password, user["salt"], user["password_hash"]):
        db.reset_failed_logins(user["username"])
        db.update_user(user["username"], last_login=datetime.utcnow().isoformat())
        db.audit(user["username"], "LOGIN")
        return True, user["username"]

    db.record_failed_login(username)
    db.audit(username, "LOGIN_FAILED")
    return False, "Invalid username or password"


def assign_role(target: str, role: str, assigned_by: str) -> Tuple[bool, str]:
    if role not in UserRole.ALL:
        return False, "Invalid role"
    if not db.get_user(target):
        return False, "User not found"
    db.update_user(target, role=role,
                   role_assigned_by=assigned_by,
                   role_assigned_at=datetime.utcnow().isoformat())
    db.audit(assigned_by, "ASSIGN_ROLE", f"target={target} role={role}")
    return True, f"Role {role} assigned to {target}"


def delete_account(username: str, deleted_by: str) -> Tuple[bool, str]:
    if not db.get_user(username):
        return False, "User not found"
    db.delete_user(username)
    db.audit(deleted_by, "DELETE_USER", f"target={username}")
    return True, f"User {username} deleted"


# ── Password reset ─────────────────────────────────────────────────────────────

def generate_reset_token(username: str) -> Optional[str]:
    user = db.get_user_by_username_ci(username)
    if not user:
        return None
    token = secrets.token_urlsafe(32)
    exp = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    db.update_user(user["username"], reset_token=token, reset_token_exp=exp)
    db.audit(user["username"], "RESET_TOKEN_GENERATED")
    return token


def reset_password(token: str, new_password: str, confirm: str) -> Tuple[bool, str]:
    ok, msg = _validate_password(new_password)
    if not ok:
        return False, msg
    if new_password != confirm:
        return False, "Passwords do not match"

    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE reset_token=?", (token,)
        ).fetchone()

    if not row:
        return False, "Invalid or expired reset token"
    row = dict(row)
    if datetime.fromisoformat(row["reset_token_exp"]) < datetime.utcnow():
        return False, "Reset token has expired"

    salt = secrets.token_hex(32)
    pw_hash = _hash_password(new_password, salt)
    db.update_user(row["username"], password_hash=pw_hash, salt=salt,
                   reset_token=None, reset_token_exp=None)
    db.audit(row["username"], "PASSWORD_RESET")
    return True, "Password reset successfully"


# ── Session helpers ────────────────────────────────────────────────────────────

def init_session():
    """Enforce session timeout on every page load."""
    if "username" not in st.session_state:
        return
    last_active = st.session_state.get("last_active")
    if last_active:
        elapsed = (datetime.utcnow() - datetime.fromisoformat(last_active)).total_seconds()
        if elapsed > SESSION_TIMEOUT_MINUTES * 60:
            logout()
            st.warning("Your session has expired. Please log in again.")
            st.rerun()
    # Always update last_active on every call
    st.session_state["last_active"] = datetime.utcnow().isoformat()


def logout():
    username = st.session_state.get("username")
    if username:
        db.audit(username, "LOGOUT")
    for key in ["username", "last_active", "disclaimer_accepted"]:
        st.session_state.pop(key, None)


def current_user() -> Optional[str]:
    return st.session_state.get("username")


def current_role() -> str:
    username = current_user()
    if not username:
        return UserRole.GENERAL_PUBLIC
    user = db.get_user(username)
    return user["role"] if user else UserRole.GENERAL_PUBLIC


# ── Rate limiting (per-session, in-memory) ─────────────────────────────────────

def can_query(username: str) -> Tuple[bool, str]:
    """Check daily query limit stored in session state."""
    role = current_role()
    limit = get_permissions(role).get("rate_limit", 10)
    if limit == 0:
        return True, "unlimited"

    today = datetime.utcnow().date().isoformat()
    key = f"query_count_{today}"
    count = st.session_state.get(key, 0)
    if count >= limit:
        return False, f"Daily limit of {limit} queries reached"
    return True, f"{limit - count} queries remaining today"


def increment_query_count():
    today = datetime.utcnow().date().isoformat()
    key = f"query_count_{today}"
    st.session_state[key] = st.session_state.get(key, 0) + 1


# ── Input validation helpers ───────────────────────────────────────────────────

def validate_file(uploaded_file) -> Tuple[bool, str]:
    """Validate file size and MIME type by magic bytes."""
    if uploaded_file is None:
        return False, "No file provided"

    size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File exceeds {MAX_FILE_SIZE_MB} MB limit"

    header = uploaded_file.getvalue()[:8]
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        if not header.startswith(b"%PDF"):
            return False, "File does not appear to be a valid PDF"
    elif name.endswith(".docx"):
        if not header.startswith(b"PK"):
            return False, "File does not appear to be a valid DOCX"
    else:
        return False, "Only PDF and DOCX files are supported"

    return True, ""


def validate_url(url: str) -> Tuple[bool, str]:
    """Validate URL against domain whitelist (if configured)."""
    if not url or not url.startswith(("http://", "https://")):
        return False, "URL must start with http:// or https://"
    if not ALLOWED_URL_DOMAINS:
        return True, ""
    from urllib.parse import urlparse
    netloc = urlparse(url).netloc.lower().split(":")[0]  # strip port
    for allowed in ALLOWED_URL_DOMAINS:
        allowed = allowed.lower()
        if netloc == allowed or netloc.endswith("." + allowed):
            return True, ""
    return False, f"Domain not in allowed list: {netloc}"


# ── OAuth2 ─────────────────────────────────────────────────────────────────────

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
MS_CLIENT_ID         = os.getenv("MICROSOFT_CLIENT_ID", "")
MS_CLIENT_SECRET     = os.getenv("MICROSOFT_CLIENT_SECRET", "")

_OAUTH2_CONFIGS = {
    "google": {
        "auth_url":      "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url":     "https://oauth2.googleapis.com/token",
        "userinfo_url":  "https://www.googleapis.com/oauth2/v2/userinfo",
        "client_id":     GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "scope":         "openid email profile",
        "redirect_uri":  os.getenv("OAUTH2_REDIRECT_URI", "http://localhost:8501"),
    },
    "microsoft": {
        "auth_url":      "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url":     "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url":  "https://graph.microsoft.com/v1.0/me",
        "client_id":     MS_CLIENT_ID,
        "client_secret": MS_CLIENT_SECRET,
        "scope":         "https://graph.microsoft.com/User.Read openid email profile",
        "redirect_uri":  os.getenv("OAUTH2_REDIRECT_URI", "http://localhost:8501/"),
    },
}


def get_oauth2_auth_url(provider: str) -> Optional[str]:
    cfg = _OAUTH2_CONFIGS.get(provider)
    if not cfg or not cfg["client_id"]:
        return None
    from urllib.parse import urlencode
    # Encode provider into state so we don't need session storage
    # Format: provider:random_token  (base64 encoded)
    import base64
    raw_state = f"{provider}:{secrets.token_urlsafe(16)}"
    state = base64.urlsafe_b64encode(raw_state.encode()).decode()
    # Also store in session as backup
    st.session_state[f"oauth2_state_{provider}"] = state
    params = {
        "client_id":     cfg["client_id"],
        "redirect_uri":  cfg["redirect_uri"],
        "scope":         cfg["scope"],
        "response_type": "code",
        "state":         state,
    }
    return f"{cfg['auth_url']}?{urlencode(params)}"


def handle_oauth2_callback() -> Tuple[Optional[str], Optional[str]]:
    """Process OAuth2 callback; returns (username, error_message)."""
    import requests as req
    import base64
    qp = st.query_params
    if "code" not in qp or "state" not in qp:
        return None, None

    code  = qp["code"]
    state = qp["state"]

    # Decode provider from state (works even after session reset)
    provider = None
    try:
        decoded = base64.urlsafe_b64decode(state.encode()).decode()
        if ":" in decoded:
            provider = decoded.split(":")[0]
            if provider not in ("google", "microsoft"):
                provider = None
    except Exception:
        provider = None

    # Fallback: check session state
    if not provider:
        for p in ("google", "microsoft"):
            key = f"oauth2_state_{p}"
            if st.session_state.get(key) == state:
                provider = p
                break

    if not provider:
        return None, "Invalid OAuth2 state — please try logging in again"

    # Clean up session state
    st.session_state.pop(f"oauth2_state_{provider}", None)

    cfg = _OAUTH2_CONFIGS[provider]
    # Exchange code for token
    try:
        resp = req.post(cfg["token_url"], data={
            "client_id":     cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "code":          code,
            "redirect_uri":  cfg["redirect_uri"],
            "grant_type":    "authorization_code",
        }, timeout=10)
        resp.raise_for_status()
        token_data = resp.json()
    except Exception as e:
        logger.error("OAuth2 token exchange failed: %s", e)
        return None, "Failed to obtain access token"

    access_token = token_data.get("access_token")
    if not access_token:
        return None, "No access token in response"

    # Get user info
    try:
        info_resp = req.get(cfg["userinfo_url"],
                            headers={"Authorization": f"Bearer {access_token}"},
                            timeout=10)
        if info_resp.status_code != 200:
            logger.error("OAuth2 userinfo error %s: %s", info_resp.status_code, info_resp.text[:300])
            return None, f"Failed to obtain user information (HTTP {info_resp.status_code})"
        user_info = info_resp.json()
    except Exception as e:
        logger.error("OAuth2 userinfo failed: %s", e)
        return None, f"Failed to obtain user information: {e}"

    # Derive username and email
    if provider == "google":
        email    = user_info.get("email", "")
        oauth_id = user_info.get("id", "")
    else:
        # Microsoft returns mail, userPrincipalName, or id
        email    = (user_info.get("mail") or
                    user_info.get("userPrincipalName") or
                    user_info.get("email") or "")
        oauth_id = user_info.get("id", "")
        logger.info("Microsoft user_info keys: %s", list(user_info.keys()))

    username = re.sub(r"[^a-zA-Z0-9_\-]", "_", email.split("@")[0])[:30] if email else None
    if not username:
        return None, "Could not determine username from OAuth2 provider"

    # Register if new
    existing = db.get_user(username)
    if not existing:
        salt    = secrets.token_hex(32)
        pw_hash = _hash_password(secrets.token_urlsafe(32), salt)   # random unusable password
        db.create_user(username, pw_hash, salt,
                       role=UserRole.GENERAL_PUBLIC,
                       email=email,
                       oauth2_provider=provider,
                       oauth2_id=oauth_id)
        db.audit(username, "OAUTH2_REGISTER", f"provider={provider}")
    else:
        db.audit(username, "OAUTH2_LOGIN", f"provider={provider}")

    db.update_user(username, last_login=datetime.utcnow().isoformat())
    return username, None
