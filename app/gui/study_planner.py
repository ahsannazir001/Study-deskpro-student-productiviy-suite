"""Study planner view - subjects with targets and progress tracking."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.services import study_service
from app.utils.helpers import format_duration


class StudyPlannerView:
    def __init__(self, main_window):
        self.mw = main_window
        self.editing_id = None

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Study Planner", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        today_min = study_service.get_today_study_minutes()
        total_min = study_service.get_total_study_minutes()
        summary = tk.Frame(parent, bg=c["content_bg"])
        summary.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(summary, text=f"Study Today: {format_duration(today_min)}",
                 bg=c["content_bg"], fg=c["accent"], font=FONTS["body_bold"]).pack(side="left", padx=(0, 20))
        tk.Label(summary, text=f"Total Study Time: {format_duration(total_min)}",
                 bg=c["content_bg"], fg=c["info"], font=FONTS["body_bold"]).pack(side="left")

        toolbar = tk.Frame(parent, bg=c["content_bg"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        ttk.Button(toolbar, text="+ Add Subject", command=self._show_add_dialog,
                   style="Accent.TButton").pack(side="left")

        table_frame = tk.Frame(parent, bg=c["content_bg"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        cols = ("id", "name", "daily", "weekly", "completed", "progress")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)
        headers = {"id": ("ID", 45), "name": ("Subject", 160), "daily": ("Daily Target", 90),
                   "weekly": ("Weekly Target", 90), "completed": ("Completed", 90),
                   "progress": ("Progress", 100)}
        for col, (text, width) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col != "name" else "w")
        ui_helpers.style_treeview_stripes(self.tree)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        btn_bar = tk.Frame(parent, bg=c["content_bg"])
        btn_bar.pack(fill="x", padx=20, pady=(0, 15))
        ttk.Button(btn_bar, text="Edit", command=self._show_edit_dialog).pack(side="left", padx=(0, 8))
        ttk.Button(btn_bar, text="Log Study Time", style="Success.TButton",
                   command=self._log_time).pack(side="left", padx=(0, 8))
        ttk.Button(btn_bar, text="Reset Progress", style="Warning.TButton",
                   command=self._reset_progress).pack(side="left", padx=(0, 8))
        ttk.Button(btn_bar, text="Delete", style="Danger.TButton",
                   command=self._delete_subject).pack(side="left")

        self._refresh()

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        subjects = study_service.get_all_subjects()
        for i, s in enumerate(subjects):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            pct = study_service.get_progress_percent(s)
            self.tree.insert("", "end", values=(
                s["id"], s["name"], f"{s['daily_target']:.1f}h",
                f"{s['weekly_target']:.1f}h", format_duration(s["completed_minutes"]),
                f"{pct}%"
            ), tags=tag)
        self.mw.set_status(f"{len(subjects)} subject(s)")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            ui_helpers.show_warning(self.mw.root, "No Selection", "Please select a subject first.")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _delete_subject(self):
        sid = self._selected_id()
        if sid is None:
            return
        if not ui_helpers.confirm(self.mw.root, "Delete Subject",
                                  "Delete this subject and its study sessions?"):
            return
        ok, msg = study_service.delete_subject(sid)
        if ok:
            self._refresh()
            self.mw.set_status(msg)
        else:
            ui_helpers.show_error(self.mw.root, "Error", msg)

    def _reset_progress(self):
        sid = self._selected_id()
        if sid is None:
            return
        if not ui_helpers.confirm(self.mw.root, "Reset Progress",
                                  "Reset completed study time to zero?"):
            return
        ok, msg = study_service.reset_progress(sid)
        if ok:
            self._refresh()
            self.mw.set_status(msg)

    def _log_time(self):
        sid = self._selected_id()
        if sid is None:
            return
        c = COLORS
        dlg = tk.Toplevel(self.mw.root)
        dlg.title("Log Study Time")
        dlg.geometry("320x150")
        dlg.transient(self.mw.root)
        dlg.grab_set()
        dlg.configure(bg=c["content_bg"])
        tk.Label(dlg, text="Minutes studied:", bg=c["content_bg"], fg=c["text"]).pack(pady=(20, 5))
        min_var = tk.StringVar(value="30")
        ttk.Entry(dlg, textvariable=min_var, width=10).pack(pady=5)
        def save():
            ok, msg = study_service.add_study_time(sid, min_var.get())
            if ok:
                dlg.destroy()
                self._refresh()
                self.mw.set_status(msg)
            else:
                ui_helpers.show_error(dlg, "Error", msg)
        ttk.Button(dlg, text="Save", command=save, style="Accent.TButton").pack(pady=10)

    def _show_add_dialog(self):
        self.editing_id = None
        self._show_dialog("Add Subject")

    def _show_edit_dialog(self):
        sid = self._selected_id()
        if sid is None:
            return
        subj = study_service.get_subject(sid)
        if not subj:
            return
        self.editing_id = sid
        self._show_dialog("Edit Subject", subj)

    def _show_dialog(self, title, subj=None):
        c = COLORS
        dlg = tk.Toplevel(self.mw.root)
        dlg.title(title)
        dlg.geometry("400x250")
        dlg.transient(self.mw.root)
        dlg.grab_set()
        dlg.configure(bg=c["content_bg"])
        tk.Label(dlg, text=title, bg=c["content_bg"], fg=c["text"],
                 font=FONTS["header"]).pack(anchor="w", padx=20, pady=(15, 10))
        form = tk.Frame(dlg, bg=c["content_bg"])
        form.pack(fill="both", expand=True, padx=20)

        tk.Label(form, text="Subject Name *", bg=c["content_bg"], fg=c["text"]).grid(row=0, column=0, sticky="w", pady=4)
        name_var = tk.StringVar(value=subj["name"] if subj else "")
        ttk.Entry(form, textvariable=name_var, width=30).grid(row=0, column=1, pady=4, padx=(10, 0))

        tk.Label(form, text="Daily Target (h)", bg=c["content_bg"], fg=c["text"]).grid(row=1, column=0, sticky="w", pady=4)
        daily_var = tk.StringVar(value=str(subj["daily_target"]) if subj else "2")
        ttk.Entry(form, textvariable=daily_var, width=10).grid(row=1, column=1, sticky="w", pady=4, padx=(10, 0))

        tk.Label(form, text="Weekly Target (h)", bg=c["content_bg"], fg=c["text"]).grid(row=2, column=0, sticky="w", pady=4)
        weekly_var = tk.StringVar(value=str(subj["weekly_target"]) if subj else "14")
        ttk.Entry(form, textvariable=weekly_var, width=10).grid(row=2, column=1, sticky="w", pady=4, padx=(10, 0))

        btns = tk.Frame(dlg, bg=c["content_bg"])
        btns.pack(fill="x", padx=20, pady=15)
        def save():
            if self.editing_id:
                ok, msg = study_service.update_subject(self.editing_id, name_var.get(),
                                                        daily_var.get(), weekly_var.get())
            else:
                ok, msg, _ = study_service.add_subject(name_var.get(), daily_var.get(), weekly_var.get())
            if ok:
                dlg.destroy()
                self._refresh()
                self.mw.set_status(msg)
            else:
                ui_helpers.show_error(dlg, "Validation Error", msg)
        ttk.Button(btns, text="Save", command=save, style="Accent.TButton").pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right")