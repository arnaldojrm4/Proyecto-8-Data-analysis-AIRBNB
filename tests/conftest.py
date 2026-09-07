from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import airbnb_supply_analysis.cli as cli


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def canonical_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "listing_key": ["madrid:1", "madrid:2"],
            "city_key": ["madrid", "madrid"],
            "listing_id": [1, 2],
            "host_id": [10, 20],
            "neighborhood": ["Centro", "Centro"],
            "neighborhood_key": ["madrid:centro", "madrid:centro"],
            "room_type": ["private_room", "entire_home_apt"],
            "price": [75.0, 140.0],
            "minimum_nights": [2, 3],
            "number_of_reviews": [0, 8],
            "reviews_per_month_observed": [pd.NA, 1.2],
            "activity_proxy": [0.0, 1.2],
            "activity_proxy_derived_zero": [True, False],
            "activity_proxy_is_analyzable": [True, True],
        }
    )


@pytest.fixture
def powerbi_export_fixture(tmp_path: Path) -> SimpleNamespace:
    """Publica un conjunto pequeño con secretos rastreables para probar el contrato BI."""

    processed = tmp_path / "processed"
    artifacts = tmp_path / "artifacts"
    powerbi = tmp_path / "powerbi"
    processed.mkdir()
    (artifacts / "quality").mkdir(parents=True)

    raw_listing_ids = (9876543210124, 9876543210123)
    raw_host_ids = (765432100124, 765432100123)
    listings = pd.DataFrame(
        {
            "listing_key": [f"madrid:{value}" for value in raw_listing_ids],
            "city_key": ["madrid", "madrid"],
            "listing_id": raw_listing_ids,
            "host_id": raw_host_ids,
            "listing_name": ["LISTING_SECRET_B", "LISTING_SECRET_A"],
            "host_name": ["HOST_SECRET_B", "HOST_SECRET_A"],
            "neighborhood": ["Centro", "Centro"],
            "neighborhood_key": ["madrid:centro", "madrid:centro"],
            "room_type": ["private_room", "entire_home_apt"],
            "price": [75.0, 140.0],
            "minimum_nights": [2, 3],
            "number_of_reviews": [8, 0],
            "reviews_per_month_observed": [1.2, pd.NA],
            "activity_proxy": [1.2, 0.0],
            "activity_proxy_derived_zero": [False, True],
            "activity_proxy_is_analyzable": [True, True],
            "price_is_valid": [True, True],
            "minimum_nights_is_valid": [True, True],
            "coordinate_is_valid": [True, True],
            "latitude": [40.41691, 40.41681],
            "longitude": [-3.70391, -3.70381],
        }
    )
    opportunities = pd.DataFrame(
        {
            "segment_key": ["madrid:centro:private_room"],
            "city_key": ["madrid"],
            "neighborhood_key": ["madrid:centro"],
            "neighborhood": ["Centro"],
            "room_type": ["private_room"],
            "build_id": ["TESTBUILD"],
            "listing_count": [1],
            "city_supply_share": [0.5],
            "neighborhood_supply_share": [0.5],
            "neighborhood_room_type_share": [0.5],
            "room_type_city_share": [0.5],
            "activity_analyzable_count": [1],
            "positive_activity_count": [1],
            "active_listing_share": [1.0],
            "activity_median": [1.2],
            "activity_iqr": [0.0],
            "positive_activity_median": [1.2],
            "activity_p90": [1.2],
            "activity_p99": [1.2],
            "valid_price_count": [1],
            "price_median": [75.0],
            "price_iqr": [0.0],
            "valid_minimum_nights_count": [1],
            "minimum_nights_median": [2.0],
            "minimum_nights_p90": [2.0],
            "probability_superiority": [0.62],
            "effect_ci_low": [0.54],
            "effect_ci_high": [0.70],
            "median_difference": [0.4],
            "p_value_raw": [0.01],
            "q_value": [0.02],
            "sensitivity_status": ["robust"],
            "centroid_latitude": [40.41686],
            "centroid_longitude": [-3.70386],
            "coordinate_coverage": [1.0],
            "quality_flag_count": [0],
            "price_position_percentile_within_city_room_type": [0.5],
            "eligibility_status": ["eligible"],
            "eligibility_reason": ["Cumple los umbrales bloqueados."],
            "opportunity_label": ["candidate"],
            "candidate_rank": [1],
        }
    )
    statistical = pd.DataFrame(
        {
            "result_id": ["segment:madrid:centro:private_room"],
            "build_id": ["TESTBUILD"],
            "analysis_family": ["segment"],
            "city_key": ["madrid"],
            "segment_key": ["madrid:centro:private_room"],
            "metric": ["activity_proxy"],
            "comparison": ["segment_vs_city"],
            "method": ["mann_whitney_u"],
            "sample_size": [2],
            "positive_sample_size": [1],
            "estimate": [0.62],
            "effect_type": ["probability_superiority"],
            "median_difference": [0.4],
            "ci_low": [0.54],
            "ci_high": [0.70],
            "p_value_raw": [0.01],
            "p_value_adjusted": [0.02],
            "correction_method": ["bh"],
            "assumption_status": ["pass"],
            "sensitivity_status": ["robust"],
            "interpretation_es": ["Actividad histórica; no implica causalidad."],
        }
    )
    quality = pd.DataFrame(
        {
            "finding_id": ["madrid:invalid_price"],
            "build_id": ["TESTBUILD"],
            "source_id": ["madrid"],
            "entity": ["RawListing"],
            "field": ["price"],
            "check_id": ["invalid_price"],
            "dimension": ["validity"],
            "severity": ["warning"],
            "failed_count": [0],
            "evaluated_count": [2],
            "failed_rate": [0.0],
            "disposition": ["accepted_valid"],
            "impact": ["Afecta al contexto local de precio."],
            "rationale": ["La regla no encontró incumplimientos."],
        }
    )
    listings.to_parquet(processed / "listings.parquet", index=False)
    opportunities.to_parquet(processed / "opportunity_segments.parquet", index=False)
    statistical.to_parquet(processed / "statistical_results.parquet", index=False)
    quality.to_parquet(artifacts / "quality" / "findings.parquet", index=False)
    source_manifest = tmp_path / "source-manifest.json"
    source_manifest.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "sources": [
                    {
                        "source_id": "madrid",
                        "city_key": "madrid",
                        "display_city_es": "Madrid",
                        "parsed_row_count": len(listings),
                        "snapshot_date": None,
                        "currency": None,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    analysis_config = tmp_path / "analysis.yml"
    analysis_config.write_text("schema_version: 1.0.0\n", encoding="utf-8")

    exit_code = cli.main(
        [
            "export",
            "--processed-dir",
            str(processed),
            "--artifacts-dir",
            str(artifacts),
            "--powerbi-dir",
            str(powerbi),
            "--source-manifest",
            str(source_manifest),
            "--config",
            str(analysis_config),
            "--build-id",
            "TESTBUILD",
            "--log-format",
            "json",
        ]
    )
    assert exit_code == 0
    return SimpleNamespace(
        directory=powerbi,
        processed=processed,
        artifacts=artifacts,
        source_manifest=source_manifest,
        analysis_config=analysis_config,
        listings=listings,
        opportunities=opportunities,
        raw_listing_ids=raw_listing_ids,
        raw_host_ids=raw_host_ids,
        secret_names=("LISTING_SECRET_A", "LISTING_SECRET_B", "HOST_SECRET_A", "HOST_SECRET_B"),
        raw_coordinates=("40.41691", "40.41681", "-3.70391", "-3.70381"),
    )
