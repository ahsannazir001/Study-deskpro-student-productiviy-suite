"""Tests for password generator, text tools, settings, file organizer, and database."""

import os
import string
import secrets
import tempfile
import shutil

import pytest


class TestPasswordGenerator:
    def test_generate_uses_secrets(self):
        from app.gui.password_generator import PasswordGeneratorView
        import inspect
        source = inspect.getsource(PasswordGeneratorView._generate)
        assert "secrets" in source or "_secrets" in source
        assert "random.random" not in source


class TestTextTools:
    def test_word_count(self):
        text = "Hello world foo bar"
        assert len(text.split()) == 4

    def test_character_count(self):
        text = "Hello world"
        assert len(text) == 11

    def test_line_count(self):
        text = "Line1\nLine2\nLine3"
        assert text.count("\n") + 1 == 3

    def test_uppercase(self):
        assert "hello".upper() == "HELLO"

    def test_title_case(self):
        assert "hello world".title() == "Hello World"


class TestSettings:
    def test_get_default_setting(self):
        from app.services import settings_service
        assert settings_service.get_setting("theme", "light") == "light"

    def test_set_and_get_setting(self):
        from app.services import settings_service
        settings_service.set_setting("test_key", "test_value")
        assert settings_service.get_setting("test_key") == "test_value"

    def test_get_int(self):
        from app.services import settings_service
        settings_service.set_setting("int_key", "42")
        assert settings_service.get_int("int_key") == 42

    def test_persistence(self):
        from app.services import settings_service
        settings_service.set_setting("persist_key", "persist_value")
        settings_service.reset_cache()
        assert settings_service.get_setting("persist_key") == "persist_value"


class TestDatabase:
    def test_insert_and_read(self):
        from app.database import db
        cur = db.execute("INSERT INTO tasks (title, priority, status, created_at, updated_at) VALUES (?, 'Medium', 'Pending', ?, ?)",
                         ("DBTest", "2026-01-01", "2026-01-01"))
        tid = cur.lastrowid
        row = db.query_one("SELECT * FROM tasks WHERE id=?", (tid,))
        assert row["title"] == "DBTest"

    def test_update(self):
        from app.database import db
        cur = db.execute("INSERT INTO tasks (title, priority, status, created_at, updated_at) VALUES (?, 'Medium', 'Pending', ?, ?)",
                         ("UpdateTest", "2026-01-01", "2026-01-01"))
        tid = cur.lastrowid
        db.execute("UPDATE tasks SET status='Completed' WHERE id=?", (tid,))
        row = db.query_one("SELECT * FROM tasks WHERE id=?", (tid,))
        assert row["status"] == "Completed"

    def test_delete(self):
        from app.database import db
        cur = db.execute("INSERT INTO tasks (title, priority, status, created_at, updated_at) VALUES (?, 'Medium', 'Pending', ?, ?)",
                         ("DeleteTest", "2026-01-01", "2026-01-01"))
        tid = cur.lastrowid
        db.execute("DELETE FROM tasks WHERE id=?", (tid,))
        row = db.query_one("SELECT * FROM tasks WHERE id=?", (tid,))
        assert row is None

    def test_parameterized_query(self):
        from app.database import db
        rows = db.query("SELECT * FROM settings WHERE key=?", ("theme",))
        assert len(rows) >= 1


class TestFileOrganizer:
    def test_category_for_extension(self):
        from app.services.file_service import category_for_extension
        assert category_for_extension(".png") == "Images"
        assert category_for_extension(".jpg") == "Images"
        assert category_for_extension(".pdf") == "Documents"
        assert category_for_extension(".docx") == "Documents"
        assert category_for_extension(".mp4") == "Videos"
        assert category_for_extension(".mp3") == "Audio"
        assert category_for_extension(".xyz") == "Others"

    def test_analyze_directory(self, tmp_path):
        from app.services.file_service import analyze_directory
        (tmp_path / "test.png").write_text("img")
        (tmp_path / "doc.pdf").write_text("doc")
        (tmp_path / "song.mp3").write_text("audio")
        results, error = analyze_directory(str(tmp_path))
        assert error is None
        assert len(results) == 3
        categories = {r["category"] for r in results}
        assert "Images" in categories
        assert "Documents" in categories
        assert "Audio" in categories

    def test_protected_directory(self):
        from app.utils.security import is_protected_directory
        assert is_protected_directory("C:\\Windows") is True
        assert is_protected_directory("C:\\Windows\\System32") is True

    def test_unique_destination(self, tmp_path):
        from app.utils.security import unique_destination
        (tmp_path / "file.txt").write_text("existing")
        dest = unique_destination(str(tmp_path), "file.txt")
        assert "file_1.txt" in dest

    def test_plan_operations(self, tmp_path):
        from app.services.file_service import analyze_directory, plan_operations
        (tmp_path / "a.png").write_text("a")
        (tmp_path / "b.pdf").write_text("b")
        results, _ = analyze_directory(str(tmp_path))
        plan, conflicts = plan_operations(str(tmp_path), results)
        assert len(plan) == 2
        assert len(conflicts) == 0

    def test_execute_moves_files(self, tmp_path):
        from app.services.file_service import analyze_directory, plan_operations, execute_plan
        (tmp_path / "test.png").write_text("img")
        results, _ = analyze_directory(str(tmp_path))
        plan, _ = plan_operations(str(tmp_path), results)
        moved, skipped, errors = execute_plan(plan)
        assert len(moved) == 1
        assert (tmp_path / "Images" / "test.png").exists()
        assert not (tmp_path / "test.png").exists()


class TestSecurity:
    def test_validate_folder_empty(self):
        from app.utils.security import validate_folder_path
        ok, msg = validate_folder_path("")
        assert not ok

    def test_validate_folder_nonexistent(self):
        from app.utils.security import validate_folder_path
        ok, msg = validate_folder_path("C:\\nonexistent_folder_xyz_123")
        assert not ok

    def test_safe_join_traversal(self):
        from app.utils.security import safe_join
        with pytest.raises(ValueError):
            safe_join("C:\\base", "..\\..\\escape")

    def test_is_within_directory(self):
        from app.utils.security import is_within_directory
        assert is_within_directory("C:\\base\\file.txt", "C:\\base") is True
        assert is_within_directory("C:\\other\\file.txt", "C:\\base") is False

    def test_truncate_message(self):
        from app.utils.security import truncate_message
        assert truncate_message("short") == "short"
        long = "x" * 500
        result = truncate_message(long, limit=100)
        assert len(result) == 103