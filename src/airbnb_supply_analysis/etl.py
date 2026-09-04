"""Transformación determinista de fuentes raw al modelo canónico."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from airbnb_supply_analysis.io import read_source
from airbnb_supply_analysis.schemas import validate_canonical, validate_raw_frame

ROOM_TYPE_MAP = {
    "Entire home/apt": "entire_home_apt",
    "Private room": "private_room",
    "Shared room": "shared_room",
    "Hotel room": "hotel_room",
}


def derive_activity_proxy(
    reviews_per_month: pd.Series, number_of_reviews: pd.Series
) -> tuple[pd.Series, pd.Series, pd.Series]:
    observed = pd.to_numeric(reviews_per_month, errors="coerce")
    counts = pd.to_numeric(number_of_reviews, errors="coerce")
    derived = observed.isna() & counts.eq(0)
    proxy = observed.mask(derived, 0.0)
    analyzable = proxy.notna()
    return proxy.astype("Float64"), derived.astype(bool), analyzable.astype(bool)


def _text(series: pd.Series) -> pd.Series:
    result = series.astype("string").str.strip()
    return result.mask(result.eq(""), pd.NA)


def canonicalize_source(
    raw: pd.DataFrame, source_id: str, city_key: str, build_id: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    validate_raw_frame(raw, source_id)
    source_columns = set(raw.columns)
    listing_id = pd.to_numeric(raw["id"], errors="coerce").astype("int64")
    host_id = pd.to_numeric(raw["host_id"], errors="coerce").astype("int64")
    neighborhood = _text(raw["neighbourhood"])
    room_type = _text(raw["room_type"]).map(ROOM_TYPE_MAP).astype("string")
    price_numeric = pd.to_numeric(raw["price"], errors="coerce")
    price_valid = price_numeric.gt(0)
    minimum_numeric = pd.to_numeric(raw["minimum_nights"], errors="coerce")
    minimum_valid = minimum_numeric.ge(1) & np.isclose(minimum_numeric % 1, 0)
    reviews = pd.to_numeric(raw["number_of_reviews"], errors="coerce")
    reviews = reviews.where(reviews.ge(0))
    activity, derived_zero, analyzable = derive_activity_proxy(
        raw["reviews_per_month"], reviews
    )
    latitude = pd.to_numeric(raw["latitude"], errors="coerce")
    longitude = pd.to_numeric(raw["longitude"], errors="coerce")
    coordinate_valid = latitude.between(-90, 90) & longitude.between(-180, 180)
    host_count_available = "calculated_host_listings_count" in source_columns
    availability_available = "availability_365" in source_columns
    group_available = "neighbourhood_group" in source_columns
    host_count = (
        pd.to_numeric(raw["calculated_host_listings_count"], errors="coerce")
        if host_count_available
        else pd.Series(pd.NA, index=raw.index, dtype="Float64")
    )
    availability = (
        pd.to_numeric(raw["availability_365"], errors="coerce")
        if availability_available
        else pd.Series(pd.NA, index=raw.index, dtype="Float64")
    )
    neighborhood_group = (
        _text(raw["neighbourhood_group"])
        if group_available
        else pd.Series(pd.NA, index=raw.index, dtype="string")
    )
    raw_hash = pd.util.hash_pandas_object(raw, index=False).map(lambda value: f"{value:016X}")
    canonical = pd.DataFrame(
        {
            "listing_key": city_key + ":" + listing_id.astype(str),
            "city_key": city_key,
            "listing_id": listing_id,
            "listing_name": _text(raw["name"]),
            "host_id": host_id,
            "host_name": _text(raw["host_name"]),
            "neighborhood_group": neighborhood_group,
            "neighborhood": neighborhood,
            "neighborhood_key": city_key + ":" + neighborhood.str.casefold(),
            "latitude": latitude.where(coordinate_valid),
            "longitude": longitude.where(coordinate_valid),
            "room_type": room_type,
            "price": price_numeric.where(price_valid),
            "price_is_valid": price_valid.fillna(False),
            "minimum_nights": minimum_numeric.where(minimum_valid).astype("Int64"),
            "minimum_nights_is_valid": minimum_valid.fillna(False),
            "number_of_reviews": reviews.astype("Int64"),
            "last_review": pd.to_datetime(raw["last_review"], errors="coerce", format="mixed"),
            "reviews_per_month_observed": pd.to_numeric(
                raw["reviews_per_month"], errors="coerce"
            ).astype("Float64"),
            "has_historical_activity": reviews.gt(0).astype("boolean"),
            "activity_proxy": activity,
            "activity_proxy_derived_zero": derived_zero,
            "activity_proxy_is_analyzable": analyzable,
            "calculated_host_listings_count": host_count.astype("Int64"),
            "availability_365": availability.astype("Int64"),
            "neighborhood_group_source_available": group_available,
            "host_listing_count_source_available": host_count_available,
            "availability_365_source_available": availability_available,
            "coordinate_is_valid": coordinate_valid.fillna(False),
            "source_id": source_id,
            "source_record_number": np.arange(1, len(raw) + 1, dtype=np.int64),
            "raw_record_hash": raw_hash,
        }
    )
    changes = [
        {
            "transformation_id": f"{source_id}:activity_proxy_derived_zero",
            "build_id": build_id,
            "source_id": source_id,
            "input_entity": "RawListing",
            "output_entity": "CanonicalListing",
            "field": "activity_proxy",
            "rule": "Derivar 0 solo si reviews_per_month falta y number_of_reviews es 0.",
            "rationale": "Distingue ausencia histórica de actividad de tasa desconocida.",
            "rows_evaluated": len(raw),
            "rows_changed": int(derived_zero.sum()),
            "rows_rejected": 0,
            "before_summary": f"missing={int(raw['reviews_per_month'].isna().sum())}",
            "after_summary": f"derived_zero={int(derived_zero.sum())}",
        },
        {
            "transformation_id": f"{source_id}:source_availability",
            "build_id": build_id,
            "source_id": source_id,
            "input_entity": "RawListing",
            "output_entity": "CanonicalListing",
            "field": "source_availability_flags",
            "rule": "Conservar nulos y marcar disponibilidad estructural por fuente.",
            "rationale": "Evita reemplazar ausencia de columna por cero.",
            "rows_evaluated": len(raw),
            "rows_changed": (
                len(raw)
                if not all((group_available, host_count_available, availability_available))
                else 0
            ),
            "rows_rejected": 0,
            "before_summary": f"columns={len(source_columns)}",
            "after_summary": "availability_flags_added=true",
        },
    ]
    return canonical, pd.DataFrame(changes)


def build_canonical(
    raw_dir: Path, manifest: dict[str, object], build_id: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    canonical_parts = []
    transformation_parts = []
    for source in manifest["sources"]:
        raw = read_source(raw_dir, source)
        canonical, transformations = canonicalize_source(
            raw, source["source_id"], source["city_key"], build_id
        )
        canonical_parts.append(canonical)
        transformation_parts.append(transformations)
    combined = pd.concat(canonical_parts, ignore_index=True)
    transformations = pd.concat(transformation_parts, ignore_index=True)
    return validate_canonical(combined), transformations
