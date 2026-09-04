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
