"""Contrato de las rutas principales de presentación del proyecto."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_readme_promotes_market_structure_eda_and_interactive_outputs() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Entrega principal" in readme
    assert "notebooks/04_market_structure_eda.ipynb" in readme
    assert "output/04_market_structure_eda.html" in readme
    assert "powerbi/AirbnbSupplyOpportunity.pbip" in readme
    assert "dashboard/app.py" in readme
    assert "## Material de soporte y análisis anteriores" in readme
