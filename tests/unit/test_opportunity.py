from __future__ import annotations

import importlib


def test_candidate_requires_every_locked_condition() -> None:
    opportunity = importlib.import_module("airbnb_supply_analysis.opportunity")
    row = {
        "activity_analyzable_count": 80,
        "positive_activity_count": 30,
        "probability_superiority": 0.60,
        "effect_ci_low": 0.54,
        "effect_ci_high": 0.66,
        "q_value": 0.01,
        "sensitivity_status": "robust",
        "neighborhood_room_type_share": 0.20,
        "room_type_city_share": 0.35,
    }

    assert opportunity.classify_opportunity(row)[0] == "candidate"
    assert opportunity.classify_opportunity({**row, "q_value": 0.08})[0] == "watch"
    assert (
        opportunity.classify_opportunity({**row, "activity_analyzable_count": 20})[0]
        == "insufficient_evidence"
    )


def test_robust_activity_with_high_supply_is_consolidated() -> None:
    opportunity = importlib.import_module("airbnb_supply_analysis.opportunity")
    row = {
        "activity_analyzable_count": 80,
        "positive_activity_count": 30,
        "probability_superiority": 0.60,
        "effect_ci_low": 0.54,
        "effect_ci_high": 0.66,
        "q_value": 0.01,
        "sensitivity_status": "robust",
        "neighborhood_room_type_share": 0.50,
        "room_type_city_share": 0.35,
    }
    assert opportunity.classify_opportunity(row)[0] == "consolidated"
