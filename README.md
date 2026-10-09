# StudyDesk Pro

**Student Productivity & Study Management Suite**

A professional Windows desktop application for student productivity, built with Python, Tkinter, and SQLite. Works entirely offline — no internet connection required.

---

## Features

| Module | Description |
|--------|-------------|
| **Dashboard** | Overview cards (tasks, notes, study, pomodoro, expenses) with charts |
| **Tasks** | Full CRUD with priority, status, due dates, search, filter, sort |
| **Notes** | Create, edit, delete, search, categorize (Study/Programming/Project/Personal/Other) |
| **Study Planner** | Subject management with daily/weekly targets and progress tracking |
| **Pomodoro** | Focus/break timer with start, pause, resume, reset, skip, session persistence |
| **Expenses** | Track spending with categories, charts, monthly totals (PKR/Rs.) |
| **File Organizer** | Organize files by type into subfolders with preview and safe conflict handling |
| **Password Generator** | Secure generation using `secrets` module with customizable options |
| **Text Tools** | Word/char/line count, case conversions, space/blank-line cleanup |
| **Calculator** | Safe expression parser (no `eval()`) with history |
| **Settings** | Theme, pomodoro durations, currency, default priority |
| **About** | Application information |

---

## Technology Stack

- **Python 3.10+**
- **Tkinter / ttk** — GUI framework
- **SQLite** — Local database (via `sqlite3`)
- **Matplotlib** — Dashboard and expense charts
- **Pillow** — Image/icon handling
- **PyInstaller** — Windows EXE packaging

No web frameworks, no cloud services, no external APIs. The entire application runs locally.

---

## Project Structure

```
studydesk-pro/
├── app/
│   ├── gui/            # GUI modules (dashboard, tasks, notes, etc.)
│   ├── database/       # SQLite schema and connection management
│   ├── services/       # Business logic (task, note, expense, etc.)
│   └── utils/          # Validators, security, helpers, logger
├── assets/
│   ├── icons/          # studydesk.ico, studydesk.png
│   └── images/
├── data/               # SQLite database and logs (auto-created)
├── tests/              # Test suite
├── build/              # PyInstaller build output
├── main.py             # Entry point
├── run_tests.py        # Test runner
├── requirements.txt    # Python dependencies
├── StudyDeskPro.spec   # PyInstaller spec
├── build_exe.bat       # EXE build script
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.10 or later (download from https://python.org)
- Windows 10 or 11

### Setup

```bash
# Clone or download the project
cd studydesk-pro

# Install dependencies
pip install -r requirements.txt
```

---

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run tests
python run_tests.py
```

---

## Running with Python

The primary command to launch the application:

```bash
python main.py
```

This directly opens the StudyDesk Pro GUI. No CLI interaction, no web server, no browser.

---

## Database

- **Engine:** SQLite (via Python's `sqlite3` module)
- **Location:** `data/studydesk.db` (auto-created on first launch)
- **Tables:** `users`, `tasks`, `notes`, `subjects`, `study_sessions`, `pomodoro_sessions`, `expenses`, `settings`, `activity_logs`
- **Initialization:** Automatic on first launch. Existing data is never overwritten.
- **Queries:** All queries use parameterized statements (no string concatenation).

---

## Testing

```bash
# Run all tests (uses Python standard library unittest)
python run_tests.py
```

Tests cover:
- Task CRUD, search, filter, stats
- Note CRUD, search, categories
- Expense CRUD, totals, category breakdowns
- Study planner subjects, study time, progress
- Calculator safe parser (valid/invalid expressions, division by zero, parentheses)
- Settings persistence
- Database insert/update/delete/read
- File organizer analysis, execution, conflict handling
- Security: path traversal, protected directories, validation
- Password generator uses `secrets` module

---

## PyInstaller Packaging

### Build the EXE

```bash
# Option 1: Use the build script
build_exe.bat

# Option 2: Run PyInstaller directly
python -m PyInstaller StudyDeskPro.spec --noconfirm
```

### Output

```
dist/StudyDeskPro/StudyDeskPro.exe
```

The executable:
- Runs without requiring Python to be installed
- Contains the custom StudyDesk Pro icon
- Bundles all assets and dependencies
- Creates `data/` directory next to the EXE for local storage

---

## EXE Usage

1. Navigate to `dist/StudyDeskPro/`
2. Double-click `StudyDeskPro.exe`
3. The application opens with the Dashboard
4. All data is stored in `dist/StudyDeskPro/data/`

---

## Icon Configuration

- **Source:** `assets/icons/studydesk.png` (256x256 master)
- **Windows icon:** `assets/icons/studydesk.ico` (16-256px, 7 resolutions)
- **Generation:** `python assets/generate_icon.py` (pure Python, no external deps)
- **Window icon:** Loaded via `root.iconbitmap()` with PIL fallback
- **EXE icon:** Embedded via PyInstaller `--icon` in the spec file

---

## Security Considerations

- **Input validation:** All user input is validated (empty, length, type, date format)
- **SQL injection:** All queries use parameterized statements
- **Path traversal:** `safe_join()` prevents directory escape
- **Protected directories:** System folders (Windows, System32, Program Files) are blocked
- **File organizer:** Never deletes files, never overwrites (renames on conflict), requires confirmation
- **Calculator:** Uses a recursive descent parser — no `eval()` on user input
- **Password generator:** Uses `secrets` module — never `random.random()`
- **No secrets stored:** Settings contain no passwords or API keys
- **Error handling:** User-friendly messages; stack traces go to logs only
- **Logging:** Sensitive data (passwords, keys) is never logged

---

## Known Limitations

- Charts require Matplotlib and Pillow (text fallback if unavailable)
- File Organizer moves files (does not copy) — use with caution
- Dark theme is functional but some ttk widgets may show light elements
- No multi-user support (single local user)
- No cloud sync (by design — fully offline)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'matplotlib'` | Run `pip install matplotlib Pillow` |
| GUI doesn't open | Check `data/logs/studydesk.log` for errors |
| Icon not showing in EXE | Rebuild with `build_exe.bat`; clear Windows icon cache |
| Database locked | Ensure no other instance is running |
| File Organizer refuses a folder | It's a protected system directory — choose a user folder |
| Calculator shows "Error" | Invalid expression — check for unmatched parentheses |

---

## Version

**1.0.0**

## License

This project is provided as-is for educational and personal use.