from __future__ import annotations

import importlib
from pathlib import Path

import nbformat
import pytest

EXPECTED_ORDER = (
    "01_data_audit.ipynb",
    "02_etl.ipynb",
    "03_executive_eda.ipynb",
)


def test_notebook_runner_uses_contract_order_and_separate_executions(
    project_root: Path, tmp_path: Path, monkeypatch
) -> None:
    notebooks = importlib.import_module("airbnb_supply_analysis.notebooks")
    calls: list[tuple[str, str]] = []

    def fake_execute(source: Path, destination: Path, timeout: int = 600) -> None:
        del timeout
        calls.append((source.name, destination.name))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("executed", encoding="utf-8")

    monkeypatch.setattr(notebooks, "execute_notebook", fake_execute)
    outputs = notebooks.execute_notebooks(project_root / "notebooks", tmp_path)

    assert tuple(source for source, _ in calls) == EXPECTED_ORDER
    assert tuple(path.name for path in outputs) == EXPECTED_ORDER
    assert len(calls) == 3


def test_notebook_runner_rejects_a_missing_contract_notebook(
    tmp_path: Path, monkeypatch
) -> None:
    notebooks = importlib.import_module("airbnb_supply_analysis.notebooks")
    nbformat.write(nbformat.v4.new_notebook(cells=[]), tmp_path / "01_data_audit.ipynb")
    monkeypatch.setattr(notebooks, "execute_notebook", lambda *args, **kwargs: None)

    with pytest.raises(FileNotFoundError, match="02_etl.ipynb"):
        notebooks.execute_notebooks(tmp_path, tmp_path / "executed")


def test_each_notebook_execution_creates_a_fresh_client(tmp_path: Path, monkeypatch) -> None:
    notebooks = importlib.import_module("airbnb_supply_analysis.notebooks")
    clients: list[object] = []

    class FakeClient:
        def __init__(self, notebook, **options) -> None:
            self.notebook = notebook
            self.options = options
            clients.append(self)

        def execute(self):
            return self.notebook

    monkeypatch.setattr(notebooks, "NotebookClient", FakeClient)
    source = tmp_path / "source.ipynb"
    nbformat.write(nbformat.v4.new_notebook(cells=[]), source)

    notebooks.execute_notebook(source, tmp_path / "first.ipynb")
    notebooks.execute_notebook(source, tmp_path / "second.ipynb")

    assert len(clients) == 2
    assert clients[0] is not clients[1]
    assert all(client.options["kernel_name"] == "python3" for client in clients)


def test_notebook_sources_meet_markdown_and_conclusion_contract(project_root: Path) -> None:
    notebooks = importlib.import_module("airbnb_supply_analysis.notebooks")

    for filename in EXPECTED_ORDER:
        issues = notebooks.validate_notebook_narrative(project_root / "notebooks" / filename)
        assert issues == [], f"{filename}: {issues}"


def test_notebook_narrative_reports_missing_required_blocks(tmp_path: Path) -> None:
    notebooks = importlib.import_module("airbnb_supply_analysis.notebooks")
    source = tmp_path / "incomplete.ipynb"
    notebook = nbformat.v4.new_notebook(
        cells=[nbformat.v4.new_markdown_cell("# Informe\n\n## tl;dr\n\nResumen.")]
    )
    nbformat.write(notebook, source)

    issues = notebooks.validate_notebook_narrative(source)

    assert "Falta el bloque Markdown de contexto y métodos." in issues
    assert "Falta al menos una conclusión explícita." in issues
    assert "Falta el cierre Markdown 'Takeaways'." in issues
