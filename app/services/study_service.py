"""Study planner service."""

from app.database import db
from app.utils.validators import validate_nonempty, validate_length, validate_float, sanitize_text
from app.utils.helpers import now_iso, today_iso
from app.utils.logger import get_logger

_log = get_logger("studydesk.study")


def add_subject(name, daily_target=0, weekly_target=0):
    ok, val = validate_nonempty(name, "Subject name")
    if not ok:
        return False, val, None
    ok, name = validate_length(val, 1, 100, "Subject name")
    if not ok:
        return False, name, None
    ok, daily_target = validate_float(daily_target, 0, 24, "Daily target")
    if not ok:
        return False, daily_target, None
    ok, weekly_target = validate_float(weekly_target, 0, 168, "Weekly target")
    if not ok:
        return False, weekly_target, None
    now = now_iso()
    try:
        cur = db.execute(
            "INSERT INTO subjects (name, daily_target, weekly_target, "
            "completed_minutes, created_at, updated_at) VALUES (?, ?, ?, 0, ?, ?)",
            (name, daily_target, weekly_target, now, now),
        )
        db.log_activity("study", "add_subject", name)
        return True, "Subject added.", cur.lastrowid
    except Exception as exc:
        _log.error("Failed to add subject: %s", exc)
        return False, "Could not save the subject.", None


def update_subject(subject_id, name, daily_target=0, weekly_target=0):
    ok, val = validate_nonempty(name, "Subject name")
    if not ok:
        return False, val
    ok, name = validate_length(val, 1, 100, "Subject name")
    if not ok:
        return False, name
    ok, daily_target = validate_float(daily_target, 0, 24, "Daily target")
    if not ok:
        return False, daily_target
    ok, weekly_target = validate_float(weekly_target, 0, 168, "Weekly target")
    if not ok:
        return False, weekly_target
    try:
        db.execute(
            "UPDATE subjects SET name=?, daily_target=?, weekly_target=?, updated_at=? "
            "WHERE id=?",
            (name, daily_target, weekly_target, now_iso(), subject_id),
        )
        db.log_activity("study", "edit_subject", name)
        return True, "Subject updated."
    except Exception as exc:
        _log.error("Failed to update subject: %s", exc)
        return False, "Could not update the subject."


def delete_subject(subject_id):
    try:
        db.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
        db.log_activity("study", "delete_subject", str(subject_id))
        return True, "Subject deleted."
    except Exception as exc:
        _log.error("Failed to delete subject: %s", exc)
        return False, "Could not delete the subject."


def get_all_subjects():
    try:
        return db.query("SELECT * FROM subjects ORDER BY name ASC")
    except Exception as exc:
        _log.error("Failed to fetch subjects: %s", exc)
        return []


def get_subject(subject_id):
    return db.query_one("SELECT * FROM subjects WHERE id=?", (subject_id,))


def add_study_time(subject_id, minutes):
    ok, minutes = validate_float(minutes, 0, 1440, "Minutes")
    if not ok:
        return False, minutes
    minutes = int(minutes)
    try:
        subj = get_subject(subject_id)
        if not subj:
            return False, "Subject not found."
        db.execute(
            "UPDATE subjects SET completed_minutes=completed_minutes+?, updated_at=? WHERE id=?",
            (minutes, now_iso(), subject_id),
        )
        db.execute(
            "INSERT INTO study_sessions (subject_id, subject_name, minutes, "
            "session_date, created_at) VALUES (?, ?, ?, ?, ?)",
            (subject_id, subj["name"], minutes, today_iso(), now_iso()),
        )
        db.log_activity("study", "log_time", f"{subj['name']}:{minutes}m")
        return True, f"Added {minutes} minutes to {subj['name']}."
    except Exception as exc:
        _log.error("Failed to add study time: %s", exc)
        return False, "Could not record study time."


def reset_progress(subject_id):
    try:
        db.execute(
            "UPDATE subjects SET completed_minutes=0, updated_at=? WHERE id=?",
            (now_iso(), subject_id),
        )
        return True, "Progress reset."
    except Exception as exc:
        _log.error("Failed to reset progress: %s", exc)
        return False, "Could not reset progress."


def get_today_study_minutes():
    today = today_iso()
    try:
        row = db.query_one(
            "SELECT COALESCE(SUM(minutes), 0) AS total FROM study_sessions "
            "WHERE session_date=?", (today,)
        )
        return row["total"] if row else 0
    except Exception:
        return 0


def get_total_study_minutes():
    try:
        row = db.query_one(
            "SELECT COALESCE(SUM(minutes), 0) AS total FROM study_sessions"
        )
        return row["total"] if row else 0
    except Exception:
        return 0


def get_progress_percent(subject):
    daily = subject.get("daily_target", 0) or 0
    completed = subject.get("completed_minutes", 0) or 0
    if daily <= 0:
        return 0
    target_minutes = daily * 60
    return min(100, int((completed / target_minutes) * 100))