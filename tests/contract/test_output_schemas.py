from __future__ import annotations

import pandas as pd
import pandera.errors
import pytest

import airbnb_supply_analysis.schemas as schemas
from airbnb_supply_analysis.schemas import (
    EXPECTED_POWERBI_FILES,
    OutputContractError,
    validate_no_restricted_columns,
)


def test_powerbi_contract_has_exactly_eight_files() -> None:
    assert EXPECTED_POWERBI_FILES == {
        "dim_city.csv",
        "dim_neighborhood.csv",
        "dim_room_type.csv",
        "fact_listings.csv",
        "fact_opportunity_segments.csv",
        "fact_statistical_results.csv",
        "fact_quality_summary.csv",
        "build_control.csv",
    }


@pytest.mark.parametrize(
    "restricted",
    ["listing_name", "host_name", "listing_id", "host_id", "latitude", "longitude"],
)
def test_powerbi_contract_rejects_restricted_columns(restricted: str) -> None:
    with pytest.raises(OutputContractError):
        validate_no_restricted_columns(pd.DataFrame({restricted: ["secret"]}))


def test_canonical_schema_rejects_duplicate_listing_keys(canonical_frame: pd.DataFrame) -> None:
    validator = getattr(schemas, "validate_canonical", None)
    assert validator is not None, "Falta el validador canónico compartido"
    duplicate = pd.concat([canonical_frame, canonical_frame.iloc[[0]]], ignore_index=True)
    with pytest.raises(pandera.errors.SchemaErrors):
        validator(duplicate)
