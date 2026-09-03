"""Imprime un resumen agregado y seguro de los resultados aceptados."""

from __future__ import annotations

import pandas as pd

segments = pd.read_parquet("data/processed/opportunity_segments.parquet")
results = pd.read_parquet("data/processed/statistical_results.parquet")
candidates = segments.query("opportunity_label == 'candidate'")

print("ETIQUETAS")
print(segments["opportunity_label"].value_counts().to_string())
print("\nCANDIDATOS POR CIUDAD")
print(candidates.groupby("city_key", observed=True).size().to_string())
print("\nCANDIDATOS POR CIUDAD Y TIPO")
print(candidates.groupby(["city_key", "room_type"], observed=True).size().to_string())

columns = [
    "city_key",
    "neighborhood",
    "room_type",
    "listing_count",
    "activity_median",
    "probability_superiority",
    "effect_ci_low",
    "q_value",
    "neighborhood_room_type_share",
    "room_type_city_share",
    "candidate_rank",
]
print("\nTOP TRES POR CIUDAD")
top = candidates.sort_values(["city_key", "candidate_rank"])[columns]
print(top.groupby("city_key", observed=True).head(3).to_string(index=False))

print("\nASOCIACIONES SPEARMAN")
association_columns = [
    "city_key",
    "metric",
    "estimate",
    "ci_low",
    "ci_high",
    "p_value_adjusted",
]
print(results.query("method == 'spearman'")[association_columns].to_string(index=False))
