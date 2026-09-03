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
