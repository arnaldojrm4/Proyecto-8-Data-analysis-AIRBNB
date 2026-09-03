"""Publicación estable y atómica de artefactos tabulares."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd


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
