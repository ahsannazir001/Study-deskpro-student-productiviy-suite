"""Tests for study planner."""

from app.services import study_service


class TestStudyPlanner:
    def test_add_subject(self):
        ok, msg, sid = study_service.add_subject("Python", "2", "14")
        assert ok
        assert sid is not None

    def test_empty_name_fails(self):
        ok, msg, sid = study_service.add_subject("", "2", "14")
        assert not ok

    def test_invalid_target_fails(self):
        ok, msg, sid = study_service.add_subject("Test", "abc", "14")
        assert not ok

    def test_get_all_subjects(self):
        study_service.add_subject("Math", "1", "7")
        subjects = study_service.get_all_subjects()
        assert len(subjects) >= 1

    def test_update_subject(self):
        ok, _, sid = study_service.add_subject("Original", "1", "7")
        ok2, _ = study_service.update_subject(sid, "Updated", "2", "14")
        assert ok2
        subj = study_service.get_subject(sid)
        assert subj["name"] == "Updated"

    def test_delete_subject(self):
        ok, _, sid = study_service.add_subject("ToDelete", "1", "7")
        ok2, _ = study_service.delete_subject(sid)
        assert ok2
        assert study_service.get_subject(sid) is None

    def test_add_study_time(self):
        ok, _, sid = study_service.add_subject("StudyTime", "2", "14")
        ok2, _ = study_service.add_study_time(sid, "30")
        assert ok2
        subj = study_service.get_subject(sid)
        assert subj["completed_minutes"] == 30

    def test_reset_progress(self):
        ok, _, sid = study_service.add_subject("ResetTest", "2", "14")
        study_service.add_study_time(sid, "60")
        ok2, _ = study_service.reset_progress(sid)
        assert ok2
        subj = study_service.get_subject(sid)
        assert subj["completed_minutes"] == 0

    def test_progress_percent(self):
        subj = {"daily_target": 2, "completed_minutes": 60}
        pct = study_service.get_progress_percent(subj)
        assert pct == 50

    def test_progress_percent_no_target(self):
        subj = {"daily_target": 0, "completed_minutes": 60}
        pct = study_service.get_progress_percent(subj)
        assert pct == 0

    def test_today_study_minutes(self):
        ok, _, sid = study_service.add_subject("TodayTest", "1", "7")
        study_service.add_study_time(sid, "45")
        assert study_service.get_today_study_minutes() >= 45