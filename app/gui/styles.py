"""Theme and ttk style definitions for StudyDesk Pro.

Provides a professional light/dark theme with consistent colors, fonts,
and widget styling. All GUI modules import COLORS and FONTS from here.
"""

import tkinter as tk
from tkinter import ttk

LIGHT = {
    "sidebar_bg": "#2C3E50",
    "sidebar_active": "#3498DB",
    "sidebar_hover": "#34495E",
    "sidebar_text": "#ECF0F1",
    "sidebar_title": "#FFFFFF",
    "content_bg": "#F5F6FA",
    "card_bg": "#FFFFFF",
    "card_border": "#E0E4E8",
    "header_bg": "#FFFFFF",
    "text": "#2C3E50",
    "text_secondary": "#7F8C8D",
    "accent": "#3498DB",
    "accent_dark": "#2980B9",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "info": "#1ABC9C",
    "input_bg": "#FFFFFF",
    "input_border": "#BDC3C7",
    "table_header": "#34495E",
    "table_row_alt": "#F8F9FB",
    "tree_bg": "#FFFFFF",
    "progress_bg": "#E0E4E8",
}

DARK = {
    "sidebar_bg": "#1A1A2E",
    "sidebar_active": "#0F3460",
    "sidebar_hover": "#16213E",
    "sidebar_text": "#AAB7B8",
    "sidebar_title": "#FFFFFF",
    "content_bg": "#0D1117",
    "card_bg": "#1C2128",
    "card_border": "#30363D",
    "header_bg": "#161B22",
    "text": "#E6EDF3",
    "text_secondary": "#8B949E",
    "accent": "#58A6FF",
    "accent_dark": "#1F6FEB",
    "success": "#3FB950",
    "warning": "#D29922",
    "danger": "#F85149",
    "info": "#39D0D8",
    "input_bg": "#0D1117",
    "input_border": "#30363D",
    "table_header": "#1F2937",
    "table_row_alt": "#161B22",
    "tree_bg": "#0D1117",
    "progress_bg": "#30363D",
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "header": ("Segoe UI", 15, "bold"),
    "subheader": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "small_bold": ("Segoe UI", 9, "bold"),
    "sidebar": ("Segoe UI", 11),
    "sidebar_title": ("Segoe UI", 16, "bold"),
    "card_value": ("Segoe UI", 22, "bold"),
    "card_label": ("Segoe UI", 9),
    "button": ("Segoe UI", 10, "bold"),
    "timer": ("Segoe UI", 48, "bold"),
    "mono": ("Consolas", 14),
    "mono_large": ("Consolas", 24, "bold"),
}

_current_theme = "light"
COLORS = LIGHT


def get_theme():
    return _current_theme


def get_colors():
    return COLORS


def set_theme(name):
    global _current_theme, COLORS
    _current_theme = name if name in ("light", "dark") else "light"
    COLORS = DARK if _current_theme == "dark" else LIGHT
    return COLORS


def apply_styles(root, theme="light"):
    """Configure ttk styles for the whole application."""
    colors = set_theme(theme)
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", font=FONTS["body"], background=colors["content_bg"],
                    foreground=colors["text"])

    style.configure("TFrame", background=colors["content_bg"])
    style.configure("Card.TFrame", background=colors["card_bg"])
    style.configure("Sidebar.TFrame", background=colors["sidebar_bg"])
    style.configure("Header.TFrame", background=colors["header_bg"])

    style.configure("TLabel", background=colors["content_bg"],
                    foreground=colors["text"], font=FONTS["body"])
    style.configure("Card.TLabel", background=colors["card_bg"],
                    foreground=colors["text"])
    style.configure("CardValue.TLabel", background=colors["card_bg"],
                    foreground=colors["accent"], font=FONTS["card_value"])
    style.configure("CardLabel.TLabel", background=colors["card_bg"],
                    foreground=colors["text_secondary"], font=FONTS["card_label"])
    style.configure("Header.TLabel", background=colors["header_bg"],
                    foreground=colors["text"], font=FONTS["header"])
    style.configure("Title.TLabel", background=colors["content_bg"],
                    foreground=colors["text"], font=FONTS["title"])
    style.configure("Subheader.TLabel", background=colors["content_bg"],
                    foreground=colors["text"], font=FONTS["subheader"])
    style.configure("Secondary.TLabel", background=colors["content_bg"],
                    foreground=colors["text_secondary"], font=FONTS["small"])
    style.configure("Sidebar.TLabel", background=colors["sidebar_bg"],
                    foreground=colors["sidebar_text"], font=FONTS["sidebar"])
    style.configure("SidebarTitle.TLabel", background=colors["sidebar_bg"],
                    foreground=colors["sidebar_title"], font=FONTS["sidebar_title"])

    style.configure("TButton", font=FONTS["button"], padding=(12, 6))
    style.configure("Accent.TButton", font=FONTS["button"],
                    background=colors["accent"], foreground="#FFFFFF",
                    borderwidth=0, padding=(14, 7))
    style.map("Accent.TButton",
              background=[("active", colors["accent_dark"]),
                          ("pressed", colors["accent_dark"])])
    style.configure("Success.TButton", font=FONTS["button"],
                    background=colors["success"], foreground="#FFFFFF",
                    borderwidth=0, padding=(14, 7))
    style.map("Success.TButton",
              background=[("active", "#229954"), ("pressed", "#229954")])
    style.configure("Danger.TButton", font=FONTS["button"],
                    background=colors["danger"], foreground="#FFFFFF",
                    borderwidth=0, padding=(14, 7))
    style.map("Danger.TButton",
              background=[("active", "#C0392B"), ("pressed", "#C0392B")])
    style.configure("Warning.TButton", font=FONTS["button"],
                    background=colors["warning"], foreground="#FFFFFF",
                    borderwidth=0, padding=(14, 7))
    style.map("Warning.TButton",
              background=[("active", "#D68910"), ("pressed", "#D68910")])
    style.configure("Outline.TButton", font=FONTS["button"],
                    background=colors["card_bg"], foreground=colors["text"],
                    borderwidth=1, padding=(14, 7))
    style.map("Outline.TButton",
              background=[("active", colors["table_row_alt"])])

    style.configure("TEntry", fieldbackground=colors["input_bg"],
                    foreground=colors["text"], borderwidth=1,
                    insertcolor=colors["text"], padding=(6, 4))
    style.configure("TCombobox", fieldbackground=colors["input_bg"],
                    background=colors["card_bg"], foreground=colors["text"],
                    padding=(6, 4))
    style.map("TCombobox",
              fieldbackground=[("readonly", colors["input_bg"])],
              selectbackground=[("readonly", colors["accent"])],
              selectforeground=[("readonly", "#FFFFFF")])

    style.configure("TCheckbutton", background=colors["content_bg"],
                    foreground=colors["text"])
    style.configure("Card.TCheckbutton", background=colors["card_bg"],
                    foreground=colors["text"])

    style.configure("Treeview", background=colors["tree_bg"],
                    foreground=colors["text"], fieldbackground=colors["tree_bg"],
                    borderwidth=0, font=FONTS["body"], rowheight=28)
    style.configure("Treeview.Heading", background=colors["table_header"],
                    foreground="#FFFFFF", font=FONTS["small_bold"],
                    borderwidth=0, relief="flat")
    style.map("Treeview",
              background=[("selected", colors["accent"])],
              foreground=[("selected", "#FFFFFF")])
    style.map("Treeview.Heading",
              background=[("active", colors["sidebar_hover"])])

    style.configure("TNotebook", background=colors["content_bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=colors["card_bg"],
                    foreground=colors["text_secondary"], padding=(16, 6),
                    font=FONTS["body"])
    style.map("TNotebook.Tab",
              background=[("selected", colors["accent"])],
              foreground=[("selected", "#FFFFFF")])

    style.configure("Horizontal.TProgressbar",
                    background=colors["accent"], borderwidth=0,
                    troughcolor=colors["progress_bg"], thickness=10)
    style.configure("Success.Horizontal.TProgressbar",
                    background=colors["success"], borderwidth=0,
                    troughcolor=colors["progress_bg"], thickness=10)

    style.configure("TLabelframe", background=colors["content_bg"],
                    foreground=colors["text"], bordercolor=colors["card_border"])
    style.configure("TLabelframe.Label", background=colors["content_bg"],
                    foreground=colors["text"], font=FONTS["subheader"])

    style.configure("TSeparator", background=colors["card_border"])

    return colors


def style_treeview_stripes(tree, colors=None):
    """Apply alternating row colors to a Treeview."""
    if colors is None:
        colors = COLORS
    try:
        tree.tag_configure("evenrow", background=colors["tree_bg"])
        tree.tag_configure("oddrow", background=colors["table_row_alt"])
        tree.tag_configure("overdue", foreground=colors["danger"])
        tree.tag_configure("completed", foreground=colors["success"])
    except tk.TclError:
        pass