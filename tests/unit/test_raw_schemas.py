from __future__ import annotations

import pandas as pd
import pytest

import airbnb_supply_analysis.schemas as schemas


def test_raw_schema_requires_identifier_and_core_fields() -> None:
    validator = getattr(schemas, "validate_raw_frame", None)
    assert validator is not None, "Falta el validador raw"
    frame = pd.DataFrame({"name": ["sin id"]})

    with pytest.raises(Exception, match="id"):
        validator(frame, "london")


def test_raw_schema_allows_source_specific_missing_columns() -> None:
    validator = getattr(schemas, "validate_raw_frame", None)
    assert validator is not None, "Falta el validador raw"
    frame = pd.DataFrame(
        {
            "id": [1],
            "name": ["A"],
            "host_id": [10],
            "host_name": ["H"],
            "neighbourhood": ["Centro"],
            "latitude": [40.4],
            "longitude": [-3.7],
            "room_type": ["Private room"],
            "price": [50],
            "minimum_nights": [1],
            "number_of_reviews": [0],
            "last_review": [None],
            "reviews_per_month": [None],
        }
    )

    assert len(validator(frame, "tokyo")) == 1


def test_raw_schema_rejects_duplicate_city_listing_id() -> None:
    validator = getattr(schemas, "validate_raw_frame", None)
    assert validator is not None, "Falta el validador raw"
    frame = pd.DataFrame(
        {
            "id": [1, 1],
            "name": ["A", "B"],
            "host_id": [10, 10],
            "host_name": ["H", "H"],
            "neighbourhood": ["Centro", "Centro"],
            "latitude": [40.4, 40.4],
            "longitude": [-3.7, -3.7],
            "room_type": ["Private room", "Private room"],
            "price": [50, 50],
            "minimum_nights": [1, 1],
            "number_of_reviews": [0, 0],
            "last_review": [None, None],
            "reviews_per_month": [None, None],
        }
    )

    with pytest.raises(Exception, match="duplicad"):
        validator(frame, "madrid")
