from __future__ import annotations

import pandas as pd
import pytest


def _listings() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "listing_key": ["a", "b", "c", "d"],
            "neighborhood_key": ["n1", "n1", "n2", "n2"],
            "activity_proxy": [2.0, 0.0, 1.0, pd.NA],
            "activity_proxy_is_analyzable": [True, True, True, False],
            "number_of_reviews": [8, 2, 0, 0],
            "portfolio_bucket": ["1", "2–5", "2–5", ">10"],
        }
    )


def _neighborhoods() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "neighborhood_key": ["n1", "n2"],
            "neighborhood_label": ["Centro", "Norte"],
            "centroid_latitude": [40.4, 40.5],
            "centroid_longitude": [-3.7, -3.6],
        }
    )


def test_neighborhood_metrics_excludes_unknown_activity_from_denominator() -> None:
    from dashboard.market_structure import neighborhood_metrics

    result = neighborhood_metrics(_listings(), _neighborhoods(), min_listings=1).set_index(
        "neighborhood_key"
    )

    assert result.loc["n1", "listing_count"] == 2
    assert result.loc["n1", "activity_per_listing"] == pytest.approx(1.0)
    assert result.loc["n2", "activity_per_listing"] == pytest.approx(1.0)
    assert result.loc["n2", "activity_coverage"] == pytest.approx(0.5)


def test_pareto_metrics_reports_real_top_share_and_listing_share_for_80() -> None:
    from dashboard.market_structure import pareto_metrics

    result = pareto_metrics(_listings())

    assert result["top20_review_share"] == pytest.approx(0.8)
    assert result["listing_share_for_80"] == pytest.approx(0.25)


def test_portfolio_mix_keeps_all_exclusive_buckets() -> None:
    from dashboard.market_structure import portfolio_mix

    result = portfolio_mix(_listings()).set_index("portfolio_bucket")

    assert result.index.tolist() == ["1", "2–5", "6–10", ">10"]
    assert result.loc["1", "listing_share"] == pytest.approx(0.25)
    assert result.loc["2–5", "listing_share"] == pytest.approx(0.50)
    assert result.loc["6–10", "listing_share"] == pytest.approx(0.0)
    assert result["listing_share"].sum() == pytest.approx(1.0)
