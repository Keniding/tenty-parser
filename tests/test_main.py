import runpy
from unittest.mock import MagicMock

import src.cli


def test_dunder_main_invokes_app(monkeypatch):
    mock_app = MagicMock()
    monkeypatch.setattr(src.cli, "app", mock_app)
    runpy.run_module("src.__main__", run_name="__main__")
    mock_app.assert_called_once()
