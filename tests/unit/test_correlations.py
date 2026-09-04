from __future__ import annotations

import importlib

import pandas as pd


def test_associations_are_within_city_and_corrected_as_one_family() -> None:
    statistics = importlib.import_module("airbnb_supply_analysis.statistics")
    frame = pd.DataFrame(
        {
            "city_key": ["madrid"] * 8,
            "activity_proxy": range(8),
            "price": range(10, 18),
            "minimum_nights": list(reversed(range(1, 9))),
        }
    )

    results = statistics.association_tests(frame, "build-test")

    assert set(results["metric"]) == {"price_vs_activity", "minimum_nights_vs_activity"}
    assert results["city_key"].eq("madrid").all()
    assert results["p_value_adjusted"].between(0, 1).all()
    assert results["interpretation_es"].str.contains("no implica causalidad").all()


def test_association_family_contains_twelve_tests_and_skips_insufficient_data() -> None:
    statistics = importlib.import_module("airbnb_supply_analysis.statistics")
    rows = []
    for city_index in range(6):
        for value in range(5):
            rows.append(
                {
                    "city_key": f"city-{city_index}",
                    "activity_proxy": value,
                    "price": value + city_index,
                    "minimum_nights": 5 - value,
                }
            )
    rows.extend(
        [
            {"city_key": "insufficient", "activity_proxy": 1, "price": 1, "minimum_nights": 1},
            {"city_key": "insufficient", "activity_proxy": 2, "price": 1, "minimum_nights": 1},
        ]
    )

    results = statistics.association_tests(pd.DataFrame(rows), "build-test")

    assert len(results) == 12
    assert results["correction_method"].eq("benjamini_hochberg_across_12").all()
    assert "insufficient" not in set(results["city_key"])
