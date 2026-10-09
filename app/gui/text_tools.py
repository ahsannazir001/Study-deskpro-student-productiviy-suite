"""Text tools view - word/char/line count and text transformations."""

import re
import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.utils.helpers import safe_clipboard_set


class TextToolsView:
    def __init__(self, main_window):
        self.mw = main_window

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Text Tools", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        stats_frame = tk.Frame(parent, bg=c["content_bg"])
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.words_label = tk.Label(stats_frame, text="Words: 0", bg=c["content_bg"],
                                    fg=c["accent"], font=FONTS["body_bold"])
        self.words_label.pack(side="left", padx=(0, 20))
        self.chars_label = tk.Label(stats_frame, text="Characters: 0", bg=c["content_bg"],
                                    fg=c["info"], font=FONTS["body_bold"])
        self.chars_label.pack(side="left", padx=(0, 20))
        self.lines_label = tk.Label(stats_frame, text="Lines: 0", bg=c["content_bg"],
                                    fg=c["success"], font=FONTS["body_bold"])
        self.lines_label.pack(side="left")

        input_frame = tk.Frame(parent, bg=c["card_bg"],
                               highlightbackground=c["card_border"], highlightthickness=1)
        input_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        tk.Label(input_frame, text="Input Text", bg=c["card_bg"], fg=c["text"],
                 font=FONTS["subheader"], anchor="w").pack(fill="x", padx=15, pady=(12, 5))
        self.text_area = tk.Text(input_frame, wrap="word", font=FONTS["body"],
                                 bg=c["card_bg"], fg=c["text"], relief="flat",
                                 padx=10, pady=10, undo=True)
        self.text_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.text_area.bind("<KeyRelease>", lambda e: self._update_stats())

        btn_frame = tk.Frame(parent, bg=c["content_bg"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ttk.Button(btn_frame, text="UPPERCASE", command=self._to_upper).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="lowercase", command=self._to_lower).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Title Case", command=self._to_title).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Remove Extra Spaces", command=self._remove_extra_spaces).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Remove Blank Lines", command=self._remove_blank_lines).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Copy", command=self._copy).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Clear", command=self._clear, style="Danger.TButton").pack(side="left")

    def _get_text(self):
        return self.text_area.get("1.0", "end-1c")

    def _set_text(self, text):
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text)
        self._update_stats()

    def _update_stats(self):
        text = self._get_text()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        lines = text.count("\n") + 1 if text else 0
        self.words_label.configure(text=f"Words: {words}")
        self.chars_label.configure(text=f"Characters: {chars}")
        self.lines_label.configure(text=f"Lines: {lines}")

    def _to_upper(self):
        self._set_text(self._get_text().upper())

    def _to_lower(self):
        self._set_text(self._get_text().lower())

    def _to_title(self):
        self._set_text(self._get_text().title())

    def _remove_extra_spaces(self):
        text = self._get_text()
        lines = text.split("\n")
        cleaned = []
        for line in lines:
            line = re.sub(r"[ \t]+", " ", line).strip()
            cleaned.append(line)
        self._set_text("\n".join(cleaned))

    def _remove_blank_lines(self):
        text = self._get_text()
        lines = [l for l in text.split("\n") if l.strip()]
        self._set_text("\n".join(lines))

    def _copy(self):
        text = self._get_text()
        if not text:
            ui_helpers.show_warning(self.mw.root, "Nothing to Copy", "Text is empty.")
            return
        if safe_clipboard_set(self.mw.root, text):
            self.mw.set_status("Text copied to clipboard")
        else:
            ui_helpers.show_error(self.mw.root, "Clipboard Error", "Could not copy.")

    def _clear(self):
        self._set_text("")
        self.mw.set_status("Text cleared")