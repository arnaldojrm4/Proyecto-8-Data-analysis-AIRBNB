from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def test_dashboard_shell_reports_missing_exports_without_a_trace(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AIRBNB_DASHBOARD_DATA_DIR", str(tmp_path / "missing"))

    app_path = Path(__file__).resolve().parents[2] / "dashboard" / "app.py"
    try:
        app = AppTest.from_file(app_path).run(timeout=10)
    except FileNotFoundError:
        pytest.fail("Falta el punto de entrada ejecutable del panel")

    assert not app.exception
    assert any("No se puede abrir el panel" in item.value for item in app.error)
    assert any("pipeline all" in item.value for item in app.info)
