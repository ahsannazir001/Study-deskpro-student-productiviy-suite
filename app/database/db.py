"""Database connection and initialization.

Provides a thread-safe connection helper and idempotent initialization that
creates missing tables and seeds default settings without destroying data.
"""

import os
import sqlite3
import threading

from app.database import schema
from app.utils.logger import get_logger
from app.utils.helpers import get_app_data_dir, now_iso

_log = get_logger("studydesk.db")

_db_path = None
_local = threading.local()


def get_db_path():
    global _db_path
    if _db_path is None:
        _db_path = os.path.join(get_app_data_dir(), "studydesk.db")
    return _db_path


def _row_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_connection():
    """Return a SQLite connection for the current thread.

    Each thread gets its own connection. Row factory returns dicts.
    """
    conn = getattr(_local, "conn", None)
    if conn is None:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = _row_factory
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return conn


def close_connection():
    conn = getattr(_local, "conn", None)
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
        _local.conn = None


def execute(sql, params=()):
    conn = get_connection()
    cur = conn.execute(sql, params)
    conn.commit()
    return cur


def query(sql, params=()):
    conn = get_connection()
    return conn.execute(sql, params).fetchall()


def query_one(sql, params=()):
    conn = get_connection()
    return conn.execute(sql, params).fetchone()


def initialize():
    """Create tables and seed default settings. Idempotent and safe."""
    try:
        os.makedirs(os.path.dirname(get_db_path()), exist_ok=True)
    except OSError:
        pass

    conn = get_connection()
    try:
        for stmt in schema.get_schema():
            conn.execute(stmt)

        defaults = schema.get_default_settings()
        for key, value in defaults.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value)),
            )

        conn.execute(
            "INSERT OR IGNORE INTO users (id, username, display_name, created_at) "
            "VALUES (1, 'default', 'Student', ?)",
            (now_iso(),),
        )
        conn.commit()
        _log.info("Database initialized at %s", get_db_path())
        return True
    except sqlite3.Error as exc:
        _log.error("Database initialization failed: %s", exc)
        return False


def log_activity(module, action, detail=""):
    try:
        execute(
            "INSERT INTO activity_logs (module, action, detail, created_at) "
            "VALUES (?, ?, ?, ?)",
            (module, action, str(detail)[:500], now_iso()),
        )
    except sqlite3.Error:
        pass