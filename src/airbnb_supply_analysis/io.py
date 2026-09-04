"""Entrada/salida determinista y trazabilidad de fuentes."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def csv_shape(path: Path, encoding: str = "utf-8") -> tuple[list[str], int]:
    with path.open("r", encoding=encoding, newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        row_count = sum(1 for _ in reader)
    return header, row_count


def atomic_write_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temp_name, path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"Se esperaba un objeto JSON en {path}")
    return payload


def inventory_sources(raw_dir: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Verifica que cada fuente coincide exactamente con el manifiesto aprobado."""

    observed: list[dict[str, Any]] = []
    for expected in manifest.get("sources", []):
        path = (raw_dir / expected["relative_path"]).resolve()
        if raw_dir.resolve() not in path.parents:
            raise ValueError(f"Ruta raw fuera del directorio permitido: {path}")
        if not path.is_file():
            raise ValueError(f"Fuente ausente: {expected['file_name']}")
        header, rows = csv_shape(path, expected.get("encoding", "utf-8"))
        actual_hash = sha256_file(path)
        checks = {
            "SHA-256": actual_hash == expected["sha256"],
            "bytes": path.stat().st_size == expected["byte_size"],
            "filas": rows == expected["parsed_row_count"],
            "cabecera": header == expected["column_names"],
            "nombre": path.name == expected["file_name"],
        }
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            raise ValueError(
                f"Contrato de {expected['file_name']} incumplido: {', '.join(failed)}"
            )
        observed.append(
            {
                "source_id": expected["source_id"],
                "city_key": expected.get("city_key"),
                "file_name": path.name,
                "sha256": actual_hash,
                "byte_size": path.stat().st_size,
                "parsed_row_count": rows,
                "column_names": header,
                "encoding": expected.get("encoding", "utf-8"),
                "delimiter": expected.get("delimiter", ","),
                "identity_status": "identity_verified",
            }
        )
    return observed


def read_source(raw_dir: Path, source: dict[str, Any]) -> pd.DataFrame:
    path = raw_dir / source["relative_path"]
    return pd.read_csv(
        path,
        encoding=source.get("encoding", "utf-8"),
        sep=source.get("delimiter", ","),
        low_memory=False,
    )
