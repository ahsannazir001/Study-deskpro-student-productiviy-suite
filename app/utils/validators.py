"""Input validation utilities.

All validators return (is_valid: bool, message: str). A non-empty message on
success is the normalized/cleaned value where relevant.
"""

import re
from datetime import datetime, date

_DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y")


def validate_nonempty(value, field_name="Value"):
    value = (value or "").strip()
    if not value:
        return False, f"{field_name} cannot be empty."
    return True, value


def validate_length(value, min_len=1, max_len=500, field_name="Value"):
    value = (value or "").strip()
    if len(value) < min_len:
        return False, f"{field_name} must be at least {min_len} characters."
    if len(value) > max_len:
        return False, f"{field_name} must be at most {max_len} characters."
    return True, value


def validate_date(value):
    value = (value or "").strip()
    if not value:
        return False, "Date cannot be empty."
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(value, fmt).date()
            return True, parsed.isoformat()
        except ValueError:
            continue
    return False, "Invalid date format. Use YYYY-MM-DD."


def validate_optional_date(value):
    value = (value or "").strip()
    if not value:
        return True, ""
    return validate_date(value)


def validate_int(value, min_val=None, max_val=None, field_name="Value"):
    value = (value or "").strip()
    if not value:
        return False, f"{field_name} cannot be empty."
    try:
        n = int(value)
    except ValueError:
        return False, f"{field_name} must be a whole number."
    if min_val is not None and n < min_val:
        return False, f"{field_name} must be at least {min_val}."
    if max_val is not None and n > max_val:
        return False, f"{field_name} must be at most {max_val}."
    return True, n


def validate_float(value, min_val=None, max_val=None, field_name="Value"):
    value = (value or "").strip()
    if not value:
        return False, f"{field_name} cannot be empty."
    try:
        n = float(value)
    except ValueError:
        return False, f"{field_name} must be a number."
    if n != n:
        return False, f"{field_name} is not a valid number."
    if min_val is not None and n < min_val:
        return False, f"{field_name} must be at least {min_val}."
    if max_val is not None and n > max_val:
        return False, f"{field_name} must be at most {max_val}."
    return True, n


def validate_amount(value, field_name="Amount"):
    ok, result = validate_float(value, min_val=0, field_name=field_name)
    if not ok:
        return ok, result
    if result > 1_000_000_000:
        return False, f"{field_name} is too large."
    return True, result


def validate_priority(value):
    value = (value or "").strip().capitalize()
    if value not in ("Low", "Medium", "High"):
        return False, "Priority must be Low, Medium, or High."
    return True, value


def validate_status(value):
    value = (value or "").strip().capitalize()
    if value not in ("Pending", "Completed"):
        return False, "Status must be Pending or Completed."
    return True, value


def validate_category(value, allowed, field_name="Category"):
    value = (value or "").strip()
    if value not in allowed:
        return False, f"{field_name} must be one of: {', '.join(allowed)}."
    return True, value


def is_overdue(due_date_str, status="Pending"):
    if not due_date_str or status.lower() == "completed":
        return False
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    except ValueError:
        return False
    return due < date.today()


def sanitize_text(value, max_len=5000):
    value = (value or "").strip()
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value)
    if len(value) > max_len:
        value = value[:max_len]
    return value