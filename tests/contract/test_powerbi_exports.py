from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = {
    "dim_city.csv": [
        "city_key",
        "city_label_es",
        "source_snapshot_date_status",
        "price_currency_status",
        "scope_note_es",
    ],
    "dim_neighborhood.csv": [
        "neighborhood_key",
        "city_key",
        "neighborhood_label",
        "centroid_latitude",
        "centroid_longitude",
        "coordinate_coverage",
    ],
    "dim_room_type.csv": [
        "room_type_key",
        "room_type",
        "room_type_label_es",
        "sort_order",
    ],
    "fact_listings.csv": [
        "listing_key",
        "city_key",
        "neighborhood_key",
        "room_type_key",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "reviews_per_month_observed",
        "activity_proxy",
        "activity_proxy_derived_zero",
        "activity_proxy_is_analyzable",
        "portfolio_size",
        "portfolio_bucket",
        "price_is_valid",
        "minimum_nights_is_valid",
        "coordinate_is_valid",
    ],
    "fact_opportunity_segments.csv": [
        "segment_key",
        "city_key",
        "neighborhood_key",
        "room_type_key",
        "build_id",
        "listing_count",
        "city_supply_share",
        "neighborhood_supply_share",
        "neighborhood_room_type_share",
        "room_type_city_share",
        "activity_analyzable_count",
        "positive_activity_count",
        "active_listing_share",
        "activity_median",
        "activity_iqr",
        "positive_activity_median",
        "activity_p90",
        "activity_p99",
        "valid_price_count",
        "price_median",
        "price_iqr",
        "valid_minimum_nights_count",
        "minimum_nights_median",
        "minimum_nights_p90",
        "probability_superiority",
        "effect_ci_low",
        "effect_ci_high",
        "median_difference",
        "p_value_raw",
        "q_value",
        "sensitivity_status",
        "centroid_latitude",
        "centroid_longitude",
        "coordinate_coverage",
        "quality_flag_count",
        "price_position_percentile_within_city_room_type",
        "eligibility_status",
        "eligibility_reason",
        "opportunity_label",
        "candidate_rank",
    ],
    "fact_statistical_results.csv": [
        "result_id",
        "build_id",
        "analysis_family",
        "city_key",
        "segment_key",
        "metric",
        "comparison",
        "method",
        "sample_size",
        "positive_sample_size",
        "estimate",
        "effect_type",
        "median_difference",
        "ci_low",
        "ci_high",
        "p_value_raw",
        "p_value_adjusted",
        "correction_method",
        "assumption_status",
        "sensitivity_status",
        "interpretation_es",
    ],
    "fact_quality_summary.csv": [
        "build_id",
        "source_id",
        "quality_metric",
        "field",
        "evaluated_count",
        "failed_count",
        "failure_rate",
        "severity",
        "status",
        "interpretation_es",
    ],
    "build_control.csv": [
        "build_id",
        "schema_version",
        "generated_at_utc",
        "source_manifest_hash",
        "analysis_config_hash",
        "source_file_count",
        "source_row_count",
        "canonical_row_count",
        "distinct_listing_key_count",
        "segment_count",
        "output_file",
        "output_row_count",
        "output_sha256",
        "release_gate_status",
    ],
}

PRIMARY_KEYS = {
    "dim_city.csv": ["city_key"],
    "dim_neighborhood.csv": ["neighborhood_key"],
    "dim_room_type.csv": ["room_type_key"],
    "fact_listings.csv": ["listing_key"],
    "fact_opportunity_segments.csv": ["segment_key"],
    "fact_statistical_results.csv": ["result_id"],
    "fact_quality_summary.csv": ["build_id", "source_id", "quality_metric", "field"],
    "build_control.csv": ["output_file"],
}

NUMERIC_COLUMNS = {
    "dim_neighborhood.csv": {"centroid_latitude", "centroid_longitude", "coordinate_coverage"},
    "dim_room_type.csv": {"sort_order"},
    "fact_listings.csv": {
        "price",
        "minimum_nights",
        "number_of_reviews",
        "reviews_per_month_observed",
        "activity_proxy",
        "portfolio_size",
    },
    "fact_opportunity_segments.csv": {
        "listing_count",
        "city_supply_share",
        "neighborhood_supply_share",
        "neighborhood_room_type_share",
        "room_type_city_share",
        "activity_analyzable_count",
        "positive_activity_count",
        "active_listing_share",
        "activity_median",
        "activity_iqr",
        "positive_activity_median",
        "activity_p90",
        "activity_p99",
        "valid_price_count",
        "price_median",
        "price_iqr",
        "valid_minimum_nights_count",
        "minimum_nights_median",
        "minimum_nights_p90",
        "probability_superiority",
        "effect_ci_low",
        "effect_ci_high",
        "median_difference",
        "p_value_raw",
        "q_value",
        "centroid_latitude",
        "centroid_longitude",
        "coordinate_coverage",
        "quality_flag_count",
        "price_position_percentile_within_city_room_type",
        "candidate_rank",
    },
    "fact_statistical_results.csv": {
        "sample_size",
        "positive_sample_size",
        "estimate",
        "ci_low",
        "ci_high",
        "p_value_raw",
        "p_value_adjusted",
    },
    "fact_quality_summary.csv": {"evaluated_count", "failed_count", "failure_rate"},
    "build_control.csv": {
        "source_file_count",
        "source_row_count",
        "canonical_row_count",
        "distinct_listing_key_count",
        "segment_count",
        "output_row_count",
    },
}

BOOLEAN_COLUMNS = {
    "fact_listings.csv": {
        "activity_proxy_derived_zero",
        "activity_proxy_is_analyzable",
        "price_is_valid",
        "minimum_nights_is_valid",
        "coordinate_is_valid",
    }
}


def test_listing_export_publishes_anonymized_observed_portfolio_size(
    powerbi_export_fixture,
) -> None:
    from airbnb_supply_analysis.exports import _build_listing_fact

    listings = powerbi_export_fixture.listings.copy()
    listings["host_id"] = 42

    exported = _build_listing_fact(listings)

    assert exported["portfolio_size"].tolist() == [2, 2]
    assert exported["portfolio_bucket"].tolist() == ["2–5", "2–5"]
    assert "host_id" not in exported.columns


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, keep_default_na=False)


def test_powerbi_exports_have_exact_files_and_ordered_columns(powerbi_export_fixture) -> None:
    directory = powerbi_export_fixture.directory
    assert {path.name for path in directory.glob("*.csv")} == set(EXPECTED_COLUMNS)
    for filename, expected in EXPECTED_COLUMNS.items():
        assert _read(directory / filename).columns.tolist() == expected, filename


def test_powerbi_exports_have_non_null_unique_keys_and_parseable_types(
    powerbi_export_fixture,
) -> None:
    directory = powerbi_export_fixture.directory
    for filename, keys in PRIMARY_KEYS.items():
        frame = _read(directory / filename)
        missing = set(keys).difference(frame.columns)
        assert not missing, f"{filename}: faltan claves {sorted(missing)}"
        assert not frame[keys].isna().any().any(), filename
        assert not frame.duplicated(keys).any(), filename
        for column in NUMERIC_COLUMNS.get(filename, set()):
            assert column in frame, f"{filename}: falta columna numérica {column}"
            present = frame[column].astype(str).ne("")
            assert pd.to_numeric(frame.loc[present, column], errors="coerce").notna().all(), (
                filename,
                column,
            )
        for column in BOOLEAN_COLUMNS.get(filename, set()):
            assert column in frame, f"{filename}: falta columna booleana {column}"
            assert set(frame[column].astype(str)).issubset({"True", "False"}), (filename, column)
        classified = NUMERIC_COLUMNS.get(filename, set()) | BOOLEAN_COLUMNS.get(filename, set())
        assert classified.issubset(set(EXPECTED_COLUMNS[filename])), filename


def test_powerbi_csv_format_is_portable_and_rows_are_stably_key_sorted(
    powerbi_export_fixture,
) -> None:
    directory = powerbi_export_fixture.directory
    for filename, keys in PRIMARY_KEYS.items():
        path = directory / filename
        payload = path.read_bytes()
        assert not payload.startswith(b"\xef\xbb\xbf"), filename
        assert b"\r\n" not in payload, filename
        text = payload.decode("utf-8")
        header = next(csv.reader(text.splitlines()))
        assert header == EXPECTED_COLUMNS[filename], filename
        frame = _read(path)
        expected = frame.sort_values(keys, kind="stable").reset_index(drop=True)
        pd.testing.assert_frame_equal(frame.reset_index(drop=True), expected)


def test_build_control_declares_compatible_semantic_schema(powerbi_export_fixture) -> None:
    control = _read(powerbi_export_fixture.directory / "build_control.csv")
    assert control.columns.tolist() == EXPECTED_COLUMNS["build_control.csv"]
    assert set(control["schema_version"]) == {"1.0.0"}
    assert set(control["release_gate_status"]) == {"pass"}
