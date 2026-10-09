"""Pomodoro timer view - non-blocking timer using after()."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.services import settings_service
from app.database import db
from app.utils.helpers import now_iso
from app.utils.logger import get_logger

_log = get_logger("studydesk.pomodoro")


class PomodoroView:
    def __init__(self, main_window):
        self.mw = main_window
        self.running = False
        self.paused = False
        self.remaining = 0
        self.total = 0
        self.mode = "focus"
        self.session_count = 0
        self.after_id = None

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Pomodoro Timer", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        center = tk.Frame(parent, bg=c["content_bg"])
        center.pack(fill="both", expand=True, padx=20, pady=10)

        timer_card = tk.Frame(center, bg=c["card_bg"],
                              highlightbackground=c["card_border"], highlightthickness=1)
        timer_card.pack(pady=20)

        self.mode_label = tk.Label(timer_card, text="Focus Time", bg=c["card_bg"],
                                   fg=c["accent"], font=FONTS["subheader"])
        self.mode_label.pack(pady=(20, 5))

        self.time_label = tk.Label(timer_card, text="25:00", bg=c["card_bg"],
                                   fg=c["text"], font=FONTS["timer"])
        self.time_label.pack(pady=10)

        self.session_label = tk.Label(timer_card, text="Sessions completed: 0",
                                      bg=c["card_bg"], fg=c["text_secondary"],
                                      font=FONTS["body"])
        self.session_label.pack(pady=(5, 20))

        btn_frame = tk.Frame(timer_card, bg=c["card_bg"])
        btn_frame.pack(pady=(0, 20))

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self._start,
                                    style="Accent.TButton", width=10)
        self.start_btn.pack(side="left", padx=5)
        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self._pause,
                                    state="disabled", width=10)
        self.pause_btn.pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset", command=self._reset, width=10).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Skip", command=self._skip, width=10).pack(side="left", padx=5)

        settings_frame = tk.Frame(center, bg=c["card_bg"],
                                  highlightbackground=c["card_border"], highlightthickness=1)
        settings_frame.pack(fill="x", padx=50, pady=10)

        tk.Label(settings_frame, text="Custom Duration", bg=c["card_bg"],
                 fg=c["text"], font=FONTS["subheader"]).pack(anchor="w", padx=15, pady=(12, 5))

        row = tk.Frame(settings_frame, bg=c["card_bg"])
        row.pack(padx=15, pady=(0, 12))

        focus_min = settings_service.get_int("pomodoro_focus", 25)
        break_min = settings_service.get_int("pomodoro_break", 5)

        tk.Label(row, text="Focus (min):", bg=c["card_bg"], fg=c["text"]).pack(side="left", padx=(0, 5))
        self.focus_var = tk.StringVar(value=str(focus_min))
        ttk.Entry(row, textvariable=self.focus_var, width=5).pack(side="left", padx=(0, 15))

        tk.Label(row, text="Break (min):", bg=c["card_bg"], fg=c["text"]).pack(side="left", padx=(0, 5))
        self.break_var = tk.StringVar(value=str(break_min))
        ttk.Entry(row, textvariable=self.break_var, width=5).pack(side="left", padx=(0, 15))

        ttk.Button(row, text="Apply", command=self._apply_duration).pack(side="left")

        self._reset_display()

    def _apply_duration(self):
        try:
            f = int(self.focus_var.get())
            b = int(self.break_var.get())
            if f < 1 or f > 120:
                ui_helpers.show_error(self.mw.root, "Invalid", "Focus must be 1-120 minutes.")
                return
            if b < 1 or b > 60:
                ui_helpers.show_error(self.mw.root, "Invalid", "Break must be 1-60 minutes.")
                return
            settings_service.set_setting("pomodoro_focus", str(f))
            settings_service.set_setting("pomodoro_break", str(b))
            if not self.running:
                self._reset_display()
            self.mw.set_status("Duration updated")
        except ValueError:
            ui_helpers.show_error(self.mw.root, "Invalid", "Please enter valid numbers.")

    def _reset_display(self):
        focus = settings_service.get_int("pomodoro_focus", 25)
        self.remaining = focus * 60
        self.total = focus * 60
        self.mode = "focus"
        self.mode_label.configure(text="Focus Time", fg=COLORS["accent"])
        self._update_display()

    def _update_display(self):
        m = self.remaining // 60
        s = self.remaining % 60
        self.time_label.configure(text=f"{m:02d}:{s:02d}")

    def _start(self):
        if self.running and self.paused:
            self.paused = False
            self.pause_btn.configure(text="Pause")
            self.start_btn.configure(state="disabled")
            self._tick()
            return
        if self.running:
            return
        if self.remaining <= 0:
            self._reset_display()
        self.running = True
        self.paused = False
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal", text="Pause")
        self._tick()

    def _pause(self):
        if not self.running:
            return
        self.paused = True
        if self.after_id:
            self.mw.root.after_cancel(self.after_id)
            self.after_id = None
        self.pause_btn.configure(state="disabled")
        self.start_btn.configure(state="normal", text="Resume")

    def _reset(self):
        self.running = False
        self.paused = False
        if self.after_id:
            self.mw.root.after_cancel(self.after_id)
            self.after_id = None
        self.start_btn.configure(state="normal", text="Start")
        self.pause_btn.configure(state="disabled", text="Pause")
        self._reset_display()
        self.mw.set_status("Timer reset")

    def _skip(self):
        self._complete_session()

    def _tick(self):
        if not self.running or self.paused:
            return
        self.remaining -= 1
        self._update_display()
        if self.remaining <= 0:
            self._complete_session()
            return
        self.after_id = self.mw.root.after(1000, self._tick)

    def _complete_session(self):
        self.running = False
        self.paused = False
        if self.after_id:
            self.mw.root.after_cancel(self.after_id)
            self.after_id = None

        if self.mode == "focus":
            self.session_count += 1
            self.session_label.configure(text=f"Sessions completed: {self.session_count}")
            try:
                duration = self.total // 60
                db.execute(
                    "INSERT INTO pomodoro_sessions (duration_minutes, session_type, "
                    "completed_at) VALUES (?, 'focus', ?)",
                    (duration, now_iso()),
                )
                db.log_activity("pomodoro", "complete_focus", f"{duration}min")
            except Exception as exc:
                _log.error("Failed to save pomodoro session: %s", exc)
            ui_helpers.show_info(self.mw.root, "Focus Complete!",
                                 "Great work! Time for a break.")
            self.mode = "break"
            break_min = settings_service.get_int("pomodoro_break", 5)
            self.remaining = break_min * 60
            self.total = break_min * 60
            self.mode_label.configure(text="Break Time", fg=COLORS["success"])
        else:
            ui_helpers.show_info(self.mw.root, "Break Over",
                                 "Break complete. Ready for the next focus session?")
            self.mode = "focus"
            focus_min = settings_service.get_int("pomodoro_focus", 25)
            self.remaining = focus_min * 60
            self.total = focus_min * 60
            self.mode_label.configure(text="Focus Time", fg=COLORS["accent"])

        self._update_display()
        self.start_btn.configure(state="normal", text="Start")
        self.pause_btn.configure(state="disabled", text="Pause")