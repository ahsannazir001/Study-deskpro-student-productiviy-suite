"""Tests for task management."""

from app.services import task_service
from app.utils.validators import is_overdue


class TestTaskCRUD:
    def test_add_task(self):
        ok, msg, tid = task_service.add_task("Buy groceries", "Milk and eggs", "High", "2026-12-31")
        assert ok
        assert tid is not None

    def test_add_empty_title_fails(self):
        ok, msg, tid = task_service.add_task("", "", "Medium")
        assert not ok
        assert "empty" in msg.lower()

    def test_add_invalid_date_fails(self):
        ok, msg, tid = task_service.add_task("Test", "", "Medium", "not-a-date")
        assert not ok

    def test_add_invalid_priority_fails(self):
        ok, msg, tid = task_service.add_task("Test", "", "Urgent")
        assert not ok

    def test_get_all_tasks(self):
        task_service.add_task("Task A", "", "Low")
        task_service.add_task("Task B", "", "High")
        tasks = task_service.get_all_tasks()
        assert len(tasks) >= 2

    def test_update_task(self):
        ok, _, tid = task_service.add_task("Original", "", "Low")
        ok2, msg = task_service.update_task(tid, "Updated", "desc", "High", "Pending", "2026-12-25")
        assert ok2
        task = task_service.get_task(tid)
        assert task["title"] == "Updated"
        assert task["priority"] == "High"

    def test_delete_task(self):
        ok, _, tid = task_service.add_task("ToDelete", "", "Medium")
        ok2, _ = task_service.delete_task(tid)
        assert ok2
        assert task_service.get_task(tid) is None

    def test_set_status_complete(self):
        ok, _, tid = task_service.add_task("StatusTest", "", "Medium")
        ok2, _ = task_service.set_status(tid, "Completed")
        assert ok2
        task = task_service.get_task(tid)
        assert task["status"] == "Completed"

    def test_search_tasks(self):
        task_service.add_task("UniqueSearchTerm", "", "Medium")
        results = task_service.get_all_tasks("UniqueSearchTerm")
        assert len(results) == 1
        assert results[0]["title"] == "UniqueSearchTerm"

    def test_filter_by_priority(self):
        task_service.add_task("LowTask", "", "Low")
        task_service.add_task("HighTask", "", "High")
        results = task_service.get_all_tasks(priority_filter="High")
        assert all(t["priority"] == "High" for t in results)

    def test_filter_by_status(self):
        ok, _, tid = task_service.add_task("CompleteMe", "", "Medium")
        task_service.set_status(tid, "Completed")
        results = task_service.get_all_tasks(status_filter="Completed")
        assert all(t["status"] == "Completed" for t in results)

    def test_stats(self):
        task_service.add_task("S1", "", "Medium")
        ok, _, tid = task_service.add_task("S2", "", "Medium")
        task_service.set_status(tid, "Completed")
        stats = task_service.get_stats()
        assert stats["total"] >= 2
        assert stats["completed"] >= 1
        assert stats["pending"] >= 1


class TestOverdue:
    def test_overdue_detection(self):
        assert is_overdue("2020-01-01", "Pending") is True
        assert is_overdue("2020-01-01", "Completed") is False
        assert is_overdue("", "Pending") is False
        assert is_overdue("2099-12-31", "Pending") is False