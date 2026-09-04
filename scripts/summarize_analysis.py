"""Imprime un resumen agregado y seguro de los resultados aceptados."""

from __future__ import annotations

import pandas as pd

segments = pd.read_parquet("data/processed/opportunity_segments.parquet")
results = pd.read_parquet("data/processed/statistical_results.parquet")
listings = pd.read_parquet("data/processed/listings.parquet")
candidates = segments.query("opportunity_label == 'candidate'")
analyzable = listings.loc[listings["activity_proxy_is_analyzable"]]

print("ACTIVIDAD POR CIUDAD Y TIPOLOGÍA")
print(
    analyzable.groupby(["city_key", "room_type"], observed=True)
    .agg(
        n=("listing_key", "size"),
        median=("activity_proxy", "median"),
        mean=("activity_proxy", "mean"),
        positive_share=("activity_proxy", lambda values: values.gt(0).mean()),
    )
    .round(3)
    .to_string()
)

print("\nCONTRASTES GLOBALES DE TIPOLOGÍA")
print(
    results.query("method == 'kruskal_wallis'")[
        ["city_key", "estimate", "ci_low", "ci_high", "p_value_adjusted"]
    ]
    .round(4)
    .to_string(index=False)
)

print("\nTRES BARRIOS CON MAYOR MEDIANA DE ACTIVIDAD POR CIUDAD (N>=30)")
neighborhoods = (
    analyzable.groupby(["city_key", "neighborhood"], observed=True)
    .agg(n=("listing_key", "size"), median=("activity_proxy", "median"))
    .query("n >= 30")
    .reset_index()
)
print(
    neighborhoods.sort_values(
        ["city_key", "median", "n"], ascending=[True, False, False]
    )
    .groupby("city_key", observed=True)
    .head(3)
    .round(3)
    .to_string(index=False)
)

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
    "effect_ci_high",
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

print("\nMODELOS AJUSTADOS EN DOS PARTES")
model_columns = [
    "city_key",
    "metric",
    "comparison",
    "estimate",
    "ci_low",
    "ci_high",
    "p_value_raw",
    "sensitivity_status",
]
print(
    results.query("analysis_family == 'sensitivity'")[model_columns]
    .round(4)
    .to_string(index=False)
)
