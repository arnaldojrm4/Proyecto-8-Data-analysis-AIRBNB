from __future__ import annotations

import importlib

import pandas as pd


def test_chart_titles_use_proxy_safe_business_language(canonical_frame) -> None:
    visualization = importlib.import_module("airbnb_supply_analysis.visualization")

    figure = visualization.activity_by_room_type(canonical_frame)

    assert "actividad histórica" in figure.axes[0].get_title().lower()
    forbidden = {"listing_name", "host_name", "listing_id", "host_id"}
    assert not forbidden.intersection(figure.axes[0].get_xlabel().split())


def test_plotly_export_is_self_contained_and_has_no_restricted_tooltips(tmp_path) -> None:
    visualization = importlib.import_module("airbnb_supply_analysis.visualization")
    segments = pd.DataFrame(
        {
            "neighborhood_room_type_share": [0.2],
            "probability_superiority": [0.6],
            "listing_count": [50],
            "opportunity_label": ["candidate"],
            "neighborhood": ["Centro"],
            "city_key": ["madrid"],
            "room_type": ["private_room"],
            "q_value": [0.01],
            "segment_key": ["hidden-key"],
        }
    )

    figure = visualization.opportunity_scatter(segments)
    destination = tmp_path / "figure.html"
    figure.write_html(destination, include_plotlyjs=True, full_html=True)
    html = destination.read_text(encoding="utf-8")

    assert "plotly.js" in html.lower()
    assert "listing_id" not in html
    assert "host_id" not in html
    assert "Precio" not in figure.layout.xaxis.title.text


def test_correlation_figure_compares_effects_by_city_not_monetary_amounts() -> None:
    visualization = importlib.import_module("airbnb_supply_analysis.visualization")
    results = pd.DataFrame(
        {
            "method": ["spearman", "spearman"],
            "city_key": ["madrid", "tokyo"],
            "metric": ["price_vs_activity", "price_vs_activity"],
            "estimate": [-0.1, 0.2],
        }
    )

    figure = visualization.association_effects(results)

    assert "Spearman" in figure.axes[0].get_ylabel()
    assert "moneda" not in figure.axes[0].get_ylabel().lower()
    assert {label.get_text() for label in figure.axes[0].get_xticklabels()} == {
        "madrid",
        "tokyo",
    }
