"""Entrada Streamlit del panel avanzado."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from dashboard.data import DashboardDataError, DashboardDataset, load_dashboard_dataset
from dashboard.filters import (
    EVIDENCE_STATES,
    FilterSelection,
    apply_listing_filters,
    apply_opportunity_filters,
    apply_statistical_filters,
    initial_selection,
    normalize_selection,
    safe_option_index,
)
from dashboard.presentation import dashboard_error_message
from dashboard.views import evidence, market_structure, opportunities, summary

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


def _filters(dataset: DashboardDataset) -> FilterSelection:
    initial = initial_selection(dataset.cities, dataset.listings)
    city_labels = dict(
        zip(dataset.cities["city_key"], dataset.cities["city_label_es"], strict=True)
    )
    city_options = sorted(city_labels, key=lambda key: city_labels[key])
    city_key = st.sidebar.selectbox(
        "Ciudad",
        city_options,
        format_func=city_labels.get,
        index=safe_option_index(
            city_options,
            st.session_state.get("selected_city", initial.city_key),
            initial.city_key,
        ),
    )
    st.session_state["selected_city"] = city_key
    listing_scope = dataset.listings.loc[dataset.listings["city_key"].eq(city_key)]
    room_keys = sorted(listing_scope["room_type_key"].dropna().astype(str).unique())
    room_labels = dict(
        zip(
            dataset.room_types["room_type_key"],
            dataset.room_types["room_type_label_es"],
            strict=True,
        )
    )
    selected_rooms = st.sidebar.multiselect(
        "Tipología",
        room_keys,
        default=room_keys,
        format_func=room_labels.get,
        key=f"rooms_{city_key}",
    )
    neighborhood_scope = listing_scope.loc[listing_scope["room_type_key"].isin(selected_rooms)]
    neighborhood_keys = sorted(
        neighborhood_scope["neighborhood_key"].dropna().astype(str).unique()
    )
    neighborhood_labels = dict(
        zip(
            dataset.neighborhoods["neighborhood_key"],
            dataset.neighborhoods["neighborhood_label"],
            strict=True,
        )
    )
    selected_neighborhoods = st.sidebar.multiselect(
        "Barrio",
        neighborhood_keys,
        format_func=neighborhood_labels.get,
        key=f"neighborhoods_{city_key}",
    )
    evidence = st.sidebar.multiselect("Estado de evidencia", EVIDENCE_STATES)
    if st.sidebar.button("Restablecer filtros"):
        for key in list(st.session_state):
            if key.startswith(("rooms_", "neighborhoods_")) or key in {
                "selected_city",
                "Estado de evidencia",
            }:
                del st.session_state[key]
        st.rerun()
    return normalize_selection(
        FilterSelection(
            city_key=str(city_key),
            room_type_keys=tuple(selected_rooms),
            neighborhood_keys=tuple(selected_neighborhoods),
            evidence_states=tuple(evidence),
        ),
        dataset.cities,
        dataset.listings,
    )


def main() -> None:
    st.set_page_config(page_title="Estructura del mercado Airbnb", page_icon="🏠", layout="wide")
    st.title("Estructura del mercado Airbnb")
    data_dir = Path(os.environ.get("AIRBNB_DASHBOARD_DATA_DIR", DEFAULT_DATA_DIR))
    try:
        dataset = _load_cached(str(data_dir), _control_identity(data_dir))
    except DashboardDataError as error:
        message, recovery = dashboard_error_message(error)
        st.error(f"No se puede abrir el panel: {message}")
        st.caption(f"Estado: blocked · Código: {error.code} · Artefacto: {error.artifact}")
        st.info(f"{recovery} Comando: `docker compose run --rm pipeline all --log-format json`.")
        st.stop()

    view = st.sidebar.radio(
        "Vista",
        (
            "Estructura del mercado",
            "Resumen ejecutivo",
            "Oportunidades",
            "Evidencia estadística",
        ),
        key="dashboard_view",
    )
    selection = _filters(dataset)
    filtered_listings = apply_listing_filters(dataset.listings, selection)
    filtered_opportunities = apply_opportunity_filters(dataset.opportunities, selection)
    filtered_statistics = apply_statistical_filters(
        dataset.statistics,
        dataset.opportunities,
        selection,
    )
    st.caption(
        f"Build {dataset.build.build_id} aprobado · "
        f"{len(filtered_listings):,} anuncios en la selección".replace(",", ".")
    )
    if view == "Resumen ejecutivo":
        summary.render(dataset, filtered_listings, filtered_opportunities)
    elif view == "Estructura del mercado":
        market_structure.render(dataset, filtered_listings)
    elif view == "Oportunidades":
        opportunities.render(dataset, filtered_opportunities)
    else:
        evidence.render(dataset, filtered_statistics)



main()
