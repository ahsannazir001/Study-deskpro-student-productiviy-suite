"""Password generator view - secure generation using secrets module."""

import string
import secrets as _secrets
import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.utils.helpers import safe_clipboard_set
from app.utils.logger import get_logger

_log = get_logger("studydesk.password")


class PasswordGeneratorView:
    def __init__(self, main_window):
        self.mw = main_window
        self.length_var = tk.IntVar(value=16)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.num_var = tk.BooleanVar(value=True)
        self.sym_var = tk.BooleanVar(value=True)

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Password Generator", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        card = tk.Frame(parent, bg=c["card_bg"],
                        highlightbackground=c["card_border"], highlightthickness=1)
        card.pack(fill="x", padx=20, pady=10)

        result_frame = tk.Frame(card, bg=c["card_bg"])
        result_frame.pack(fill="x", padx=20, pady=(20, 10))
        self.result_var = tk.StringVar(value="Click Generate to create a password")
        self.result_entry = tk.Entry(result_frame, textvariable=self.result_var,
                                     font=FONTS["mono_large"], bg=c["input_bg"],
                                     fg=c["text"], relief="solid", borderwidth=1,
                                     readonlybackground=c["input_bg"], state="readonly",
                                     justify="center")
        self.result_entry.pack(fill="x", ipady=8)

        strength_frame = tk.Frame(card, bg=c["card_bg"])
        strength_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.strength_label = tk.Label(strength_frame, text="", bg=c["card_bg"],
                                       fg=c["text_secondary"], font=FONTS["small"])
        self.strength_label.pack(anchor="w")

        options_frame = tk.Frame(card, bg=c["card_bg"])
        options_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(options_frame, text="Length:", bg=c["card_bg"], fg=c["text"]).grid(row=0, column=0, sticky="w", pady=5)
        length_scale = ttk.Scale(options_frame, from_=4, to=64, orient="horizontal",
                                 variable=self.length_var, length=200, command=self._on_length)
        length_scale.grid(row=0, column=1, padx=10, pady=5)
        self.length_display = tk.Label(options_frame, text="16", bg=c["card_bg"],
                                       fg=c["accent"], font=FONTS["body_bold"])
        self.length_display.grid(row=0, column=2, pady=5)

        ttk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=self.upper_var,
                         style="Card.TCheckbutton").grid(row=1, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=self.lower_var,
                         style="Card.TCheckbutton").grid(row=2, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Checkbutton(options_frame, text="Numbers (0-9)", variable=self.num_var,
                         style="Card.TCheckbutton").grid(row=3, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Checkbutton(options_frame, text="Symbols (!@#$...)", variable=self.sym_var,
                         style="Card.TCheckbutton").grid(row=4, column=0, columnspan=3, sticky="w", pady=2)

        btn_frame = tk.Frame(card, bg=c["card_bg"])
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        ttk.Button(btn_frame, text="Generate", command=self._generate,
                   style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="Copy", command=self._copy).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(side="left")

    def _on_length(self, event=None):
        val = int(self.length_var.get())
        self.length_display.configure(text=str(val))

    def _generate(self):
        length = int(self.length_var.get())
        if length < 4:
            ui_helpers.show_warning(self.mw.root, "Too Short", "Minimum length is 4.")
            return
        if length > 64:
            ui_helpers.show_warning(self.mw.root, "Too Long", "Maximum length is 64.")
            return
        pools = []
        if self.upper_var.get():
            pools.append(string.ascii_uppercase)
        if self.lower_var.get():
            pools.append(string.ascii_lowercase)
        if self.num_var.get():
            pools.append(string.digits)
        if self.sym_var.get():
            pools.append("!@#$%^&*()_+-=[]{}|;:,.<>?")
        if not pools:
            ui_helpers.show_warning(self.mw.root, "No Character Types",
                                    "Select at least one character type.")
            return
        all_chars = "".join(pools)
        password = []
        for pool in pools:
            password.append(_secrets.choice(pool))
        for _ in range(length - len(pools)):
            password.append(_secrets.choice(all_chars))
        _secrets.SystemRandom().shuffle(password)
        result = "".join(password[:length])
        self.result_var.set(result)
        self.result_entry.configure(state="normal")
        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, result)
        self.result_entry.configure(state="readonly")
        self._check_strength(result)
        self.mw.set_status("Password generated")

    def _check_strength(self, password):
        c = COLORS
        score = 0
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        variety = sum([self.upper_var.get(), self.lower_var.get(),
                       self.num_var.get(), self.sym_var.get()])
        score += variety - 1
        if score >= 4:
            self.strength_label.configure(text="Strength: Strong", fg=c["success"])
        elif score >= 2:
            self.strength_label.configure(text="Strength: Medium", fg=c["warning"])
        else:
            self.strength_label.configure(text="Strength: Weak", fg=c["danger"])

    def _copy(self):
        pwd = self.result_var.get()
        if not pwd or pwd == "Click Generate to create a password":
            ui_helpers.show_warning(self.mw.root, "Nothing to Copy", "Generate a password first.")
            return
        if safe_clipboard_set(self.mw.root, pwd):
            self.mw.set_status("Password copied to clipboard")
        else:
            ui_helpers.show_error(self.mw.root, "Clipboard Error", "Could not copy to clipboard.")

    def _clear(self):
        self.result_var.set("")
        self.result_entry.configure(state="normal")
        self.result_entry.delete(0, "end")
        self.result_entry.configure(state="readonly")
        self.strength_label.configure(text="", fg=COLORS["text_secondary"])