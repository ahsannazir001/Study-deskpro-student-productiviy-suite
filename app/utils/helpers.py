"""General helper utilities."""

import os
import sys
from datetime import datetime, date, timedelta


def get_app_data_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
        data_dir = os.path.join(base, "data")
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_log_dir():
    data_dir = get_app_data_dir()
    log_dir = os.path.join(data_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_assets_dir():
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidate = os.path.join(meipass, "assets")
            if os.path.exists(candidate):
                return candidate
        base = os.path.dirname(sys.executable)
        candidate = os.path.join(base, "assets")
        if os.path.exists(candidate):
            return candidate
        candidate = os.path.join(base, "internal", "assets")
        if os.path.exists(candidate):
            return candidate
        return os.path.join(base, "assets")
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "assets")


def get_icon_path():
    assets = get_assets_dir()
    ico = os.path.join(assets, "icons", "studydesk.ico")
    return ico if os.path.exists(ico) else None


def get_png_icon_path():
    assets = get_assets_dir()
    png = os.path.join(assets, "icons", "studydesk.png")
    return png if os.path.exists(png) else None


def today_iso():
    return date.today().isoformat()


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def format_duration(minutes):
    if minutes is None or minutes < 0:
        return "0m"
    h = int(minutes) // 60
    m = int(minutes) % 60
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


def format_currency(amount, symbol="Rs."):
    try:
        amt = float(amount)
    except (TypeError, ValueError):
        amt = 0.0
    return f"{symbol} {amt:,.2f}"


def month_range(year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start.isoformat(), end.isoformat()


def relative_time(iso_str):
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
    except ValueError:
        return iso_str
    delta = datetime.now() - dt
    secs = int(delta.total_seconds())
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{secs // 60}m ago"
    if secs < 86400:
        return f"{secs // 3600}h ago"
    if secs < 604800:
        return f"{secs // 86400}d ago"
    return dt.strftime("%Y-%m-%d %H:%M")


def safe_clipboard_set(root, text):
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        return True
    except Exception:
        return False