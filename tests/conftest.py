"""Shared test fixtures."""

import os
import sys
import tempfile
import shutil

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Redirect data directory to a temp folder for each test."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    (tmp_path / "data" / "logs").mkdir(exist_ok=True)

    monkeypatch.setattr("app.utils.helpers.get_app_data_dir", lambda: str(data_dir))
    monkeypatch.setattr("app.utils.helpers.get_log_dir", lambda: str(data_dir / "logs"))

    from app.utils.logger import init_logging
    init_logging(str(data_dir / "logs"))

    from app.database import db
    db._db_path = str(data_dir / "studydesk.db")
    db.close_connection()
    db.initialize()

    from app.services import settings_service
    settings_service.reset_cache()

    yield

    db.close_connection()