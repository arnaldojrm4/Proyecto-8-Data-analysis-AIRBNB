"""Contratos tabulares compartidos."""

from __future__ import annotations

import pandas as pd
import pandera.pandas as pa


class OutputContractError(ValueError):
    """Indica que una salida no cumple el contrato publicado."""


EXPECTED_POWERBI_FILES: set[str] = {
    "dim_city.csv",
    "dim_neighborhood.csv",
    "dim_room_type.csv",
    "fact_listings.csv",
    "fact_opportunity_segments.csv",
    "fact_statistical_results.csv",
    "fact_quality_summary.csv",
    "build_control.csv",
}

RESTRICTED_POWERBI_COLUMNS: frozenset[str] = frozenset(
    {"listing_name", "host_name", "listing_id", "host_id", "latitude", "longitude"}
)

RAW_CORE_COLUMNS = frozenset(
    {
        "id",
        "name",
        "host_id",
        "host_name",
        "neighbourhood",
        "latitude",
        "longitude",
        "room_type",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "last_review",
        "reviews_per_month",
    }
)


def validate_no_restricted_columns(frame: pd.DataFrame) -> None:
    """Valida la frontera de privacidad de una tabla destinada al informe."""

    present = RESTRICTED_POWERBI_COLUMNS.intersection(frame.columns)
    if present:
        fields = ", ".join(sorted(present))
        raise OutputContractError(f"Campos restringidos en salida Power BI: {fields}")


CANONICAL_SCHEMA = pa.DataFrameSchema(
    {
        "listing_key": pa.Column(str, nullable=False, unique=True),
        "city_key": pa.Column(str, nullable=False),
        "listing_id": pa.Column(int, nullable=False, coerce=True),
        "host_id": pa.Column(int, nullable=False, coerce=True),
        "neighborhood": pa.Column(str, nullable=True, coerce=True),
        "neighborhood_key": pa.Column(str, nullable=True, coerce=True),
        "room_type": pa.Column(str, nullable=True, coerce=True),
        "price": pa.Column(float, nullable=True, coerce=True),
        "minimum_nights": pa.Column(int, nullable=True, coerce=True),
        "number_of_reviews": pa.Column(int, nullable=True, coerce=True),
        "reviews_per_month_observed": pa.Column(float, nullable=True, coerce=True),
        "activity_proxy": pa.Column(float, nullable=True, coerce=True),
        "activity_proxy_derived_zero": pa.Column(bool, nullable=False, coerce=True),
        "activity_proxy_is_analyzable": pa.Column(bool, nullable=False, coerce=True),
    },
    coerce=True,
    strict=False,
)


def validate_canonical(frame: pd.DataFrame) -> pd.DataFrame:
    """Valida el núcleo común del dataset canónico."""

    return CANONICAL_SCHEMA.validate(frame, lazy=True)


def validate_raw_frame(frame: pd.DataFrame, source_id: str) -> pd.DataFrame:
    """Aplica reglas permisivas comunes sin fabricar columnas no disponibles."""

    missing = sorted(RAW_CORE_COLUMNS.difference(frame.columns))
    if missing:
        raise ValueError(f"Columnas raw requeridas ausentes en {source_id}: {', '.join(missing)}")
    ids = pd.to_numeric(frame["id"], errors="coerce")
    if ids.isna().any():
        raise ValueError(f"id no parseable en {source_id}")
    if ids.duplicated(keep=False).any():
        raise ValueError(f"id duplicado dentro de {source_id}")
    if pd.to_numeric(frame["host_id"], errors="coerce").isna().any():
        raise ValueError(f"host_id no parseable en {source_id}")
    return frame
