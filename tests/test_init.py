import importlib


def test_version_matches_installed_package():
    import tenty_parser

    from importlib.metadata import version

    assert tenty_parser.__version__ == version("tenty-parser")


def test_version_falls_back_when_package_not_found(monkeypatch):
    import importlib.metadata as metadata

    def raise_not_found(_name):
        raise metadata.PackageNotFoundError

    monkeypatch.setattr(metadata, "version", raise_not_found)

    import tenty_parser

    importlib.reload(tenty_parser)
    try:
        assert tenty_parser.__version__ == "unknown"
    finally:
        importlib.reload(tenty_parser)  # restore the real version for any tests that run after
