from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest


def test_load_dashboard_dataset_exposes_one_immutable_approved_build(
    powerbi_export_fixture,
) -> None:
    from dashboard.data import load_dashboard_dataset

    dataset = load_dashboard_dataset(powerbi_export_fixture.directory)

    assert dataset.build.build_id == "TESTBUILD"
    assert dataset.build.schema_version == "1.0.0"
    assert dataset.build.release_gate_status == "pass"
    assert dataset.cities["city_label_es"].tolist() == ["Madrid"]
    assert len(dataset.listings) == 2
    with pytest.raises(FrozenInstanceError):
        dataset.build.build_id = "OTHER"


def test_load_dashboard_dataset_keeps_frames_independent_from_csv_reload(
    powerbi_export_fixture,
) -> None:
    from dashboard.data import load_dashboard_dataset

    dataset = load_dashboard_dataset(powerbi_export_fixture.directory)
    original = dataset.opportunities.loc[0, "listing_count"]
    dataset.opportunities.loc[0, "listing_count"] = 999

    reloaded = load_dashboard_dataset(powerbi_export_fixture.directory)

    assert original == 1
    assert reloaded.opportunities.loc[0, "listing_count"] == 1

