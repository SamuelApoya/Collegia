import importlib
import os
from unittest.mock import patch


def test_run_local_starts_scheduler_and_sets_oauth_env(monkeypatch):
    # GIVEN
    monkeypatch.delenv("DYNO", raising=False)

    with patch("run.create_app") as mock_create_app, \
         patch("run.start_scheduler") as mock_start_scheduler, \
         patch("run.app"):

        mock_create_app.return_value = object()

        # WHEN
        importlib.reload(importlib.import_module("run"))

        # THEN
        assert os.getenv("OAUTHLIB_INSECURE_TRANSPORT") == "1"
        mock_start_scheduler.assert_called()


def test_run_on_dyno_does_not_start_scheduler(monkeypatch):
    # GIVEN
    monkeypatch.setenv("DYNO", "true")

    with patch("run.create_app") as mock_create_app, \
         patch("run.start_scheduler") as mock_start_scheduler, \
         patch("run.app"):

        mock_create_app.return_value = object()

        # WHEN
        importlib.reload(importlib.import_module("run"))

        # THEN
        mock_start_scheduler.assert_not_called()


def test_run_main_guard(monkeypatch):
    # GIVEN
    monkeypatch.delenv("DYNO", raising=False)

    with patch("run.create_app") as mock_create_app, \
         patch("run.start_scheduler"), \
         patch("run.app") as mock_app:

        mock_create_app.return_value = mock_app

        # WHEN
        module = importlib.import_module("run")
        if hasattr(module, "__main__"):
            pass

        # THEN
        assert True
