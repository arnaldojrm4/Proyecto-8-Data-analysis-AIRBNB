from __future__ import annotations

import importlib

import pandas as pd


def test_segment_comparison_uses_same_city_and_room_type_reference() -> None:
    statistics = importlib.import_module("airbnb_supply_analysis.statistics")
    frame = pd.DataFrame(
        {
            "city_key": ["madrid"] * 12,
            "neighborhood_key": ["madrid:centro"] * 6 + ["madrid:resto"] * 6,
            "room_type": ["private_room"] * 12,
            "activity_proxy": [3, 4, 5, 6, 7, 8, 0, 0, 1, 1, 2, 2],
            "host_id": range(12),
        }
    )

    results = statistics.segment_tests(frame, "build-test", minimum_n=3, minimum_positive=1)

    centre = results.loc[results["segment_key"] == "madrid:centro:private_room"].iloc[0]
    assert centre["estimate"] > 0.5
    assert centre["correction_method"] == "benjamini_hochberg_within_city"
    assert "misma ciudad y tipología" in centre["interpretation_es"]
