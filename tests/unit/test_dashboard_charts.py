from __future__ import annotations

import pandas as pd
import pytest


def test_activity_chart_uses_hand_checked_room_type_medians() -> None:
    from dashboard.charts import activity_by_room_type_chart

    listings = pd.DataFrame(
        {
            "room_type_key": ["private", "private", "entire"],
            "activity_proxy": [0.0, 2.0, 3.0],
        }
    )
    room_types = pd.DataFrame(
        {
            "room_type_key": ["private", "entire"],
            "room_type_label_es": ["Habitación privada", "Alojamiento entero"],
        }
    )

    figure = activity_by_room_type_chart(listings, room_types)

    values = dict(zip(figure.data[0].x, figure.data[0].y, strict=True))
    assert values == {"Alojamiento entero": 3.0, "Habitación privada": 1.0}
    assert "proxy" in figure.layout.yaxis.title.text.lower()


def test_activity_chart_explains_an_empty_population() -> None:
    from dashboard.charts import activity_by_room_type_chart

    figure = activity_by_room_type_chart(pd.DataFrame(), pd.DataFrame())

    assert not figure.data
    assert figure.layout.annotations[0].text == "Sin datos para la selección"


def test_opportunity_map_only_plots_rows_with_aggregate_centroids() -> None:
    from dashboard.charts import opportunity_map_chart

    opportunities = pd.DataFrame(
        {
            "neighborhood_label": ["Centro", "Sin coordenadas"],
            "room_type_label_es": ["Habitación privada", "Alojamiento entero"],
            "centroid_latitude": [40.4, pd.NA],
            "centroid_longitude": [-3.7, pd.NA],
            "listing_count": [10, 8],
            "activity_median": [1.2, 0.4],
        }
    )

    figure = opportunity_map_chart(opportunities)

    assert len(figure.data) == 1
    assert list(figure.data[0].lat) == [40.4]


def test_effect_chart_uses_estimate_and_confidence_interval() -> None:
    from dashboard.charts import effect_interval_chart

    statistics = pd.DataFrame(
        {
            "comparison": ["segmento frente a referencia"],
            "estimate": [0.62],
            "ci_low": [0.54],
            "ci_high": [0.70],
            "effect_type": ["probability_superiority"],
        }
    )

    figure = effect_interval_chart(statistics)

    assert list(figure.data[0].x) == [0.62]
    assert list(figure.data[0].error_x.array) == pytest.approx([0.08])
    assert list(figure.data[0].error_x.arrayminus) == pytest.approx([0.08])


def test_supply_activity_scatter_retains_neighborhood_context() -> None:
    from dashboard.charts import supply_activity_scatter

    metrics = pd.DataFrame(
        {
            "neighborhood_label": ["Centro", "Norte"],
            "listing_count": [100, 20],
            "activity_per_listing": [1.2, 0.5],
            "activity_coverage": [1.0, 0.8],
        }
    )

    figure = supply_activity_scatter(metrics)

    assert list(figure.data[0].x) == [100, 20]
    assert list(figure.data[0].y) == [1.2, 0.5]
    assert list(figure.data[0].text) == ["Centro", "Norte"]
    assert figure.layout.xaxis.type == "log"


def test_portfolio_mix_chart_uses_percent_scale_and_exclusive_buckets() -> None:
    from dashboard.charts import portfolio_mix_chart

    mix = pd.DataFrame(
        {
            "portfolio_bucket": ["1", "2–5", "6–10", ">10"],
            "listing_count": [6, 2, 1, 1],
            "listing_share": [0.6, 0.2, 0.1, 0.1],
        }
    )

    figure = portfolio_mix_chart(mix)

    assert list(figure.data[0].x) == [0.6, 0.2, 0.1, 0.1]
    assert figure.layout.xaxis.tickformat == ".0%"
