"""Settings service - persistent key/value settings stored in SQLite."""

from app.database import db
from app.database.schema import get_default_settings
from app.utils.logger import get_logger

_log = get_logger("studydesk.settings")

_cache = None


def _load_all():
    global _cache
    if _cache is None:
        defaults = get_default_settings()
        try:
            rows = db.query("SELECT key, value FROM settings")
            _cache = {r["key"]: r["value"] for r in rows}
        except Exception as exc:
            _log.error("Failed to load settings: %s", exc)
            _cache = {}
        for k, v in defaults.items():
            if k not in _cache:
                _cache[k] = str(v)
    return _cache


def get_setting(key, default=None):
    data = _load_all()
    if key in data:
        return data[key]
    return default


def get_int(key, default=0):
    try:
        return int(get_setting(key, default))
    except (TypeError, ValueError):
        return default


def get_float(key, default=0.0):
    try:
        return float(get_setting(key, default))
    except (TypeError, ValueError):
        return default


def set_setting(key, value):
    try:
        db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )
        _load_all()[key] = str(value)
        return True
    except Exception as exc:
        _log.error("Failed to save setting %s: %s", key, exc)
        return False


def get_all():
    return dict(_load_all())


def reset_cache():
    global _cache
    _cache = None