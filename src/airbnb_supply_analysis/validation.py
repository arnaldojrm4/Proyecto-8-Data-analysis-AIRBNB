"""Validaciones sin efectos de escritura para la puerta de publicación."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import pandas as pd

from airbnb_supply_analysis.config import SCHEMA_VERSION
from airbnb_supply_analysis.exports import (
    CITY_COLUMNS,
    CONTROL_COLUMNS,
    LISTING_COLUMNS,
    NEIGHBORHOOD_COLUMNS,
    OPPORTUNITY_COLUMNS,
    QUALITY_COLUMNS,
    ROOM_TYPE_COLUMNS,
    STATISTICAL_COLUMNS,
)
from airbnb_supply_analysis.schemas import EXPECTED_POWERBI_FILES, validate_no_restricted_columns

EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^]]+\]\(([^)]+)\)")
UNSUPPORTED_CLAIMS = (
    "demuestra demanda",
    "demanda insatisfecha",
    "garantiza reservas",
    "garantiza ocupación",
    "garantiza rentabilidad",
)

POWERBI_COLUMN_CONTRACT = {
    "dim_city.csv": CITY_COLUMNS,
    "dim_neighborhood.csv": NEIGHBORHOOD_COLUMNS,
    "dim_room_type.csv": ROOM_TYPE_COLUMNS,
    "fact_listings.csv": LISTING_COLUMNS,
    "fact_opportunity_segments.csv": OPPORTUNITY_COLUMNS,
    "fact_statistical_results.csv": STATISTICAL_COLUMNS,
    "fact_quality_summary.csv": QUALITY_COLUMNS,
    "build_control.csv": CONTROL_COLUMNS,
}

POWERBI_PRIMARY_KEYS = {
    "dim_city.csv": ["city_key"],
    "dim_neighborhood.csv": ["neighborhood_key"],
    "dim_room_type.csv": ["room_type_key"],
    "fact_listings.csv": ["listing_key"],
    "fact_opportunity_segments.csv": ["segment_key"],
    "fact_statistical_results.csv": ["result_id"],
    "fact_quality_summary.csv": ["build_id", "source_id", "quality_metric", "field"],
    "build_control.csv": ["build_id", "output_file"],
}


class DocumentationContractError(ValueError):
    """Indica que la documentación publicada incumple sus guardarraíles."""


def validate_documentation_tree(root: Path) -> dict[str, Any]:
    """Comprueba enlaces locales, PII y afirmaciones no respaldadas en documentación pública."""
    files = _documentation_files(root)
    broken_links: list[str] = []
    unsupported_claims: list[str] = []
    pii_findings: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        for target in MARKDOWN_LINK_PATTERN.findall(text):
            target_path = path.parent / target.split("#", maxsplit=1)[0]
            if _is_local_link(target) and not target_path.exists():
                broken_links.append(f"{relative}: {target}")
        if EMAIL_PATTERN.search(text):
            pii_findings.append(str(relative))
        lowered = text.casefold()
        unsupported_claims.extend(
            f"{relative}: {claim}"
            for claim in UNSUPPORTED_CLAIMS
            if claim in lowered
        )

    report = {
        "checked_files": len(files),
        "broken_local_links": broken_links,
        "unsupported_claims": unsupported_claims,
        "pii_findings": pii_findings,
    }
    if broken_links:
        raise DocumentationContractError(f"enlace local inválido: {broken_links[0]}")
    if pii_findings:
        raise DocumentationContractError(
            f"Dato personal identificable en documentación: {pii_findings[0]}"
        )
    if unsupported_claims:
        raise DocumentationContractError(
            f"Afirmación no sustentada en documentación: {unsupported_claims[0]}"
        )
    return report


def validate_release_artifacts(
    processed_directory: Path,
    powerbi_directory: Path,
    artifacts_directory: Path,
    *,
    source_manifest_path: Path | None = None,
    analysis_config_path: Path | None = None,
) -> dict[str, Any]:
    """Valida la evidencia mínima creada por el flujo sin volver a calcularla."""
    required_processed = {
        "listings.parquet",
        "statistical_results.parquet",
        "opportunity_segments.parquet",
    }
    missing_processed = sorted(
        filename
        for filename in required_processed
        if not (processed_directory / filename).is_file()
    )
    reconciliation_path = artifacts_directory / "quality" / "row-reconciliation.json"
    missing_notebooks = sorted(
        filename
        for filename in ("01_data_audit.ipynb", "02_etl.ipynb", "03_executive_eda.ipynb")
        if not (artifacts_directory / "executed_notebooks" / filename).is_file()
    )
    missing_exports = sorted(
        filename
        for filename in EXPECTED_POWERBI_FILES
        if not (powerbi_directory / filename).is_file()
    )
    errors = [
        *(f"Falta salida procesada: {filename}" for filename in missing_processed),
        *(f"Falta notebook ejecutado: {filename}" for filename in missing_notebooks),
        *(f"Falta exportación Power BI: {filename}" for filename in missing_exports),
    ]
    if not reconciliation_path.is_file():
        errors.append("Falta evidencia de conciliación.")
    else:
        reconciliation = _read_json(reconciliation_path)
        if reconciliation.get("release_gate_status") != "pass":
            errors.append("La conciliación no aprobó la puerta de publicación.")

    if not missing_exports:
        validate_powerbi_exports(
            powerbi_directory,
            processed_directory,
            source_manifest_path=source_manifest_path,
            analysis_config_path=analysis_config_path,
        )
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "processed_files": len(required_processed),
        "powerbi_files": len(EXPECTED_POWERBI_FILES),
        "executed_notebooks": 3,
    }


def validate_powerbi_exports(
    powerbi_directory: Path,
    processed_directory: Path,
    *,
    source_manifest_path: Path | None = None,
    analysis_config_path: Path | None = None,
) -> dict[str, Any]:
    """Valida el modelo estrella y su control antes de permitir su publicación."""

    actual_files = {path.name for path in powerbi_directory.glob("*.csv")}
    if actual_files != EXPECTED_POWERBI_FILES:
        missing = sorted(EXPECTED_POWERBI_FILES - actual_files)
        unexpected = sorted(actual_files - EXPECTED_POWERBI_FILES)
        raise ValueError(
            f"Conjunto Power BI incorrecto; faltan={missing}, inesperados={unexpected}"
        )

    tables = {
        filename: pd.read_csv(powerbi_directory / filename, keep_default_na=False)
        for filename in EXPECTED_POWERBI_FILES
    }
    for filename, frame in tables.items():
        expected_columns = POWERBI_COLUMN_CONTRACT[filename]
        if frame.columns.tolist() != expected_columns:
            raise ValueError(f"Esquema Power BI incompatible en {filename}")
        validate_no_restricted_columns(frame)
        keys = POWERBI_PRIMARY_KEYS[filename]
        if frame[keys].astype("string").eq("").any().any():
            raise ValueError(f"Clave nula en {filename}")
        if frame.duplicated(keys).any():
            raise ValueError(f"Clave duplicada en {filename}")
        expected_order = frame.sort_values(keys, kind="stable").reset_index(drop=True)
        if not frame.reset_index(drop=True).equals(expected_order):
            raise ValueError(f"Orden inestable en {filename}")

    _validate_powerbi_relationships(tables)
    _validate_powerbi_privacy(tables)
    _validate_powerbi_control(
        tables,
        powerbi_directory,
        processed_directory,
        source_manifest_path,
        analysis_config_path,
    )
    return {
        "powerbi_files": len(tables),
        "validated_rows": sum(len(frame) for frame in tables.values()),
        "release_gate_status": "pass",
    }


def _validate_powerbi_relationships(tables: dict[str, pd.DataFrame]) -> None:
    relationships = (
        ("dim_neighborhood.csv", "city_key", "dim_city.csv", "city_key"),
        ("fact_listings.csv", "city_key", "dim_city.csv", "city_key"),
        (
            "fact_listings.csv",
            "neighborhood_key",
            "dim_neighborhood.csv",
            "neighborhood_key",
        ),
        ("fact_listings.csv", "room_type_key", "dim_room_type.csv", "room_type_key"),
        ("fact_opportunity_segments.csv", "city_key", "dim_city.csv", "city_key"),
        (
            "fact_opportunity_segments.csv",
            "neighborhood_key",
            "dim_neighborhood.csv",
            "neighborhood_key",
        ),
        (
            "fact_opportunity_segments.csv",
            "room_type_key",
            "dim_room_type.csv",
            "room_type_key",
        ),
    )
    for child_name, foreign_key, parent_name, primary_key in relationships:
        child_values = set(tables[child_name][foreign_key])
        parent_values = set(tables[parent_name][primary_key])
        if not child_values.issubset(parent_values):
            raise ValueError(f"Relación huérfana: {child_name}.{foreign_key}")

    statistical_segments = set(
        tables["fact_statistical_results.csv"].loc[
            lambda frame: frame["segment_key"].ne(""), "segment_key"
        ]
    )
    opportunity_segments = set(tables["fact_opportunity_segments.csv"]["segment_key"])
    if not statistical_segments.issubset(opportunity_segments):
        raise ValueError("Relación huérfana: fact_statistical_results.csv.segment_key")


def _validate_powerbi_privacy(tables: dict[str, pd.DataFrame]) -> None:
    listing_keys = tables["fact_listings.csv"]["listing_key"].astype(str)
    if not listing_keys.str.fullmatch(r"listing_[0-9a-f]{64}").all():
        raise ValueError("listing_key no cumple el contrato de seudonimización")
    room_type_keys = tables["dim_room_type.csv"]["room_type_key"].astype(str)
    if not room_type_keys.str.fullmatch(r"room_type_[0-9a-f]{64}").all():
        raise ValueError("room_type_key no cumple el contrato de clave sustituta")


def _validate_powerbi_control(
    tables: dict[str, pd.DataFrame],
    powerbi_directory: Path,
    processed_directory: Path,
    source_manifest_path: Path | None,
    analysis_config_path: Path | None,
) -> None:
    control = tables["build_control.csv"]
    output_files = EXPECTED_POWERBI_FILES - {"build_control.csv"}
    if set(control["output_file"]) != output_files:
        raise ValueError("build_control.csv no declara exactamente todas las salidas")
    if control["build_id"].nunique() != 1:
        raise ValueError("build_id inconsistente en build_control.csv")
    build_id = str(control["build_id"].iat[0])
    for filename in (
        "fact_opportunity_segments.csv",
        "fact_statistical_results.csv",
        "fact_quality_summary.csv",
    ):
        if not tables[filename]["build_id"].astype(str).eq(build_id).all():
            raise ValueError(f"build_id inconsistente en {filename}")
    if control["schema_version"].astype(str).str.split(".").str[0].nunique() != 1:
        raise ValueError("Versiones de esquema inconsistentes en build_control.csv")
    actual_major = str(control["schema_version"].iat[0]).split(".", maxsplit=1)[0]
    expected_major = SCHEMA_VERSION.split(".", maxsplit=1)[0]
    if actual_major != expected_major:
        raise ValueError("Versión mayor Power BI incompatible")
    if not control["release_gate_status"].eq("pass").all():
        raise ValueError("La puerta Power BI no está aprobada")

    for row in control.itertuples(index=False):
        path = powerbi_directory / row.output_file
        if int(row.output_row_count) != len(tables[row.output_file]):
            raise ValueError(f"Conteo de filas incorrecto en {row.output_file}")
        if row.output_sha256 != _sha256(path):
            raise ValueError(f"Hash de salida incorrecto en {row.output_file}")

    listings = pd.read_parquet(processed_directory / "listings.parquet", columns=["listing_key"])
    opportunities = pd.read_parquet(
        processed_directory / "opportunity_segments.parquet", columns=["segment_key"]
    )
    expected_counts = {
        "canonical_row_count": len(listings),
        "distinct_listing_key_count": int(listings["listing_key"].nunique()),
        "segment_count": len(opportunities),
    }
    for field, expected in expected_counts.items():
        if not control[field].eq(expected).all():
            raise ValueError(f"Conteo de control incorrecto: {field}")
    if source_manifest_path is not None:
        manifest = _read_json(source_manifest_path)
        sources = manifest.get("sources", [])
        source_counts = {
            "source_file_count": len(sources),
            "source_row_count": sum(int(source["parsed_row_count"]) for source in sources),
        }
        for field, expected in source_counts.items():
            if not control[field].eq(expected).all():
                raise ValueError(f"Conteo de control incorrecto: {field}")
    for field, path in (
        ("source_manifest_hash", source_manifest_path),
        ("analysis_config_hash", analysis_config_path),
    ):
        if path is not None and not control[field].eq(_sha256(path)).all():
            raise ValueError(f"Hash de entrada incorrecto: {field}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _documentation_files(root: Path) -> list[Path]:
    roots = [root / "README.md", root / "docs"]
    return sorted(
        path
        for documentation_root in roots
        if documentation_root.exists()
        for path in (
            [documentation_root]
            if documentation_root.is_file()
            else documentation_root.rglob("*.md")
        )
    )


def _is_local_link(target: str) -> bool:
    return bool(target) and not target.startswith(("#", "http://", "https://", "mailto:"))


def _read_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))
