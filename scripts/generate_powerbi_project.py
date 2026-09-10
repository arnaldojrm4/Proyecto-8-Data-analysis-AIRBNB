"""Genera el proyecto PBIP/PBIR versionable del informe ejecutivo."""

# Las descripciones ejecutivas se mantienen como literales completos para que el
# texto alternativo versionado sea fácil de auditar.
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POWERBI = ROOT / "powerbi"
MODEL = POWERBI / "AirbnbSupplyOpportunity.SemanticModel"
REPORT = POWERBI / "AirbnbSupplyOpportunity.Report"
DEFINITION = REPORT / "definition"
PAGES = DEFINITION / "pages"
THEME_FILE = "AirbnbAccessible-e785ad6.json"
VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
    "visualContainer/2.9.0/schema.json"
)
PAGE_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
    "page/2.1.0/schema.json"
)
PLATFORM_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/"
    "platformProperties/2.0.0/schema.json"
)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def identifier(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:20]


def literal(value: str | bool | int) -> dict[str, Any]:
    if isinstance(value, bool):
        encoded = str(value).lower()
    elif isinstance(value, int):
        encoded = f"{value}D"
    else:
        encoded = f"'{value.replace("'", "''")}'"
    return {"expr": {"Literal": {"Value": encoded}}}


def field(kind: str, table: str, property_name: str) -> dict[str, Any]:
    return {
        kind: {
            "Expression": {"SourceRef": {"Entity": table}},
            "Property": property_name,
        }
    }


def projection(kind: str, table: str, property_name: str) -> dict[str, Any]:
    return {
        "field": field(kind, table, property_name),
        "queryRef": f"{table}.{property_name}",
        "nativeQueryRef": property_name,
    }


def chrome(alt_text: str) -> dict[str, Any]:
    return {
        "general": [{"properties": {"altText": literal(alt_text)}}],
        "visualHeader": [{"properties": {"show": literal(True)}}],
    }


def visual_container(
    page_id: str,
    slug: str,
    x: int,
    y: int,
    width: int,
    height: int,
    tab_order: int,
    visual: dict[str, Any],
) -> dict[str, Any]:
    return {
        "$schema": VISUAL_SCHEMA,
        "name": identifier(page_id, slug),
        "position": {
            "x": x,
            "y": y,
            "z": (tab_order + 1) * 1000,
            "height": height,
            "width": width,
            "tabOrder": tab_order,
        },
        "visual": visual,
    }


def textbox(
    page_id: str,
    slug: str,
    text: str,
    position: tuple[int, int, int, int],
    tab: int,
    *,
    size: int = 12,
    bold: bool = False,
) -> dict[str, Any]:
    x, y, width, height = position
    visual = {
        "visualType": "textbox",
        "objects": {
            "general": [
                {
                    "properties": {
                        "paragraphs": [
                            {
                                "textRuns": [
                                    {
                                        "value": text,
                                        "textStyle": {
                                            "fontFamily": "Segoe UI Semibold"
                                            if bold
                                            else "Segoe UI",
                                            "fontSize": f"{size}px",
                                            "color": "#1A1A1A",
                                        },
                                    }
                                ],
                                "horizontalTextAlignment": "left",
                            }
                        ]
                    }
                }
            ]
        },
        "visualContainerObjects": chrome(text),
    }
    return visual_container(page_id, slug, x, y, width, height, tab, visual)


def card(
    page_id: str,
    slug: str,
    measures: list[str],
    position: tuple[int, int, int, int],
    tab: int,
    alt_text: str,
) -> dict[str, Any]:
    x, y, width, height = position
    visual = {
        "visualType": "cardVisual",
        "query": {
            "queryState": {
                "Data": {
                    "projections": [projection("Measure", "_Measures", item) for item in measures]
                }
            }
        },
        "visualContainerObjects": chrome(alt_text),
    }
    return visual_container(page_id, slug, x, y, width, height, tab, visual)


def slicer(
    page_id: str,
    slug: str,
    table: str,
    column: str,
    label: str,
    group: str,
    position: tuple[int, int, int, int],
    tab: int,
) -> dict[str, Any]:
    x, y, width, height = position
    visual = {
        "visualType": "slicer",
        "syncGroup": {"groupName": group, "fieldChanges": True, "filterChanges": True},
        "query": {"queryState": {"Values": {"projections": [projection("Column", table, column)]}}},
        "objects": {
            "data": [{"properties": {"mode": literal("Dropdown")}}],
            "header": [{"properties": {"show": literal(True), "text": literal(label)}}],
        },
        "visualContainerObjects": {
            **chrome(f"Filtro {label}. Use Alt+Flecha abajo para abrir la lista."),
            "padding": [
                {"properties": {side: literal(8) for side in ("top", "bottom", "left", "right")}}
            ],
        },
    }
    return visual_container(page_id, slug, x, y, width, height, tab, visual)


def table(
    page_id: str,
    slug: str,
    fields: list[tuple[str, str, str]],
    position: tuple[int, int, int, int],
    tab: int,
    alt_text: str,
) -> dict[str, Any]:
    x, y, width, height = position
    visual = {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [projection(kind, entity, prop) for kind, entity, prop in fields]
                }
            }
        },
        "objects": {
            "columnHeaders": [
                {
                    "properties": {
                        "columnAdjustment": literal("growToFit"),
                        "autoSizeColumnWidth": literal(True),
                    }
                }
            ]
        },
        "visualContainerObjects": chrome(alt_text),
    }
    return visual_container(page_id, slug, x, y, width, height, tab, visual)


def chart(
    page_id: str,
    slug: str,
    visual_type: str,
    roles: dict[str, list[tuple[str, str, str]]],
    position: tuple[int, int, int, int],
    tab: int,
    alt_text: str,
) -> dict[str, Any]:
    x, y, width, height = position
    visual = {
        "visualType": visual_type,
        "query": {
            "queryState": {
                role: {
                    "projections": [projection(kind, entity, prop) for kind, entity, prop in items]
                }
                for role, items in roles.items()
            }
        },
        "visualContainerObjects": chrome(alt_text),
    }
    return visual_container(page_id, slug, x, y, width, height, tab, visual)


def navigator(page_id: str, tab: int = 90) -> dict[str, Any]:
    visual = {
        "visualType": "pageNavigator",
        "visualContainerObjects": chrome(
            "Navegación entre Resumen ejecutivo, Estructura del mercado, "
            "Oportunidades de captación y Detalle y confianza."
        ),
    }
    return visual_container(page_id, "navigation", 20, 672, 1020, 40, tab, visual)


def reset_button(page_id: str, tab: int = 89) -> dict[str, Any]:
    """Create an explicit, keyboard-accessible clear-all-slicers control."""
    visual = {
        "visualType": "actionButton",
        "objects": {
            "text": [
                {
                    "properties": {
                        "show": literal(True),
                        "text": literal("Restablecer filtros"),
                    }
                }
            ]
        },
        "visualContainerObjects": {
            **chrome("Restablecer todos los filtros y segmentadores de esta página."),
            "visualLink": [
                {
                    "properties": {
                        "show": literal(True),
                        "type": literal("ClearAllSlicers"),
                        "enabledTooltip": literal("Restablecer filtros"),
                    }
                }
            ],
        },
    }
    return visual_container(page_id, "reset_filters", 1060, 672, 200, 40, tab, visual)


def categorical_filter(name: str, table_name: str, column: str, value: str) -> dict[str, Any]:
    alias = "f"
    return {
        "name": name,
        "field": field("Column", table_name, column),
        "type": "Categorical",
        "filter": {
            "Version": 2,
            "From": [{"Name": alias, "Entity": table_name, "Type": 0}],
            "Where": [
                {
                    "Condition": {
                        "In": {
                            "Expressions": [
                                {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": alias}},
                                        "Property": column,
                                    }
                                }
                            ],
                            "Values": [[{"Literal": {"Value": f"'{value}'"}}]],
                        }
                    }
                }
            ],
        },
        "howCreated": "User",
        "isHiddenInViewMode": True,
        "isLockedInViewMode": True,
    }


def maximum_filter(name: str, table_name: str, column: str, value: int) -> dict[str, Any]:
    """Create a locked visual filter equivalent to ``column <= value``."""
    alias = "f"
    return {
        "name": name,
        "field": field("Column", table_name, column),
        "type": "Advanced",
        "filter": {
            "Version": 2,
            "From": [{"Name": alias, "Entity": table_name, "Type": 0}],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 4,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": alias}},
                                    "Property": column,
                                }
                            },
                            "Right": {"Literal": {"Value": f"{value}L"}},
                        }
                    }
                }
            ],
        },
        "howCreated": "User",
        "isHiddenInViewMode": True,
        "isLockedInViewMode": True,
    }


def page(
    page_id: str,
    display_name: str,
    visuals: dict[str, dict[str, Any]],
    *,
    page_binding: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "$schema": PAGE_SCHEMA,
        "name": page_id,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
    }
    if page_binding:
        payload.update(page_binding)
    write_json(PAGES / page_id / "page.json", payload)
    for slug, visual in visuals.items():
        write_json(PAGES / page_id / "visuals" / identifier(page_id, slug) / "visual.json", visual)


def common_slicers(page_id: str, include_status: bool = True) -> dict[str, dict[str, Any]]:
    visuals = {
        "slicer_city": slicer(
            page_id,
            "slicer_city",
            "Dim City",
            "city_label_es",
            "Ciudad",
            "GlobalCity",
            (720, 16, 170, 80),
            1,
        ),
        "slicer_room": slicer(
            page_id,
            "slicer_room",
            "Dim Room Type",
            "room_type_label_es",
            "Tipología",
            "GlobalRoomType",
            (900, 16, 170, 80),
            2,
        ),
    }
    if include_status:
        visuals["slicer_status"] = slicer(
            page_id,
            "slicer_status",
            "Fact Opportunity Segments",
            "opportunity_label",
            "Evidencia",
            "GlobalEvidence",
            (1080, 16, 180, 80),
            3,
        )
    return visuals


def build_pages() -> list[str]:
    summary = identifier("page", "summary")
    market_structure = identifier("page", "market_structure")
    opportunity = identifier("page", "opportunity")
    detail = identifier("page", "detail")
    page_ids = [market_structure, summary, opportunity, detail]

    summary_visuals = {
        "title": textbox(
            summary,
            "title",
            "¿Dónde conviene investigar primero la captación?",
            (20, 16, 680, 60),
            0,
            size=24,
            bold=True,
        ),
        **common_slicers(summary),
        "kpis": card(
            summary,
            "kpis",
            ["Segmentos candidatos", "Anuncios analizables", "Cuota activa histórica"],
            (20, 112, 600, 110),
            10,
            "Indicadores del contexto: candidatos, anuncios analizables y cuota activa histórica.",
        ),
        "recommendation": card(
            summary,
            "recommendation",
            ["Recomendación provisional", "Disponibilidad de candidatos"],
            (640, 112, 620, 110),
            11,
            "Recomendación provisional y disponibilidad de hasta tres candidatos; exige validación comercial, regulatoria y operativa.",
        ),
        "candidate_table": table(
            summary,
            "candidate_table",
            [
                ("Column", "Dim City", "city_label_es"),
                ("Column", "Dim Neighborhood", "neighborhood_label"),
                ("Column", "Dim Room Type", "room_type_label_es"),
                ("Measure", "_Measures", "Estado de evidencia"),
                ("Measure", "_Measures", "Ranking candidato"),
                ("Measure", "_Measures", "Anuncios del segmento"),
                ("Measure", "_Measures", "Cuota activa del segmento"),
                ("Measure", "_Measures", "Posición de precio local"),
                ("Measure", "_Measures", "Efecto de actividad"),
                ("Measure", "_Measures", "Valor ajustado"),
                ("Measure", "_Measures", "Sensibilidad del segmento"),
            ],
            (20, 242, 1240, 340),
            20,
            "Hasta tres candidatos: barrio, tipología, escala, actividad, oferta, precio local, efecto, valor ajustado y sensibilidad.",
        ),
        "warning": textbox(
            summary,
            "warning",
            "Reseñas = proxy de actividad histórica. Precios = valores publicados locales. No son demanda, reservas, ocupación, ingresos ni margen.",
            (20, 596, 1240, 60),
            30,
            size=14,
            bold=True,
        ),
        "reset": reset_button(summary),
        "navigation": navigator(summary),
    }
    summary_visuals["candidate_table"]["filterConfig"] = {
        "filters": [
            categorical_filter(
                "FilterCandidateOnly000001",
                "Fact Opportunity Segments",
                "opportunity_label",
                "candidate",
            ),
            maximum_filter(
                "FilterTopThree00000002", "Fact Opportunity Segments", "candidate_rank", 3
            ),
        ]
    }
    market_visuals = {
        "title": textbox(
            market_structure,
            "title",
            "¿Dónde coinciden oferta y actividad relativa por barrio?",
            (20, 16, 680, 60),
            0,
            size=23,
            bold=True,
        ),
        **common_slicers(market_structure, include_status=False),
        "kpis": card(
            market_structure,
            "kpis",
            [
                "Anuncios analizables",
                "Actividad por anuncio",
                "Cobertura de actividad",
                "Cuota de anuncios en carteras >5",
            ],
            (20, 100, 1240, 90),
            10,
            "Anuncios analizables, actividad media, cobertura y cuota de carteras mayores de cinco.",
        ),
        "scatter": chart(
            market_structure,
            "scatter",
            "scatterChart",
            {
                "Category": [("Column", "Dim Neighborhood", "neighborhood_label")],
                "X": [("Measure", "_Measures", "Anuncios analizables")],
                "Y": [("Measure", "_Measures", "Actividad por anuncio")],
                "Size": [("Measure", "_Measures", "Anuncios analizables")],
                "Tooltips": [("Measure", "_Measures", "Cobertura de actividad")],
            },
            (20, 208, 600, 270),
            20,
            "Dispersión por barrio: anuncios analizables frente a reseñas mensuales por anuncio, con cobertura en tooltip.",
        ),
        "map": chart(
            market_structure,
            "map",
            "azureMap",
            {
                "Category": [("Column", "Dim Neighborhood", "neighborhood_label")],
                "Y": [("Column", "Dim Neighborhood", "centroid_latitude")],
                "X": [("Column", "Dim Neighborhood", "centroid_longitude")],
                "Size": [("Measure", "_Measures", "Anuncios analizables")],
                "Tooltips": [
                    ("Measure", "_Measures", "Actividad por anuncio"),
                    ("Measure", "_Measures", "Cobertura de actividad"),
                ],
            },
            (640, 208, 620, 270),
            21,
            "Mapa de centroides agregados por barrio; tamaño según anuncios y actividad disponible en tooltip.",
        ),
        "ranking": chart(
            market_structure,
            "ranking",
            "clusteredBarChart",
            {
                "Category": [("Column", "Dim Neighborhood", "neighborhood_label")],
                "Y": [("Measure", "_Measures", "Actividad por anuncio")],
                "Tooltips": [
                    ("Measure", "_Measures", "Anuncios analizables"),
                    ("Measure", "_Measures", "Cobertura de actividad"),
                ],
            },
            (20, 496, 600, 150),
            30,
            "Ranking de actividad por anuncio y barrio con volumen y cobertura en contexto.",
        ),
        "portfolio": chart(
            market_structure,
            "portfolio",
            "clusteredBarChart",
            {
                "Category": [("Column", "Fact Listings", "portfolio_bucket")],
                "Y": [("Measure", "_Measures", "Anuncios analizables")],
            },
            (640, 496, 620, 150),
            31,
            "Anuncios analizables por grupo excluyente de tamaño de cartera observado.",
        ),
        "warning": textbox(
            market_structure,
            "warning",
            "Actividad = proxy de reseñas mensuales; cartera = escala observada. No demuestran demanda, reservas, ocupación, propiedad ni profesionalidad.",
            (20, 652, 1000, 44),
            40,
            size=12,
            bold=True,
        ),
        "reset": reset_button(market_structure),
        "navigation": navigator(market_structure),
    }
    page(market_structure, "Estructura del mercado", market_visuals)
    page(summary, "Resumen ejecutivo", summary_visuals)

    opportunity_visuals = {
        "title": textbox(
            opportunity,
            "title",
            "¿En qué barrios y tipologías se concentra la oportunidad aparente?",
            (20, 16, 680, 60),
            0,
            size=23,
            bold=True,
        ),
        **common_slicers(opportunity),
        "ranking": chart(
            opportunity,
            "ranking",
            "clusteredBarChart",
            {
                "Category": [("Column", "Dim Neighborhood", "neighborhood_label")],
                "Y": [("Measure", "_Measures", "Anuncios en segmentos")],
                "Series": [("Column", "Fact Opportunity Segments", "opportunity_label")],
                "Tooltips": [
                    ("Measure", "_Measures", "Cuota de oferta"),
                    ("Measure", "_Measures", "Efecto de actividad"),
                ],
            },
            (20, 118, 600, 300),
            10,
            "Ranking accesible permanente por barrio; muestra volumen, estado por texto en la tabla y evidencia en contexto.",
        ),
        "map": chart(
            opportunity,
            "map",
            "azureMap",
            {
                "Category": [("Column", "Dim Neighborhood", "neighborhood_label")],
                "Y": [("Column", "Dim Neighborhood", "centroid_latitude")],
                "X": [("Column", "Dim Neighborhood", "centroid_longitude")],
                "Series": [("Column", "Fact Opportunity Segments", "opportunity_label")],
                "Size": [("Measure", "_Measures", "Anuncios en segmentos")],
            },
            (640, 118, 620, 300),
            11,
            "Mapa opcional de centroides agregados por barrio; la tabla y ranking son el fallback sin red.",
        ),
        "detail_table": table(
            opportunity,
            "detail_table",
            [
                ("Column", "Dim City", "city_label_es"),
                ("Column", "Dim Neighborhood", "neighborhood_label"),
                ("Column", "Dim Room Type", "room_type_label_es"),
                ("Measure", "_Measures", "Estado de evidencia"),
                ("Measure", "_Measures", "Anuncios del segmento"),
                ("Measure", "_Measures", "Cuota de oferta"),
                ("Measure", "_Measures", "Efecto de actividad"),
                ("Measure", "_Measures", "Posición de precio local"),
            ],
            (20, 438, 1240, 174),
            20,
            "Ranking tabular accesible y exportable; clic derecho en un barrio para acceder al detalle y confianza.",
        ),
        "fallback": textbox(
            opportunity,
            "fallback",
            "Si Azure Maps no carga, decide con el ranking y la tabla: contienen la misma unidad agregada y no muestran coordenadas individuales.",
            (20, 622, 1240, 38),
            30,
            size=12,
            bold=True,
        ),
        "reset": reset_button(opportunity),
        "navigation": navigator(opportunity),
    }
    page(opportunity, "Oportunidades de captación", opportunity_visuals)

    drill_filters = []
    parameters = []
    for index, (table_name, column) in enumerate(
        (("Dim Neighborhood", "neighborhood_label"), ("Dim Room Type", "room_type_label_es")),
        start=1,
    ):
        filter_name = f"FilterDrillthrough00000{index}"
        drill_filters.append(
            {
                "name": filter_name,
                "field": field("Column", table_name, column),
                "type": "Categorical",
                "howCreated": "Drillthrough",
            }
        )
        parameters.append(
            {
                "name": f"Param_{filter_name}",
                "boundFilter": filter_name,
                "fieldExpr": field("Column", table_name, column),
            }
        )
    detail_visuals = {
        "title": textbox(
            detail,
            "title",
            "¿Qué evidencia respalda la oportunidad y qué puede cambiar la decisión?",
            (20, 16, 680, 60),
            0,
            size=23,
            bold=True,
        ),
        **common_slicers(detail, include_status=False),
        "evidence": card(
            detail,
            "evidence",
            [
                "Muestra del segmento",
                "Efecto de actividad",
                "IC 95% del efecto",
                "Valor ajustado",
                "Estado de evidencia",
            ],
            (20, 112, 1240, 112),
            10,
            "Muestra, efecto, intervalo de confianza, valor ajustado y estado del segmento seleccionado.",
        ),
        "scatter": chart(
            detail,
            "scatter",
            "scatterChart",
            {
                "Category": [("Column", "Dim Neighborhood", "neighborhood_label")],
                "Series": [("Column", "Fact Opportunity Segments", "opportunity_label")],
                "X": [
                    ("Measure", "_Measures", "Posición de precio local")
                ],
                "Y": [("Measure", "_Measures", "Efecto de actividad")],
                "Size": [("Measure", "_Measures", "Anuncios del segmento")],
            },
            (20, 242, 500, 260),
            20,
            "Dispersión entre posición de precio local y efecto de actividad; tamaño según anuncios analizables y estado con texto en tablas.",
        ),
        "statistics": table(
            detail,
            "statistics",
            [
                ("Column", "Fact Statistical Results", "method"),
                ("Column", "Fact Statistical Results", "sample_size"),
                ("Column", "Fact Statistical Results", "estimate"),
                ("Column", "Fact Statistical Results", "ci_low"),
                ("Column", "Fact Statistical Results", "ci_high"),
                ("Column", "Fact Statistical Results", "p_value_adjusted"),
                ("Column", "Fact Statistical Results", "correction_method"),
                ("Column", "Fact Statistical Results", "sensitivity_status"),
            ],
            (540, 242, 720, 260),
            21,
            "Método, muestra, efecto, intervalo, valor ajustado, corrección y sensibilidad de la evidencia estadística.",
        ),
        "quality": table(
            detail,
            "quality",
            [
                ("Column", "Fact Quality Summary", "quality_metric"),
                ("Column", "Fact Quality Summary", "field"),
                ("Column", "Fact Quality Summary", "failed_count"),
                ("Column", "Fact Quality Summary", "failure_rate"),
                ("Column", "Fact Quality Summary", "severity"),
                ("Column", "Fact Quality Summary", "status"),
            ],
            (20, 518, 600, 132),
            30,
            "Indicadores de calidad, exclusiones y tasas de fallo para la ciudad seleccionada.",
        ),
        "control": card(
            detail,
            "control",
            [
                "Build ID",
                "Versión de schema",
                "Generado UTC",
                "Filas fuente",
                "Filas importadas",
                "Diferencia de conciliación",
            ],
            (640, 518, 620, 132),
            31,
            "Control del build: identidad, schema, hora, filas fuente e importadas; la diferencia debe ser cero.",
        ),
        "reset": reset_button(detail),
        "navigation": navigator(detail),
    }
    page(
        detail,
        "Detalle y confianza",
        detail_visuals,
        page_binding={
            "filterConfig": {"filters": drill_filters},
            "pageBinding": {"name": "Pod", "type": "Drillthrough", "parameters": parameters},
        },
    )
    return page_ids


def main() -> None:
    write_json(
        POWERBI / "AirbnbSupplyOpportunity.pbip",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
            "version": "1.0",
            "artifacts": [{"report": {"path": "AirbnbSupplyOpportunity.Report"}}],
            "settings": {"enableAutoRecovery": True},
        },
    )
    write_json(
        MODEL / "definition.pbism",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.2",
            "settings": {"qnaEnabled": False},
        },
    )
    write_json(
        MODEL / ".platform",
        {
            "$schema": PLATFORM_SCHEMA,
            "metadata": {
                "type": "SemanticModel",
                "displayName": "Airbnb Supply Opportunity",
                "description": "Modelo semántico local y reproducible para el análisis de captación.",
            },
            "config": {
                "version": "2.0",
                "logicalId": "386b16f2-6bad-504b-8dfb-c71dc9d44018",
            },
        },
    )
    write_json(
        REPORT / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {"byPath": {"path": "../AirbnbSupplyOpportunity.SemanticModel"}},
        },
    )
    write_json(
        REPORT / ".platform",
        {
            "$schema": PLATFORM_SCHEMA,
            "metadata": {
                "type": "Report",
                "displayName": "Airbnb Supply Opportunity",
                "description": "Informe ejecutivo de oportunidades aparentes de captación.",
            },
            "config": {
                "version": "2.0",
                "logicalId": "537f70f7-c325-551f-97ff-58acf4aee235",
            },
        },
    )
    write_json(
        DEFINITION / "version.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
            "version": "2.0.0",
        },
    )
    theme = json.loads((POWERBI / "theme.json").read_text(encoding="utf-8"))
    theme["name"] = THEME_FILE
    write_json(REPORT / "StaticResources" / "RegisteredResources" / THEME_FILE, theme)
    write_json(
        DEFINITION / "report.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU06",
                    "reportVersionAtImport": {
                        "visual": "2.9.0",
                        "report": "3.3.0",
                        "page": "2.1.0",
                    },
                    "type": "SharedResources",
                },
                "customTheme": {
                    "name": THEME_FILE,
                    "reportVersionAtImport": {
                        "visual": "2.9.0",
                        "report": "3.3.0",
                        "page": "2.1.0",
                    },
                    "type": "RegisteredResources",
                },
            },
            "resourcePackages": [
                {
                    "name": "RegisteredResources",
                    "type": "RegisteredResources",
                    "items": [{"name": THEME_FILE, "path": THEME_FILE, "type": "CustomTheme"}],
                }
            ],
            "annotations": [
                {"name": "defaultPage", "value": identifier("page", "market_structure")}
            ],
        },
    )
    page_ids = build_pages()
    write_json(
        PAGES / "pages.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": page_ids,
            "activePageName": page_ids[0],
        },
    )


if __name__ == "__main__":
    main()
