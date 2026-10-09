"""StudyDesk Pro - Main Entry Point

Student Productivity & Study Management Suite

Usage:
    python main.py

This launches the graphical Tkinter interface directly.
No CLI interaction, no web server, no browser.
"""

import sys
import os
import traceback


def _setup_path():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    if base not in sys.path:
        sys.path.insert(0, base)


def main():
    _setup_path()

    from app.utils.logger import init_logging, get_logger
    from app.utils.helpers import get_log_dir, get_app_data_dir

    log_dir = get_log_dir()
    data_dir = get_app_data_dir()
    log = init_logging(log_dir)

    log.info("=" * 50)
    log.info("StudyDesk Pro starting up...")
    log.info("Data directory: %s", data_dir)
    log.info("Log directory: %s", log_dir)

    from app.database import db
    if not db.initialize():
        _show_fatal_error("Database initialization failed. Check logs in:\n" + log_dir)
        return

    from app.services import settings_service
    settings_service.reset_cache()

    import tkinter as tk
    root = tk.Tk()

    from app.gui.main_window import MainWindow
    app = MainWindow(root)

    log.info("GUI launched successfully")

    def on_closing():
        log.info("Application closing...")
        db.close_connection()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    log.info("Application closed.")


def _write_crash_log(error_text):
    try:
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        crash_dir = os.path.join(base, "data", "logs")
        os.makedirs(crash_dir, exist_ok=True)
        crash_path = os.path.join(crash_dir, "crash.log")
        with open(crash_path, "w", encoding="utf-8") as f:
            f.write("StudyDesk Pro - Crash Report\n")
            f.write("=" * 50 + "\n")
            f.write(error_text)
    except Exception:
        pass


def _show_fatal_error(message):
    _write_crash_log(message)
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("StudyDesk Pro - Fatal Error", message)
        root.destroy()
    except Exception:
        print("FATAL ERROR:", message, file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        error_text = traceback.format_exc()
        _show_fatal_error("An unexpected error occurred:\n\n" + error_text)