"""Tasks view - full CRUD with search, filter, sort."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.services import task_service
from app.utils.validators import is_overdue
from app.utils.helpers import today_iso


class TasksView:
    def __init__(self, main_window):
        self.mw = main_window
        self.search_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="All")
        self.status_var = tk.StringVar(value="All")
        self.sort_var = tk.StringVar(value="created_desc")
        self.editing_id = None

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)

        tk.Label(top, text="Task Manager", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        toolbar = tk.Frame(parent, bg=c["content_bg"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(toolbar, text="Search:", bg=c["content_bg"],
                 fg=c["text"]).pack(side="left", padx=(0, 5))
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self._refresh())

        ttk.Label(toolbar, text="Priority:").pack(side="left", padx=(0, 5))
        prio = ttk.Combobox(toolbar, textvariable=self.priority_var, width=8,
                            values=["All", "Low", "Medium", "High"],
                            state="readonly")
        prio.pack(side="left", padx=(0, 10))
        prio.bind("<<ComboboxSelected>>", lambda e: self._refresh())

        ttk.Label(toolbar, text="Status:").pack(side="left", padx=(0, 5))
        stat = ttk.Combobox(toolbar, textvariable=self.status_var, width=10,
                            values=["All", "Pending", "Completed"],
                            state="readonly")
        stat.pack(side="left", padx=(0, 10))
        stat.bind("<<ComboboxSelected>>", lambda e: self._refresh())

        ttk.Label(toolbar, text="Sort:").pack(side="left", padx=(0, 5))
        sort = ttk.Combobox(toolbar, textvariable=self.sort_var, width=14,
                            state="readonly",
                            values=["created_desc", "created_asc", "due_asc",
                                    "due_desc", "priority_desc", "title_asc"])
        sort.pack(side="left", padx=(0, 10))
        sort.bind("<<ComboboxSelected>>", lambda e: self._refresh())

        ttk.Button(toolbar, text="+ Add Task", command=self._show_add_dialog,
                   style="Accent.TButton").pack(side="right")

        table_frame = tk.Frame(parent, bg=c["content_bg"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        cols = ("id", "title", "priority", "status", "due", "created")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                 selectmode="browse")
        headers = {"id": ("ID", 50), "title": ("Title", 280), "priority": ("Priority", 80),
                   "status": ("Status", 90), "due": ("Due Date", 100),
                   "created": ("Created", 100)}
        for col, (text, width) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col != "title" else "w")
        ui_helpers.style_treeview_stripes(self.tree)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._show_edit_dialog())

        btn_bar = tk.Frame(parent, bg=c["content_bg"])
        btn_bar.pack(fill="x", padx=20, pady=(0, 15))
        ttk.Button(btn_bar, text="Edit", command=self._show_edit_dialog).pack(side="left", padx=(0, 8))
        ttk.Button(btn_bar, text="Mark Complete", style="Success.TButton",
                   command=lambda: self._toggle_status("Completed")).pack(side="left", padx=(0, 8))
        ttk.Button(btn_bar, text="Mark Pending", style="Warning.TButton",
                   command=lambda: self._toggle_status("Pending")).pack(side="left", padx=(0, 8))
        ttk.Button(btn_bar, text="Delete", style="Danger.TButton",
                   command=self._delete_task).pack(side="left")

        self._refresh()

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        search = self.search_var.get().strip()
        prio = self.priority_var.get()
        stat = self.status_var.get()
        sort = self.sort_var.get()
        prio_f = "" if prio == "All" else prio
        stat_f = "" if stat == "All" else stat
        tasks = task_service.get_all_tasks(search, prio_f, stat_f, sort)
        for i, t in enumerate(tasks):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tags = [tag]
            if t["status"] == "Completed":
                tags.append("completed")
            elif is_overdue(t["due_date"], t["status"]):
                tags.append("overdue")
            self.tree.insert("", "end", values=(
                t["id"], t["title"], t["priority"], t["status"],
                t["due_date"] or "-", t["created_at"][:10]
            ), tags=tags)
        self.mw.set_status(f"{len(tasks)} task(s) shown")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            ui_helpers.show_warning(self.mw.root, "No Selection", "Please select a task first.")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _toggle_status(self, status):
        tid = self._selected_id()
        if tid is None:
            return
        ok, msg = task_service.set_status(tid, status)
        if ok:
            self._refresh()
            self.mw.set_status(msg)
        else:
            ui_helpers.show_error(self.mw.root, "Error", msg)

    def _delete_task(self):
        tid = self._selected_id()
        if tid is None:
            return
        if not ui_helpers.confirm(self.mw.root, "Delete Task",
                                  "Are you sure you want to delete this task?"):
            return
        ok, msg = task_service.delete_task(tid)
        if ok:
            self._refresh()
            self.mw.set_status(msg)
        else:
            ui_helpers.show_error(self.mw.root, "Error", msg)

    def _show_add_dialog(self):
        self.editing_id = None
        self._show_dialog("Add Task")

    def _show_edit_dialog(self):
        tid = self._selected_id()
        if tid is None:
            return
        task = task_service.get_task(tid)
        if not task:
            return
        self.editing_id = tid
        self._show_dialog("Edit Task", task)

    def _show_dialog(self, title, task=None):
        c = COLORS
        dlg = tk.Toplevel(self.mw.root)
        dlg.title(title)
        dlg.geometry("460x380")
        dlg.transient(self.mw.root)
        dlg.grab_set()
        dlg.configure(bg=c["content_bg"])

        tk.Label(dlg, text=title, bg=c["content_bg"], fg=c["text"],
                 font=FONTS["header"]).pack(anchor="w", padx=20, pady=(15, 10))

        form = tk.Frame(dlg, bg=c["content_bg"])
        form.pack(fill="both", expand=True, padx=20)

        tk.Label(form, text="Title *", bg=c["content_bg"], fg=c["text"]).grid(
            row=0, column=0, sticky="w", pady=4)
        title_var = tk.StringVar(value=task["title"] if task else "")
        ttk.Entry(form, textvariable=title_var, width=40).grid(
            row=0, column=1, pady=4, padx=(10, 0))

        tk.Label(form, text="Priority", bg=c["content_bg"], fg=c["text"]).grid(
            row=1, column=0, sticky="w", pady=4)
        prio_var = tk.StringVar(value=task["priority"] if task else "Medium")
        ttk.Combobox(form, textvariable=prio_var, width=15, state="readonly",
                     values=["Low", "Medium", "High"]).grid(row=1, column=1, sticky="w", pady=4, padx=(10, 0))

        tk.Label(form, text="Status", bg=c["content_bg"], fg=c["text"]).grid(
            row=2, column=0, sticky="w", pady=4)
        stat_var = tk.StringVar(value=task["status"] if task else "Pending")
        ttk.Combobox(form, textvariable=stat_var, width=15, state="readonly",
                     values=["Pending", "Completed"]).grid(row=2, column=1, sticky="w", pady=4, padx=(10, 0))

        tk.Label(form, text="Due Date", bg=c["content_bg"], fg=c["text"]).grid(
            row=3, column=0, sticky="w", pady=4)
        due_var = tk.StringVar(value=task["due_date"] if task else "")
        ttk.Entry(form, textvariable=due_var, width=20).grid(row=3, column=1, sticky="w", pady=4, padx=(10, 0))
        tk.Label(form, text="(YYYY-MM-DD)", bg=c["content_bg"],
                 fg=c["text_secondary"], font=FONTS["small"]).grid(
            row=3, column=1, sticky="w", padx=(130, 0))

        tk.Label(form, text="Description", bg=c["content_bg"], fg=c["text"]).grid(
            row=4, column=0, sticky="nw", pady=4)
        desc_text = tk.Text(form, width=40, height=4, font=FONTS["body"],
                            bg=c["input_bg"], fg=c["text"], relief="solid",
                            borderwidth=1)
        if task:
            desc_text.insert("1.0", task["description"] or "")
        desc_text.grid(row=4, column=1, pady=4, padx=(10, 0))

        btns = tk.Frame(dlg, bg=c["content_bg"])
        btns.pack(fill="x", padx=20, pady=15)

        def save():
            title_val = title_var.get()
            desc_val = desc_text.get("1.0", "end-1c")
            prio_val = prio_var.get()
            stat_val = stat_var.get()
            due_val = due_var.get().strip()
            if self.editing_id:
                ok, msg = task_service.update_task(
                    self.editing_id, title_val, desc_val, prio_val, stat_val, due_val)
            else:
                ok, msg, _ = task_service.add_task(title_val, desc_val, prio_val, due_val)
            if ok:
                dlg.destroy()
                self._refresh()
                self.mw.set_status(msg)
            else:
                ui_helpers.show_error(dlg, "Validation Error", msg)

        ttk.Button(btns, text="Save", command=save, style="Accent.TButton").pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right")