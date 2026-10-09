"""Settings view - theme, pomodoro, currency, defaults."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.services import settings_service


class SettingsView:
    def __init__(self, main_window):
        self.mw = main_window

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Settings", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        scroll = ui_helpers.ScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        form = scroll.inner

        self._section(form, "Appearance")
        theme_frame = tk.Frame(form, bg=c["content_bg"])
        theme_frame.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(theme_frame, text="Theme:", bg=c["content_bg"], fg=c["text"]).pack(side="left", padx=(0, 10))
        self.theme_var = tk.StringVar(value=settings_service.get_setting("theme", "light"))
        ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var,
                        value="light").pack(side="left", padx=(0, 15))
        ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var,
                        value="dark").pack(side="left")

        self._section(form, "Pomodoro Timer")
        pomo_frame = tk.Frame(form, bg=c["content_bg"])
        pomo_frame.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(pomo_frame, text="Focus Duration (min):", bg=c["content_bg"],
                 fg=c["text"]).grid(row=0, column=0, sticky="w", pady=4)
        self.focus_var = tk.StringVar(value=settings_service.get_setting("pomodoro_focus", "25"))
        ttk.Entry(pomo_frame, textvariable=self.focus_var, width=8).grid(row=0, column=1, pady=4, padx=(10, 20))
        tk.Label(pomo_frame, text="Break Duration (min):", bg=c["content_bg"],
                 fg=c["text"]).grid(row=0, column=2, sticky="w", pady=4)
        self.break_var = tk.StringVar(value=settings_service.get_setting("pomodoro_break", "5"))
        ttk.Entry(pomo_frame, textvariable=self.break_var, width=8).grid(row=0, column=3, pady=4, padx=(10, 0))

        self._section(form, "Preferences")
        pref_frame = tk.Frame(form, bg=c["content_bg"])
        pref_frame.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(pref_frame, text="Currency Symbol:", bg=c["content_bg"],
                 fg=c["text"]).grid(row=0, column=0, sticky="w", pady=4)
        self.currency_var = tk.StringVar(value=settings_service.get_setting("currency", "Rs."))
        ttk.Entry(pref_frame, textvariable=self.currency_var, width=10).grid(row=0, column=1, pady=4, padx=(10, 20))
        tk.Label(pref_frame, text="Default Task Priority:", bg=c["content_bg"],
                 fg=c["text"]).grid(row=0, column=2, sticky="w", pady=4)
        self.prio_var = tk.StringVar(value=settings_service.get_setting("default_priority", "Medium"))
        ttk.Combobox(pref_frame, textvariable=self.prio_var, width=10, state="readonly",
                     values=["Low", "Medium", "High"]).grid(row=0, column=3, pady=4, padx=(10, 0))

        self._section(form, "Data Management")
        data_frame = tk.Frame(form, bg=c["content_bg"])
        data_frame.pack(fill="x", padx=15, pady=(0, 10))
        from app.utils.helpers import get_app_data_dir
        tk.Label(data_frame, text=f"Data directory: {get_app_data_dir()}", bg=c["content_bg"],
                 fg=c["text_secondary"], font=FONTS["small"], anchor="w", wraplength=600).pack(fill="x", pady=4)
        ttk.Button(data_frame, text="Clear Activity Log", style="Warning.TButton",
                   command=self._clear_logs).pack(pady=5)

        save_frame = tk.Frame(form, bg=c["content_bg"])
        save_frame.pack(fill="x", padx=15, pady=15)
        ttk.Button(save_frame, text="Save Settings", command=self._save,
                   style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(save_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side="left")

    def _section(self, parent, title):
        c = COLORS
        tk.Label(parent, text=title, bg=c["content_bg"], fg=c["text"],
                 font=FONTS["subheader"], anchor="w").pack(fill="x", padx=15, pady=(15, 5))
        ttk.Separator(parent).pack(fill="x", padx=15, pady=(0, 5))

    def _save(self):
        theme = self.theme_var.get()
        focus = self.focus_var.get().strip()
        break_v = self.break_var.get().strip()
        currency = self.currency_var.get().strip()
        prio = self.prio_var.get()

        try:
            f = int(focus)
            b = int(break_v)
            if f < 1 or f > 120:
                ui_helpers.show_error(self.mw.root, "Invalid", "Focus must be 1-120.")
                return
            if b < 1 or b > 60:
                ui_helpers.show_error(self.mw.root, "Invalid", "Break must be 1-60.")
                return
        except ValueError:
            ui_helpers.show_error(self.mw.root, "Invalid", "Durations must be numbers.")
            return

        if not currency:
            currency = "Rs."

        settings_service.set_setting("theme", theme)
        settings_service.set_setting("pomodoro_focus", str(f))
        settings_service.set_setting("pomodoro_break", str(b))
        settings_service.set_setting("currency", currency)
        settings_service.set_setting("default_priority", prio)

        ui_helpers.show_info(self.mw.root, "Saved", "Settings saved successfully.")
        self.mw.set_status("Settings saved")
        if theme != settings_service.get_setting("theme", "light"):
            self.mw.refresh_theme()

    def _reset_defaults(self):
        if not ui_helpers.confirm(self.mw.root, "Reset Settings",
                                  "Reset all settings to defaults?"):
            return
        defaults = {"theme": "light", "pomodoro_focus": "25", "pomodoro_break": "5",
                    "currency": "Rs.", "default_priority": "Medium"}
        for k, v in defaults.items():
            settings_service.set_setting(k, v)
        ui_helpers.show_info(self.mw.root, "Reset", "Settings reset to defaults.")
        self.mw.refresh_theme()

    def _clear_logs(self):
        if not ui_helpers.confirm(self.mw.root, "Clear Logs",
                                  "Clear all activity log entries?"):
            return
        from app.database import db
        try:
            db.execute("DELETE FROM activity_logs")
            ui_helpers.show_info(self.mw.root, "Cleared", "Activity log cleared.")
        except Exception:
            ui_helpers.show_error(self.mw.root, "Error", "Could not clear logs.")