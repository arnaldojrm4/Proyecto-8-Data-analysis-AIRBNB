from __future__ import annotations

import importlib


def test_chart_titles_use_proxy_safe_business_language(canonical_frame) -> None:
    visualization = importlib.import_module("airbnb_supply_analysis.visualization")

    figure = visualization.activity_by_room_type(canonical_frame)

    assert "actividad histórica" in figure.axes[0].get_title().lower()
    forbidden = {"listing_name", "host_name", "listing_id", "host_id"}
    assert not forbidden.intersection(figure.axes[0].get_xlabel().split())
