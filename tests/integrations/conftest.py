"""Reset OTEL state around integration tests (#588)."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_otel():
    from cauterule.integrations import otel as otel_module

    otel_module._CONFIGURED = False
    yield
    otel_module._CONFIGURED = False
