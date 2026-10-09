"""Tests for notes management."""

from app.services import note_service


class TestNoteCRUD:
    def test_add_note(self):
        ok, msg, nid = note_service.add_note("My Note", "Content here", "Study")
        assert ok
        assert nid is not None

    def test_add_empty_title_fails(self):
        ok, msg, nid = note_service.add_note("", "content", "Other")
        assert not ok

    def test_invalid_category_fails(self):
        ok, msg, nid = note_service.add_note("Test", "content", "InvalidCat")
        assert not ok

    def test_get_all_notes(self):
        note_service.add_note("Note A", "a", "Study")
        note_service.add_note("Note B", "b", "Programming")
        notes = note_service.get_all_notes()
        assert len(notes) >= 2

    def test_update_note(self):
        ok, _, nid = note_service.add_note("Original", "old", "Personal")
        ok2, _ = note_service.update_note(nid, "Updated", "new content", "Project")
        assert ok2
        note = note_service.get_note(nid)
        assert note["title"] == "Updated"
        assert note["category"] == "Project"

    def test_delete_note(self):
        ok, _, nid = note_service.add_note("ToDelete", "", "Other")
        ok2, _ = note_service.delete_note(nid)
        assert ok2
        assert note_service.get_note(nid) is None

    def test_search_notes(self):
        note_service.add_note("UniqueNoteSearch", "find me", "Study")
        results = note_service.get_all_notes("UniqueNoteSearch")
        assert len(results) == 1

    def test_filter_by_category(self):
        note_service.add_note("ProgNote", "", "Programming")
        results = note_service.get_all_notes(category_filter="Programming")
        assert all(n["category"] == "Programming" for n in results)

    def test_get_count(self):
        note_service.add_note("CountTest", "", "Other")
        assert note_service.get_count() >= 1