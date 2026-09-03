from __future__ import annotations

import pandas as pd
import pytest

from airbnb_supply_analysis.opportunity import build_opportunity_matrix
from airbnb_supply_analysis.statistics import run_statistical_analysis


@pytest.mark.full_data
def test_full_analysis_produces_traceable_and_rule_compliant_opportunities(project_root) -> None:
    listings = pd.read_parquet(project_root / "data/processed/listings.parquet")

    results = run_statistical_analysis(listings, "test-build")
    segment_results = results.loc[results["analysis_family"].eq("segment")]
    opportunities = build_opportunity_matrix(listings, segment_results, "test-build")

    assert results.query("method == 'kruskal_wallis'")["city_key"].nunique() == 6
    assert len(results.query("method == 'spearman'")) == 12
    assert len(opportunities) == 1_497
    assert opportunities["segment_key"].is_unique
    candidates = opportunities.query("opportunity_label == 'candidate'")
    assert candidates["activity_analyzable_count"].ge(30).all()
    assert candidates["positive_activity_count"].ge(10).all()
    assert candidates["probability_superiority"].ge(0.56).all()
    assert candidates["effect_ci_low"].gt(0.5).all()
    assert candidates["q_value"].lt(0.05).all()
    assert candidates["sensitivity_status"].eq("robust").all()
    assert (
        candidates["neighborhood_room_type_share"] < candidates["room_type_city_share"]
    ).all()
