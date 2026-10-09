# StudyDesk Pro — Project Defense Document

## Student Productivity & Study Management Suite

---

## 1. Project Overview

**StudyDesk Pro** is a professional **Windows desktop application** built for students to manage their daily productivity and study activities. It is **not** a web application — it runs entirely locally on the user's machine with no internet connection required.

The application combines **12 integrated modules** into a single unified desktop interface:

1. **Dashboard** — Analytics overview with stat cards and charts
2. **Tasks** — Task management with priority, status, due dates, search/filter/sort
3. **Notes** — Note-taking with categories and a text editor
4. **Study Planner** — Subject tracking with daily/weekly targets and progress
5. **Pomodoro Timer** — Focus/break timer with session persistence
6. **Expenses** — Expense tracking with category charts (PKR/Rs. currency)
7. **File Organizer** — Organize files by type into subfolders (with safety checks)
8. **Password Generator** — Secure password generation using Python's `secrets` module
9. **Text Tools** — Text utilities (word count, case conversion, cleanup)
10. **Calculator** — Safe expression calculator (no `eval()`)
11. **Settings** — Theme, pomodoro durations, currency, defaults
12. **About** — Application information

---

## 2. Technology Stack & Justification

| Technology | Purpose | Why It Was Chosen |
|---|---|---|
| **Python 3.10** | Core programming language | Cross-platform, rich standard library, rapid development |
| **Tkinter / ttk** | GUI framework | Built into Python (no extra install), native Windows look, ttk styling for professional appearance |
| **SQLite** (via `sqlite3`) | Local database | Zero-config, serverless, file-based, built into Python, perfect for desktop apps |
| **Matplotlib** | Charts/graphs | Industry-standard Python plotting library for dashboard and expense visualizations |
| **Pillow** | Image processing | For loading the application icon and rendering chart images in Tkinter |
| **PyInstaller** | EXE packaging | Creates a standalone `.exe` that runs without Python installed |

### Standard Library Modules Used

`tkinter`, `sqlite3`, `os`, `sys`, `pathlib`, `shutil`, `datetime`, `time`, `threading`, `json`, `secrets`, `hashlib`, `logging`, `re`, `struct`, `zlib`, `math`, `string`, `unittest`, `tempfile`, `traceback`, `inspect`

### What Was NOT Used (and Why)

No web frameworks (Flask/Django/FastAPI), no cloud services, no external APIs, no machine learning, no PostgreSQL/Firebase. The entire application is **offline and local-first** by design.

---

## 3. Architecture & Design

### 3.1 Layered Architecture

The application follows a clean **4-layer architecture**:

```
┌─────────────────────────────────────────────┐
│           main.py (Entry Point)              │
├─────────────────────────────────────────────┤
│              GUI Layer (app/gui/)            │
│  Dashboard, Tasks, Notes, Pomodoro, etc.     │
│  Main window, styles, UI helpers             │
├─────────────────────────────────────────────┤
│           Services Layer (app/services/)      │
│  TaskService, NoteService, ExpenseService    │
│  StudyService, FileService, SettingsService  │
│  → Business logic + input validation          │
├─────────────────────────────────────────────┤
│          Database Layer (app/database/)       │
│  db.py (connection, queries)                  │
│  schema.py (table definitions)               │
├─────────────────────────────────────────────┤
│            Utils Layer (app/utils/)           │
│  validators, security, helpers, logger       │
└─────────────────────────────────────────────┘
```

**Design principle:** Each layer only talks to the layer directly below it. The GUI never writes SQL directly — it calls services. Services validate input and call the database layer. This separation makes the code maintainable and testable.

### 3.2 Why This Architecture?

- **Separation of concerns:** GUI code focuses on presentation, services on business logic, database on persistence
- **Testability:** Services can be tested without the GUI (and are, in `run_tests.py`)
- **Maintainability:** Adding a new feature means adding a service + GUI module without touching existing code
- **Security:** Validation happens in services before data reaches the database

---

## 4. File Structure (with line counts)

```
studydesk-pro/                          34 Python files, ~4,600 lines
│
├── main.py                             84 lines  — Entry point
├── run_tests.py                       420 lines  — Test runner (56 tests)
├── requirements.txt                              — Dependencies
├── StudyDeskPro.spec                             — PyInstaller config
├── build_exe.bat                                 — Windows build script
├── .gitignore                                    — Git ignore rules
├── README.md                                     — User documentation
│
├── app/
│   ├── __init__.py                      4 lines  — Version info
│   │
│   ├── gui/                                      — GUI Layer (12 modules)
│   │   ├── main_window.py            257 lines   — Sidebar nav + content switching
│   │   ├── styles.py                 229 lines   — Light/dark themes, ttk styling
│   │   ├── ui_helpers.py             120 lines   — Reusable dialogs, cards, scrollable frame
│   │   ├── dashboard.py              201 lines   — Stat cards + charts
│   │   ├── tasks.py                  238 lines   — Task CRUD + search/filter/sort
│   │   ├── notes.py                  208 lines   — Notes CRUD + categories
│   │   ├── study_planner.py          192 lines   — Subject management + progress
│   │   ├── pomodoro.py               211 lines   — Timer using after() (non-blocking)
│   │   ├── expenses.py               226 lines   — Expense CRUD + charts
│   │   ├── file_organizer.py         147 lines   — Safe file organization
│   │   ├── password_generator.py     152 lines   — Secure password generation
│   │   ├── text_tools.py             109 lines   — Text utilities
│   │   ├── calculator.py             252 lines   — Safe parser + calculator UI
│   │   ├── settings.py               136 lines   — Settings management
│   │   └── about.py                   59 lines   — About page
│   │
│   ├── database/                                 — Database Layer
│   │   ├── schema.py                111 lines   — 9 table definitions + default settings
│   │   └── db.py                    115 lines   — Connection, init, query helpers
│   │
│   ├── services/                                 — Services Layer
│   │   ├── task_service.py          146 lines   — Task business logic
│   │   ├── note_service.py           96 lines   — Note business logic
│   │   ├── expense_service.py       136 lines   — Expense business logic
│   │   ├── study_service.py         151 lines   — Study planner logic
│   │   ├── file_service.py          117 lines   — File organizer logic
│   │   └── settings_service.py       69 lines   — Settings read/write
│   │
│   └── utils/                                    — Utilities
│       ├── logger.py                 61 lines   — Rotating file logger
│       ├── validators.py            126 lines   — Input validation functions
│       ├── security.py              103 lines   — Path safety, protected dirs
│       └── helpers.py               112 lines   — Paths, formatting, clipboard
│
├── assets/
│   ├── icons/
│   │   ├── studydesk.ico                       — Windows icon (7 resolutions)
│   │   ├── studydesk.png                       — 256x256 master artwork
│   │   └── generate_icon.py                    — Pure-Python icon generator
│   └── images/
│
├── data/                                        — Auto-created at runtime
│   ├── studydesk.db                            — SQLite database
│   └── logs/studydesk.log                      — Application log
│
├── tests/                                       — Test suite
│   ├── test_tasks.py                           — Task tests
│   ├── test_notes.py                           — Note tests
│   ├── test_expenses.py                        — Expense tests
│   ├── test_study.py                           — Study planner tests
│   ├── test_calculator.py                      — Calculator tests
│   └── test_misc.py                            — Settings, DB, security, file tests
│
└── build/                                       — PyInstaller build output
```

---

## 5. Database Design

### 5.1 SQLite Schema (9 Tables)

The database is initialized automatically on first launch using `CREATE TABLE IF NOT EXISTS` — existing data is never overwritten.

| Table | Purpose | Key Columns |
|---|---|---|
| `users` | Single local user | id, username, display_name |
| `tasks` | Task storage | id, title, description, priority, status, due_date |
| `notes` | Note storage | id, title, content, category |
| `subjects` | Study subjects | id, name, daily_target, weekly_target, completed_minutes |
| `study_sessions` | Study time logs | id, subject_id, minutes, session_date |
| `pomodoro_sessions` | Pomodoro history | id, duration_minutes, session_type, completed_at |
| `expenses` | Expense records | id, amount, category, description, expense_date |
| `settings` | Key-value settings | key, value |
| `activity_logs` | Recent activity | id, module, action, detail, created_at |

### 5.2 Database Safety

- **Parameterized queries:** Every SQL query uses `?` placeholders — no string concatenation. This prevents SQL injection.
- **WAL mode:** `PRAGMA journal_mode=WAL` for better concurrent read performance.
- **Foreign keys:** `PRAGMA foreign_keys=ON` with `ON DELETE SET NULL`.
- **Thread-safe:** Each thread gets its own connection via `threading.local()`.
- **Auto-initialization:** Tables and default settings are created on first launch without user action.

### 5.3 Example: How a Task is Saved

```
User clicks "Save" in GUI
    ↓
tasks.py → task_service.add_task(title, desc, priority, due_date)
    ↓
task_service validates:
    - title not empty (validate_nonempty)
    - title length 1-200 (validate_length)
    - priority is Low/Medium/High (validate_priority)
    - due_date is valid YYYY-MM-DD (validate_optional_date)
    ↓
db.execute("INSERT INTO tasks (...) VALUES (?, ?, ?, ...)", params)
    ↓
SQLite stores the row → returns lastrowid
    ↓
db.log_activity("tasks", "add", title)  → activity_logs table
    ↓
GUI refreshes the task list
```

---

## 6. Module-by-Module Technical Explanation

### 6.1 Main Window & Navigation (`main_window.py`)

- **Sidebar navigation:** 12 navigation items rendered as `tk.Label` widgets with hover effects (color changes on `<Enter>`/`<Leave>` events).
- **Content switching:** When a nav item is clicked, the current content frame's children are destroyed and the new module is loaded into the same frame. No separate windows open.
- **Header:** Shows the current page title.
- **Status bar:** Bottom bar showing operation status messages.
- **Window icon:** Loaded via `root.iconbitmap()` with a PIL fallback to `root.iconphoto()`.
- **Window size persistence:** Size is saved to settings on resize and restored on next launch.

### 6.2 Styling System (`styles.py`)

- **Two themes:** Light and Dark, each defining ~25 color constants.
- **ttk Style configuration:** Custom styles for buttons (`Accent.TButton`, `Success.TButton`, `Danger.TButton`, `Warning.TButton`), Treeview headers, entries, comboboxes, progress bars, and labels.
- **Font system:** Consistent `Segoe UI` font family with defined sizes for titles, headers, body text, sidebar, cards, and monospace.
- **Theme switching:** `apply_styles()` reconfigures all ttk styles; `refresh_theme()` rebuilds the entire UI.

### 6.3 Dashboard (`dashboard.py`)

- **8 stat cards:** Total Tasks, Completed, Pending, Today's Tasks, Total Notes, Study Today, Pomodoro Sessions, Monthly Expenses.
- **Cards:** Custom `tk.Frame` with colored top bar, title label, and large value label.
- **Charts:** Matplotlib pie chart for task status, bar chart for expenses by category. Rendered to PNG via `fig.canvas.draw()` → `Image.frombytes()` → `ImageTk.PhotoImage()`.
- **Graceful fallback:** If Matplotlib/Pillow are unavailable, charts are replaced with text-based progress bars.
- **Overdue warning:** Red banner if overdue tasks exist.
- **Recent activity:** Last 8 entries from `activity_logs` table with relative timestamps ("5m ago", "2h ago").
- **All data from SQLite:** No hard-coded statistics — every number comes from a database query.

### 6.4 Task Manager (`tasks.py` + `task_service.py`)

- **Full CRUD:** Add, edit, delete, mark complete/pending.
- **Search:** Real-time search on title and description (bound to `<KeyRelease>`).
- **Filters:** By priority (Low/Medium/High) and status (Pending/Completed).
- **Sorting:** By created date, due date, priority, or title (ascending/descending).
- **Overdue highlighting:** Overdue tasks shown in red via Treeview tags.
- **Completed highlighting:** Completed tasks shown in green.
- **Dialog forms:** Add/Edit dialogs use `tk.Toplevel` with `grab_set()` for modal behavior.
- **Validation:** Empty titles rejected, invalid dates rejected, invalid priority rejected — all with user-friendly error messages.

### 6.5 Notes Manager (`notes.py` + `note_service.py`)

- **Full CRUD:** Create, edit, delete notes.
- **Categories:** Study, Programming, Project, Personal, Other (enforced by validation).
- **Search:** Real-time search on title and content.
- **Category filter:** Filter notes by category.
- **Split view:** Left panel shows note list (Treeview), right panel shows selected note content (read-only Text widget).
- **Content limit:** 20,000 characters (sanitized to remove control characters).

### 6.6 Study Planner (`study_planner.py` + `study_service.py`)

- **Subject management:** Add, edit, delete subjects with daily and weekly targets (in hours).
- **Progress tracking:** `completed_minutes` accumulates as study time is logged.
- **Progress percentage:** Calculated as `(completed_minutes / (daily_target * 60)) * 100`, capped at 100%.
- **Study time logging:** "Log Study Time" dialog adds minutes to a subject and records a session in `study_sessions` table with today's date.
- **Reset progress:** Zeros out `completed_minutes` for a subject.
- **Summary:** Shows today's total study time and all-time total.

### 6.7 Pomodoro Timer (`pomodoro.py`)

- **Non-blocking timer:** Uses `root.after(1000, self._tick)` — Tkinter's event-based scheduling. **No threads needed.** The GUI remains fully responsive.
- **States:** Focus mode (default 25 min) and Break mode (default 5 min).
- **Controls:** Start, Pause, Resume, Reset, Skip.
- **Custom duration:** User can set focus and break durations (saved to settings).
- **Session completion:** When timer reaches 0:
  - Shows a notification dialog
  - Increments session counter
  - Saves to `pomodoro_sessions` table with duration and timestamp
  - Automatically switches to break mode (or back to focus after break)
- **No GUI freeze:** The `after()` method schedules the next tick in the Tkinter event loop, so the UI stays responsive between ticks.

### 6.8 Expense Tracker (`expenses.py` + `expense_service.py`)

- **Full CRUD:** Add, edit, delete expenses.
- **Categories:** Food, Transport, Books, Internet, Education, Other.
- **Fields:** Amount (validated as positive float), category, description, date.
- **Currency:** PKR / Rs. (configurable in settings).
- **Summary:** Monthly total and all-time total displayed at top.
- **Filters:** Search by description, filter by category.
- **Charts:** Matplotlib bar chart showing expenses by category for the current month.
- **Monthly calculation:** Uses `month_range()` to get first/last day of current month, queries `SUM(amount)` with date range.
- **Category totals:** `GROUP BY category` with `SUM(amount)` for chart data.

### 6.9 File Organizer (`file_organizer.py` + `file_service.py`)

This is the most safety-critical module. It modifies user files, so extensive safety measures are implemented:

**Category mapping:**
- Images: png, jpg, jpeg, gif, webp, bmp, svg, tiff
- Documents: pdf, doc, docx, txt, xlsx, csv, ppt, pptx, rtf, odt
- Videos: mp4, mkv, avi, mov, wmv, flv, webm
- Audio: mp3, wav, aac, flac, ogg, m4a, wma
- Archives: zip, rar, 7z, tar, gz, bz2
- Code: py, js, ts, java, c, cpp, h, html, css, json, xml, yml, yaml, sql
- Others: everything else

**Safety workflow (8 steps):**
1. **Browse:** User selects a folder via `filedialog.askdirectory()`.
2. **Validate:** `validate_folder_path()` checks it's not empty, exists, is a directory, and is NOT a protected system directory.
3. **Protected directories:** `is_protected_directory()` blocks Windows, System32, Program Files, Program Files (x86), ProgramData, $Recycle.Bin, Boot, Recovery, and AppData root.
4. **Analyze:** `analyze_directory()` lists all files and categorizes each by extension.
5. **Plan:** `plan_operations()` builds a move plan with destination paths and conflict detection.
6. **Preview:** Shows a Treeview with every file, its category, destination, and conflict status.
7. **Conflict handling:** If a destination file already exists, `unique_destination()` generates a renamed path (`file_1.txt`, `file_2.txt`, etc.). **No overwriting.**
8. **Confirmation:** `messagebox.askyesno()` requires explicit user confirmation before any file is moved.
9. **Execute:** `execute_plan()` uses `shutil.move()` to move files. Returns counts of moved/skipped/errored files.
10. **Summary:** Shows completion summary with counts and any errors.

**What it NEVER does:**
- Never deletes files
- Never overwrites files (renames on conflict)
- Never executes files
- Never moves files outside the selected root
- Never processes system directories without explicit user selection

### 6.10 Password Generator (`password_generator.py`)

- **Secure randomness:** Uses Python's `secrets` module (cryptographically secure). **Never uses `random.random()`.**
- **Character pools:** Uppercase, lowercase, numbers, symbols — each selectable via checkboxes.
- **Length:** Adjustable from 4 to 64 characters via a scale slider.
- **Guaranteed variety:** At least one character from each selected pool is included, then the rest are randomly chosen from the combined pool. The result is shuffled using `secrets.SystemRandom().shuffle()`.
- **Strength indicator:** Shows Weak/Medium/Strong based on length and character variety.
- **Copy to clipboard:** Uses Tkinter's `clipboard_clear()` + `clipboard_append()`.
- **No storage:** Generated passwords are never saved to the database or logs.

### 6.11 Text Tools (`text_tools.py`)

- **Live statistics:** Word count, character count, line count update on every keystroke (`<KeyRelease>` binding).
- **Transformations:** UPPERCASE, lowercase, Title Case.
- **Cleanup:** Remove extra spaces (collapses multiple spaces/tabs to single, strips each line), remove blank lines (filters out empty lines).
- **Copy/Clear:** Standard clipboard and clear operations.

### 6.12 Calculator (`calculator.py`)

**This is a key security feature — the calculator does NOT use `eval()`.**

Instead, it implements a **recursive descent parser** — a standard compiler technique:

- **Lexer/Parser:** The `_Parser` class tokenizes the input and parses it using recursive descent.
- **Grammar:** Supports `+`, `-`, `*`, `/`, `%`, parentheses `()`, decimal numbers, and unary minus.
- **Precedence:** Multiplication/division/modulo bind tighter than addition/subtraction (standard math precedence).
- **Error handling:** `CalcError` exceptions for: empty expression, division by zero, modulo by zero, missing parenthesis, unexpected characters, invalid numbers, result too large (>10^15).
- **History:** Last 20 calculations stored in memory and displayed in a side panel.
- **GUI:** Standard calculator button grid (0-9, operators, C, =, backspace).

**Why not eval()?** `eval()` can execute arbitrary Python code. If a user types `__import__('os').system('rm -rf /')`, `eval()` would execute it. The recursive descent parser only understands mathematical operations — it cannot execute code.

### 6.13 Settings (`settings.py` + `settings_service.py`)

- **Key-value store:** Settings stored in SQLite `settings` table as key-value pairs.
- **Configurable options:** Theme (light/dark), pomodoro focus/break durations, currency symbol, default task priority.
- **Persistence:** Settings survive application restart (stored in SQLite, loaded on startup).
- **In-memory cache:** `settings_service` caches settings in a dict for fast access; `reset_cache()` forces a reload from the database.
- **Reset to defaults:** One-click reset to factory defaults.
- **Clear activity log:** Button to clear the `activity_logs` table.
- **Data directory display:** Shows the path where data is stored.

### 6.14 About (`about.py`)

- Application name, description, version (1.0.0).
- Technology stack listing.
- Feature overview.
- "All data stored locally" notice.

---

## 7. Security Implementation

### 7.1 Input Validation (`validators.py`)

Every user input is validated before it reaches the database:

| Validator | What It Checks |
|---|---|
| `validate_nonempty()` | Value is not empty/whitespace |
| `validate_length()` | String length within min/max bounds |
| `validate_date()` | Valid date in YYYY-MM-DD (or DD-MM-YYYY, etc.) |
| `validate_int()` | Valid integer within bounds |
| `validate_float()` | Valid float within bounds, not NaN |
| `validate_amount()` | Positive float, not too large (<1 billion) |
| `validate_priority()` | Must be "Low", "Medium", or "High" |
| `validate_status()` | Must be "Pending" or "Completed" |
| `validate_category()` | Must be in the allowed set |
| `sanitize_text()` | Removes control characters, truncates to max length |

### 7.2 Path Security (`security.py`)

| Function | Purpose |
|---|---|
| `is_protected_directory()` | Blocks Windows, System32, Program Files, etc. |
| `safe_join()` | Prevents path traversal (`../` escape) |
| `is_within_directory()` | Checks if a path is inside a directory |
| `validate_folder_path()` | Validates user-selected folder |
| `unique_destination()` | Generates non-conflicting filename |

### 7.3 Calculator Safety

- **No `eval()`:** Recursive descent parser only understands math.
- **Division by zero:** Raises `CalcError("Division by zero")`.
- **Overflow:** Results > 10^15 are rejected.
- **Invalid expressions:** Malformed input raises `CalcError` with a clear message.

### 7.4 Password Security

- **`secrets` module:** Uses `secrets.choice()` for each character — cryptographically secure.
- **No `random.random()`:** The `random` module is not used for password generation.
- **No logging:** Generated passwords are never written to logs.
- **No storage:** Passwords are not saved to the database.

### 7.5 SQL Injection Prevention

- **Parameterized queries:** All SQL uses `?` placeholders: `db.execute("INSERT INTO tasks VALUES (?, ?, ?)", (title, desc, date))`.
- **No string concatenation:** SQL is never built by concatenating user input.

### 7.6 Error Handling

- **User-friendly messages:** Errors show clear messages via `messagebox.showerror()`.
- **No stack traces to users:** Technical details go to the log file only.
- **Logging:** All errors logged via `get_logger()` with context.

---

## 8. Logging System (`logger.py`)

- **Rotating file handler:** Log file in `data/logs/studydesk.log`, max 2MB per file, 3 backup files.
- **Console handler:** INFO level to console during development.
- **Format:** `2026-10-08 19:12:00 | INFO | studydesk.db | Database initialized at ...`
- **What IS logged:** App startup, DB init, task/note/expense operations, file organizer operations, errors.
- **What is NOT logged:** Passwords, generated passwords, API keys, sensitive user data.

---

## 9. Application Icon

### 9.1 Design

The icon is a **graduation cap (mortarboard)** on a **blue rounded-square background** with a **yellow tassel**. It represents study/education/productivity.

### 9.2 Generation (`assets/generate_icon.py`)

The icon is generated **entirely in pure Python** — no external image editing tools required:

1. **Pixel rendering:** The `render(size)` function creates an RGBA pixel array at any size. It draws:
   - Rounded rectangle background with blue gradient (top lighter, bottom darker)
   - White graduation cap board (diamond shape using point-in-polygon test)
   - Cap base (trapezoid)
   - Yellow tassel (vertical line + circular knot)

2. **ICO file format:** The `write_ico()` function writes a valid Windows ICO file:
   - 6-byte header (reserved, type=1, count)
   - 16-byte directory entries per size (width, height, colors, reserved, planes, BPP, size, offset)
   - Image data: BMP DIB format for sizes < 64, PNG format for sizes >= 64

3. **PNG generation:** `pixels_to_png()` creates a valid PNG using `zlib` compression (from stdlib).

4. **7 resolutions:** 16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256.

### 9.3 Icon Usage

- **Window icon:** `root.iconbitmap(default=ico_path)` — falls back to `root.iconphoto()` via PIL if ICO fails.
- **EXE icon:** Embedded via PyInstaller `icon='assets/icons/studydesk.ico'` in the spec file.
- **Graceful fallback:** If the icon file is missing, the app still runs with the default Tkinter icon.

---

## 10. Testing (`run_tests.py`)

### 10.1 Test Runner

Since `pytest` is not available in the environment, tests use Python's built-in `unittest` module. The `run_tests.py` script:

1. Creates an isolated temp directory for test data
2. Redirects `get_app_data_dir()` and `get_log_dir()` to the temp dir
3. Initializes a fresh database
4. Runs all test classes
5. Cleans up the temp directory

### 10.2 Test Coverage (56 tests)

| Test Class | Tests | What's Covered |
|---|---|---|
| `TestTaskService` | 10 | Add, empty title, invalid date, invalid priority, update, delete, set status, search, filter, stats |
| `TestNoteService` | 6 | Add, empty title, invalid category, update, delete, search |
| `TestExpenseService` | 7 | Add, negative amount, invalid amount, update, delete, monthly total, category totals |
| `TestStudyService` | 5 | Add subject, empty name, add study time, progress percent, delete |
| `TestCalculator` | 12 | Addition, subtraction, multiplication, division, div by zero, modulo, parentheses, nested parens, decimals, complex expression, empty, invalid, missing paren |
| `TestSettings` | 3 | Set/get, get_int, persistence after cache reset |
| `TestDatabase` | 3 | Insert/read, update, delete |
| `TestFileOrganizer` | 6 | Category mapping, analyze, execute moves, protected dirs, unique destination, path traversal |
| `TestSecurity` | 3 | Empty folder, nonexistent folder, truncate message |
| `TestPasswordGenerator` | 1 | Verifies `secrets` module is used (not `random.random`) |

### 10.3 Result

```
Ran 56 tests in 0.208s — OK
```

---

## 11. PyInstaller Packaging

### 11.1 Spec File (`StudyDeskPro.spec`)

- **Entry point:** `main.py`
- **Bundled data:** `studydesk.ico` and `studydesk.png` (included in `assets/icons/`)
- **Hidden imports:** `matplotlib.backends.backend_agg`, `PIL.Image`, `PIL.ImageTk`
- **Excluded:** `tkinter.test`, `unittest.test`, `pydoc` (reduces size)
- **Icon:** `assets/icons/studydesk.ico` embedded in the EXE
- **Console:** `console=False` (windowed app, no console window)
- **UPX:** Enabled for compression

### 11.2 Build Script (`build_exe.bat`)

1. Checks Python is installed
2. Installs dependencies (`pyinstaller`, `matplotlib`, `Pillow`)
3. Cleans previous build (`build/`, `dist/`)
4. Runs `python -m PyInstaller StudyDeskPro.spec --noconfirm`
5. Output: `dist/StudyDeskPro/StudyDeskPro.exe`

### 11.3 Runtime Behavior

- The EXE creates a `data/` directory next to itself for the SQLite database and logs.
- No data is written to protected Windows directories.
- The EXE displays the custom StudyDesk Pro icon in Windows Explorer, taskbar, and application window.

---

## 12. UI/UX Design Decisions

### 12.1 Layout

- **Sidebar (220px):** App title at top, 12 navigation items below. Active item highlighted in blue.
- **Header (56px):** Current page title.
- **Content area:** Fills remaining space, scrollable where needed.
- **Status bar (24px):** Operation feedback at bottom.

### 12.2 Color System

- **Light theme:** Blue accent (#3498DB), green success (#27AE60), orange warning (#F39C12), red danger (#E74C3C), light gray content background.
- **Dark theme:** GitHub-dark-inspired colors (#0D1117 background, #58A6FF accent).
- **Consistent:** All colors defined as constants in `styles.py`, never hard-coded in modules.

### 12.3 Typography

- **Font family:** `Segoe UI` (Windows native) for all text, `Consolas` for monospace (calculator, passwords).
- **Size hierarchy:** Title (20pt), Header (15pt), Subheader (12pt), Body (10pt), Small (9pt), Card Value (22pt), Timer (48pt).

### 12.4 Components

- **Dashboard cards:** White background, colored top bar, title + large value.
- **Tables (Treeview):** Alternating row colors, colored status (red overdue, green completed), sortable headers.
- **Buttons:** 4 variants — Accent (blue), Success (green), Danger (red), Outline (neutral).
- **Dialogs:** Modal `Toplevel` windows with form fields and Save/Cancel buttons.
- **Progress bars:** ttk Progressbar with accent color.

---

## 13. Technical Challenges & Solutions

### Challenge 1: Non-blocking Pomodoro Timer
**Problem:** A `time.sleep()` loop would freeze the GUI.
**Solution:** Used `root.after(1000, self._tick)` — Tkinter's event-based scheduling. Each tick decrements the counter by 1 and schedules the next tick. The GUI remains fully responsive between ticks. No threads needed.

### Challenge 2: Safe Calculator (no eval)
**Problem:** `eval()` can execute arbitrary Python code (security risk).
**Solution:** Implemented a recursive descent parser (`_Parser` class) that only understands mathematical operations. It tokenizes input and evaluates using standard operator precedence. Division by zero, invalid expressions, and overflow are caught and reported as `CalcError`.

### Challenge 3: Icon Generation Without External Tools
**Problem:** No image editing software available; needed a valid `.ico` file.
**Solution:** Wrote a pure-Python icon generator (`generate_icon.py`) that:
- Renders pixels programmatically (graduation cap design)
- Writes valid ICO file format (BMP DIB + PNG entries)
- Uses only `struct`, `zlib`, `math` from stdlib
- Produces 7 resolutions (16-256px)

### Challenge 4: Matplotlib/Pillow Not Installed
**Problem:** Network restricted; can't `pip install matplotlib Pillow`.
**Solution:** All chart code wrapped in `try/except`. If libraries are available, charts render with Matplotlib. If not, text-based fallback (progress bars, category lists). The app works either way.

### Challenge 5: Thread-safe Database Access
**Problem:** SQLite connections can't be shared across threads.
**Solution:** Used `threading.local()` to give each thread its own connection. The `get_connection()` function returns the current thread's connection, creating one if needed.

### Challenge 6: File Organizer Safety
**Problem:** Moving files can cause data loss if done carelessly.
**Solution:** 8-step safety workflow: validate → analyze → plan → preview → detect conflicts → confirm → execute → summarize. Protected directories blocked. Conflicts resolved by renaming. No silent overwrites. No deletions.

---

## 14. How to Run

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application (opens GUI directly)
python main.py

# Run tests
python run_tests.py
```

### Build EXE

```bash
# Build the Windows executable
build_exe.bat

# Or manually
python -m PyInstaller StudyDeskPro.spec --noconfirm

# Output
dist/StudyDeskPro/StudyDeskPro.exe
```

---

## 15. Key Numbers

| Metric | Value |
|---|---|
| Python files | 34 |
| Lines of code | ~4,600 |
| GUI modules | 12 |
| Database tables | 9 |
| Tests | 56 |
| Icon resolutions | 7 |
| Dependencies | 3 (matplotlib, Pillow, pyinstaller) |
| External APIs | 0 |
| Internet required | No |

---

## 16. Defense Q&A — Common Questions

**Q: Why Tkinter instead of PyQt or a web framework?**
A: Tkinter is built into Python — no extra installation needed. It's lightweight, native to Windows, and perfect for a desktop productivity app. PyQt requires a license for commercial use, and web frameworks would make this a web app, which contradicts the requirement.

**Q: Why SQLite instead of PostgreSQL?**
A: SQLite is serverless, file-based, built into Python, and perfect for a local desktop app. PostgreSQL requires a server process and network configuration — unnecessary for a single-user offline app.

**Q: How does the calculator avoid eval()?**
A: It uses a recursive descent parser — a compiler technique. The `_Parser` class tokenizes the input string and evaluates it using a grammar that only allows numbers, +, -, *, /, %, and parentheses. It cannot execute Python code.

**Q: How does the Pomodoro timer not freeze the GUI?**
A: It uses `root.after(1000, callback)` — Tkinter's built-in event scheduling. This schedules the next timer tick in the event loop without blocking. The GUI processes user events between ticks.

**Q: How is the file organizer safe?**
A: It follows an 8-step safety workflow with protected directory detection, conflict resolution via renaming, explicit user confirmation, and no silent overwrites or deletions.

**Q: Where is user data stored?**
A: In `data/studydesk.db` (SQLite database) next to the application. When packaged as EXE, it's in `dist/StudyDeskPro/data/`. Never in protected Windows directories.

**Q: How does the app handle missing dependencies?**
A: Matplotlib and Pillow are optional — if missing, charts fall back to text-based displays and the icon uses a built-in fallback. The app still runs.

**Q: How was the icon created?**
A: Generated programmatically in pure Python (`assets/generate_icon.py`). It renders a graduation cap design as pixels and writes a valid Windows ICO file with 7 resolutions using only the standard library (`struct`, `zlib`, `math`).

---

*StudyDesk Pro v1.0.0 — Built with Python + Tkinter + SQLite*