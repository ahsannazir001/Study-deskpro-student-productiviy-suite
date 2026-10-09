"""Tests for expense tracking."""

from app.services import expense_service


class TestExpenseCRUD:
    def test_add_expense(self):
        ok, msg, eid = expense_service.add_expense("500", "Food", "Lunch", "2026-10-08")
        assert ok
        assert eid is not None

    def test_negative_amount_fails(self):
        ok, msg, eid = expense_service.add_expense("-100", "Food", "", "")
        assert not ok

    def test_invalid_amount_fails(self):
        ok, msg, eid = expense_service.add_expense("abc", "Food", "", "")
        assert not ok

    def test_invalid_category_fails(self):
        ok, msg, eid = expense_service.add_expense("100", "InvalidCat", "", "")
        assert not ok

    def test_invalid_date_fails(self):
        ok, msg, eid = expense_service.add_expense("100", "Food", "", "bad-date")
        assert not ok

    def test_default_date(self):
        ok, _, eid = expense_service.add_expense("100", "Transport", "", "")
        assert ok
        exp = expense_service.get_expense(eid)
        assert exp["expense_date"] is not None

    def test_get_all_expenses(self):
        expense_service.add_expense("100", "Food", "a", "")
        expense_service.add_expense("200", "Books", "b", "")
        expenses = expense_service.get_all_expenses()
        assert len(expenses) >= 2

    def test_update_expense(self):
        ok, _, eid = expense_service.add_expense("100", "Food", "old", "2026-10-01")
        ok2, _ = expense_service.update_expense(eid, "250", "Transport", "new", "2026-10-05")
        assert ok2
        exp = expense_service.get_expense(eid)
        assert exp["amount"] == 250.0
        assert exp["category"] == "Transport"

    def test_delete_expense(self):
        ok, _, eid = expense_service.add_expense("100", "Food", "", "")
        ok2, _ = expense_service.delete_expense(eid)
        assert ok2
        assert expense_service.get_expense(eid) is None

    def test_search_expenses(self):
        expense_service.add_expense("100", "Food", "UniqueExpenseSearch", "")
        results = expense_service.get_all_expenses("UniqueExpenseSearch")
        assert len(results) == 1

    def test_filter_by_category(self):
        expense_service.add_expense("100", "Books", "", "")
        results = expense_service.get_all_expenses(category_filter="Books")
        assert all(e["category"] == "Books" for e in results)

    def test_monthly_total(self):
        expense_service.add_expense("1000", "Food", "", "")
        expense_service.add_expense("500", "Transport", "", "")
        total = expense_service.get_monthly_total()
        assert total >= 1500

    def test_category_totals(self):
        expense_service.add_expense("300", "Food", "", "")
        totals = expense_service.get_category_totals()
        assert "Food" in totals
        assert totals["Food"] >= 300

    def test_get_total(self):
        expense_service.add_expense("100", "Food", "", "")
        assert expense_service.get_total() >= 100