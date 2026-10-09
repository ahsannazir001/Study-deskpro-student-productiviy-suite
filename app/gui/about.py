"""About view - application information."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app import __version__, __app_name__


class AboutView:
    def __init__(self, main_window):
        self.mw = main_window

    def build(self, parent):
        c = COLORS
        scroll_frame = tk.Frame(parent, bg=c["content_bg"])
        scroll_frame.pack(fill="both", expand=True)

        card = tk.Frame(scroll_frame, bg=c["card_bg"],
                        highlightbackground=c["card_border"], highlightthickness=1)
        card.pack(fill="both", expand=True, padx=40, pady=30)

        tk.Label(card, text="StudyDesk Pro", bg=c["card_bg"], fg=c["accent"],
                 font=("Segoe UI", 28, "bold")).pack(pady=(30, 5))
        tk.Label(card, text="Student Productivity & Study Management Suite",
                 bg=c["card_bg"], fg=c["text_secondary"], font=FONTS["body"]).pack(pady=(0, 20))

        info_frame = tk.Frame(card, bg=c["card_bg"])
        info_frame.pack(fill="x", padx=40, pady=10)

        rows = [
            ("Version", __version__),
            ("Technology", "Python + Tkinter + SQLite"),
            ("Charts", "Matplotlib"),
            ("Image Processing", "Pillow"),
            ("Packaging", "PyInstaller"),
            ("Platform", "Windows 10/11"),
        ]
        for i, (key, val) in enumerate(rows):
            tk.Label(info_frame, text=key, bg=c["card_bg"], fg=c["text_secondary"],
                     font=FONTS["small_bold"], width=18, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            tk.Label(info_frame, text=val, bg=c["card_bg"], fg=c["text"],
                     font=FONTS["body"], anchor="w").grid(row=i, column=1, sticky="w", pady=3)

        ttk.Separator(card).pack(fill="x", padx=40, pady=20)

        tk.Label(card, text="Features", bg=c["card_bg"], fg=c["text"],
                 font=FONTS["subheader"]).pack(anchor="w", padx=40, pady=(0, 8))
        features = (
            "Task Management  -  Notes Management  -  Study Planning\n"
            "Pomodoro Timer  -  Expense Tracking  -  File Organizer\n"
            "Password Generator  -  Text Utilities  -  Calculator\n"
            "Dashboard Analytics  -  Settings"
        )
        tk.Label(card, text=features, bg=c["card_bg"], fg=c["text_secondary"],
                 font=FONTS["body"], justify="center").pack(pady=(0, 20))

        tk.Label(card, text="All data is stored locally. No internet connection required.",
                 bg=c["card_bg"], fg=c["text_secondary"], font=FONTS["small"]).pack(pady=(0, 30))