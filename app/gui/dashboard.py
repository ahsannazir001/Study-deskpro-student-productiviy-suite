"""Dashboard view - overview cards and charts."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.services import task_service, note_service, expense_service, study_service
from app.database import db
from app.utils.helpers import format_currency, format_duration, relative_time, today_iso
from app.services import settings_service


class DashboardView:
    def __init__(self, main_window):
        self.mw = main_window

    def build(self, parent):
        c = COLORS
        scroll = ui_helpers.ScrollableFrame(parent)
        scroll.pack(fill="both", expand=True)
        container = scroll.inner

        stats = task_service.get_stats()
        note_count = note_service.get_count()
        study_min = study_service.get_today_study_minutes()
        pomo_count = self._get_pomodoro_count()
        currency = settings_service.get_setting("currency", "Rs.")
        monthly_exp = expense_service.get_monthly_total()

        cards_frame = tk.Frame(container, bg=c["content_bg"])
        cards_frame.pack(fill="x", padx=20, pady=(20, 10))

        row1 = tk.Frame(cards_frame, bg=c["content_bg"])
        row1.pack(fill="x", pady=(0, 12))
        self._card(row1, "Total Tasks", stats["total"], c["accent"])
        self._card(row1, "Completed", stats["completed"], c["success"])
        self._card(row1, "Pending", stats["pending"], c["warning"])
        self._card(row1, "Today's Tasks", stats["today"], c["info"])

        row2 = tk.Frame(cards_frame, bg=c["content_bg"])
        row2.pack(fill="x", pady=(0, 12))
        self._card(row2, "Total Notes", note_count, c["accent"])
        self._card(row2, "Study Today", format_duration(study_min), c["info"])
        self._card(row2, "Pomodoro Sessions", pomo_count, c["success"])
        self._card(row2, "Monthly Expenses", format_currency(monthly_exp, currency), c["danger"])

        if stats["overdue"] > 0:
            warn = tk.Frame(container, bg=c["danger"])
            warn.pack(fill="x", padx=20, pady=(0, 10))
            tk.Label(warn, text=f"  {stats['overdue']} task(s) are overdue!",
                     bg=c["danger"], fg="#FFFFFF", font=FONTS["body_bold"],
                     pady=6, anchor="w").pack(fill="x")

        charts_frame = tk.Frame(container, bg=c["content_bg"])
        charts_frame.pack(fill="x", padx=20, pady=(5, 10))
        self._build_task_chart(charts_frame, stats)
        self._build_expense_chart(charts_frame)

        activity_frame = tk.Frame(container, bg=c["card_bg"],
                                  highlightbackground=c["card_border"],
                                  highlightthickness=1)
        activity_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        tk.Label(activity_frame, text="Recent Activity", bg=c["card_bg"],
                 fg=c["text"], font=FONTS["subheader"], anchor="w").pack(
            fill="x", padx=15, pady=(12, 5))
        self._build_activity_list(activity_frame)

    def _card(self, parent, title, value, color):
        card = ui_helpers.create_card(parent, title, value, color=color, width=200)
        card.pack(side="left", padx=(0, 12))

    def _get_pomodoro_count(self):
        try:
            row = db.query_one(
                "SELECT COUNT(*) AS c FROM pomodoro_sessions WHERE session_type='focus'"
            )
            return row["c"] if row else 0
        except Exception:
            return 0

    def _build_task_chart(self, parent, stats):
        c = COLORS
        frame = tk.Frame(parent, bg=c["card_bg"],
                         highlightbackground=c["card_border"],
                         highlightthickness=1)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(frame, text="Task Status", bg=c["card_bg"], fg=c["text"],
                 font=FONTS["subheader"], anchor="w").pack(fill="x", padx=15, pady=(12, 5))

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from PIL import Image, ImageTk

            fig, ax = plt.subplots(figsize=(3.2, 2.4), dpi=80)
            labels = ["Completed", "Pending"]
            sizes = [stats["completed"], stats["pending"]]
            colors_pie = [c["success"], c["warning"]]
            if sum(sizes) == 0:
                sizes = [1]
                labels = ["No Tasks"]
                colors_pie = [c["text_secondary"]]
            ax.pie(sizes, labels=labels, colors=colors_pie, autopct=None,
                   startangle=90, textprops={"fontsize": 8})
            ax.axis("equal")
            fig.tight_layout()
            fig.canvas.draw()
            img = Image.frombytes("RGB", fig.canvas.get_width_height(),
                                  fig.canvas.tostring_rgb())
            self._task_img = ImageTk.PhotoImage(img)
            tk.Label(frame, image=self._task_img, bg=c["card_bg"]).pack(padx=10, pady=5)
            plt.close(fig)
        except Exception:
            self._text_task_chart(frame, stats)

    def _text_task_chart(self, frame, stats):
        c = COLORS
        total = max(1, stats["total"])
        for label, val, col in [("Completed", stats["completed"], c["success"]),
                                ("Pending", stats["pending"], c["warning"])]:
            row = tk.Frame(frame, bg=c["card_bg"])
            row.pack(fill="x", padx=15, pady=3)
            tk.Label(row, text=label, bg=c["card_bg"], fg=c["text"],
                     font=FONTS["small"], width=12, anchor="w").pack(side="left")
            bar = ttk.Progressbar(row, length=120,
                                  value=int((val / total) * 100))
            bar.pack(side="left", padx=5)
            tk.Label(row, text=str(val), bg=c["card_bg"], fg=col,
                     font=FONTS["small_bold"]).pack(side="left")

    def _build_expense_chart(self, parent):
        c = COLORS
        frame = tk.Frame(parent, bg=c["card_bg"],
                         highlightbackground=c["card_border"],
                         highlightthickness=1)
        frame.pack(side="left", fill="both", expand=True)
        tk.Label(frame, text="Expenses by Category", bg=c["card_bg"],
                 fg=c["text"], font=FONTS["subheader"], anchor="w").pack(
            fill="x", padx=15, pady=(12, 5))

        totals = expense_service.get_category_totals()
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from PIL import Image, ImageTk

            if totals:
                cats = list(totals.keys())
                vals = [totals[k] for k in cats]
                fig, ax = plt.subplots(figsize=(3.2, 2.4), dpi=80)
                ax.barh(cats, vals, color=c["accent"])
                ax.tick_params(axis="both", labelsize=7)
                fig.tight_layout()
                fig.canvas.draw()
                img = Image.frombytes("RGB", fig.canvas.get_width_height(),
                                      fig.canvas.tostring_rgb())
                self._exp_img = ImageTk.PhotoImage(img)
                tk.Label(frame, image=self._exp_img, bg=c["card_bg"]).pack(padx=10, pady=5)
                plt.close(fig)
            else:
                tk.Label(frame, text="No expenses recorded", bg=c["card_bg"],
                         fg=c["text_secondary"], font=FONTS["small"]).pack(pady=20)
        except Exception:
            if totals:
                for cat, val in totals.items():
                    row = tk.Frame(frame, bg=c["card_bg"])
                    row.pack(fill="x", padx=15, pady=2)
                    tk.Label(row, text=cat, bg=c["card_bg"], fg=c["text"],
                             font=FONTS["small"], width=12, anchor="w").pack(side="left")
                    tk.Label(row, text=f"Rs. {val:,.0f}", bg=c["card_bg"],
                             fg=c["accent"], font=FONTS["small_bold"]).pack(side="left")
            else:
                tk.Label(frame, text="No expenses recorded", bg=c["card_bg"],
                         fg=c["text_secondary"], font=FONTS["small"]).pack(pady=20)

    def _build_activity_list(self, parent):
        c = COLORS
        try:
            logs = db.query(
                "SELECT module, action, detail, created_at FROM activity_logs "
                "ORDER BY created_at DESC LIMIT 8"
            )
        except Exception:
            logs = []

        if not logs:
            tk.Label(parent, text="No recent activity", bg=c["card_bg"],
                     fg=c["text_secondary"], font=FONTS["small"]).pack(pady=15)
            return

        for log in logs:
            row = tk.Frame(parent, bg=c["card_bg"])
            row.pack(fill="x", padx=15, pady=2)
            text = f"{log['module'].title()} - {log['action']}"
            tk.Label(row, text=text, bg=c["card_bg"], fg=c["text"],
                     font=FONTS["small"], anchor="w").pack(side="left")
            tk.Label(row, text=relative_time(log["created_at"]), bg=c["card_bg"],
                     fg=c["text_secondary"], font=FONTS["small"]).pack(side="right")