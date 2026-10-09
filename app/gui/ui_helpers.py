"""Reusable UI components and dialog helpers."""

import tkinter as tk
from tkinter import ttk, messagebox

from app.gui.styles import COLORS, FONTS, style_treeview_stripes


def show_error(parent, title, message):
    messagebox.showerror(title, message, parent=parent)


def show_info(parent, title, message):
    messagebox.showinfo(title, message, parent=parent)


def show_warning(parent, title, message):
    messagebox.showwarning(title, message, parent=parent)


def confirm(parent, title, message):
    return messagebox.askyesno(title, message, parent=parent)


class ScrollableFrame(ttk.Frame):
    """A scrollable frame using a canvas + inner frame."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                bg=COLORS["content_bg"])
        self.scrollbar = ttk.Scrollbar(self, orient="vertical",
                                       command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self.inner.bind("<Configure>",
                         lambda e: self.canvas.configure(
                             scrollregion=self.canvas.bbox("all")))
        self._inner_id = self.canvas.create_window((0, 0), window=self.inner,
                                                   anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind("<Destroy>", self._on_destroy)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._inner_id, width=event.width)

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")
        except tk.TclError:
            pass

    def _on_destroy(self, event):
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass


def create_card(parent, title, value, icon="", color=None, width=180):
    """Create a dashboard stat card. Returns the frame."""
    colors = COLORS
    if color is None:
        color = colors["accent"]
    card = tk.Frame(parent, bg=colors["card_bg"], relief="flat",
                    highlightbackground=colors["card_border"],
                    highlightthickness=1)
    card.pack_propagate(False)
    card.configure(width=width, height=100)

    bar = tk.Frame(card, bg=color, height=4)
    bar.pack(fill="x", side="top")

    content = tk.Frame(card, bg=colors["card_bg"])
    content.pack(fill="both", expand=True, padx=12, pady=8)

    label = tk.Label(content, text=title, bg=colors["card_bg"],
                     fg=colors["text_secondary"], font=FONTS["card_label"],
                     anchor="w")
    label.pack(fill="x")

    val = tk.Label(content, text=str(value), bg=colors["card_bg"],
                   fg=color, font=FONTS["card_value"], anchor="w")
    val.pack(fill="x", pady=(2, 0))

    if icon:
        ic = tk.Label(content, text=icon, bg=colors["card_bg"],
                      fg=colors["text_secondary"], font=FONTS["body_bold"])
        ic.place(relx=0.95, rely=0.15, anchor="ne")

    return card


def section_label(parent, text):
    colors = COLORS
    lbl = tk.Label(parent, text=text, bg=colors["content_bg"],
                   fg=colors["text"], font=FONTS["subheader"], anchor="w")
    return lbl


def make_button(parent, text, command, style="Accent.TButton", width=None):
    btn = ttk.Button(parent, text=text, command=command, style=style)
    if width:
        btn.configure(width=width)
    return btn


def empty_state(parent, message):
    colors = COLORS
    frame = tk.Frame(parent, bg=colors["content_bg"])
    frame.pack(fill="both", expand=True)
    lbl = tk.Label(frame, text=message, bg=colors["content_bg"],
                   fg=colors["text_secondary"], font=FONTS["body"])
    lbl.pack(expand=True)
    return frame