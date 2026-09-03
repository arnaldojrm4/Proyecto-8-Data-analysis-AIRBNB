from __future__ import annotations

import runpy


def test_generated_code_cells_remove_template_indentation(project_root) -> None:
    namespace = runpy.run_path(project_root / "scripts/generate_notebooks.py")

    cell = namespace["code"]("""
        value = 1
        value
    """)

    assert cell.source.startswith("value = 1")
    assert "\nvalue" in cell.source
