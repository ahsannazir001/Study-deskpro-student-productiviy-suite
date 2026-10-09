"""Security utilities: path validation, traversal protection, safe paths."""

import os
from pathlib import Path

PROTECTED_DIRS = (
    "windows", "system32", "program files", "program files (x86)",
    "programdata", "$recycle.bin", "boot", "recovery",
)

PROTECTED_ENV_VARS = (
    "WINDIR", "SystemRoot", "ProgramFiles", "ProgramFiles(x86)",
    "ProgramData",
)


def get_protected_paths():
    paths = set()
    for var in PROTECTED_ENV_VARS:
        val = os.environ.get(var)
        if val:
            paths.add(os.path.realpath(val).lower())
    sys_root = os.environ.get("SystemRoot")
    if sys_root:
        paths.add(os.path.realpath(os.path.join(sys_root, "System32")).lower())
    return paths


def is_protected_directory(path):
    if not path:
        return True
    try:
        real = os.path.realpath(str(path)).lower()
    except (OSError, ValueError):
        return True
    for p in get_protected_paths():
        if real == p or real.startswith(p + os.sep):
            return True
    parts = real.replace("\\", "/").split("/")
    for part in parts:
        if part in PROTECTED_DIRS:
            return True
    home = os.path.expanduser("~")
    appdata = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
    if appdata:
        appdata_real = os.path.realpath(appdata).lower()
        if real == appdata_real:
            return True
    return False


def safe_join(base, *parts):
    base_real = os.path.realpath(str(base))
    candidate = os.path.realpath(os.path.join(base_real, *parts))
    if not (candidate == base_real or candidate.startswith(base_real + os.sep)):
        raise ValueError("Path traversal detected.")
    return candidate


def is_within_directory(file_path, directory):
    try:
        fp = os.path.realpath(str(file_path))
        dp = os.path.realpath(str(directory))
    except (OSError, ValueError):
        return False
    return fp == dp or fp.startswith(dp + os.sep)


def validate_folder_path(path):
    if not path or not str(path).strip():
        return False, "No folder selected."
    p = str(path).strip()
    if is_protected_directory(p):
        return False, "This is a system-protected directory. Operation refused for safety."
    if not os.path.exists(p):
        return False, "The selected folder does not exist."
    if not os.path.isdir(p):
        return False, "The selected path is not a folder."
    return True, p


def unique_destination(dest_dir, filename):
    dest = os.path.join(dest_dir, filename)
    if not os.path.exists(dest):
        return dest
    stem, ext = os.path.splitext(filename)
    counter = 1
    while True:
        candidate = os.path.join(dest_dir, f"{stem}_{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1
        if counter > 9999:
            raise ValueError("Too many filename conflicts.")


def truncate_message(msg, limit=300):
    if not msg:
        return ""
    s = str(msg)
    if len(s) > limit:
        s = s[:limit] + "..."
    return s