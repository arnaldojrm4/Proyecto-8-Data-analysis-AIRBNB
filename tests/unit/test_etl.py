from __future__ import annotations

import importlib

import pandas as pd


def _etl_module():
    try:
        return importlib.import_module("airbnb_supply_analysis.etl")
    except ModuleNotFoundError:
        return None


def test_activity_proxy_only_derives_zero_for_zero_reviews() -> None:
    etl = _etl_module()
    assert etl is not None, "Falta el módulo ETL"
    reviews_per_month = pd.Series([None, None, 1.5])
    review_count = pd.Series([0, 4, 8])

    proxy, derived, analyzable = etl.derive_activity_proxy(reviews_per_month, review_count)

    assert proxy.iloc[0] == 0.0
    assert bool(derived.iloc[0]) is True
    assert pd.isna(proxy.iloc[1])
    assert bool(analyzable.iloc[1]) is False
    assert proxy.iloc[2] == 1.5


def test_canonicalization_preserves_rows_and_source_unavailability() -> None:
    etl = _etl_module()
    assert etl is not None, "Falta el módulo ETL"
    raw = pd.DataFrame(
        {
            "id": [1],
            "name": [None],
            "host_id": [10],
            "host_name": [None],
            "neighbourhood": ["  Shinjuku  "],
            "latitude": [35.7],
            "longitude": [139.7],
            "room_type": ["Private room"],
            "price": [75],
            "minimum_nights": [1],
            "number_of_reviews": [0],
            "last_review": [None],
            "reviews_per_month": [None],
        }
    )

    canonical, transformations = etl.canonicalize_source(raw, "tokyo", "tokyo", "build-test")

    assert len(canonical) == 1
    assert canonical.loc[0, "listing_key"] == "tokyo:1"
    assert canonical.loc[0, "room_type"] == "private_room"
    assert pd.isna(canonical.loc[0, "availability_365"])
    assert bool(canonical.loc[0, "availability_365_source_available"]) is False
    assert not transformations.empty
    assert transformations["source_id"].eq("tokyo").all()
