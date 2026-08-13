import runpy
from unittest.mock import MagicMock

import tenty_parser.cli


def test_dunder_main_invokes_app(monkeypatch):
    mock_app = MagicMock()
    monkeypatch.setattr(tenty_parser.cli, "app", mock_app)
    runpy.run_module("tenty_parser.__main__", run_name="__main__")
    mock_app.assert_called_once()
