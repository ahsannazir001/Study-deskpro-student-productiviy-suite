"""Safe mathematical expression parser - recursive descent.

Supports: + - * / % (), decimal numbers, unary minus.
Does NOT use eval(). Handles division by zero and invalid expressions.
"""


class CalcError(Exception):
    pass


class _Parser:
    def __init__(self, text):
        self.text = text.replace(" ", "").replace("\t", "")
        self.pos = 0

    def peek(self):
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None

    def consume(self):
        ch = self.peek()
        self.pos += 1
        return ch

    def parse(self):
        if not self.text:
            raise CalcError("Empty expression")
        result = self._expr()
        if self.pos < len(self.text):
            raise CalcError(f"Unexpected character: {self.peek()}")
        return result

    def _expr(self):
        result = self._term()
        while self.peek() in ("+", "-"):
            op = self.consume()
            right = self._term()
            if op == "+":
                result = result + right
            else:
                result = result - right
        return result

    def _term(self):
        result = self._factor()
        while self.peek() in ("*", "/", "%"):
            op = self.consume()
            right = self._factor()
            if op == "*":
                result = result * right
            elif op == "/":
                if right == 0:
                    raise CalcError("Division by zero")
                result = result / right
            else:
                if right == 0:
                    raise CalcError("Modulo by zero")
                result = result % right
        return result

    def _factor(self):
        ch = self.peek()
        if ch == "(":
            self.consume()
            result = self._expr()
            if self.peek() != ")":
                raise CalcError("Missing closing parenthesis")
            self.consume()
            return result
        if ch == "-":
            self.consume()
            return -self._factor()
        if ch == "+":
            self.consume()
            return self._factor()
        return self._number()

    def _number(self):
        start = self.pos
        seen_dot = False
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch.isdigit():
                self.pos += 1
            elif ch == "." and not seen_dot:
                seen_dot = True
                self.pos += 1
            else:
                break
        if self.pos == start:
            raise CalcError(f"Expected number at position {self.pos}")
        num_str = self.text[start:self.pos]
        try:
            if seen_dot:
                return float(num_str)
            return float(num_str)
        except ValueError:
            raise CalcError("Invalid number")


def safe_eval(expression):
    """Safely evaluate a mathematical expression. Returns float or raises CalcError."""
    if not expression or not expression.strip():
        raise CalcError("Empty expression")
    parser = _Parser(expression)
    result = parser.parse()
    if abs(result) > 1e15:
        raise CalcError("Result too large")
    return result


def format_result(value):
    if isinstance(value, float):
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.10g}"
    return str(value)

import tkinter as tk
from tkinter import ttk
from app.gui.styles import COLORS, FONTS
from app.gui import ui_helpers
from app.utils.logger import get_logger

_log = get_logger("studydesk.calculator")


class CalculatorView:
    def __init__(self, main_window):
        self.mw = main_window
        self.expression = ""
        self.history = []

    def build(self, parent):
        c = COLORS
        top = tk.Frame(parent, bg=c["content_bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Calculator", bg=c["content_bg"], fg=c["text"],
                 font=FONTS["title"]).pack(anchor="w")

        main_frame = tk.Frame(parent, bg=c["content_bg"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        calc_card = tk.Frame(main_frame, bg=c["card_bg"],
                             highlightbackground=c["card_border"], highlightthickness=1)
        calc_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.display_var = tk.StringVar(value="0")
        display = tk.Entry(calc_card, textvariable=self.display_var,
                           font=FONTS["mono_large"], bg=c["input_bg"], fg=c["text"],
                           relief="solid", borderwidth=1, justify="right",
                           state="readonly", readonlybackground=c["input_bg"])
        display.pack(fill="x", padx=15, pady=(15, 5), ipady=6)

        self.expr_label = tk.Label(calc_card, text="", bg=c["card_bg"],
                                   fg=c["text_secondary"], font=FONTS["small"],
                                   anchor="e")
        self.expr_label.pack(fill="x", padx=15)

        btn_frame = tk.Frame(calc_card, bg=c["card_bg"])
        btn_frame.pack(fill="both", expand=True, padx=15, pady=10)

        buttons = [
            ("C", "clear", "Danger.TButton"), ("(", "op", None), (")", "op", None), ("/", "op", "Warning.TButton"),
            ("7", "num", None), ("8", "num", None), ("9", "num", None), ("*", "op", "Warning.TButton"),
            ("4", "num", None), ("5", "num", None), ("6", "num", None), ("-", "op", "Warning.TButton"),
            ("1", "num", None), ("2", "num", None), ("3", "num", None), ("+", "op", "Warning.TButton"),
            ("0", "num", None), (".", "num", None), ("%", "op", None), ("=", "equals", "Success.TButton"),
        ]

        for i, (label, kind, style) in enumerate(buttons):
            row, col = divmod(i, 4)
            btn_style = style or "Outline.TButton"
            btn = ttk.Button(btn_frame, text=label, style=btn_style)
            btn.grid(row=row, column=col, sticky="nsew", padx=3, pady=3, ipady=8)
            if kind == "num":
                btn.configure(command=lambda l=label: self._input(l))
            elif kind == "op":
                btn.configure(command=lambda l=label: self._input(l))
            elif kind == "clear":
                btn.configure(command=self._clear)
            elif kind == "equals":
                btn.configure(command=self._equals)

        for i in range(4):
            btn_frame.columnconfigure(i, weight=1)
        for i in range(5):
            btn_frame.rowconfigure(i, weight=1)

        ttk.Button(calc_card, text="Backspace", command=self._backspace).pack(fill="x", padx=15, pady=(0, 15))

        hist_card = tk.Frame(main_frame, bg=c["card_bg"],
                             highlightbackground=c["card_border"], highlightthickness=1)
        hist_card.pack(side="left", fill="both", expand=True)
        tk.Label(hist_card, text="History", bg=c["card_bg"], fg=c["text"],
                 font=FONTS["subheader"], anchor="w").pack(fill="x", padx=15, pady=(12, 5))
        self.hist_text = tk.Text(hist_card, font=FONTS["mono"], bg=c["card_bg"],
                                 fg=c["text"], relief="flat", state="disabled",
                                 padx=10, pady=5)
        self.hist_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        ttk.Button(hist_card, text="Clear History", command=self._clear_history).pack(pady=(0, 12))

    def _input(self, char):
        self.expression += char
        self.display_var.set(self.expression if self.expression else "0")
        self.expr_label.configure(text=self.expression)

    def _clear(self):
        self.expression = ""
        self.display_var.set("0")
        self.expr_label.configure(text="")

    def _backspace(self):
        self.expression = self.expression[:-1]
        self.display_var.set(self.expression if self.expression else "0")
        self.expr_label.configure(text=self.expression)

    def _equals(self):
        if not self.expression:
            return
        try:
            result = safe_eval(self.expression)
            formatted = format_result(result)
            self.history.append(f"{self.expression} = {formatted}")
            self.display_var.set(formatted)
            self.expr_label.configure(text=f"{self.expression} =")
            self.expression = ""
            self._update_history()
            self.mw.set_status(f"Result: {formatted}")
        except CalcError as exc:
            self.display_var.set("Error")
            self.expr_label.configure(text=str(exc))
            self.expression = ""
            _log.warning("Calc error: %s", exc)
        except Exception as exc:
            self.display_var.set("Error")
            self.expr_label.configure(text="Invalid expression")
            self.expression = ""
            _log.error("Calc unexpected error: %s", exc)

    def _update_history(self):
        self.hist_text.configure(state="normal")
        self.hist_text.delete("1.0", "end")
        for h in reversed(self.history[-20:]):
            self.hist_text.insert("end", h + "\n")
        self.hist_text.configure(state="disabled")

    def _clear_history(self):
        self.history = []
        self._update_history()