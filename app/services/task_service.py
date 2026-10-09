"""Task management service."""

from app.database import db
from app.utils.validators import (
    validate_nonempty, validate_length, validate_priority, validate_status,
    validate_optional_date, sanitize_text,
)
from app.utils.helpers import now_iso, today_iso
from app.utils.logger import get_logger

_log = get_logger("studydesk.tasks")


def add_task(title, description="", priority="Medium", due_date=""):
    ok, val = validate_nonempty(title, "Task title")
    if not ok:
        return False, val, None
    ok, title = validate_length(val, 1, 200, "Task title")
    if not ok:
        return False, title, None
    ok, priority = validate_priority(priority)
    if not ok:
        return False, priority, None
    ok, due_date = validate_optional_date(due_date)
    if not ok:
        return False, due_date, None
    description = sanitize_text(description, 5000)
    now = now_iso()
    try:
        cur = db.execute(
            "INSERT INTO tasks (title, description, priority, status, due_date, "
            "created_at, updated_at) VALUES (?, ?, ?, 'Pending', ?, ?, ?)",
            (title, description, priority, due_date, now, now),
        )
        db.log_activity("tasks", "add", title)
        _log.info("Task added: %s", title)
        return True, "Task added successfully.", cur.lastrowid
    except Exception as exc:
        _log.error("Failed to add task: %s", exc)
        return False, "Could not save the task.", None


def update_task(task_id, title, description="", priority="Medium",
                status="Pending", due_date=""):
    ok, val = validate_nonempty(title, "Task title")
    if not ok:
        return False, val
    ok, title = validate_length(val, 1, 200, "Task title")
    if not ok:
        return False, title
    ok, priority = validate_priority(priority)
    if not ok:
        return False, priority
    ok, status = validate_status(status)
    if not ok:
        return False, status
    ok, due_date = validate_optional_date(due_date)
    if not ok:
        return False, due_date
    description = sanitize_text(description, 5000)
    try:
        db.execute(
            "UPDATE tasks SET title=?, description=?, priority=?, status=?, "
            "due_date=?, updated_at=? WHERE id=?",
            (title, description, priority, status, due_date, now_iso(), task_id),
        )
        db.log_activity("tasks", "edit", title)
        return True, "Task updated successfully."
    except Exception as exc:
        _log.error("Failed to update task %s: %s", task_id, exc)
        return False, "Could not update the task."


def delete_task(task_id):
    try:
        db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        db.log_activity("tasks", "delete", str(task_id))
        return True, "Task deleted."
    except Exception as exc:
        _log.error("Failed to delete task %s: %s", task_id, exc)
        return False, "Could not delete the task."


def set_status(task_id, status):
    ok, status = validate_status(status)
    if not ok:
        return False, status
    try:
        db.execute("UPDATE tasks SET status=?, updated_at=? WHERE id=?",
                   (status, now_iso(), task_id))
        db.log_activity("tasks", "status", status)
        return True, f"Task marked as {status}."
    except Exception as exc:
        _log.error("Failed to set status: %s", exc)
        return False, "Could not update task status."


def get_all_tasks(search="", priority_filter="", status_filter="",
                  sort_by="created_desc"):
    sql = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if search:
        sql += " AND (title LIKE ? OR description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if priority_filter:
        sql += " AND priority=?"
        params.append(priority_filter)
    if status_filter:
        sql += " AND status=?"
        params.append(status_filter)
    sort_map = {
        "created_desc": "created_at DESC",
        "created_asc": "created_at ASC",
        "due_asc": "due_date ASC",
        "due_desc": "due_date DESC",
        "priority_desc": "CASE priority WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END DESC",
        "title_asc": "title ASC",
    }
    sql += " ORDER BY " + sort_map.get(sort_by, "created_at DESC")
    try:
        return db.query(sql, params)
    except Exception as exc:
        _log.error("Failed to fetch tasks: %s", exc)
        return []


def get_task(task_id):
    return db.query_one("SELECT * FROM tasks WHERE id=?", (task_id,))


def get_stats():
    today = today_iso()
    try:
        total = db.query_one("SELECT COUNT(*) AS c FROM tasks")["c"]
        completed = db.query_one("SELECT COUNT(*) AS c FROM tasks WHERE status='Completed'")["c"]
        pending = total - completed
        todays = db.query_one("SELECT COUNT(*) AS c FROM tasks WHERE due_date=?", (today,))["c"]
        overdue = db.query_one(
            "SELECT COUNT(*) AS c FROM tasks WHERE status='Pending' AND due_date < ? AND due_date != ''",
            (today,),
        )["c"]
        return {"total": total, "completed": completed, "pending": pending,
                "today": todays, "overdue": overdue}
    except Exception as exc:
        _log.error("Failed to get task stats: %s", exc)
        return {"total": 0, "completed": 0, "pending": 0, "today": 0, "overdue": 0}