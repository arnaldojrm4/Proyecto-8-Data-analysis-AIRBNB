"""Cálculos puros para la vista de estructura del mercado."""

from __future__ import annotations

import numpy as np
import pandas as pd

PORTFOLIO_ORDER = ["1", "2–5", "6–10", ">10"]


def neighborhood_metrics(
    listings: pd.DataFrame,
    neighborhoods: pd.DataFrame,
    *,
    min_listings: int = 1,
) -> pd.DataFrame:
    """Agrega oferta, actividad y cobertura al grano de barrio."""

    frame = listings.copy()
    analyzable = frame["activity_proxy_is_analyzable"].fillna(False).astype(bool)
    frame["analyzable_activity"] = frame["activity_proxy"].where(analyzable)
    summary = (
        frame.groupby("neighborhood_key", observed=True)
        .agg(
            listing_count=("listing_key", "nunique"),
            analyzable_count=("analyzable_activity", "count"),
            activity_per_listing=("analyzable_activity", "mean"),
        )
        .reset_index()
    )
    summary["activity_coverage"] = summary["analyzable_count"] / summary["listing_count"]
    labels = neighborhoods[
        [
            "neighborhood_key",
            "neighborhood_label",
            "centroid_latitude",
            "centroid_longitude",
        ]
    ]
    return (
        summary.merge(labels, on="neighborhood_key", how="left", validate="one_to_one")
        .loc[lambda data: data["listing_count"].ge(min_listings)]
        .sort_values("activity_per_listing", ascending=False, kind="stable")
        .reset_index(drop=True)
    )


def pareto_metrics(listings: pd.DataFrame) -> dict[str, float]:
    """Calcula la concentración real sin asumir una regla 80/20."""

    values = (
        pd.to_numeric(listings["number_of_reviews"], errors="coerce")
        .fillna(0)
        .clip(lower=0)
        .sort_values(ascending=False)
        .to_numpy()
    )
    if len(values) == 0 or values.sum() == 0:
        return {"top20_review_share": 0.0, "listing_share_for_80": 0.0}
    top_count = max(1, int(np.ceil(len(values) * 0.20)))
    cumulative = np.cumsum(values) / values.sum()
    return {
        "top20_review_share": float(values[:top_count].sum() / values.sum()),
        "listing_share_for_80": float((np.searchsorted(cumulative, 0.80) + 1) / len(values)),
    }


def pareto_curve(listings: pd.DataFrame) -> pd.DataFrame:
    """Devuelve los puntos acumulados ordenados de mayor a menor."""

    values = (
        pd.to_numeric(listings["number_of_reviews"], errors="coerce")
        .fillna(0)
        .clip(lower=0)
        .sort_values(ascending=False)
        .to_numpy()
    )
    if len(values) == 0 or values.sum() == 0:
        return pd.DataFrame(columns=["listing_share", "review_share"])
    return pd.DataFrame(
        {
            "listing_share": np.arange(1, len(values) + 1) / len(values),
            "review_share": np.cumsum(values) / values.sum(),
        }
    )


def portfolio_mix(listings: pd.DataFrame) -> pd.DataFrame:
    """Calcula el reparto de anuncios en grupos de cartera excluyentes."""

    counts = listings["portfolio_bucket"].value_counts().reindex(PORTFOLIO_ORDER, fill_value=0)
    denominator = counts.sum()
    shares = counts / denominator if denominator else counts.astype(float)
    return pd.DataFrame(
        {
            "portfolio_bucket": PORTFOLIO_ORDER,
            "listing_count": counts.to_numpy(),
            "listing_share": shares.to_numpy(),
        }
    )
