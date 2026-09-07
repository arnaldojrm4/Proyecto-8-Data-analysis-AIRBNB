from __future__ import annotations

import hashlib
import json

import pandas as pd

from airbnb_supply_analysis import cli
from airbnb_supply_analysis.validation import validate_release_artifacts

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


def _complete_release_evidence(powerbi_export_fixture) -> None:
    notebooks = powerbi_export_fixture.artifacts / "executed_notebooks"
    notebooks.mkdir(parents=True, exist_ok=True)
    for filename in ("01_data_audit.ipynb", "02_etl.ipynb", "03_executive_eda.ipynb"):
        (notebooks / filename).write_text("{}", encoding="utf-8")
    reconciliation = powerbi_export_fixture.artifacts / "quality" / "row-reconciliation.json"
    reconciliation.write_text(
        json.dumps({"release_gate_status": "pass"}),
        encoding="utf-8",
    )


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


def test_release_validation_rejects_a_tampered_powerbi_hash(powerbi_export_fixture) -> None:
    _complete_release_evidence(powerbi_export_fixture)
    listing_path = powerbi_export_fixture.directory / "fact_listings.csv"
    listing_path.write_bytes(listing_path.read_bytes() + b"\n")

    try:
        validate_release_artifacts(
            powerbi_export_fixture.processed,
            powerbi_export_fixture.directory,
            powerbi_export_fixture.artifacts,
        )
    except ValueError as error:
        assert "hash" in str(error).casefold()
    else:
        raise AssertionError("Un CSV manipulado debe bloquear la validación")


def test_release_validation_rejects_an_orphan_even_with_updated_hash(
    powerbi_export_fixture,
) -> None:
    _complete_release_evidence(powerbi_export_fixture)
    listing_path = powerbi_export_fixture.directory / "fact_listings.csv"
    listings = _read(powerbi_export_fixture.directory, "fact_listings.csv")
    listings.loc[0, "neighborhood_key"] = "madrid:barrio-inexistente"
    listings.to_csv(listing_path, index=False, lineterminator="\n")

    control_path = powerbi_export_fixture.directory / "build_control.csv"
    control = _read(powerbi_export_fixture.directory, "build_control.csv")
    row = control["output_file"].eq("fact_listings.csv")
    control.loc[row, "output_sha256"] = hashlib.sha256(listing_path.read_bytes()).hexdigest()
    control.to_csv(control_path, index=False, lineterminator="\n")

    try:
        validate_release_artifacts(
            powerbi_export_fixture.processed,
            powerbi_export_fixture.directory,
            powerbi_export_fixture.artifacts,
        )
    except ValueError as error:
        assert "huérfana" in str(error).casefold()
    else:
        raise AssertionError("Una relación huérfana debe bloquear la validación")


def test_export_does_not_replace_the_previous_dataset_when_validation_fails(
    powerbi_export_fixture,
) -> None:
    listing_path = powerbi_export_fixture.directory / "fact_listings.csv"
    previous_listing_bytes = listing_path.read_bytes()
    opportunities_path = powerbi_export_fixture.processed / "opportunity_segments.parquet"
    opportunities = pd.read_parquet(opportunities_path)
    opportunities.loc[0, "neighborhood_key"] = "madrid:barrio-inexistente"
    opportunities.to_parquet(opportunities_path, index=False)

    exit_code = cli.main(
        [
            "export",
            "--processed-dir",
            str(powerbi_export_fixture.processed),
            "--artifacts-dir",
            str(powerbi_export_fixture.artifacts),
            "--powerbi-dir",
            str(powerbi_export_fixture.directory),
            "--source-manifest",
            str(powerbi_export_fixture.source_manifest),
            "--config",
            str(powerbi_export_fixture.analysis_config),
            "--build-id",
            "TESTBUILD",
            "--log-format",
            "json",
        ]
    )

    assert exit_code == 6
    assert listing_path.read_bytes() == previous_listing_bytes


def test_release_validation_rejects_source_counts_that_disagree_with_manifest(
    powerbi_export_fixture,
) -> None:
    _complete_release_evidence(powerbi_export_fixture)
    control_path = powerbi_export_fixture.directory / "build_control.csv"
    control = _read(powerbi_export_fixture.directory, "build_control.csv")
    control["source_row_count"] = 999
    control.to_csv(control_path, index=False, lineterminator="\n")

    try:
        validate_release_artifacts(
            powerbi_export_fixture.processed,
            powerbi_export_fixture.directory,
            powerbi_export_fixture.artifacts,
            source_manifest_path=powerbi_export_fixture.source_manifest,
            analysis_config_path=powerbi_export_fixture.analysis_config,
        )
    except ValueError as error:
        assert "source_row_count" in str(error)
    else:
        raise AssertionError("Un conteo de fuentes falso debe bloquear la validación")


def test_release_validation_rejects_mixed_build_identity(powerbi_export_fixture) -> None:
    _complete_release_evidence(powerbi_export_fixture)
    opportunity_path = powerbi_export_fixture.directory / "fact_opportunity_segments.csv"
    opportunities = _read(powerbi_export_fixture.directory, "fact_opportunity_segments.csv")
    opportunities["build_id"] = "OTHERBUILD"
    opportunities.to_csv(opportunity_path, index=False, lineterminator="\n")

    control_path = powerbi_export_fixture.directory / "build_control.csv"
    control = _read(powerbi_export_fixture.directory, "build_control.csv")
    row = control["output_file"].eq("fact_opportunity_segments.csv")
    control.loc[row, "output_sha256"] = hashlib.sha256(opportunity_path.read_bytes()).hexdigest()
    control.to_csv(control_path, index=False, lineterminator="\n")

    try:
        validate_release_artifacts(
            powerbi_export_fixture.processed,
            powerbi_export_fixture.directory,
            powerbi_export_fixture.artifacts,
        )
    except ValueError as error:
        assert "build_id" in str(error)
    else:
        raise AssertionError("Mezclar builds debe bloquear la validación")
