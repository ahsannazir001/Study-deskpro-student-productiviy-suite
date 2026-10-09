"""Main application window with sidebar navigation and content area."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import apply_styles, COLORS, FONTS, set_theme
from app.gui import ui_helpers
from app.services import settings_service
from app.utils.helpers import get_icon_path, get_png_icon_path
from app.utils.logger import get_logger

_log = get_logger("studydesk.gui.main")

NAV_ITEMS = [
    ("Dashboard", "dashboard"),
    ("Tasks", "tasks"),
    ("Notes", "notes"),
    ("Study Planner", "study"),
    ("Pomodoro", "pomodoro"),
    ("Expenses", "expenses"),
    ("File Organizer", "files"),
    ("Password Generator", "password"),
    ("Text Tools", "texttools"),
    ("Calculator", "calculator"),
    ("Settings", "settings"),
    ("About", "about"),
]


class MainWindow:
    def __init__(self, root):
        self.root = root
        theme = settings_service.get_setting("theme", "light")
        self.colors = apply_styles(root, theme)

        w = settings_service.get_int("window_width", 1180)
        h = settings_service.get_int("window_height", 720)
        root.geometry(f"{w}x{h}")
        root.minsize(960, 600)
        root.title("StudyDesk Pro - Student Productivity Suite")

        self._set_window_icon()

        self.current_page = None
        self.nav_buttons = {}
        self.module_instances = {}

        self._build_sidebar()
        self._build_main_area()
        self._build_status_bar()

        root.bind("<Configure>", self._on_resize)

        self.navigate("dashboard")

    def _set_window_icon(self):
        ico = get_icon_path()
        if ico:
            try:
                self.root.iconbitmap(default=ico)
                return
            except tk.TclError:
                pass
        png = get_png_icon_path()
        if png:
            try:
                from PIL import Image, ImageTk
                img = Image.open(png)
                self._icon_img = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, self._icon_img)
            except Exception:
                pass

    def _build_sidebar(self):
        c = self.colors
        self.sidebar = tk.Frame(self.root, bg=c["sidebar_bg"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        title_frame = tk.Frame(self.sidebar, bg=c["sidebar_bg"])
        title_frame.pack(fill="x", padx=15, pady=(20, 5))

        tk.Label(title_frame, text="StudyDesk", bg=c["sidebar_bg"],
                 fg=c["sidebar_title"], font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(title_frame, text="PRO", bg=c["sidebar_bg"],
                 fg=c["accent"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(title_frame, text="Productivity Suite", bg=c["sidebar_bg"],
                 fg=c["text_secondary"], font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

        sep = tk.Frame(self.sidebar, bg=c["sidebar_hover"], height=1)
        sep.pack(fill="x", padx=10, pady=10)

        nav_container = tk.Frame(self.sidebar, bg=c["sidebar_bg"])
        nav_container.pack(fill="both", expand=True, padx=5)

        for label, key in NAV_ITEMS:
            btn = tk.Label(nav_container, text=f"  {label}", bg=c["sidebar_bg"],
                           fg=c["sidebar_text"], font=FONTS["sidebar"],
                           anchor="w", padx=10, pady=8, cursor="hand2")
            btn.pack(fill="x", pady=1)
            btn.bind("<Button-1>", lambda e, k=key: self.navigate(k))
            btn.bind("<Enter>", lambda e, b=btn: self._on_nav_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._on_nav_hover(b, False, k))
            self.nav_buttons[key] = btn

    def _on_nav_hover(self, btn, entering, key=None):
        c = self.colors
        if key and self.current_page == key:
            return
        btn.configure(bg=c["sidebar_hover"] if entering else c["sidebar_bg"])

    def _set_active_nav(self, key):
        c = self.colors
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg=c["sidebar_active"], fg="#FFFFFF")
            else:
                btn.configure(bg=c["sidebar_bg"], fg=c["sidebar_text"])

    def _build_main_area(self):
        c = self.colors
        self.main_area = tk.Frame(self.root, bg=c["content_bg"])
        self.main_area.pack(side="left", fill="both", expand=True)

        self.header = tk.Frame(self.main_area, bg=c["header_bg"], height=56)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        sep = tk.Frame(self.main_area, bg=c["card_border"], height=1)
        sep.pack(fill="x")

        self.header_title = tk.Label(self.header, text="Dashboard",
                                     bg=c["header_bg"], fg=c["text"],
                                     font=FONTS["header"], padx=20)
        self.header_title.pack(side="left", pady=10)

        self.content = tk.Frame(self.main_area, bg=c["content_bg"])
        self.content.pack(fill="both", expand=True)

    def _build_status_bar(self):
        c = self.colors
        self.status_bar = tk.Frame(self.main_area, bg=c["card_border"], height=24)
        self.status_bar.pack(side="bottom", fill="x")
        self.status_bar.pack_propagate(False)
        self.status_label = tk.Label(self.status_bar, text="Ready",
                                     bg=c["card_border"], fg=c["text"],
                                     font=FONTS["small"], padx=10)
        self.status_label.pack(side="left", pady=2)

    def set_status(self, text):
        try:
            self.status_label.configure(text=text)
        except tk.TclError:
            pass

    def navigate(self, key):
        if self.current_page == key:
            return
        self.current_page = key

        for child in self.content.winfo_children():
            child.destroy()

        labels = dict(NAV_ITEMS)
        self.header_title.configure(text=labels.get(key, key))
        self._set_active_nav(key)

        try:
            module = self._load_module(key)
            if module:
                module.build(self.content)
        except Exception as exc:
            _log.error("Failed to load module %s: %s", key, exc)
            ui_helpers.show_error(self.root, "Module Error",
                                  f"Could not open {labels.get(key, key)}.\n"
                                  f"Please check the application logs.")
            self._show_error_page(str(exc))

    def _load_module(self, key):
        if key in self.module_instances:
            del self.module_instances[key]

        if key == "dashboard":
            from app.gui.dashboard import DashboardView
            m = DashboardView(self)
        elif key == "tasks":
            from app.gui.tasks import TasksView
            m = TasksView(self)
        elif key == "notes":
            from app.gui.notes import NotesView
            m = NotesView(self)
        elif key == "study":
            from app.gui.study_planner import StudyPlannerView
            m = StudyPlannerView(self)
        elif key == "pomodoro":
            from app.gui.pomodoro import PomodoroView
            m = PomodoroView(self)
        elif key == "expenses":
            from app.gui.expenses import ExpensesView
            m = ExpensesView(self)
        elif key == "files":
            from app.gui.file_organizer import FileOrganizerView
            m = FileOrganizerView(self)
        elif key == "password":
            from app.gui.password_generator import PasswordGeneratorView
            m = PasswordGeneratorView(self)
        elif key == "texttools":
            from app.gui.text_tools import TextToolsView
            m = TextToolsView(self)
        elif key == "calculator":
            from app.gui.calculator import CalculatorView
            m = CalculatorView(self)
        elif key == "settings":
            from app.gui.settings import SettingsView
            m = SettingsView(self)
        elif key == "about":
            from app.gui.about import AboutView
            m = AboutView(self)
        else:
            return None

        self.module_instances[key] = m
        return m

    def _show_error_page(self, detail):
        c = self.colors
        frame = tk.Frame(self.content, bg=c["content_bg"])
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Something went wrong", bg=c["content_bg"],
                 fg=c["danger"], font=FONTS["header"]).pack(pady=40)
        tk.Label(frame, text="An unexpected error occurred.", bg=c["content_bg"],
                 fg=c["text_secondary"]).pack()

    def refresh_theme(self):
        theme = settings_service.get_setting("theme", "light")
        self.colors = apply_styles(self.root, theme)
        self.sidebar.configure(bg=self.colors["sidebar_bg"])
        self.main_area.configure(bg=self.colors["content_bg"])
        self.header.configure(bg=self.colors["header_bg"])
        self.header_title.configure(bg=self.colors["header_bg"],
                                     fg=self.colors["text"])
        self.content.configure(bg=self.colors["content_bg"])
        self.status_bar.configure(bg=self.colors["card_border"])
        self.status_label.configure(bg=self.colors["card_border"],
                                     fg=self.colors["text"])
        for child in self.content.winfo_children():
            child.destroy()
        self.current_page = None
        self.navigate("dashboard")

    def _on_resize(self, event):
        if event.widget == self.root:
            w = event.width
            h = event.height
            if w > 800 and h > 500:
                settings_service.set_setting("window_width", str(w))
                settings_service.set_setting("window_height", str(h))