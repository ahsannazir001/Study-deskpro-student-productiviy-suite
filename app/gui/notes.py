"""Notes view - CRUD with categories and search."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.services import note_service


class NotesView:
    def __init__(self, main_window):
        self.mw = main_window
        self.search_var = tk.StringVar()
        self.cat_var = tk.StringVar(value="All")
        self.editing_id = None

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Notes Manager", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        toolbar = tk.Frame(parent, bg=c["content_bg"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(toolbar, text="Search:", bg=c["content_bg"], fg=c["text"]).pack(side="left", padx=(0, 5))
        se = ttk.Entry(toolbar, textvariable=self.search_var, width=25)
        se.pack(side="left", padx=(0, 10))
        se.bind("<KeyRelease>", lambda e: self._refresh())

        ttk.Label(toolbar, text="Category:").pack(side="left", padx=(0, 5))
        cat = ttk.Combobox(toolbar, textvariable=self.cat_var, width=12, state="readonly",
                           values=["All"] + list(note_service.CATEGORIES))
        cat.pack(side="left", padx=(0, 10))
        cat.bind("<<ComboboxSelected>>", lambda e: self._refresh())

        ttk.Button(toolbar, text="+ New Note", command=self._show_add_dialog,
                   style="Accent.TButton").pack(side="right")

        paned = ttk.PanedWindow(parent, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        list_frame = tk.Frame(paned, bg=c["content_bg"])
        paned.add(list_frame, weight=1)

        cols = ("id", "title", "category", "updated")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=15)
        headers = {"id": ("ID", 45), "title": ("Title", 200), "category": ("Category", 90),
                   "updated": ("Updated", 100)}
        for col, (text, width) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col != "title" else "w")
        ui_helpers.style_treeview_stripes(self.tree)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._on_select())

        detail_frame = tk.Frame(paned, bg=c["card_bg"],
                                highlightbackground=c["card_border"], highlightthickness=1)
        paned.add(detail_frame, weight=2)

        self.detail_title = tk.Label(detail_frame, text="Select a note to view",
                                     bg=c["card_bg"], fg=c["text"], font=FONTS["subheader"],
                                     anchor="w", padx=15, pady=10)
        self.detail_title.pack(fill="x")

        self.detail_meta = tk.Label(detail_frame, text="", bg=c["card_bg"],
                                    fg=c["text_secondary"], font=FONTS["small"],
                                    anchor="w", padx=15)
        self.detail_meta.pack(fill="x")

        self.detail_text = tk.Text(detail_frame, wrap="word", font=FONTS["body"],
                                   bg=c["card_bg"], fg=c["text"], relief="flat",
                                   padx=15, pady=10, state="disabled")
        self.detail_text.pack(fill="both", expand=True, padx=10, pady=10)

        btn_bar = tk.Frame(parent, bg=c["content_bg"])
        btn_bar.pack(fill="x", padx=20, pady=(0, 15))
        ttk.Button(btn_bar, text="Edit", command=self._show_edit_dialog).pack(side="left", padx=(0, 8))
        ttk.Button(btn_bar, text="Delete", style="Danger.TButton",
                   command=self._delete_note).pack(side="left")
        self._refresh()

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        search = self.search_var.get().strip()
        cat = self.cat_var.get()
        cat_f = "" if cat == "All" else cat
        notes = note_service.get_all_notes(search, cat_f)
        for i, n in enumerate(notes):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(
                n["id"], n["title"], n["category"], n["updated_at"][:10]
            ), tags=tag)
        self.mw.set_status(f"{len(notes)} note(s) shown")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _on_select(self):
        tid = self._selected_id()
        if tid is None:
            return
        note = note_service.get_note(tid)
        if not note:
            return
        self.detail_title.configure(text=note["title"])
        self.detail_meta.configure(text=f"Category: {note['category']}  |  "
                                    f"Created: {note['created_at'][:10]}  |  "
                                    f"Updated: {note['updated_at'][:10]}")
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", note["content"] or "")
        self.detail_text.configure(state="disabled")

    def _delete_note(self):
        tid = self._selected_id()
        if tid is None:
            ui_helpers.show_warning(self.mw.root, "No Selection", "Please select a note first.")
            return
        if not ui_helpers.confirm(self.mw.root, "Delete Note",
                                  "Are you sure you want to delete this note?"):
            return
        ok, msg = note_service.delete_note(tid)
        if ok:
            self.detail_title.configure(text="Select a note to view")
            self.detail_meta.configure(text="")
            self.detail_text.configure(state="normal")
            self.detail_text.delete("1.0", "end")
            self.detail_text.configure(state="disabled")
            self._refresh()
            self.mw.set_status(msg)
        else:
            ui_helpers.show_error(self.mw.root, "Error", msg)

    def _show_add_dialog(self):
        self.editing_id = None
        self._show_dialog("New Note")

    def _show_edit_dialog(self):
        tid = self._selected_id()
        if tid is None:
            ui_helpers.show_warning(self.mw.root, "No Selection", "Please select a note first.")
            return
        note = note_service.get_note(tid)
        if not note:
            return
        self.editing_id = tid
        self._show_dialog("Edit Note", note)

    def _show_dialog(self, title, note=None):
        c = COLORS
        dlg = tk.Toplevel(self.mw.root)
        dlg.title(title)
        dlg.geometry("520x460")
        dlg.transient(self.mw.root)
        dlg.grab_set()
        dlg.configure(bg=c["content_bg"])

        tk.Label(dlg, text=title, bg=c["content_bg"], fg=c["text"],
                 font=FONTS["header"]).pack(anchor="w", padx=20, pady=(15, 10))

        form = tk.Frame(dlg, bg=c["content_bg"])
        form.pack(fill="both", expand=True, padx=20)

        tk.Label(form, text="Title *", bg=c["content_bg"], fg=c["text"]).grid(row=0, column=0, sticky="w", pady=4)
        title_var = tk.StringVar(value=note["title"] if note else "")
        ttk.Entry(form, textvariable=title_var, width=45).grid(row=0, column=1, pady=4, padx=(10, 0))

        tk.Label(form, text="Category", bg=c["content_bg"], fg=c["text"]).grid(row=1, column=0, sticky="w", pady=4)
        cat_var = tk.StringVar(value=note["category"] if note else "Other")
        ttk.Combobox(form, textvariable=cat_var, width=15, state="readonly",
                     values=list(note_service.CATEGORIES)).grid(row=1, column=1, sticky="w", pady=4, padx=(10, 0))

        tk.Label(form, text="Content", bg=c["content_bg"], fg=c["text"]).grid(row=2, column=0, sticky="nw", pady=4)
        content_text = tk.Text(form, width=45, height=12, font=FONTS["body"],
                               bg=c["input_bg"], fg=c["text"], relief="solid", borderwidth=1)
        if note:
            content_text.insert("1.0", note["content"] or "")
        content_text.grid(row=2, column=1, pady=4, padx=(10, 0))

        btns = tk.Frame(dlg, bg=c["content_bg"])
        btns.pack(fill="x", padx=20, pady=15)

        def save():
            title_val = title_var.get()
            content_val = content_text.get("1.0", "end-1c")
            cat_val = cat_var.get()
            if self.editing_id:
                ok, msg = note_service.update_note(self.editing_id, title_val, content_val, cat_val)
            else:
                ok, msg, _ = note_service.add_note(title_val, content_val, cat_val)
            if ok:
                dlg.destroy()
                self._refresh()
                self.mw.set_status(msg)
            else:
                ui_helpers.show_error(dlg, "Validation Error", msg)

        ttk.Button(btns, text="Save", command=save, style="Accent.TButton").pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right")