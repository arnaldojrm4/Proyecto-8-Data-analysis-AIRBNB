from __future__ import annotations

import importlib

import pandas as pd


def _quality_module():
    try:
        return importlib.import_module("airbnb_supply_analysis.quality")
    except ModuleNotFoundError:
        return None


def test_profile_reports_null_duplicate_and_invalid_rates() -> None:
    quality = _quality_module()
    assert quality is not None, "Falta el módulo de calidad"
    frame = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "latitude": [40.0, 95.0, None],
            "longitude": [-3.0, -3.0, -3.0],
            "price": [50, -1, 5000],
            "minimum_nights": [1, 0, 1000],
        }
    )

    profile, findings = quality.profile_source(frame, "madrid", "build-test")

    assert profile.loc[profile["field"] == "latitude", "null_count"].item() == 1
    assert findings.loc[findings["check_id"] == "duplicate_listing_id", "failed_count"].item() == 2
    assert findings.loc[findings["check_id"] == "invalid_latitude", "failed_count"].item() == 2


def test_iqr_outliers_are_flagged_not_removed() -> None:
    quality = _quality_module()
    assert quality is not None, "Falta el módulo de calidad"
    values = pd.Series([10, 11, 12, 13, 1000], dtype=float)

    mask = quality.iqr_outlier_mask(values)

    assert mask.tolist() == [False, False, False, False, True]
    assert len(values) == 5
