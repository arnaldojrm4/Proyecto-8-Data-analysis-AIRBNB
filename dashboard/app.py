"""Entrada Streamlit del panel avanzado."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from dashboard.data import DashboardDataError, DashboardDataset, load_dashboard_dataset

DEFAULT_DATA_DIR = Path("data/powerbi")


@st.cache_data(show_spinner=False)
def _load_cached(directory: str, build_identity: str) -> DashboardDataset:
    del build_identity
    return load_dashboard_dataset(directory)


def _control_identity(directory: Path) -> str:
    control = directory / "build_control.csv"
    if not control.is_file():
        return "missing"
    stat = control.stat()
    return f"{stat.st_mtime_ns}:{stat.st_size}"


def main() -> None:
    st.set_page_config(page_title="Oportunidades de captación", page_icon="🏠", layout="wide")
    st.title("Oportunidades de captación")
    data_dir = Path(os.environ.get("AIRBNB_DASHBOARD_DATA_DIR", DEFAULT_DATA_DIR))
    try:
        dataset = _load_cached(str(data_dir), _control_identity(data_dir))
    except DashboardDataError as error:
        st.error(f"No se puede abrir el panel: {error.detail}")
        st.caption(f"Código: {error.code} · Artefacto: {error.artifact}")
        st.info(
            "Genera un build aprobado con "
            "`docker compose run --rm pipeline all --log-format json`."
        )
        st.stop()

    st.sidebar.radio(
        "Vista",
        ("Resumen ejecutivo", "Oportunidades", "Evidencia estadística"),
        key="dashboard_view",
    )
    st.success(f"Build {dataset.build.build_id} aprobado")
    st.info("Las vistas analíticas se habilitarán después de seleccionar filtros.")


main()
