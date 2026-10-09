"""Expense tracking service."""

from app.database import db
from app.utils.validators import validate_amount, validate_category, validate_date, sanitize_text
from app.utils.helpers import now_iso, today_iso, month_range
from app.utils.logger import get_logger

_log = get_logger("studydesk.expenses")

CATEGORIES = ("Food", "Transport", "Books", "Internet", "Education", "Other")


def add_expense(amount, category, description="", expense_date=""):
    ok, amount = validate_amount(amount, "Amount")
    if not ok:
        return False, amount, None
    ok, category = validate_category(category, CATEGORIES, "Category")
    if not ok:
        return False, category, None
    if expense_date:
        ok, expense_date = validate_date(expense_date)
        if not ok:
            return False, expense_date, None
    else:
        expense_date = today_iso()
    description = sanitize_text(description, 500)
    now = now_iso()
    try:
        cur = db.execute(
            "INSERT INTO expenses (amount, category, description, expense_date, "
            "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (amount, category, description, expense_date, now, now),
        )
        db.log_activity("expenses", "add", f"{category}:{amount}")
        return True, "Expense added.", cur.lastrowid
    except Exception as exc:
        _log.error("Failed to add expense: %s", exc)
        return False, "Could not save the expense.", None


def update_expense(expense_id, amount, category, description="", expense_date=""):
    ok, amount = validate_amount(amount, "Amount")
    if not ok:
        return False, amount
    ok, category = validate_category(category, CATEGORIES, "Category")
    if not ok:
        return False, category
    ok, expense_date = validate_date(expense_date)
    if not ok:
        return False, expense_date
    description = sanitize_text(description, 500)
    try:
        db.execute(
            "UPDATE expenses SET amount=?, category=?, description=?, "
            "expense_date=?, updated_at=? WHERE id=?",
            (amount, category, description, expense_date, now_iso(), expense_id),
        )
        db.log_activity("expenses", "edit", str(expense_id))
        return True, "Expense updated."
    except Exception as exc:
        _log.error("Failed to update expense: %s", exc)
        return False, "Could not update the expense."


def delete_expense(expense_id):
    try:
        db.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        db.log_activity("expenses", "delete", str(expense_id))
        return True, "Expense deleted."
    except Exception as exc:
        _log.error("Failed to delete expense: %s", exc)
        return False, "Could not delete the expense."


def get_all_expenses(search="", category_filter="", date_from="", date_to=""):
    sql = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if search:
        sql += " AND (description LIKE ? OR category LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if category_filter:
        sql += " AND category=?"
        params.append(category_filter)
    if date_from:
        sql += " AND expense_date >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND expense_date <= ?"
        params.append(date_to)
    sql += " ORDER BY expense_date DESC, id DESC"
    try:
        return db.query(sql, params)
    except Exception as exc:
        _log.error("Failed to fetch expenses: %s", exc)
        return []


def get_expense(expense_id):
    return db.query_one("SELECT * FROM expenses WHERE id=?", (expense_id,))


def get_monthly_total(year=None, month=None):
    start, end = month_range(year, month)
    try:
        row = db.query_one(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses "
            "WHERE expense_date BETWEEN ? AND ?",
            (start, end),
        )
        return row["total"] if row else 0.0
    except Exception as exc:
        _log.error("Failed to get monthly total: %s", exc)
        return 0.0


def get_category_totals(year=None, month=None):
    start, end = month_range(year, month)
    try:
        rows = db.query(
            "SELECT category, COALESCE(SUM(amount), 0) AS total "
            "FROM expenses WHERE expense_date BETWEEN ? AND ? "
            "GROUP BY category ORDER BY total DESC",
            (start, end),
        )
        return {r["category"]: r["total"] for r in rows}
    except Exception as exc:
        _log.error("Failed to get category totals: %s", exc)
        return {}


def get_total():
    try:
        row = db.query_one("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses")
        return row["total"] if row else 0.0
    except Exception:
        return 0.0