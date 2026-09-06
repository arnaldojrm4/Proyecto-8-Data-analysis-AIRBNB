from __future__ import annotations

import hashlib

import pandas as pd

OUTPUT_FILES = {
    "dim_city.csv",
    "dim_neighborhood.csv",
    "dim_room_type.csv",
    "fact_listings.csv",
    "fact_opportunity_segments.csv",
    "fact_statistical_results.csv",
    "fact_quality_summary.csv",
}


def _read(directory, filename: str) -> pd.DataFrame:
    return pd.read_csv(directory / filename, keep_default_na=False)


def test_powerbi_dimension_relationships_resolve_without_orphans(
    powerbi_export_fixture,
) -> None:
    directory = powerbi_export_fixture.directory
    cities = _read(directory, "dim_city.csv")
    neighborhoods = _read(directory, "dim_neighborhood.csv")
    room_types = _read(directory, "dim_room_type.csv")
    listings = _read(directory, "fact_listings.csv")
    opportunities = _read(directory, "fact_opportunity_segments.csv")

    relationships = [
        (neighborhoods, "city_key", cities, "city_key"),
        (listings, "city_key", cities, "city_key"),
        (listings, "neighborhood_key", neighborhoods, "neighborhood_key"),
        (listings, "room_type_key", room_types, "room_type_key"),
        (opportunities, "city_key", cities, "city_key"),
        (opportunities, "neighborhood_key", neighborhoods, "neighborhood_key"),
        (opportunities, "room_type_key", room_types, "room_type_key"),
    ]
    for fact, foreign_key, dimension, primary_key in relationships:
        assert foreign_key in fact, f"Falta FK {foreign_key}"
        assert primary_key in dimension, f"Falta PK {primary_key}"
        assert set(fact[foreign_key]).issubset(set(dimension[primary_key])), foreign_key


def test_build_control_reconciles_rows_hashes_and_build_identity(powerbi_export_fixture) -> None:
    directory = powerbi_export_fixture.directory
    control = _read(directory, "build_control.csv")
    required = {
        "build_id",
        "schema_version",
        "source_manifest_hash",
        "analysis_config_hash",
        "source_row_count",
        "canonical_row_count",
        "distinct_listing_key_count",
        "segment_count",
        "output_file",
        "output_row_count",
        "output_sha256",
        "release_gate_status",
    }
    assert required.issubset(control.columns), sorted(required.difference(control.columns))
    assert set(control["output_file"]) == OUTPUT_FILES
    assert control["build_id"].nunique() == 1
    assert control["build_id"].iat[0] == "TESTBUILD"
    assert control["source_row_count"].eq(len(powerbi_export_fixture.listings)).all()
    assert control["canonical_row_count"].eq(len(powerbi_export_fixture.listings)).all()
    assert (
        control["distinct_listing_key_count"]
        .eq(powerbi_export_fixture.listings["listing_key"].nunique())
        .all()
    )
    assert control["segment_count"].eq(len(powerbi_export_fixture.opportunities)).all()
    assert control["release_gate_status"].eq("pass").all()

    for row in control.itertuples(index=False):
        path = directory / row.output_file
        actual_rows = len(pd.read_csv(path))
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        assert row.output_row_count == actual_rows, row.output_file
        assert row.output_sha256 == actual_hash, row.output_file
