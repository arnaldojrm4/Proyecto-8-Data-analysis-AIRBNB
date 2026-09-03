"""Configuración, rutas seguras y logging del pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "1.0.0"


class ConfigurationError(ValueError):
    """Configuración inválida o ruta fuera del proyecto."""


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    raw: Path
    processed: Path
    powerbi: Path
    artifacts: Path


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        payload = yaml.safe_load(stream) or {}
    if not isinstance(payload, dict):
        raise ConfigurationError(f"Se esperaba un objeto YAML en {path}")
    return payload


def resolve_below(root: Path, value: str | Path) -> Path:
    """Resuelve una ruta y rechaza escapes fuera de ``root``."""

    root = root.resolve()
    candidate = (root / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    if candidate != root and root not in candidate.parents:
        raise ConfigurationError(f"Ruta fuera de la raíz permitida: {candidate}")
    return candidate


def project_paths(root: Path, config: dict[str, Any]) -> ProjectPaths:
    configured = config.get("paths", {})
    return ProjectPaths(
        root=root.resolve(),
        raw=resolve_below(root, configured.get("raw", "data/raw")),
        processed=resolve_below(root, configured.get("processed", "data/processed")),
        powerbi=resolve_below(root, configured.get("powerbi", "data/powerbi")),
        artifacts=resolve_below(root, configured.get("artifacts", "artifacts")),
    )


def configure_logging(json_mode: bool = False) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s" if not json_mode else "%(message)s",
        force=True,
    )
