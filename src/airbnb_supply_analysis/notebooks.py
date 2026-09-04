"""Ejecución reproducible de notebooks en kernels limpios."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient

NOTEBOOK_ORDER = (
    "01_data_audit.ipynb",
    "02_etl.ipynb",
    "03_executive_eda.ipynb",
)


def execute_notebook(source: Path, destination: Path, timeout: int = 600) -> None:
    notebook = nbformat.read(source, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(source.parent)}},
    )
    client.execute()
    destination.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, destination)
