"""
Database layer — SQLite with indexes, CASCADE deletes,
document storage, data export/deletion for GDPR, retention policy.
"""

import sqlite3
import os
import logging
import shutil
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = os.getenv("DB_PATH", "legal_ai.db")
QUERY_RETENTION_DAYS = int(os.getenv("QUERY_RETENTION_DAYS", "90"))
logger = logging.getLogger(__name__)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables and indexes."""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            username        TEXT PRIMARY KEY,
            password_hash   TEXT NOT NULL,
            salt            TEXT NOT NULL,
            role            TEXT NOT NULL DEFAULT 'general_public',
            created_at      TEXT NOT NULL,
            last_login      TEXT,
            role_assigned_by TEXT,
            role_assigned_at TEXT,
            oauth2_provider TEXT,
            oauth2_id       TEXT,
            email           TEXT,
            email_verified  INTEGER NOT NULL DEFAULT 0,
            reset_token     TEXT,
            reset_token_exp TEXT,
            failed_logins   INTEGER NOT NULL DEFAULT 0,
            locked_until    TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          TEXT NOT NULL,
            username    TEXT,
            action      TEXT NOT NULL,
            detail      TEXT,
            ip          TEXT
        );

        CREATE TABLE IF NOT EXISTS cases (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
            name         TEXT NOT NULL,
            client_name  TEXT,
            case_type    TEXT,
            jurisdiction TEXT,
            status       TEXT NOT NULL DEFAULT 'Active',
            created_at   TEXT NOT NULL,
            updated_at   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS time_entries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
            case_id     INTEGER REFERENCES cases(id) ON DELETE SET NULL,
            activity    TEXT,
            hours       REAL NOT NULL,
            rate        REAL NOT NULL,
            description TEXT,
            logged_at   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
            filename    TEXT NOT NULL,
            category    TEXT,
            case_id     INTEGER REFERENCES cases(id) ON DELETE SET NULL,
            content     BLOB,
            text_content TEXT,
            uploaded_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS query_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          TEXT NOT NULL,
            username    TEXT,
            jurisdiction TEXT,
            query       TEXT,
            response    TEXT
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_users_role       ON users(role);
        CREATE INDEX IF NOT EXISTS idx_audit_username   ON audit_log(username);
        CREATE INDEX IF NOT EXISTS idx_audit_ts         ON audit_log(ts);
        CREATE INDEX IF NOT EXISTS idx_audit_action     ON audit_log(action);
        CREATE INDEX IF NOT EXISTS idx_cases_username   ON cases(username);
        CREATE INDEX IF NOT EXISTS idx_time_username    ON time_entries(username);
        CREATE INDEX IF NOT EXISTS idx_docs_username    ON documents(username);
        CREATE INDEX IF NOT EXISTS idx_query_username   ON query_log(username);
        CREATE INDEX IF NOT EXISTS idx_query_ts         ON query_log(ts);
        """)
    logger.info("Database initialised at %s", DB_PATH)


# ── Audit ──────────────────────────────────────────────────────────────────────

def audit(username: Optional[str], action: str, detail: str = "", ip: str = ""):
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO audit_log(ts,username,action,detail,ip) VALUES(?,?,?,?,?)",
                (datetime.utcnow().isoformat(), username, action, detail, ip)
            )
    except Exception as e:
        logger.error("Audit log failed: %s", e)


def get_audit_log(limit: int = 200, username: Optional[str] = None) -> list:
    with get_conn() as conn:
        if username:
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE username=? ORDER BY id DESC LIMIT ?",
                (username, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
    return [dict(r) for r in rows]


# ── Users ──────────────────────────────────────────────────────────────────────

def get_user(username: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    return dict(row) if row else None


def get_user_by_username_ci(username: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE lower(username)=lower(?)", (username,)
        ).fetchone()
    return dict(row) if row else None


def create_user(username: str, password_hash: str, salt: str, role: str = "general_public",
                email: str = "", oauth2_provider: str = "", oauth2_id: str = "") -> bool:
    try:
        with get_conn() as conn:
            conn.execute(
                """INSERT INTO users(username,password_hash,salt,role,created_at,email,oauth2_provider,oauth2_id)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (username, password_hash, salt, role,
                 datetime.utcnow().isoformat(), email, oauth2_provider, oauth2_id)
            )
        return True
    except sqlite3.IntegrityError:
        return False


def update_user(username: str, **fields) -> bool:
    if not fields:
        return False
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [username]
    try:
        with get_conn() as conn:
            conn.execute(f"UPDATE users SET {sets} WHERE username=?", vals)
        return True
    except Exception as e:
        logger.error("update_user failed: %s", e)
        return False


def list_users(limit: int = 100, offset: int = 0) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    return [dict(r) for r in rows]


def count_users() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def delete_user(username: str) -> bool:
    try:
        with get_conn() as conn:
            conn.execute("DELETE FROM users WHERE username=?", (username,))
        return True
    except Exception as e:
        logger.error("delete_user failed: %s", e)
        return False


# ── Brute-force protection ─────────────────────────────────────────────────────

def record_failed_login(username: str, max_attempts: int = 5, lockout_minutes: int = 15):
    user = get_user_by_username_ci(username)
    if not user:
        return
    fails = (user.get("failed_logins") or 0) + 1
    locked_until = None
    if fails >= max_attempts:
        locked_until = (datetime.utcnow() + timedelta(minutes=lockout_minutes)).isoformat()
        audit(username, "ACCOUNT_LOCKED", f"after {fails} failed attempts")
    update_user(user["username"], failed_logins=fails, locked_until=locked_until)


def reset_failed_logins(username: str):
    update_user(username, failed_logins=0, locked_until=None)


def is_account_locked(username: str) -> tuple:
    """Returns (is_locked, unlock_time_str)."""
    user = get_user_by_username_ci(username)
    if not user or not user.get("locked_until"):
        return False, ""
    locked_until = datetime.fromisoformat(user["locked_until"])
    if datetime.utcnow() < locked_until:
        return True, user["locked_until"][:16].replace("T", " ") + " UTC"
    # Auto-unlock
    reset_failed_logins(user["username"])
    return False, ""


# ── Cases ──────────────────────────────────────────────────────────────────────

def create_case(username: str, name: str, client_name: str, case_type: str, jurisdiction: str) -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO cases(username,name,client_name,case_type,jurisdiction,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
            (username, name, client_name, case_type, jurisdiction, now, now)
        )
        return cur.lastrowid


def get_cases(username: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM cases WHERE username=? ORDER BY updated_at DESC", (username,)
        ).fetchall()
    return [dict(r) for r in rows]


def update_case_status(case_id: int, status: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE cases SET status=?, updated_at=? WHERE id=?",
            (status, datetime.utcnow().isoformat(), case_id)
        )


# ── Time entries ───────────────────────────────────────────────────────────────

def log_time(username: str, case_id: Optional[int], activity: str,
             hours: float, rate: float, description: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO time_entries(username,case_id,activity,hours,rate,description,logged_at) VALUES(?,?,?,?,?,?,?)",
            (username, case_id, activity, hours, rate, description, datetime.utcnow().isoformat())
        )
        return cur.lastrowid


def get_time_entries(username: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM time_entries WHERE username=? ORDER BY logged_at DESC", (username,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Documents ──────────────────────────────────────────────────────────────────

def save_document(username: str, filename: str, content: bytes,
                  text_content: str, category: str = "", case_id: Optional[int] = None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO documents(username,filename,category,case_id,content,text_content,uploaded_at) VALUES(?,?,?,?,?,?,?)",
            (username, filename, category, case_id, content, text_content[:50000],
             datetime.utcnow().isoformat())
        )
        return cur.lastrowid


def get_documents(username: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id,username,filename,category,case_id,uploaded_at FROM documents "
            "WHERE username=? ORDER BY uploaded_at DESC", (username,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_document_content(doc_id: int, username: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id=? AND username=?", (doc_id, username)
        ).fetchone()
    return dict(row) if row else None


def delete_document(doc_id: int, username: str) -> bool:
    try:
        with get_conn() as conn:
            conn.execute("DELETE FROM documents WHERE id=? AND username=?", (doc_id, username))
        return True
    except Exception as e:
        logger.error("delete_document failed: %s", e)
        return False


def search_documents(username: str, query: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id,filename,category,uploaded_at FROM documents "
            "WHERE username=? AND (filename LIKE ? OR text_content LIKE ?) ORDER BY uploaded_at DESC",
            (username, f"%{query}%", f"%{query}%")
        ).fetchall()
    return [dict(r) for r in rows]


# ── Query log ──────────────────────────────────────────────────────────────────

def log_query_db(username: Optional[str], jurisdiction: str, query: str, response: str):
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO query_log(ts,username,jurisdiction,query,response) VALUES(?,?,?,?,?)",
                (datetime.utcnow().isoformat(), username, jurisdiction, query[:2000], response[:2000])
            )
    except Exception as e:
        logger.error("log_query_db failed: %s", e)


def get_query_history(username: str, limit: int = 50) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id,ts,jurisdiction,query,response FROM query_log "
            "WHERE username=? ORDER BY id DESC LIMIT ?", (username, limit)
        ).fetchall()
    return [dict(r) for r in rows]


def search_query_history(username: str, search: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id,ts,jurisdiction,query FROM query_log "
            "WHERE username=? AND query LIKE ? ORDER BY id DESC LIMIT 50",
            (username, f"%{search}%")
        ).fetchall()
    return [dict(r) for r in rows]


# ── GDPR: data export & deletion ───────────────────────────────────────────────

def export_user_data(username: str) -> dict:
    """Export all data for a user (GDPR right to portability)."""
    user = get_user(username)
    if user:
        user.pop("password_hash", None)
        user.pop("salt", None)
        user.pop("reset_token", None)
    return {
        "user":         user,
        "cases":        get_cases(username),
        "time_entries": get_time_entries(username),
        "documents":    get_documents(username),
        "query_history": get_query_history(username, limit=1000),
        "audit_log":    get_audit_log(limit=1000, username=username),
        "exported_at":  datetime.utcnow().isoformat(),
    }


def delete_all_user_data(username: str) -> bool:
    """Delete all user data (GDPR right to be forgotten). CASCADE handles related tables."""
    try:
        with get_conn() as conn:
            conn.execute("DELETE FROM query_log WHERE username=?", (username,))
            conn.execute("DELETE FROM audit_log WHERE username=?", (username,))
            conn.execute("DELETE FROM users WHERE username=?", (username,))
        return True
    except Exception as e:
        logger.error("delete_all_user_data failed: %s", e)
        return False


# ── Retention policy ───────────────────────────────────────────────────────────

def apply_retention_policy():
    """Delete query logs older than QUERY_RETENTION_DAYS."""
    cutoff = (datetime.utcnow() - timedelta(days=QUERY_RETENTION_DAYS)).isoformat()
    try:
        with get_conn() as conn:
            result = conn.execute("DELETE FROM query_log WHERE ts < ?", (cutoff,))
            deleted = result.rowcount
        if deleted:
            logger.info("Retention policy: deleted %d old query log entries", deleted)
            audit(None, "RETENTION_CLEANUP", f"deleted={deleted} cutoff={cutoff[:10]}")
    except Exception as e:
        logger.error("Retention policy failed: %s", e)


# ── Backup ─────────────────────────────────────────────────────────────────────

def backup_db() -> str:
    """Atomic backup including WAL file."""
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = f"legal_ai_backup_{ts}.db"
    try:
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(backup_path)
        src.backup(dst)
        src.close()
        dst.close()
        audit(None, "DB_BACKUP", f"path={backup_path}")
        return backup_path
    except Exception as e:
        logger.error("Backup failed: %s", e)
        raise
