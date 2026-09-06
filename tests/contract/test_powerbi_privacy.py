from __future__ import annotations

import re

import pandas as pd

RESTRICTED_HEADER_TOKENS = {
    "listingname",
    "hostname",
    "listingid",
    "hostid",
    "latitude",
    "longitude",
}


def _normalized(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def test_powerbi_exports_exclude_restricted_headers_case_insensitively(
    powerbi_export_fixture,
) -> None:
    for path in powerbi_export_fixture.directory.glob("*.csv"):
        headers = {_normalized(column) for column in pd.read_csv(path, nrows=0).columns}
        restricted = headers.intersection(RESTRICTED_HEADER_TOKENS)
        assert not restricted, f"{path.name}: campos restringidos {sorted(restricted)}"


def test_powerbi_exports_do_not_leak_raw_names_ids_or_listing_coordinates(
    powerbi_export_fixture,
) -> None:
    forbidden = {
        *powerbi_export_fixture.secret_names,
        *(str(value) for value in powerbi_export_fixture.raw_listing_ids),
        *(str(value) for value in powerbi_export_fixture.raw_host_ids),
        *powerbi_export_fixture.raw_coordinates,
    }
    for path in powerbi_export_fixture.directory.glob("*.csv"):
        cells = {
            str(value)
            for value in pd.read_csv(path, dtype=str, keep_default_na=False).to_numpy().ravel()
        }
        leaks = {
            secret
            for secret in forbidden
            if any(secret == cell or secret in cell for cell in cells)
        }
        assert not leaks, f"{path.name}: valores restringidos {sorted(leaks)}"


def test_only_aggregate_centroids_can_leave_the_pipeline(powerbi_export_fixture) -> None:
    allowed = {
        "dim_neighborhood.csv": {"centroid_latitude", "centroid_longitude"},
        "fact_opportunity_segments.csv": {"centroid_latitude", "centroid_longitude"},
    }
    for path in powerbi_export_fixture.directory.glob("*.csv"):
        coordinate_columns = {
            column
            for column in pd.read_csv(path, nrows=0).columns
            if "latitude" in column.casefold() or "longitude" in column.casefold()
        }
        assert coordinate_columns.issubset(allowed.get(path.name, set())), path.name
