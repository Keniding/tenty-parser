from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("tenty-parser")
except PackageNotFoundError:
    __version__ = "unknown"
