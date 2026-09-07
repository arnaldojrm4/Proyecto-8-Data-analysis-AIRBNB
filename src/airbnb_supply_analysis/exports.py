"""Construcción y publicación estable de artefactos tabulares."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

import pandas as pd

CITY_COLUMNS: Final = [
    "city_key",
    "city_label_es",
    "source_snapshot_date_status",
    "price_currency_status",
    "scope_note_es",
]
NEIGHBORHOOD_COLUMNS: Final = [
    "neighborhood_key",
    "city_key",
    "neighborhood_label",
    "centroid_latitude",
    "centroid_longitude",
    "coordinate_coverage",
]
ROOM_TYPE_COLUMNS: Final = [
    "room_type_key",
    "room_type",
    "room_type_label_es",
    "sort_order",
]
LISTING_COLUMNS: Final = [
    "listing_key",
    "city_key",
    "neighborhood_key",
    "room_type_key",
    "price",
    "minimum_nights",
    "number_of_reviews",
    "reviews_per_month_observed",
    "activity_proxy",
    "activity_proxy_derived_zero",
    "activity_proxy_is_analyzable",
    "price_is_valid",
    "minimum_nights_is_valid",
    "coordinate_is_valid",
]
OPPORTUNITY_COLUMNS: Final = [
    "segment_key",
    "city_key",
    "neighborhood_key",
    "room_type_key",
    "build_id",
    "listing_count",
    "city_supply_share",
    "neighborhood_supply_share",
    "neighborhood_room_type_share",
    "room_type_city_share",
    "activity_analyzable_count",
    "positive_activity_count",
    "active_listing_share",
    "activity_median",
    "activity_iqr",
    "positive_activity_median",
    "activity_p90",
    "activity_p99",
    "valid_price_count",
    "price_median",
    "price_iqr",
    "valid_minimum_nights_count",
    "minimum_nights_median",
    "minimum_nights_p90",
    "probability_superiority",
    "effect_ci_low",
    "effect_ci_high",
    "median_difference",
    "p_value_raw",
    "q_value",
    "sensitivity_status",
    "centroid_latitude",
    "centroid_longitude",
    "coordinate_coverage",
    "quality_flag_count",
    "price_position_percentile_within_city_room_type",
    "eligibility_status",
    "eligibility_reason",
    "opportunity_label",
    "candidate_rank",
]
STATISTICAL_COLUMNS: Final = [
    "result_id",
    "build_id",
    "analysis_family",
    "city_key",
    "segment_key",
    "metric",
    "comparison",
    "method",
    "sample_size",
    "positive_sample_size",
    "estimate",
    "effect_type",
    "median_difference",
    "ci_low",
    "ci_high",
    "p_value_raw",
    "p_value_adjusted",
    "correction_method",
    "assumption_status",
    "sensitivity_status",
    "interpretation_es",
]
QUALITY_COLUMNS: Final = [
    "build_id",
    "source_id",
    "quality_metric",
    "field",
    "evaluated_count",
    "failed_count",
    "failure_rate",
    "severity",
    "status",
    "interpretation_es",
]
CONTROL_COLUMNS: Final = [
    "build_id",
    "schema_version",
    "generated_at_utc",
    "source_manifest_hash",
    "analysis_config_hash",
    "source_file_count",
    "source_row_count",
    "canonical_row_count",
    "distinct_listing_key_count",
    "segment_count",
    "output_file",
    "output_row_count",
    "output_sha256",
    "release_gate_status",
]

POWERBI_SORT_KEYS: Final = {
    "dim_city.csv": ["city_key"],
    "dim_neighborhood.csv": ["neighborhood_key"],
    "dim_room_type.csv": ["room_type_key"],
    "fact_listings.csv": ["listing_key"],
    "fact_opportunity_segments.csv": ["segment_key"],
    "fact_statistical_results.csv": ["result_id"],
    "fact_quality_summary.csv": ["build_id", "source_id", "quality_metric", "field"],
}

ROOM_TYPE_LABELS: Final = {
    "entire_home_apt": ("Alojamiento entero", 1),
    "private_room": ("Habitación privada", 2),
    "hotel_room": ("Habitación de hotel", 3),
    "shared_room": ("Habitación compartida", 4),
    "unknown": ("Tipología desconocida", 99),
}

MINIMUM_AGGREGATE_COORDINATE_ROWS: Final = 3


def write_stable_csv(frame: pd.DataFrame, path: Path, sort_by: list[str] | None = None) -> None:
    output = frame.sort_values(sort_by, kind="stable") if sort_by else frame
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    os.close(descriptor)
    try:
        output.to_csv(
            temp_name,
            index=False,
            encoding="utf-8",
            lineterminator="\n",
            float_format="%.10g",
        )
        os.replace(temp_name, path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise


def write_parquet(frame: pd.DataFrame, path: Path, sort_by: list[str] | None = None) -> None:
    output = frame.sort_values(sort_by, kind="stable") if sort_by else frame
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    try:
        output.to_parquet(temp_path, index=False, compression="zstd")
        os.replace(temp_path, path)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _surrogate_key(namespace: str, value: object) -> str:
    digest = _sha256_bytes(f"airbnb-supply:{namespace}:{value}".encode())
    return f"{namespace}_{digest}"


def _load_source_manifest(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {"sources": []}
    with path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"Manifiesto de fuentes inválido: {path}")
    return payload


def _file_identity(path: Path) -> str:
    return _sha256_file(path) if path.is_file() else _sha256_bytes(b"")


def _safe_neighborhood_keys(listings: pd.DataFrame) -> pd.Series:
    fallback = listings["city_key"].astype("string") + ":unknown"
    return listings["neighborhood_key"].astype("string").fillna(fallback)


def _safe_room_types(frame: pd.DataFrame) -> pd.Series:
    return frame["room_type"].astype("string").fillna("unknown")


def _room_type_keys(room_types: pd.Series) -> pd.Series:
    return room_types.map(lambda value: _surrogate_key("room_type", value)).astype("string")


def _build_city_dimension(
    listings: pd.DataFrame, source_manifest: Mapping[str, object]
) -> pd.DataFrame:
    sources = source_manifest.get("sources", [])
    metadata = {
        str(source["city_key"]): source
        for source in sources
        if isinstance(source, dict) and source.get("city_key")
    }
    rows = []
    for city_key in sorted(listings["city_key"].astype(str).unique()):
        source = metadata.get(city_key, {})
        snapshot = source.get("snapshot_date")
        currency = source.get("currency")
        rows.append(
            {
                "city_key": city_key,
                "city_label_es": source.get("display_city_es", city_key.replace("_", " ").title()),
                "source_snapshot_date_status": (
                    str(snapshot) if snapshot else "Fecha de snapshot desconocida"
                ),
                "price_currency_status": str(currency) if currency else "Moneda desconocida",
                "scope_note_es": (
                    "Precio publicado comparable solo dentro de la ciudad; no representa ingresos."
                ),
            }
        )
    return pd.DataFrame(rows, columns=CITY_COLUMNS)


def _build_neighborhood_dimension(listings: pd.DataFrame) -> pd.DataFrame:
    geography = listings.copy()
    geography["neighborhood_key"] = _safe_neighborhood_keys(geography)
    geography["neighborhood_label"] = (
        geography["neighborhood"].astype("string").fillna("Barrio desconocido")
    )
    valid_coordinates = geography["coordinate_is_valid"].fillna(False).astype(bool)
    geography["valid_latitude"] = geography["latitude"].where(valid_coordinates)
    geography["valid_longitude"] = geography["longitude"].where(valid_coordinates)
    geography["valid_coordinate"] = valid_coordinates.astype(int)
    grouped = (
        geography.groupby(["neighborhood_key", "city_key"], observed=True, dropna=False)
        .agg(
            neighborhood_label=("neighborhood_label", "first"),
            centroid_latitude=("valid_latitude", "median"),
            centroid_longitude=("valid_longitude", "median"),
            coordinate_coverage=("valid_coordinate", "mean"),
            coordinate_count=("valid_coordinate", "sum"),
        )
        .reset_index()
    )
    disclose = grouped["coordinate_count"].ge(MINIMUM_AGGREGATE_COORDINATE_ROWS)
    grouped.loc[~disclose, ["centroid_latitude", "centroid_longitude"]] = pd.NA
    return grouped[NEIGHBORHOOD_COLUMNS]


def _build_room_type_dimension(listings: pd.DataFrame, opportunities: pd.DataFrame) -> pd.DataFrame:
    room_types = pd.concat(
        [_safe_room_types(listings), _safe_room_types(opportunities)], ignore_index=True
    ).drop_duplicates()
    rows = []
    for room_type in room_types:
        label, sort_order = ROOM_TYPE_LABELS.get(
            str(room_type), (str(room_type).replace("_", " ").title(), 98)
        )
        rows.append(
            {
                "room_type_key": _surrogate_key("room_type", room_type),
                "room_type": room_type,
                "room_type_label_es": label,
                "sort_order": sort_order,
            }
        )
    return pd.DataFrame(rows, columns=ROOM_TYPE_COLUMNS)


def _build_listing_fact(listings: pd.DataFrame) -> pd.DataFrame:
    output = listings.copy()
    output["listing_key"] = output["listing_key"].map(
        lambda value: _surrogate_key("listing", value)
    )
    output["neighborhood_key"] = _safe_neighborhood_keys(output)
    output["room_type_key"] = _room_type_keys(_safe_room_types(output))
    return output[LISTING_COLUMNS]


def _build_opportunity_fact(opportunities: pd.DataFrame) -> pd.DataFrame:
    output = opportunities.copy()
    output["room_type_key"] = _room_type_keys(_safe_room_types(output))
    disclose = output["listing_count"].ge(MINIMUM_AGGREGATE_COORDINATE_ROWS)
    output.loc[~disclose, ["centroid_latitude", "centroid_longitude"]] = pd.NA
    return output[OPPORTUNITY_COLUMNS]


def _build_statistical_fact(statistical: pd.DataFrame) -> pd.DataFrame:
    return statistical[STATISTICAL_COLUMNS].copy()


def _build_quality_fact(quality: pd.DataFrame) -> pd.DataFrame:
    output = quality.rename(
        columns={
            "check_id": "quality_metric",
            "failed_rate": "failure_rate",
            "disposition": "status",
            "impact": "interpretation_es",
        }
    )
    output = output.copy()
    if "failure_rate" not in output:
        denominator = output["evaluated_count"].replace(0, pd.NA)
        output["failure_rate"] = output["failed_count"].div(denominator).fillna(0.0)
    if "status" not in output:
        output["status"] = output["failed_count"].gt(0).map({True: "open", False: "pass"})
    output["field"] = output["field"].astype("string").fillna("")
    return output[QUALITY_COLUMNS]


def build_powerbi_tables(
    listings: pd.DataFrame,
    opportunities: pd.DataFrame,
    statistical: pd.DataFrame,
    quality: pd.DataFrame,
    source_manifest: Mapping[str, object],
) -> dict[str, pd.DataFrame]:
    """Construye las siete tablas analíticas del modelo estrella sin escribir archivos."""

    return {
        "dim_city.csv": _build_city_dimension(listings, source_manifest),
        "dim_neighborhood.csv": _build_neighborhood_dimension(listings),
        "dim_room_type.csv": _build_room_type_dimension(listings, opportunities),
        "fact_listings.csv": _build_listing_fact(listings),
        "fact_opportunity_segments.csv": _build_opportunity_fact(opportunities),
        "fact_statistical_results.csv": _build_statistical_fact(statistical),
        "fact_quality_summary.csv": _build_quality_fact(quality),
    }


def export_powerbi_dataset(
    listings: pd.DataFrame,
    opportunities: pd.DataFrame,
    statistical: pd.DataFrame,
    quality: pd.DataFrame,
    output_dir: Path,
    *,
    build_id: str,
    schema_version: str,
    source_manifest_path: Path,
    analysis_config_path: Path,
    generated_at_utc: str | None = None,
) -> dict[str, pd.DataFrame]:
    """Publica las tablas estrella y un control verificable de la misma ejecución."""

    source_manifest = _load_source_manifest(source_manifest_path)
    tables = build_powerbi_tables(
        listings,
        opportunities,
        statistical,
        quality,
        source_manifest,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, frame in tables.items():
        write_stable_csv(frame, output_dir / filename, POWERBI_SORT_KEYS[filename])

    sources = source_manifest.get("sources", [])
    generated = generated_at_utc or datetime.now(UTC).isoformat()
    shared = {
        "build_id": build_id,
        "schema_version": schema_version,
        "generated_at_utc": generated,
        "source_manifest_hash": _file_identity(source_manifest_path),
        "analysis_config_hash": _file_identity(analysis_config_path),
        "source_file_count": len(sources) if isinstance(sources, list) else 0,
        "source_row_count": len(listings),
        "canonical_row_count": len(listings),
        "distinct_listing_key_count": int(listings["listing_key"].nunique()),
        "segment_count": len(opportunities),
        "release_gate_status": "pass",
    }
    control = pd.DataFrame(
        [
            {
                **shared,
                "output_file": filename,
                "output_row_count": len(frame),
                "output_sha256": _sha256_file(output_dir / filename),
            }
            for filename, frame in tables.items()
        ],
        columns=CONTROL_COLUMNS,
    )
    write_stable_csv(control, output_dir / "build_control.csv", ["output_file"])
    return {**tables, "build_control.csv": control}
