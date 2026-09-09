"""Contrato versionable del modelo semántico y del informe Power BI."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
POWERBI_ROOT = PROJECT_ROOT / "powerbi"
MODEL_DEFINITION = POWERBI_ROOT / "AirbnbSupplyOpportunity.SemanticModel" / "definition"
REPORT_DEFINITION = POWERBI_ROOT / "AirbnbSupplyOpportunity.Report" / "definition"
EXPECTED_PAGES = [
    "Estructura del mercado",
    "Resumen ejecutivo",
    "Oportunidades de captación",
    "Detalle y confianza",
]
EXPECTED_MEASURES = {
    "Anuncios analizables",
    "Segmentos candidatos",
    "Cuota activa histórica",
    "Actividad histórica mediana",
    "Actividad por anuncio",
    "Cobertura de actividad",
    "Cuota de anuncios en carteras >5",
    "Precio local mediano",
    "Cuota de oferta",
    "Efecto de actividad",
    "Estado de evidencia",
    "Diferencia de conciliación",
}


def test_market_structure_columns_are_imported_without_host_identifiers() -> None:
    listing_model = (MODEL_DEFINITION / "tables" / "Fact Listings.tmdl").read_text(
        encoding="utf-8"
    )
    assert "column portfolio_size" in listing_model
    assert "column portfolio_bucket" in listing_model
    assert "sourceColumn: portfolio_size" in listing_model
    assert "host_id" not in listing_model


def _tmdl_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(MODEL_DEFINITION.rglob("*.tmdl"))
    )


def test_pbip_project_contains_local_model_and_report() -> None:
    project = json.loads(
        (POWERBI_ROOT / "AirbnbSupplyOpportunity.pbip").read_text(encoding="utf-8")
    )
    assert project["version"] == "1.0"
    assert project["artifacts"][0]["report"]["path"] == "AirbnbSupplyOpportunity.Report"
    assert (MODEL_DEFINITION.parent / "definition.pbism").is_file()
    assert (REPORT_DEFINITION.parent / "definition.pbir").is_file()


def test_model_uses_one_required_dataroot_parameter_and_release_gate() -> None:
    tmdl = _tmdl_text()
    assert tmdl.count("expression DataRoot") == 1
    assert "IsParameterQueryRequired=true" in tmdl
    assert "release_gate_status" in tmdl
    assert "schema_version" in tmdl
    assert "Release bloqueada" in tmdl
    assert not re.search(r"(?:C:\\\\Users|/home/|/Users/)", tmdl, flags=re.IGNORECASE)


def test_model_has_expected_explicit_measures_and_tooltip_descriptions() -> None:
    tmdl = _tmdl_text()
    for measure in EXPECTED_MEASURES:
        assert f"measure '{measure}'" in tmdl
    assert "Población:" in tmdl
    assert "Denominador:" in tmdl
    assert "Limitación:" in tmdl


def test_relationships_are_one_to_many_and_unidirectional() -> None:
    relationships = (MODEL_DEFINITION / "relationships.tmdl").read_text(encoding="utf-8")
    assert relationships.count("relationship ") >= 8
    assert "crossFilteringBehavior: bothDirections" not in relationships
    assert "fromCardinality: one" not in relationships


def test_report_has_expected_decision_first_pages() -> None:
    pages_index = json.loads(
        (REPORT_DEFINITION / "pages" / "pages.json").read_text(encoding="utf-8")
    )
    pages = []
    for page_name in pages_index["pageOrder"]:
        page = json.loads(
            (REPORT_DEFINITION / "pages" / page_name / "page.json").read_text(
                encoding="utf-8"
            )
        )
        pages.append(page["displayName"])
    assert pages == EXPECTED_PAGES
    assert pages_index["activePageName"] == pages_index["pageOrder"][0]


def test_visuals_have_reading_order_and_spanish_alt_text() -> None:
    visual_paths = sorted((REPORT_DEFINITION / "pages").rglob("visual.json"))
    assert visual_paths
    for path in visual_paths:
        visual = json.loads(path.read_text(encoding="utf-8"))
        assert visual["position"]["tabOrder"] >= 0
        serialized = json.dumps(visual, ensure_ascii=False)
        assert "altText" in serialized or visual.get("visualGroup") is not None


def test_binary_delivery_files_are_real_powerbi_packages() -> None:
    for filename in ("airbnb-supply-opportunity.pbix", "airbnb-supply-opportunity.pbit"):
        path = POWERBI_ROOT / filename
        assert path.stat().st_size > 10_000
        assert path.read_bytes()[:2] == b"PK"


def test_pbit_is_data_free_and_keeps_required_dataroot_parameter() -> None:
    template = POWERBI_ROOT / "airbnb-supply-opportunity.pbit"
    with zipfile.ZipFile(template) as package:
        names = set(package.namelist())
        assert "DataModelSchema" in names
        assert "DataMashup" not in names
        model_schema = package.read("DataModelSchema").decode("utf-16")
    assert "DataRoot" in model_schema
    assert "IsParameterQueryRequired" in model_schema
