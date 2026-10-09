"""File organizer service.

Analyzes and organizes files by type. Never deletes or overwrites files.
All moves stay within the selected root directory.
"""

import os
import shutil
from collections import OrderedDict

from app.utils.security import (
    is_protected_directory, is_within_directory, unique_destination,
)
from app.utils.logger import get_logger

_log = get_logger("studydesk.file_organizer")

CATEGORY_MAP = OrderedDict([
    ("Images", (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".tiff")),
    ("Documents", (".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".csv",
                   ".ppt", ".pptx", ".rtf", ".odt")),
    ("Videos", (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm")),
    ("Audio", (".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma")),
    ("Archives", (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2")),
    ("Code", (".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".html",
              ".css", ".json", ".xml", ".yml", ".yaml", ".sql")),
    ("Others", ()),
])


def category_for_extension(ext):
    ext = ext.lower()
    for cat, exts in CATEGORY_MAP.items():
        if cat == "Others":
            continue
        if ext in exts:
            return cat
    return "Others"


def analyze_directory(directory):
    """Return list of (filename, current_path, category, dest_subdir)."""
    results = []
    try:
        entries = os.listdir(directory)
    except (OSError, PermissionError) as exc:
        _log.error("Cannot read directory %s: %s", directory, exc)
        return results, str(exc)

    for name in entries:
        full = os.path.join(directory, name)
        if os.path.isdir(full):
            continue
        ext = os.path.splitext(name)[1]
        cat = category_for_extension(ext)
        results.append({
            "name": name,
            "source": full,
            "category": cat,
            "dest_subdir": cat,
        })
    return results, None


def plan_operations(directory, results):
    """Build move plan with conflict detection."""
    plan = []
    conflicts = []
    for item in results:
        dest_dir = os.path.join(directory, item["dest_subdir"])
        dest_name = item["name"]
        dest_path = os.path.join(dest_dir, dest_name)
        conflict = False
        if os.path.exists(dest_path) and os.path.realpath(dest_path) != os.path.realpath(item["source"]):
            conflict = True
            dest_path = unique_destination(dest_dir, dest_name)
        plan.append({
            "name": item["name"],
            "source": item["source"],
            "dest": dest_path,
            "dest_dir": dest_dir,
            "category": item["category"],
            "conflict": conflict,
        })
        if conflict:
            conflicts.append(item["name"])
    return plan, conflicts


def execute_plan(plan):
    """Execute the move plan. Returns (moved, skipped, errors)."""
    moved = []
    skipped = []
    errors = []
    for item in plan:
        try:
            src = item["source"]
            dst = item["dest"]
            if not os.path.exists(src):
                skipped.append(item["name"])
                continue
            os.makedirs(item["dest_dir"], exist_ok=True)
            if os.path.realpath(src) == os.path.realpath(dst):
                skipped.append(item["name"])
                continue
            shutil.move(src, dst)
            moved.append(item["name"])
        except (OSError, PermissionError, shutil.Error) as exc:
            _log.error("Move failed for %s: %s", item["name"], exc)
            errors.append((item["name"], str(exc)))
    _log.info("File organizer: moved=%d skipped=%d errors=%d",
              len(moved), len(skipped), len(errors))
    return moved, skipped, errors


def get_categories():
    return list(CATEGORY_MAP.keys())