"""File organizer view - safe folder organization with preview and confirmation."""

import os
import tkinter as tk
from tkinter import ttk, filedialog

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.services import file_service
from app.utils.security import validate_folder_path, is_protected_directory
from app.utils.logger import get_logger

_log = get_logger("studydesk.file_organizer_gui")


class FileOrganizerView:
    def __init__(self, main_window):
        self.mw = main_window
        self.selected_dir = None
        self.plan = None

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="File Organizer", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        info = tk.Frame(parent, bg=c["card_bg"],
                        highlightbackground=c["card_border"], highlightthickness=1)
        info.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(info, text="Select a folder to organize files by type. Files will be moved "
                 "into category subfolders (Images, Documents, Videos, Audio, etc.).\n"
                 "Nothing is deleted. Conflicts are resolved by renaming. System directories "
                 "are protected.", bg=c["card_bg"], fg=c["text_secondary"],
                 font=FONTS["small"], justify="left", anchor="w").pack(fill="x", padx=15, pady=12)

        select_frame = tk.Frame(parent, bg=c["content_bg"])
        select_frame.pack(fill="x", padx=20, pady=(0, 10))
        ttk.Button(select_frame, text="Browse Folder", command=self._browse,
                   style="Accent.TButton").pack(side="left", padx=(0, 10))
        self.dir_label = tk.Label(select_frame, text="No folder selected", bg=c["content_bg"],
                                  fg=c["text_secondary"], font=FONTS["body"])
        self.dir_label.pack(side="left")

        self.preview_frame = tk.Frame(parent, bg=c["content_bg"])
        self.preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def _browse(self):
        directory = filedialog.askdirectory(title="Select folder to organize",
                                            initialdir=os.path.expanduser("~"))
        if not directory:
            return
        ok, msg = validate_folder_path(directory)
        if not ok:
            ui_helpers.show_error(self.mw.root, "Invalid Folder", msg)
            return
        self.selected_dir = msg
        self.dir_label.configure(text=self.selected_dir, fg=COLORS["text"])
        self._analyze()

    def _analyze(self):
        c = COLORS
        for child in self.preview_frame.winfo_children():
            child.destroy()
        self.plan = None

        results, error = file_service.analyze_directory(self.selected_dir)
        if error:
            ui_helpers.show_error(self.mw.root, "Cannot Read Folder",
                                  f"Could not read the folder:\n{error}")
            return
        if not results:
            tk.Label(self.preview_frame, text="No files found to organize.",
                     bg=c["content_bg"], fg=c["text_secondary"]).pack(pady=30)
            return

        self.plan, conflicts = file_service.plan_operations(self.selected_dir, results)

        tk.Label(self.preview_frame, text=f"Preview: {len(self.plan)} file(s) to organize",
                 bg=c["content_bg"], fg=c["text"], font=FONTS["subheader"]).pack(anchor="w", pady=(0, 8))

        if conflicts:
            warn = tk.Frame(self.preview_frame, bg=c["warning"])
            warn.pack(fill="x", pady=(0, 8))
            tk.Label(warn, text=f"  {len(conflicts)} conflict(s) detected - files will be renamed with suffix.",
                     bg=c["warning"], fg="#FFFFFF", font=FONTS["small_bold"], anchor="w").pack(fill="x", pady=3)

        tree_frame = tk.Frame(self.preview_frame, bg=c["content_bg"])
        tree_frame.pack(fill="both", expand=True)
        cols = ("name", "category", "destination", "conflict")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
        headers = {"name": ("File", 200), "category": ("Category", 100),
                   "destination": ("Destination", 250), "conflict": ("Conflict", 80)}
        for col, (text, width) in headers.items():
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor="center" if col in ("category", "conflict") else "w")
        ui_helpers.style_treeview_stripes(tree)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for i, item in enumerate(self.plan):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            rel_dest = os.path.relpath(item["dest"], self.selected_dir)
            tree.insert("", "end", values=(
                item["name"], item["category"], rel_dest,
                "Yes" if item["conflict"] else "No"
            ), tags=tag)

        btn_frame = tk.Frame(self.preview_frame, bg=c["content_bg"])
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Organize Now", command=self._execute,
                   style="Success.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="Cancel", command=self._clear_preview).pack(side="left")

    def _clear_preview(self):
        for child in self.preview_frame.winfo_children():
            child.destroy()
        self.plan = None

    def _execute(self):
        if not self.plan:
            return
        count = len(self.plan)
        if not ui_helpers.confirm(self.mw.root, "Confirm Organization",
                                  f"Move {count} file(s) into category subfolders?\n"
                                  f"Folder: {self.selected_dir}\n\n"
                                  f"This cannot be undone. Continue?"):
            return
        moved, skipped, errors = file_service.execute_plan(self.plan)
        summary = (f"Organization complete!\n\n"
                   f"Moved: {len(moved)}\n"
                   f"Skipped: {len(skipped)}\n"
                   f"Errors: {len(errors)}")
        if errors:
            summary += "\n\nErrors:\n" + "\n".join(f"  {n}: {e}" for n, e in errors[:5])
            if len(errors) > 5:
                summary += f"\n  ... and {len(errors) - 5} more"
        ui_helpers.show_info(self.mw.root, "Complete", summary)
        db_log = f"moved={len(moved)} skipped={len(skipped)} errors={len(errors)}"
        _log.info("File organizer executed: %s", db_log)
        self._clear_preview()
        self.dir_label.configure(text="No folder selected", fg=COLORS["text_secondary"])
        self.selected_dir = None
        self.mw.set_status(f"Organized {len(moved)} file(s)")