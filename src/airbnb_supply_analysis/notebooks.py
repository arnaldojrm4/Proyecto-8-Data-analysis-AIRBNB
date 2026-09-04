"""Ejecución reproducible de notebooks en kernels limpios."""

from __future__ import annotations

import unicodedata
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


def execute_notebooks(
    source_directory: Path, output_directory: Path, timeout: int = 600
) -> list[Path]:
    """Ejecuta los notebooks contractuales en orden y en kernels separados."""
    outputs: list[Path] = []
    for filename in NOTEBOOK_ORDER:
        source = source_directory / filename
        if not source.is_file():
            raise FileNotFoundError(f"No se encontró el notebook contractual: {source}")

        destination = output_directory / filename
        execute_notebook(source, destination, timeout=timeout)
        outputs.append(destination)
    return outputs


def validate_notebook_narrative(source: Path) -> list[str]:
    """Devuelve las incidencias del contrato Markdown de un notebook fuente."""
    notebook = nbformat.read(source, as_version=4)
    markdown_sources = [
        str(cell.source).strip()
        for cell in notebook.cells
        if cell.cell_type == "markdown" and str(cell.source).strip()
    ]
    normalized = _normalize_text("\n".join(markdown_sources))
    issues: list[str] = []

    if not markdown_sources or not markdown_sources[0].lstrip().startswith("# "):
        issues.append("Falta un título Markdown inicial.")
    if "tl;dr" not in normalized:
        issues.append("Falta el bloque Markdown 'tl;dr'.")
    if "contexto" not in normalized or "metodos" not in normalized:
        issues.append("Falta el bloque Markdown de contexto y métodos.")
    if "conclusion" not in normalized:
        issues.append("Falta al menos una conclusión explícita.")
    if "takeaways" not in normalized:
        issues.append("Falta el cierre Markdown 'Takeaways'.")
    return issues


def _normalize_text(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(character)
    )
