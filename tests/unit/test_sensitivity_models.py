from __future__ import annotations

import importlib

import pandas as pd


def test_two_part_summary_separates_presence_and_positive_intensity() -> None:
    statistics = importlib.import_module("airbnb_supply_analysis.statistics")
    frame = pd.DataFrame(
        {
            "city_key": ["madrid"] * 8,
            "room_type": ["private_room"] * 4 + ["entire_home_apt"] * 4,
            "activity_proxy": [0, 0, 2, 4, 0, 1, 1, 2],
            "host_id": range(8),
        }
    )

    results = statistics.two_part_summary(frame, "build-test")

    assert set(results["metric"]) == {"activity_presence", "positive_activity_intensity"}
    assert results["analysis_family"].eq("sensitivity").all()
    assert results["sensitivity_status"].isin(["robust", "fragile", "conflicting"]).all()
    assert set(results["method"]) == {"binomial_glm_adjusted", "ols_log_positive_adjusted"}


def test_adjusted_two_part_models_report_effect_intervals() -> None:
    statistics = importlib.import_module("airbnb_supply_analysis.statistics")
    frame = pd.DataFrame(
        {
            "city_key": ["madrid"] * 80,
            "room_type": ["private_room"] * 40 + ["entire_home_apt"] * 40,
            "neighborhood_key": ["madrid:centro"] * 80,
            "activity_proxy": ([0, 1, 2, 3] * 10) + ([0, 0, 1, 1] * 10),
            "host_id": list(range(80)),
        }
    )

    results = statistics.two_part_summary(frame, "build-test")

    assert results["estimate"].notna().all()
    assert results["ci_low"].notna().all()
    assert results["ci_high"].notna().all()
    assert results["p_value_raw"].between(0, 1).all()
