"""StudyDesk Pro - Standalone Test Runner

Run all tests without pytest:
    python run_tests.py

Uses only the Python standard library (unittest).
"""

import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setUpModule():
    global _tmp_dir
    _tmp_dir = tempfile.mkdtemp(prefix="studydesk_test_")
    data_dir = os.path.join(_tmp_dir, "data")
    log_dir = os.path.join(data_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    import app.utils.helpers as helpers
    helpers.get_app_data_dir = lambda: data_dir
    helpers.get_log_dir = lambda: log_dir

    from app.utils.logger import init_logging
    init_logging(log_dir)

    from app.database import db
    db._db_path = os.path.join(data_dir, "studydesk.db")
    db.close_connection()
    db.initialize()

    from app.services import settings_service
    settings_service.reset_cache()


def tearDownModule():
    from app.database import db
    db.close_connection()
    if _tmp_dir and os.path.exists(_tmp_dir):
        shutil.rmtree(_tmp_dir, ignore_errors=True)


class TestTaskService(unittest.TestCase):
    def test_add_task(self):
        from app.services import task_service
        ok, msg, tid = task_service.add_task("Buy groceries", "Milk and eggs", "High", "2026-12-31")
        self.assertTrue(ok)
        self.assertIsNotNone(tid)

    def test_empty_title_fails(self):
        from app.services import task_service
        ok, msg, tid = task_service.add_task("", "", "Medium")
        self.assertFalse(ok)

    def test_invalid_date_fails(self):
        from app.services import task_service
        ok, msg, tid = task_service.add_task("Test", "", "Medium", "not-a-date")
        self.assertFalse(ok)

    def test_invalid_priority_fails(self):
        from app.services import task_service
        ok, msg, tid = task_service.add_task("Test", "", "Urgent")
        self.assertFalse(ok)

    def test_update_task(self):
        from app.services import task_service
        ok, _, tid = task_service.add_task("Original", "", "Low")
        ok2, _ = task_service.update_task(tid, "Updated", "desc", "High", "Pending", "2026-12-25")
        self.assertTrue(ok2)
        task = task_service.get_task(tid)
        self.assertEqual(task["title"], "Updated")

    def test_delete_task(self):
        from app.services import task_service
        ok, _, tid = task_service.add_task("ToDelete", "", "Medium")
        ok2, _ = task_service.delete_task(tid)
        self.assertTrue(ok2)
        self.assertIsNone(task_service.get_task(tid))

    def test_set_status(self):
        from app.services import task_service
        ok, _, tid = task_service.add_task("StatusTest", "", "Medium")
        ok2, _ = task_service.set_status(tid, "Completed")
        self.assertTrue(ok2)
        task = task_service.get_task(tid)
        self.assertEqual(task["status"], "Completed")

    def test_search(self):
        from app.services import task_service
        task_service.add_task("UniqueSearchTerm123", "", "Medium")
        results = task_service.get_all_tasks("UniqueSearchTerm123")
        self.assertEqual(len(results), 1)

    def test_filter_priority(self):
        from app.services import task_service
        task_service.add_task("LowTask", "", "Low")
        task_service.add_task("HighTask", "", "High")
        results = task_service.get_all_tasks(priority_filter="High")
        self.assertTrue(all(t["priority"] == "High" for t in results))

    def test_stats(self):
        from app.services import task_service
        task_service.add_task("S1", "", "Medium")
        ok, _, tid = task_service.add_task("S2", "", "Medium")
        task_service.set_status(tid, "Completed")
        stats = task_service.get_stats()
        self.assertGreaterEqual(stats["total"], 2)
        self.assertGreaterEqual(stats["completed"], 1)


class TestNoteService(unittest.TestCase):
    def test_add_note(self):
        from app.services import note_service
        ok, msg, nid = note_service.add_note("My Note", "Content", "Study")
        self.assertTrue(ok)

    def test_empty_title_fails(self):
        from app.services import note_service
        ok, _, _ = note_service.add_note("", "content", "Other")
        self.assertFalse(ok)

    def test_invalid_category_fails(self):
        from app.services import note_service
        ok, _, _ = note_service.add_note("Test", "content", "InvalidCat")
        self.assertFalse(ok)

    def test_update_note(self):
        from app.services import note_service
        ok, _, nid = note_service.add_note("Original", "old", "Personal")
        ok2, _ = note_service.update_note(nid, "Updated", "new", "Project")
        self.assertTrue(ok2)
        note = note_service.get_note(nid)
        self.assertEqual(note["title"], "Updated")

    def test_delete_note(self):
        from app.services import note_service
        ok, _, nid = note_service.add_note("ToDelete", "", "Other")
        ok2, _ = note_service.delete_note(nid)
        self.assertTrue(ok2)

    def test_search(self):
        from app.services import note_service
        note_service.add_note("UniqueNoteSearch456", "find me", "Study")
        results = note_service.get_all_notes("UniqueNoteSearch456")
        self.assertEqual(len(results), 1)


class TestExpenseService(unittest.TestCase):
    def test_add_expense(self):
        from app.services import expense_service
        ok, _, eid = expense_service.add_expense("500", "Food", "Lunch", "2026-10-08")
        self.assertTrue(ok)

    def test_negative_fails(self):
        from app.services import expense_service
        ok, _, _ = expense_service.add_expense("-100", "Food", "", "")
        self.assertFalse(ok)

    def test_invalid_amount_fails(self):
        from app.services import expense_service
        ok, _, _ = expense_service.add_expense("abc", "Food", "", "")
        self.assertFalse(ok)

    def test_update_expense(self):
        from app.services import expense_service
        ok, _, eid = expense_service.add_expense("100", "Food", "old", "2026-10-01")
        ok2, _ = expense_service.update_expense(eid, "250", "Transport", "new", "2026-10-05")
        self.assertTrue(ok2)
        exp = expense_service.get_expense(eid)
        self.assertEqual(exp["amount"], 250.0)

    def test_delete_expense(self):
        from app.services import expense_service
        ok, _, eid = expense_service.add_expense("100", "Food", "", "")
        ok2, _ = expense_service.delete_expense(eid)
        self.assertTrue(ok2)

    def test_monthly_total(self):
        from app.services import expense_service
        expense_service.add_expense("1000", "Food", "", "")
        expense_service.add_expense("500", "Transport", "", "")
        total = expense_service.get_monthly_total()
        self.assertGreaterEqual(total, 1500)

    def test_category_totals(self):
        from app.services import expense_service
        expense_service.add_expense("300", "Food", "", "")
        totals = expense_service.get_category_totals()
        self.assertIn("Food", totals)


class TestStudyService(unittest.TestCase):
    def test_add_subject(self):
        from app.services import study_service
        ok, _, sid = study_service.add_subject("Python", "2", "14")
        self.assertTrue(ok)

    def test_empty_name_fails(self):
        from app.services import study_service
        ok, _, _ = study_service.add_subject("", "2", "14")
        self.assertFalse(ok)

    def test_add_study_time(self):
        from app.services import study_service
        ok, _, sid = study_service.add_subject("StudyTime", "2", "14")
        ok2, _ = study_service.add_study_time(sid, "30")
        self.assertTrue(ok2)
        subj = study_service.get_subject(sid)
        self.assertEqual(subj["completed_minutes"], 30)

    def test_progress_percent(self):
        from app.services import study_service
        subj = {"daily_target": 2, "completed_minutes": 60}
        self.assertEqual(study_service.get_progress_percent(subj), 50)

    def test_delete_subject(self):
        from app.services import study_service
        ok, _, sid = study_service.add_subject("ToDelete", "1", "7")
        ok2, _ = study_service.delete_subject(sid)
        self.assertTrue(ok2)


class TestCalculator(unittest.TestCase):
    def test_addition(self):
        from app.gui.calculator import safe_eval
        self.assertEqual(safe_eval("2+3"), 5)

    def test_subtraction(self):
        from app.gui.calculator import safe_eval
        self.assertEqual(safe_eval("10-4"), 6)

    def test_multiplication(self):
        from app.gui.calculator import safe_eval
        self.assertEqual(safe_eval("6*7"), 42)

    def test_division(self):
        from app.gui.calculator import safe_eval
        self.assertEqual(safe_eval("10/2"), 5)

    def test_division_by_zero(self):
        from app.gui.calculator import safe_eval, CalcError
        with self.assertRaises(CalcError):
            safe_eval("1/0")

    def test_parentheses(self):
        from app.gui.calculator import safe_eval
        self.assertEqual(safe_eval("(2+3)*4"), 20)

    def test_nested_parentheses(self):
        from app.gui.calculator import safe_eval
        self.assertEqual(safe_eval("((2+3)*2)"), 10)

    def test_decimal(self):
        from app.gui.calculator import safe_eval
        self.assertEqual(safe_eval("3.5+2.5"), 6.0)

    def test_complex_expression(self):
        from app.gui.calculator import safe_eval
        self.assertEqual(safe_eval("2+3*4"), 14)

    def test_empty_expression(self):
        from app.gui.calculator import safe_eval, CalcError
        with self.assertRaises(CalcError):
            safe_eval("")

    def test_invalid_expression(self):
        from app.gui.calculator import safe_eval, CalcError
        with self.assertRaises(CalcError):
            safe_eval("2++")

    def test_missing_paren(self):
        from app.gui.calculator import safe_eval, CalcError
        with self.assertRaises(CalcError):
            safe_eval("(2+3")


class TestSettings(unittest.TestCase):
    def test_set_and_get(self):
        from app.services import settings_service
        settings_service.set_setting("test_key", "test_value")
        self.assertEqual(settings_service.get_setting("test_key"), "test_value")

    def test_get_int(self):
        from app.services import settings_service
        settings_service.set_setting("int_key", "42")
        self.assertEqual(settings_service.get_int("int_key"), 42)

    def test_persistence(self):
        from app.services import settings_service
        settings_service.set_setting("persist_key", "persist_value")
        settings_service.reset_cache()
        self.assertEqual(settings_service.get_setting("persist_key"), "persist_value")


class TestDatabase(unittest.TestCase):
    def test_insert_and_read(self):
        from app.database import db
        cur = db.execute("INSERT INTO tasks (title, priority, status, created_at, updated_at) VALUES (?, 'Medium', 'Pending', ?, ?)",
                         ("DBTest", "2026-01-01", "2026-01-01"))
        tid = cur.lastrowid
        row = db.query_one("SELECT * FROM tasks WHERE id=?", (tid,))
        self.assertEqual(row["title"], "DBTest")

    def test_update(self):
        from app.database import db
        cur = db.execute("INSERT INTO tasks (title, priority, status, created_at, updated_at) VALUES (?, 'Medium', 'Pending', ?, ?)",
                         ("UpdTest", "2026-01-01", "2026-01-01"))
        tid = cur.lastrowid
        db.execute("UPDATE tasks SET status='Completed' WHERE id=?", (tid,))
        row = db.query_one("SELECT * FROM tasks WHERE id=?", (tid,))
        self.assertEqual(row["status"], "Completed")

    def test_delete(self):
        from app.database import db
        cur = db.execute("INSERT INTO tasks (title, priority, status, created_at, updated_at) VALUES (?, 'Medium', 'Pending', ?, ?)",
                         ("DelTest", "2026-01-01", "2026-01-01"))
        tid = cur.lastrowid
        db.execute("DELETE FROM tasks WHERE id=?", (tid,))
        self.assertIsNone(db.query_one("SELECT * FROM tasks WHERE id=?", (tid,)))


class TestFileOrganizer(unittest.TestCase):
    def test_category_for_extension(self):
        from app.services.file_service import category_for_extension
        self.assertEqual(category_for_extension(".png"), "Images")
        self.assertEqual(category_for_extension(".pdf"), "Documents")
        self.assertEqual(category_for_extension(".mp4"), "Videos")
        self.assertEqual(category_for_extension(".mp3"), "Audio")
        self.assertEqual(category_for_extension(".xyz"), "Others")

    def test_analyze_directory(self):
        from app.services.file_service import analyze_directory
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, "test.png"), "w") as f: f.write("img")
            with open(os.path.join(d, "doc.pdf"), "w") as f: f.write("doc")
            results, error = analyze_directory(d)
            self.assertIsNone(error)
            self.assertEqual(len(results), 2)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_execute_moves_files(self):
        from app.services.file_service import analyze_directory, plan_operations, execute_plan
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, "test.png"), "w") as f: f.write("img")
            results, _ = analyze_directory(d)
            plan, _ = plan_operations(d, results)
            moved, skipped, errors = execute_plan(plan)
            self.assertEqual(len(moved), 1)
            self.assertTrue(os.path.exists(os.path.join(d, "Images", "test.png")))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_protected_directory(self):
        from app.utils.security import is_protected_directory
        self.assertTrue(is_protected_directory("C:\\Windows"))
        self.assertTrue(is_protected_directory("C:\\Windows\\System32"))

    def test_unique_destination(self):
        from app.utils.security import unique_destination
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, "file.txt"), "w") as f: f.write("existing")
            dest = unique_destination(d, "file.txt")
            self.assertIn("file_1.txt", dest)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_safe_join_traversal(self):
        from app.utils.security import safe_join
        with self.assertRaises(ValueError):
            safe_join("C:\\base", "..\\..\\escape")


class TestSecurity(unittest.TestCase):
    def test_validate_folder_empty(self):
        from app.utils.security import validate_folder_path
        ok, _ = validate_folder_path("")
        self.assertFalse(ok)

    def test_validate_folder_nonexistent(self):
        from app.utils.security import validate_folder_path
        ok, _ = validate_folder_path("C:\\nonexistent_xyz_123")
        self.assertFalse(ok)

    def test_truncate_message(self):
        from app.utils.security import truncate_message
        self.assertEqual(truncate_message("short"), "short")
        result = truncate_message("x" * 500, limit=100)
        self.assertEqual(len(result), 103)


class TestPasswordGenerator(unittest.TestCase):
    def test_uses_secrets_module(self):
        import inspect
        from app.gui.password_generator import PasswordGeneratorView
        source = inspect.getsource(PasswordGeneratorView._generate)
        self.assertIn("_secrets", source)
        self.assertNotIn("random.random", source)


if __name__ == "__main__":
    setUpModule()
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        tearDownModule()
        sys.exit(0 if result.wasSuccessful() else 1)
    except Exception:
        tearDownModule()
        raise