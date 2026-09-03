from __future__ import annotations

import importlib

import pandas as pd


def test_room_type_test_reports_corrected_omnibus_and_effect() -> None:
    statistics = importlib.import_module("airbnb_supply_analysis.statistics")
    frame = pd.DataFrame(
        {
            "city_key": ["madrid"] * 12,
            "room_type": ["private_room"] * 6 + ["entire_home_apt"] * 6,
            "activity_proxy": [3, 4, 5, 6, 7, 8, 0, 0, 1, 1, 2, 2],
            "host_id": range(12),
        }
    )

    results = statistics.room_type_tests(frame, "build-test")

    omnibus = results.query("method == 'kruskal_wallis'").iloc[0]
    assert omnibus["analysis_family"] == "room_type"
    assert 0 <= omnibus["p_value_adjusted"] <= 1
    pairwise = results.query("method == 'mann_whitney_u'").iloc[0]
    assert pairwise["effect_type"] == "probability_superiority"
    assert pairwise["estimate"] > 0.5


def test_multiple_testing_corrections_are_bounded() -> None:
    statistics = importlib.import_module("airbnb_supply_analysis.statistics")

    adjusted = statistics.adjust_pvalues([0.001, 0.02, 0.8], "holm")

    assert len(adjusted) == 3
    assert all(0 <= value <= 1 for value in adjusted)
    assert adjusted[0] <= adjusted[1] <= adjusted[2]
