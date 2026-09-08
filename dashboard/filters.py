"""Estado normalizado y filtros puros del panel."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

EVIDENCE_STATES = ("robusta", "frágil", "conflictiva", "no evaluada")


@dataclass(frozen=True)
class FilterSelection:
    """Selección coherente compartida por las vistas."""

    city_key: str
    room_type_keys: tuple[str, ...]
    neighborhood_keys: tuple[str, ...] = ()
    evidence_states: tuple[str, ...] = ()


def canonical_evidence_status(value: object) -> str:
    return {
        "robust": "robusta",
        "fragile": "frágil",
        "conflicting": "conflictiva",
    }.get(str(value), "no evaluada")


def _available_values(frame: pd.DataFrame, city_key: str, column: str) -> tuple[str, ...]:
    values = frame.loc[frame["city_key"].eq(city_key), column].dropna().astype(str).unique()
    return tuple(sorted(values))


def initial_selection(cities: pd.DataFrame, listings: pd.DataFrame) -> FilterSelection:
    """Crea un inicio determinista sin favorecer el orden técnico de las claves."""

    ordered = cities.sort_values("city_label_es", kind="stable")
    if ordered.empty:
        raise ValueError("No hay ciudades disponibles")
    city_key = str(ordered.iloc[0]["city_key"])
    return FilterSelection(
        city_key=city_key,
        room_type_keys=_available_values(listings, city_key, "room_type_key"),
    )


def normalize_selection(
    selection: FilterSelection,
    cities: pd.DataFrame,
    listings: pd.DataFrame,
) -> FilterSelection:
    """Elimina opciones huérfanas y garantiza al menos una tipología."""

    city_keys = set(cities["city_key"].astype(str))
    city_key = selection.city_key
    if city_key not in city_keys:
        return initial_selection(cities, listings)
    available_rooms = _available_values(listings, city_key, "room_type_key")
    room_types = tuple(value for value in selection.room_type_keys if value in available_rooms)
    if not room_types:
        room_types = available_rooms
    eligible = listings.loc[
        listings["city_key"].eq(city_key) & listings["room_type_key"].isin(room_types)
    ]
    available_neighborhoods = set(eligible["neighborhood_key"].dropna().astype(str))
    neighborhoods = tuple(
        value for value in selection.neighborhood_keys if value in available_neighborhoods
    )
    evidence = tuple(value for value in selection.evidence_states if value in EVIDENCE_STATES)
    return FilterSelection(city_key, room_types, neighborhoods, evidence)


def apply_listing_filters(frame: pd.DataFrame, selection: FilterSelection) -> pd.DataFrame:
    """Devuelve una copia de los anuncios compatibles con la selección."""

    mask = frame["city_key"].eq(selection.city_key) & frame["room_type_key"].isin(
        selection.room_type_keys
    )
    if selection.neighborhood_keys:
        mask &= frame["neighborhood_key"].isin(selection.neighborhood_keys)
    return frame.loc[mask].copy()

