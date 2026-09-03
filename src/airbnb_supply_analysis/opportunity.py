"""Matriz transparente de oportunidades de captación."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd


def classify_opportunity(row: Mapping[str, object]) -> tuple[str, str]:
    analyzable = int(row.get("activity_analyzable_count", 0) or 0)
    positive = int(row.get("positive_activity_count", 0) or 0)
    if analyzable < 30 or positive < 10:
        return "insufficient_evidence", "Muestra inferior a 30 analizables o 10 positivos."
    effect = float(row.get("probability_superiority", np.nan))
    low = float(row.get("effect_ci_low", np.nan))
    qvalue = float(row.get("q_value", np.nan))
    robust = row.get("sensitivity_status") == "robust"
    evidence = (
        np.isfinite(effect)
        and effect >= 0.56
        and np.isfinite(low)
        and low > 0.5
        and np.isfinite(qvalue)
        and qvalue < 0.05
        and robust
    )
    if not evidence:
        return "watch", "El segmento es elegible, pero la evidencia no supera todos los umbrales."
    neighborhood_share = float(row.get("neighborhood_room_type_share", np.nan))
    city_share = float(row.get("room_type_city_share", np.nan))
    lower_local_share = (
        np.isfinite(neighborhood_share)
        and np.isfinite(city_share)
        and neighborhood_share < city_share
    )
    if lower_local_share:
        return "candidate", "Actividad relativa robusta con cuota local inferior a la ciudad."
    return "consolidated", "Actividad relativa robusta sin condición de baja cuota local."


def build_opportunity_matrix(
    listings: pd.DataFrame, segment_results: pd.DataFrame, build_id: str
) -> pd.DataFrame:
    usable = listings.dropna(subset=["city_key", "neighborhood_key", "room_type"])
    city_counts = usable.groupby("city_key", observed=True).size()
    neighborhood_counts = usable.groupby(["city_key", "neighborhood_key"], observed=True).size()
    room_city_counts = usable.groupby(["city_key", "room_type"], observed=True).size()
    rows: list[dict[str, object]] = []
    for (city, neighborhood, room_type), group in usable.groupby(
        ["city_key", "neighborhood_key", "room_type"], observed=True
    ):
        activity = group.loc[group["activity_proxy_is_analyzable"], "activity_proxy"].dropna()
        positive = activity[activity > 0]
        prices = group.loc[group["price_is_valid"], "price"].dropna()
        minimums = group.loc[group["minimum_nights_is_valid"], "minimum_nights"].dropna()
        coordinates = group.loc[group["coordinate_is_valid"], ["latitude", "longitude"]].dropna()
        segment_key = f"{neighborhood}:{room_type}"
        evidence = segment_results.loc[segment_results["segment_key"].eq(segment_key)]
        evidence_row = evidence.iloc[0] if not evidence.empty else None
        row = {
            "segment_key": segment_key,
            "city_key": city,
            "neighborhood_key": neighborhood,
            "neighborhood": group["neighborhood"].iloc[0],
            "room_type": room_type,
            "build_id": build_id,
            "listing_count": len(group),
            "city_supply_share": len(group) / city_counts.loc[city],
            "neighborhood_supply_share": len(group) / neighborhood_counts.loc[(city, neighborhood)],
            "neighborhood_room_type_share": len(group)
            / neighborhood_counts.loc[(city, neighborhood)],
            "room_type_city_share": room_city_counts.loc[(city, room_type)] / city_counts.loc[city],
            "activity_analyzable_count": len(activity),
            "positive_activity_count": len(positive),
            "active_listing_share": float(activity.gt(0).mean()) if len(activity) else np.nan,
            "activity_median": float(activity.median()) if len(activity) else np.nan,
            "activity_iqr": float(activity.quantile(0.75) - activity.quantile(0.25))
            if len(activity)
            else np.nan,
            "positive_activity_median": float(positive.median()) if len(positive) else np.nan,
            "activity_p90": float(activity.quantile(0.90)) if len(activity) else np.nan,
            "activity_p99": float(activity.quantile(0.99)) if len(activity) else np.nan,
            "valid_price_count": len(prices),
            "price_median": float(prices.median()) if len(prices) else np.nan,
            "price_iqr": float(prices.quantile(0.75) - prices.quantile(0.25))
            if len(prices)
            else np.nan,
            "valid_minimum_nights_count": len(minimums),
            "minimum_nights_median": float(minimums.median()) if len(minimums) else np.nan,
            "minimum_nights_p90": float(minimums.quantile(0.90)) if len(minimums) else np.nan,
            "probability_superiority": (
                evidence_row["estimate"] if evidence_row is not None else np.nan
            ),
            "effect_ci_low": evidence_row["ci_low"] if evidence_row is not None else np.nan,
            "effect_ci_high": evidence_row["ci_high"] if evidence_row is not None else np.nan,
            "median_difference": np.nan,
            "p_value_raw": evidence_row["p_value_raw"] if evidence_row is not None else np.nan,
            "q_value": evidence_row["p_value_adjusted"] if evidence_row is not None else np.nan,
            "sensitivity_status": evidence_row["sensitivity_status"]
            if evidence_row is not None
            else "not_run",
            "centroid_latitude": float(coordinates["latitude"].median())
            if len(coordinates)
            else np.nan,
            "centroid_longitude": float(coordinates["longitude"].median())
            if len(coordinates)
            else np.nan,
            "coordinate_coverage": len(coordinates) / len(group),
            "quality_flag_count": int((~group["price_is_valid"]).sum())
            + int((~group["minimum_nights_is_valid"]).sum())
            + int((~group["coordinate_is_valid"]).sum()),
        }
        row["price_position_percentile_within_city_room_type"] = np.nan
        label, reason = classify_opportunity(row)
        row["eligibility_status"] = "eligible" if label != "insufficient_evidence" else "ineligible"
        row["eligibility_reason"] = reason
        row["opportunity_label"] = label
        row["candidate_rank"] = pd.NA
        rows.append(row)
    result = pd.DataFrame(rows)
    result["price_position_percentile_within_city_room_type"] = result.groupby(
        ["city_key", "room_type"], observed=True
    )["price_median"].rank(pct=True, method="average")
    candidates = result.loc[result["opportunity_label"].eq("candidate")].sort_values(
        ["city_key", "listing_count", "probability_superiority", "segment_key"],
        ascending=[True, False, False, True],
    )
    ranks = candidates.groupby("city_key", observed=True).cumcount() + 1
    result.loc[candidates.index, "candidate_rank"] = ranks.astype("Int64")
    return result.sort_values("segment_key", kind="stable").reset_index(drop=True)
