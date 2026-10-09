"""Note management service."""

from app.database import db
from app.utils.validators import validate_nonempty, validate_length, validate_category, sanitize_text
from app.utils.helpers import now_iso
from app.utils.logger import get_logger

_log = get_logger("studydesk.notes")

CATEGORIES = ("Study", "Programming", "Project", "Personal", "Other")


def add_note(title, content="", category="Other"):
    ok, val = validate_nonempty(title, "Note title")
    if not ok:
        return False, val, None
    ok, title = validate_length(val, 1, 200, "Note title")
    if not ok:
        return False, title, None
    ok, category = validate_category(category, CATEGORIES, "Category")
    if not ok:
        return False, category, None
    content = sanitize_text(content, 20000)
    now = now_iso()
    try:
        cur = db.execute(
            "INSERT INTO notes (title, content, category, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, content, category, now, now),
        )
        db.log_activity("notes", "add", title)
        return True, "Note created.", cur.lastrowid
    except Exception as exc:
        _log.error("Failed to add note: %s", exc)
        return False, "Could not save the note.", None


def update_note(note_id, title, content="", category="Other"):
    ok, val = validate_nonempty(title, "Note title")
    if not ok:
        return False, val
    ok, title = validate_length(val, 1, 200, "Note title")
    if not ok:
        return False, title
    ok, category = validate_category(category, CATEGORIES, "Category")
    if not ok:
        return False, category
    content = sanitize_text(content, 20000)
    try:
        db.execute(
            "UPDATE notes SET title=?, content=?, category=?, updated_at=? WHERE id=?",
            (title, content, category, now_iso(), note_id),
        )
        db.log_activity("notes", "edit", title)
        return True, "Note updated."
    except Exception as exc:
        _log.error("Failed to update note %s: %s", note_id, exc)
        return False, "Could not update the note."


def delete_note(note_id):
    try:
        db.execute("DELETE FROM notes WHERE id=?", (note_id,))
        db.log_activity("notes", "delete", str(note_id))
        return True, "Note deleted."
    except Exception as exc:
        _log.error("Failed to delete note: %s", exc)
        return False, "Could not delete the note."


def get_all_notes(search="", category_filter=""):
    sql = "SELECT * FROM notes WHERE 1=1"
    params = []
    if search:
        sql += " AND (title LIKE ? OR content LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if category_filter:
        sql += " AND category=?"
        params.append(category_filter)
    sql += " ORDER BY updated_at DESC"
    try:
        return db.query(sql, params)
    except Exception as exc:
        _log.error("Failed to fetch notes: %s", exc)
        return []


def get_note(note_id):
    return db.query_one("SELECT * FROM notes WHERE id=?", (note_id,))


def get_count():
    try:
        return db.query_one("SELECT COUNT(*) AS c FROM notes")["c"]
    except Exception:
        return 0