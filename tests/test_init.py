import importlib


def test_version_matches_installed_package():
    import src

    from importlib.metadata import version

    assert src.__version__ == version("tenty-parser")


def test_version_falls_back_when_package_not_found(monkeypatch):
    import importlib.metadata as metadata

    def raise_not_found(_name):
        raise metadata.PackageNotFoundError

    monkeypatch.setattr(metadata, "version", raise_not_found)

    import src

    importlib.reload(src)
    try:
        assert src.__version__ == "unknown"
    finally:
        importlib.reload(src)  # restore the real version for any tests that run after
