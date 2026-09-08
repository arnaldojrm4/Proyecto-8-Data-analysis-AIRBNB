from __future__ import annotations

import pandas as pd


def test_safe_option_index_falls_back_when_a_saved_choice_disappears() -> None:
    from dashboard.filters import safe_option_index

    assert safe_option_index(["madrid", "sevilla"], "removed", "sevilla") == 1
    assert safe_option_index(["madrid", "sevilla"], "madrid", "sevilla") == 0


def _cities() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city_key": ["madrid", "barcelona"],
            "city_label_es": ["Madrid", "Barcelona"],
        }
    )


def _listings() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city_key": ["madrid", "madrid", "barcelona"],
            "room_type_key": ["private", "entire", "entire"],
            "neighborhood_key": ["madrid:centro", "madrid:sur", "barcelona:gracia"],
        }
    )


def test_initial_selection_uses_first_spanish_city_and_its_room_types() -> None:
    from dashboard.filters import initial_selection

    selection = initial_selection(_cities(), _listings())

    assert selection.city_key == "barcelona"
    assert selection.room_type_keys == ("entire",)
    assert selection.neighborhood_keys == ()


def test_normalize_selection_removes_values_outside_the_active_city() -> None:
    from dashboard.filters import FilterSelection, normalize_selection

    requested = FilterSelection(
        city_key="madrid",
        room_type_keys=("private", "missing"),
        neighborhood_keys=("madrid:centro", "barcelona:gracia"),
        evidence_states=("robusta", "desconocida"),
    )

    normalized = normalize_selection(requested, _cities(), _listings())

    assert normalized.room_type_keys == ("private",)
    assert normalized.neighborhood_keys == ("madrid:centro",)
    assert normalized.evidence_states == ("robusta",)


def test_apply_listing_filters_uses_city_room_type_and_optional_neighborhood() -> None:
    from dashboard.filters import FilterSelection, apply_listing_filters

    selection = FilterSelection(
        city_key="madrid",
        room_type_keys=("private", "entire"),
        neighborhood_keys=("madrid:centro",),
    )

    filtered = apply_listing_filters(_listings(), selection)

    assert filtered.index.tolist() == [0]


def test_evidence_status_has_four_canonical_outcomes() -> None:
    from dashboard.filters import canonical_evidence_status

    assert canonical_evidence_status("robust") == "robusta"
    assert canonical_evidence_status("fragile") == "frágil"
    assert canonical_evidence_status("conflicting") == "conflictiva"
    assert canonical_evidence_status("not_run") == "no evaluada"
    assert canonical_evidence_status(None) == "no evaluada"
    assert canonical_evidence_status("unexpected") == "no evaluada"


def test_apply_opportunity_filters_includes_canonical_evidence_status() -> None:
    from dashboard.filters import FilterSelection, apply_opportunity_filters

    opportunities = pd.DataFrame(
        {
            "city_key": ["madrid", "madrid"],
            "room_type_key": ["private", "private"],
            "neighborhood_key": ["centro", "sur"],
            "sensitivity_status": ["robust", "fragile"],
        }
    )
    selection = FilterSelection(
        city_key="madrid",
        room_type_keys=("private",),
        evidence_states=("robusta",),
    )

    filtered = apply_opportunity_filters(opportunities, selection)

    assert filtered["neighborhood_key"].tolist() == ["centro"]


def test_statistical_filters_keep_citywide_results_and_matching_segments() -> None:
    from dashboard.filters import FilterSelection, apply_statistical_filters

    statistics = pd.DataFrame(
        {
            "result_id": ["association", "segment-centro", "segment-sur"],
            "analysis_family": ["association", "segment", "segment"],
            "city_key": ["madrid", "madrid", "madrid"],
            "segment_key": [pd.NA, "centro:private", "sur:entire"],
            "sensitivity_status": ["not_run", "robust", "fragile"],
        }
    )
    opportunities = pd.DataFrame(
        {
            "segment_key": ["centro:private", "sur:entire"],
            "city_key": ["madrid", "madrid"],
            "room_type_key": ["private", "entire"],
            "neighborhood_key": ["centro", "sur"],
        }
    )
    selection = FilterSelection(city_key="madrid", room_type_keys=("private",))

    filtered = apply_statistical_filters(statistics, opportunities, selection)

    assert filtered["result_id"].tolist() == ["association", "segment-centro"]
