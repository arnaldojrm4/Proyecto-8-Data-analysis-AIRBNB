from __future__ import annotations

import runpy

import nbformat


def test_generated_code_cells_remove_template_indentation(project_root) -> None:
    namespace = runpy.run_path(project_root / "scripts/generate_notebooks.py")

    cell = namespace["code"]("""
        value = 1
        value
    """)

    assert cell.source.startswith("value = 1")
    assert "\nvalue" in cell.source


def test_generated_notebooks_read_pipeline_output_directories(project_root, tmp_path) -> None:
    namespace = runpy.run_path(project_root / "scripts/generate_notebooks.py")
    namespace["write_notebook"].__globals__["NOTEBOOKS"] = tmp_path

    for factory in ("audit_notebook", "etl_notebook", "executive_eda_notebook"):
        namespace[factory]()

    sources = "\n".join(
        str(cell.source)
        for path in sorted(tmp_path.glob("*.ipynb"))
        for cell in nbformat.read(path, as_version=4).cells
        if cell.cell_type == "code"
    )
    assert "AIRBNB_SUPPLY_ARTIFACTS_DIR" in sources
    assert "AIRBNB_SUPPLY_PROCESSED_DIR" in sources


def test_find_project_root_works_from_workspace_and_notebook_directory(project_root) -> None:
    namespace = runpy.run_path(project_root / "scripts/generate_notebooks.py")

    assert namespace["find_project_root"](project_root) == project_root
    assert namespace["find_project_root"](project_root / "notebooks") == project_root


def test_generated_notebook_code_cells_compile(project_root, tmp_path) -> None:
    namespace = runpy.run_path(project_root / "scripts/generate_notebooks.py")
    namespace["write_notebook"].__globals__["NOTEBOOKS"] = tmp_path

    for factory in ("audit_notebook", "etl_notebook", "executive_eda_notebook"):
        namespace[factory]()

    for path in sorted(tmp_path.glob("*.ipynb")):
        for cell in nbformat.read(path, as_version=4).cells:
            if cell.cell_type == "code":
                compile(cell.source, path.name, "exec")


def test_regeneration_preserves_versioned_notebook_content(project_root, tmp_path) -> None:
    """Regeneration must retain reviewed conclusions and geographic exploration."""
    namespace = runpy.run_path(project_root / "scripts/generate_notebooks.py")
    namespace["write_notebook"].__globals__["NOTEBOOKS"] = tmp_path
    for factory in ("audit_notebook", "etl_notebook", "executive_eda_notebook"):
        namespace[factory]()
    for generated in sorted(tmp_path.glob("*.ipynb")):
        expected = nbformat.read(project_root / "notebooks" / generated.name, as_version=4)
        actual = nbformat.read(generated, as_version=4)
        assert [(c.cell_type, c.source) for c in actual.cells] == [
            (c.cell_type, c.source) for c in expected.cells
        ], generated.name
