from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
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


def test_dashboard_filters_and_reset_share_one_population(
    monkeypatch, powerbi_export_fixture
) -> None:
    monkeypatch.setenv("AIRBNB_DASHBOARD_DATA_DIR", str(powerbi_export_fixture.directory))
    app_path = Path(__file__).resolve().parents[2] / "dashboard" / "app.py"

    app = AppTest.from_file(app_path).run(timeout=10)

    assert not app.exception
    assert app.selectbox[0].label == "Ciudad"
    assert app.multiselect[0].label == "Tipología"
    assert any(metric.label == "Anuncios" and metric.value == "2" for metric in app.metric)
    app.radio[0].set_value("Oportunidades").run(timeout=10)
    assert any("Ranking" in heading.value for heading in app.subheader)
    app.button[0].click().run(timeout=10)
    assert not app.exception


def test_dashboard_evidence_view_explains_all_hypothesis_families(
    monkeypatch, powerbi_export_fixture
) -> None:
    monkeypatch.setenv("AIRBNB_DASHBOARD_DATA_DIR", str(powerbi_export_fixture.directory))
    app_path = Path(__file__).resolve().parents[2] / "dashboard" / "app.py"
    app = AppTest.from_file(app_path).run(timeout=10)

    app.radio[0].set_value("Evidencia estadística").run(timeout=10)

    assert not app.exception
    rendered = " ".join(item.value for item in [*app.header, *app.subheader, *app.markdown])
    assert "H1" in rendered
    assert "H2" in rendered
    assert "H3" in rendered
    assert "H₀" in rendered
    assert "Población de referencia" in rendered
    assert "no implica causalidad" in rendered


def test_dashboard_summary_surfaces_priority_candidates(
    monkeypatch, powerbi_export_fixture
) -> None:
    monkeypatch.setenv("AIRBNB_DASHBOARD_DATA_DIR", str(powerbi_export_fixture.directory))
    app_path = Path(__file__).resolve().parents[2] / "dashboard" / "app.py"

    app = AppTest.from_file(app_path).run(timeout=10)

    assert not app.exception
    assert any("Candidatos prioritarios" in item.value for item in app.subheader)
    assert app.dataframe


def test_dashboard_blocks_a_rejected_build_and_recovers_without_residual_metrics(
    monkeypatch, powerbi_export_fixture, tmp_path: Path
) -> None:
    export_dir = tmp_path / "recovery"
    shutil.copytree(powerbi_export_fixture.directory, export_dir)
    control_path = export_dir / "build_control.csv"
    original = pd.read_csv(control_path)
    rejected = original.copy()
    rejected["release_gate_status"] = "fail"
    rejected.to_csv(control_path, index=False)
    monkeypatch.setenv("AIRBNB_DASHBOARD_DATA_DIR", str(export_dir))
    app_path = Path(__file__).resolve().parents[2] / "dashboard" / "app.py"

    blocked = AppTest.from_file(app_path).run(timeout=10)

    assert not blocked.exception
    assert not blocked.metric
    assert any("release_gate_failed" in item.value for item in blocked.caption)
    assert any("build rechazado" in item.value.casefold() for item in blocked.error)

    original.to_csv(control_path, index=False)
    recovered = AppTest.from_file(app_path).run(timeout=10)

    assert not recovered.exception
    assert any(metric.label == "Anuncios" for metric in recovered.metric)


def test_dashboard_distinguishes_empty_segments_from_insufficient_evidence(
    monkeypatch, powerbi_export_fixture
) -> None:
    monkeypatch.setenv("AIRBNB_DASHBOARD_DATA_DIR", str(powerbi_export_fixture.directory))
    app_path = Path(__file__).resolve().parents[2] / "dashboard" / "app.py"
    app = AppTest.from_file(app_path).run(timeout=10)

    app.multiselect[2].set_value(["frágil"])
    app.radio[0].set_value("Oportunidades").run(timeout=10)
    assert not app.exception
    assert any("Estado empty" in item.value for item in app.info)
    assert not app.dataframe

    app.radio[0].set_value("Evidencia estadística").run(timeout=10)
    assert not app.exception
    assert any("Estado insufficient" in item.value for item in app.info)
    assert not app.dataframe
