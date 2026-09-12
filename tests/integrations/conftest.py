"""Reset OTEL state around integration tests (#588)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def _reset_otel() -> Iterator[None]:
    from cauterule.integrations import otel as otel_module

    otel_module._CONFIGURED = False
    yield
    otel_module._CONFIGURED = False
