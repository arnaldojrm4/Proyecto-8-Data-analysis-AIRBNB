"""Carga y validación del conjunto público consumido por el panel."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from airbnb_supply_analysis.schemas import EXPECTED_POWERBI_FILES

SUPPORTED_SCHEMA_MAJOR = "1"

TABLE_FILES = {
    "cities": "dim_city.csv",
    "neighborhoods": "dim_neighborhood.csv",
    "room_types": "dim_room_type.csv",
    "listings": "fact_listings.csv",
    "opportunities": "fact_opportunity_segments.csv",
    "statistics": "fact_statistical_results.csv",
    "quality": "fact_quality_summary.csv",
    "control": "build_control.csv",
}

REQUIRED_COLUMNS = {
    "cities": {"city_key", "city_label_es"},
    "neighborhoods": {"neighborhood_key", "neighborhood_label"},
    "room_types": {"room_type_key", "room_type_label_es"},
    "listings": {
        "city_key", "neighborhood_key", "room_type_key", "activity_proxy", "price"
    },
    "opportunities": {
        "build_id", "segment_key", "city_key", "neighborhood_key", "room_type_key",
        "listing_count", "activity_median", "price_median", "sensitivity_status",
        "opportunity_label", "candidate_rank",
    },
    "statistics": {
        "build_id", "analysis_family", "city_key", "segment_key", "comparison", "method",
        "sample_size", "estimate", "effect_type", "ci_low", "ci_high", "p_value_adjusted",
        "sensitivity_status",
    },
    "quality": {"build_id"},
    "control": {
        "build_id", "schema_version", "generated_at_utc", "release_gate_status",
        "output_file", "output_row_count",
    },
}


class DashboardDataError(ValueError):
    """Error publicable y estable al abrir un build del panel."""

    def __init__(self, code: str, artifact: str, detail: str) -> None:
        self.code = code
        self.artifact = artifact
        self.detail = detail
        super().__init__(f"{code}: {artifact}: {detail}")


@dataclass(frozen=True)
class BuildMetadata:
    """Identidad inmutable de la publicación activa."""

    build_id: str
    schema_version: str
    generated_at_utc: str
    release_gate_status: str


@dataclass(frozen=True)
class DashboardDataset:
    """Tablas validadas que alimentan las vistas."""

    build: BuildMetadata
    cities: pd.DataFrame
    neighborhoods: pd.DataFrame
    room_types: pd.DataFrame
    listings: pd.DataFrame
    opportunities: pd.DataFrame
    statistics: pd.DataFrame
    quality: pd.DataFrame
    control: pd.DataFrame


def _fail(code: str, artifact: str, detail: str) -> None:
    raise DashboardDataError(code, artifact, detail)


def _read_tables(directory: Path) -> dict[str, pd.DataFrame]:
    for filename in sorted(EXPECTED_POWERBI_FILES):
        if not (directory / filename).is_file():
            _fail("missing_file", filename, "No existe la exportación obligatoria.")
    return {
        name: pd.read_csv(directory / filename)
        for name, filename in TABLE_FILES.items()
    }


def _validate_required_columns(tables: dict[str, pd.DataFrame]) -> None:
    for name, required in REQUIRED_COLUMNS.items():
        missing = required.difference(tables[name].columns)
        if missing:
            _fail(
                "unsupported_schema",
                TABLE_FILES[name],
                f"Faltan columnas consumidas: {sorted(missing)}",
            )


def _build_metadata(control: pd.DataFrame) -> BuildMetadata:
    required = {"build_id", "schema_version", "generated_at_utc", "release_gate_status"}
    missing = required.difference(control.columns)
    if missing:
        _fail("unsupported_schema", "build_control.csv", f"Faltan columnas: {sorted(missing)}")
    build_ids = control["build_id"].dropna().astype(str).unique()
    if len(build_ids) != 1:
        _fail("mixed_build", "build_control.csv", "Contiene más de una identidad de build.")
    versions = control["schema_version"].dropna().astype(str).unique()
    if len(versions) != 1 or versions[0].split(".", maxsplit=1)[0] != SUPPORTED_SCHEMA_MAJOR:
        _fail("unsupported_schema", "build_control.csv", "La versión mayor no es compatible.")
    statuses = control["release_gate_status"].dropna().astype(str).unique()
    if len(statuses) != 1 or statuses[0] != "pass":
        _fail("release_gate_failed", "build_control.csv", "El build no está aprobado.")
    generated = control["generated_at_utc"].dropna().astype(str).unique()
    return BuildMetadata(
        build_id=build_ids[0],
        schema_version=versions[0],
        generated_at_utc=generated[0] if len(generated) == 1 else "desconocida",
        release_gate_status=statuses[0],
    )


def _validate_row_counts(tables: dict[str, pd.DataFrame]) -> None:
    control = tables["control"]
    required = {"output_file", "output_row_count"}
    if not required.issubset(control.columns):
        _fail("unsupported_schema", "build_control.csv", "Falta el contrato de recuentos.")
    for row in control[["output_file", "output_row_count"]].itertuples(index=False):
        matches = [name for name, filename in TABLE_FILES.items() if filename == row.output_file]
        if not matches:
            continue
        actual = len(tables[matches[0]])
        if actual != int(row.output_row_count):
            detail = f"Esperadas {row.output_row_count}; leídas {actual}."
            _fail("row_count_mismatch", str(row.output_file), detail)


def _validate_unique(frame: pd.DataFrame, key: str, filename: str) -> None:
    if key not in frame or frame[key].isna().any() or frame[key].duplicated().any():
        _fail("duplicate_dimension_key", filename, f"La clave {key} no es única y completa.")


def _validate_relation(
    fact: pd.DataFrame,
    dimension: pd.DataFrame,
    key: str,
    filename: str,
    *,
    nullable: bool = False,
) -> None:
    if key not in fact or key not in dimension:
        _fail("unsupported_schema", filename, f"Falta la relación {key}.")
    values = fact[key].dropna() if nullable else fact[key]
    if not nullable and values.isna().any():
        _fail("orphan_dimension_key", filename, f"La relación {key} contiene nulos.")
    if not set(values.astype(str)).issubset(set(dimension[key].astype(str))):
        _fail("orphan_dimension_key", filename, f"La relación {key} contiene claves huérfanas.")


def _validate_build_columns(tables: dict[str, pd.DataFrame], build_id: str) -> None:
    for name in ("opportunities", "statistics", "quality"):
        frame = tables[name]
        if "build_id" not in frame:
            _fail("unsupported_schema", TABLE_FILES[name], "Falta build_id.")
        values = set(frame["build_id"].dropna().astype(str))
        if values != {build_id}:
            _fail("mixed_build", TABLE_FILES[name], "No coincide con el build activo.")


def _validate_dimensions(tables: dict[str, pd.DataFrame]) -> None:
    dimensions = (
        ("cities", "city_key"),
        ("neighborhoods", "neighborhood_key"),
        ("room_types", "room_type_key"),
    )
    for name, key in dimensions:
        _validate_unique(tables[name], key, TABLE_FILES[name])
    for fact_name in ("listings", "opportunities"):
        for dimension_name, key in dimensions:
            _validate_relation(
                tables[fact_name],
                tables[dimension_name],
                key,
                TABLE_FILES[fact_name],
            )
    _validate_relation(
        tables["statistics"],
        tables["cities"],
        "city_key",
        TABLE_FILES["statistics"],
        nullable=True,
    )
    _validate_relation(
        tables["statistics"],
        tables["opportunities"],
        "segment_key",
        TABLE_FILES["statistics"],
        nullable=True,
    )


def load_dashboard_dataset(directory: str | Path) -> DashboardDataset:
    """Lee un build aprobado y falla antes de devolver datos inconsistentes."""

    root = Path(directory)
    tables = _read_tables(root)
    _validate_required_columns(tables)
    build = _build_metadata(tables["control"])
    _validate_row_counts(tables)
    _validate_build_columns(tables, build.build_id)
    _validate_dimensions(tables)
    return DashboardDataset(build=build, **tables)
