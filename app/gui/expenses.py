"""Expenses view - CRUD with charts and filtering."""

import tkinter as tk
from tkinter import ttk

from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.services import expense_service, settings_service
from app.utils.helpers import format_currency, month_range


class ExpensesView:
    def __init__(self, main_window):
        self.mw = main_window
        self.search_var = tk.StringVar()
        self.cat_var = tk.StringVar(value="All")
        self.editing_id = None

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Expense Tracker", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        currency = settings_service.get_setting("currency", "Rs.")
        monthly = expense_service.get_monthly_total()
        total = expense_service.get_total()
        summary = tk.Frame(parent, bg=c["content_bg"])
        summary.pack(fill="x", padx=20, pady=(0, 10))
        self.monthly_label = tk.Label(summary, text=f"This Month: {format_currency(monthly, currency)}",
                                      bg=c["content_bg"], fg=c["danger"], font=FONTS["body_bold"])
        self.monthly_label.pack(side="left", padx=(0, 20))
        self.total_label = tk.Label(summary, text=f"Total: {format_currency(total, currency)}",
                                    bg=c["content_bg"], fg=c["accent"], font=FONTS["body_bold"])
        self.total_label.pack(side="left")

        toolbar = tk.Frame(parent, bg=c["content_bg"])
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(toolbar, text="Search:", bg=c["content_bg"], fg=c["text"]).pack(side="left", padx=(0, 5))
        se = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        se.pack(side="left", padx=(0, 10))
        se.bind("<KeyRelease>", lambda e: self._refresh())
        ttk.Label(toolbar, text="Category:").pack(side="left", padx=(0, 5))
        cat = ttk.Combobox(toolbar, textvariable=self.cat_var, width=12, state="readonly",
                           values=["All"] + list(expense_service.CATEGORIES))
        cat.pack(side="left", padx=(0, 10))
        cat.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        ttk.Button(toolbar, text="+ Add Expense", command=self._show_add_dialog,
                   style="Accent.TButton").pack(side="right")

        paned = ttk.PanedWindow(parent, orient="vertical")
        paned.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        table_frame = tk.Frame(paned, bg=c["content_bg"])
        paned.add(table_frame, weight=2)
        cols = ("id", "date", "amount", "category", "description")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        headers = {"id": ("ID", 45), "date": ("Date", 100), "amount": ("Amount", 100),
                   "category": ("Category", 100), "description": ("Description", 250)}
        for col, (text, width) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col not in ("description",) else "w")
        ui_helpers.style_treeview_stripes(self.tree)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        chart_frame = tk.Frame(paned, bg=c["card_bg"],
                               highlightbackground=c["card_border"], highlightthickness=1)
        paned.add(chart_frame, weight=1)
        tk.Label(chart_frame, text="Expenses by Category (This Month)", bg=c["card_bg"],
                 fg=c["text"], font=FONTS["subheader"], anchor="w").pack(fill="x", padx=15, pady=(10, 5))
        self.chart_container = tk.Frame(chart_frame, bg=c["card_bg"])
        self.chart_container.pack(fill="both", expand=True, padx=10, pady=5)

        btn_bar = tk.Frame(parent, bg=c["content_bg"])
        btn_bar.pack(fill="x", padx=20, pady=(0, 15))
        ttk.Button(btn_bar, text="Edit", command=self._show_edit_dialog).pack(side="left", padx=(0, 8))
        ttk.Button(btn_bar, text="Delete", style="Danger.TButton",
                   command=self._delete_expense).pack(side="left")

        self._refresh()

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        search = self.search_var.get().strip()
        cat = self.cat_var.get()
        cat_f = "" if cat == "All" else cat
        expenses = expense_service.get_all_expenses(search, cat_f)
        currency = settings_service.get_setting("currency", "Rs.")
        for i, e in enumerate(expenses):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(
                e["id"], e["expense_date"], format_currency(e["amount"], currency),
                e["category"], e["description"] or ""
            ), tags=tag)
        monthly = expense_service.get_monthly_total()
        total = expense_service.get_total()
        self.monthly_label.configure(text=f"This Month: {format_currency(monthly, currency)}")
        self.total_label.configure(text=f"Total: {format_currency(total, currency)}")
        self._build_chart()
        self.mw.set_status(f"{len(expenses)} expense(s) shown")

    def _build_chart(self):
        c = COLORS
        for child in self.chart_container.winfo_children():
            child.destroy()
        totals = expense_service.get_category_totals()
        if not totals:
            tk.Label(self.chart_container, text="No expenses to chart", bg=c["card_bg"],
                     fg=c["text_secondary"]).pack(pady=20)
            return
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from PIL import Image, ImageTk

            cats = list(totals.keys())
            vals = [totals[k] for k in cats]
            fig, ax = plt.subplots(figsize=(5, 2.2), dpi=80)
            ax.bar(cats, vals, color=c["accent"])
            ax.tick_params(axis="x", labelsize=8, rotation=20)
            ax.tick_params(axis="y", labelsize=8)
            fig.tight_layout()
            fig.canvas.draw()
            img = Image.frombytes("RGB", fig.canvas.get_width_height(),
                                  fig.canvas.tostring_rgb())
            self._chart_img = ImageTk.PhotoImage(img)
            tk.Label(self.chart_container, image=self._chart_img, bg=c["card_bg"]).pack()
            plt.close(fig)
        except Exception:
            for cat, val in totals.items():
                row = tk.Frame(self.chart_container, bg=c["card_bg"])
                row.pack(fill="x", padx=15, pady=2)
                tk.Label(row, text=cat, bg=c["card_bg"], fg=c["text"], width=12,
                         anchor="w").pack(side="left")
                tk.Label(row, text=f"Rs. {val:,.0f}", bg=c["card_bg"], fg=c["accent"],
                         font=FONTS["small_bold"]).pack(side="left")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            ui_helpers.show_warning(self.mw.root, "No Selection", "Please select an expense first.")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _delete_expense(self):
        eid = self._selected_id()
        if eid is None:
            return
        if not ui_helpers.confirm(self.mw.root, "Delete Expense",
                                  "Are you sure you want to delete this expense?"):
            return
        ok, msg = expense_service.delete_expense(eid)
        if ok:
            self._refresh()
            self.mw.set_status(msg)
        else:
            ui_helpers.show_error(self.mw.root, "Error", msg)

    def _show_add_dialog(self):
        self.editing_id = None
        self._show_dialog("Add Expense")

    def _show_edit_dialog(self):
        eid = self._selected_id()
        if eid is None:
            return
        exp = expense_service.get_expense(eid)
        if not exp:
            return
        self.editing_id = eid
        self._show_dialog("Edit Expense", exp)

    def _show_dialog(self, title, exp=None):
        c = COLORS
        dlg = tk.Toplevel(self.mw.root)
        dlg.title(title)
        dlg.geometry("420x300")
        dlg.transient(self.mw.root)
        dlg.grab_set()
        dlg.configure(bg=c["content_bg"])
        tk.Label(dlg, text=title, bg=c["content_bg"], fg=c["text"],
                 font=FONTS["header"]).pack(anchor="w", padx=20, pady=(15, 10))
        form = tk.Frame(dlg, bg=c["content_bg"])
        form.pack(fill="both", expand=True, padx=20)

        tk.Label(form, text="Amount *", bg=c["content_bg"], fg=c["text"]).grid(row=0, column=0, sticky="w", pady=4)
        amt_var = tk.StringVar(value=str(exp["amount"]) if exp else "")
        ttk.Entry(form, textvariable=amt_var, width=20).grid(row=0, column=1, pady=4, padx=(10, 0))

        tk.Label(form, text="Category", bg=c["content_bg"], fg=c["text"]).grid(row=1, column=0, sticky="w", pady=4)
        cat_var = tk.StringVar(value=exp["category"] if exp else "Food")
        ttk.Combobox(form, textvariable=cat_var, width=15, state="readonly",
                     values=list(expense_service.CATEGORIES)).grid(row=1, column=1, sticky="w", pady=4, padx=(10, 0))

        tk.Label(form, text="Date", bg=c["content_bg"], fg=c["text"]).grid(row=2, column=0, sticky="w", pady=4)
        from app.utils.helpers import today_iso
        date_var = tk.StringVar(value=exp["expense_date"] if exp else today_iso())
        ttk.Entry(form, textvariable=date_var, width=15).grid(row=2, column=1, sticky="w", pady=4, padx=(10, 0))

        tk.Label(form, text="Description", bg=c["content_bg"], fg=c["text"]).grid(row=3, column=0, sticky="w", pady=4)
        desc_var = tk.StringVar(value=exp["description"] if exp else "")
        ttk.Entry(form, textvariable=desc_var, width=30).grid(row=3, column=1, pady=4, padx=(10, 0))

        btns = tk.Frame(dlg, bg=c["content_bg"])
        btns.pack(fill="x", padx=20, pady=15)
        def save():
            if self.editing_id:
                ok, msg = expense_service.update_expense(self.editing_id, amt_var.get(),
                                                          cat_var.get(), desc_var.get(), date_var.get())
            else:
                ok, msg, _ = expense_service.add_expense(amt_var.get(), cat_var.get(),
                                                         desc_var.get(), date_var.get())
            if ok:
                dlg.destroy()
                self._refresh()
                self.mw.set_status(msg)
            else:
                ui_helpers.show_error(dlg, "Validation Error", msg)
        ttk.Button(btns, text="Save", command=save, style="Accent.TButton").pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right")