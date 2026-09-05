import importlib
import sys

from _pytest.monkeypatch import MonkeyPatch


def test_version_fallback(monkeypatch: MonkeyPatch) -> None:
    """Cover the ``except Exception`` branch in ``__init__.py``."""

    def fake_version(_name: str) -> str:
        raise RuntimeError("not installed")

    monkeypatch.setattr("importlib.metadata.version", fake_version)
    # Re-import under patched version.
    if "cauterule" in sys.modules:
        del sys.modules["cauterule"]
    mod = importlib.import_module("cauterule")
    assert mod.__version__ == "0.1.0"
    # Restore real module for other tests.
    del sys.modules["cauterule"]
    import cauterule

    assert isinstance(cauterule.__version__, str)
    assert len(cauterule.__version__) > 0
