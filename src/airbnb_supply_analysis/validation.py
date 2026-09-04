"""Validaciones sin efectos de escritura para la puerta de publicación."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

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
    processed_directory: Path, powerbi_directory: Path, artifacts_directory: Path
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
        for path in powerbi_directory.glob("*.csv"):
            validate_no_restricted_columns(pd.read_csv(path))
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "processed_files": len(required_processed),
        "powerbi_files": len(EXPECTED_POWERBI_FILES),
        "executed_notebooks": 3,
    }


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
