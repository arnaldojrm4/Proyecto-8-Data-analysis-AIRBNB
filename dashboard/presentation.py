"""Presentación ejecutiva, formatos y proyecciones seguras."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from dashboard.data import DashboardDataset
from dashboard.filters import canonical_evidence_status


@dataclass(frozen=True)
class ExecutiveMetrics:
    listing_count: int
    neighborhood_count: int
    candidate_count: int
    median_activity: float
    median_price: float


def summary_metrics(
    listings: pd.DataFrame,
    opportunities: pd.DataFrame,
) -> ExecutiveMetrics:
    """Resume la población activa sin fabricar una puntuación."""

    candidates = (
        int(opportunities["opportunity_label"].eq("candidate").sum())
        if "opportunity_label" in opportunities
        else 0
    )
    neighborhood_count = (
        int(listings["neighborhood_key"].nunique()) if "neighborhood_key" in listings else 0
    )
    activity = pd.to_numeric(listings.get("activity_proxy"), errors="coerce")
    price = pd.to_numeric(listings.get("price"), errors="coerce")
    return ExecutiveMetrics(
        listing_count=len(listings),
        neighborhood_count=neighborhood_count,
        candidate_count=candidates,
        median_activity=float(activity.median()) if activity.notna().any() else float("nan"),
        median_price=float(price.median()) if price.notna().any() else float("nan"),
    )


OPPORTUNITY_COLUMNS = {
    "city_label_es": "Ciudad",
    "neighborhood_label": "Barrio",
    "room_type_label_es": "Tipología",
    "listing_count": "Anuncios",
    "city_supply_share": "Cuota de oferta ciudad",
    "active_listing_share": "Cuota con actividad",
    "activity_median": "Actividad mediana",
    "activity_iqr": "Dispersión actividad",
    "price_median": "Precio mediano local",
    "price_iqr": "Dispersión precio",
    "probability_superiority": "Probabilidad de superioridad",
    "effect_ci_low": "Intervalo inferior",
    "effect_ci_high": "Intervalo superior",
    "q_value": "Valor p ajustado",
    "sensitivity_status": "Sensibilidad",
    "eligibility_status": "Elegibilidad",
    "eligibility_reason": "Motivo de elegibilidad",
    "opportunity_label": "Clasificación",
    "candidate_rank": "Rango candidato",
}


def _labeled_opportunities(
    dataset: DashboardDataset,
    opportunities: pd.DataFrame,
) -> pd.DataFrame:
    return (
        opportunities.merge(
            dataset.cities[["city_key", "city_label_es"]],
            on="city_key",
            how="left",
            validate="many_to_one",
        )
        .merge(
            dataset.neighborhoods[["neighborhood_key", "neighborhood_label"]],
            on="neighborhood_key",
            how="left",
            validate="many_to_one",
        )
        .merge(
            dataset.room_types[["room_type_key", "room_type_label_es"]],
            on="room_type_key",
            how="left",
            validate="many_to_one",
        )
    )


def labeled_opportunities(
    dataset: DashboardDataset,
    opportunities: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Añade etiquetas de presentación sin retirar aún los centroides agregados."""

    source = dataset.opportunities if opportunities is None else opportunities
    return _labeled_opportunities(dataset, source)


def opportunity_table(
    dataset: DashboardDataset,
    opportunities: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Proyecta una allowlist sin claves técnicas ni coordenadas."""

    labeled = labeled_opportunities(dataset, opportunities)
    columns = [column for column in OPPORTUNITY_COLUMNS if column in labeled]
    table = labeled[columns].rename(columns=OPPORTUNITY_COLUMNS)
    if "Rango candidato" in table:
        table = table.sort_values(
            ["Rango candidato", "Actividad mediana"],
            na_position="last",
            kind="stable",
        )
    return table.reset_index(drop=True)


def opportunity_csv(table: pd.DataFrame) -> bytes:
    """Serializa exactamente la proyección visible y segura."""

    return table.to_csv(index=False, lineterminator="\n").encode("utf-8")


EVIDENCE_COLUMNS = {
    "city_label_es": "Ciudad",
    "neighborhood_label": "Barrio",
    "room_type_label_es": "Tipología",
    "analysis_family": "Familia",
    "metric": "Métrica",
    "comparison": "Comparación",
    "method": "Método",
    "sample_size": "Muestra",
    "positive_sample_size": "Muestra positiva",
    "estimate": "Efecto",
    "effect_type": "Tipo de efecto",
    "median_difference": "Diferencia de medianas",
    "ci_low": "Intervalo inferior",
    "ci_high": "Intervalo superior",
    "p_value_raw": "Valor p crudo",
    "p_value_adjusted": "Valor p ajustado",
    "correction_method": "Corrección",
    "assumption_status": "Supuestos",
    "sensitivity_status": "Sensibilidad",
    "interpretation_es": "Interpretación",
}


def _effect_magnitude(effect_type: object, estimate: float) -> str:
    kind = str(effect_type)
    value = abs(float(estimate))
    if kind == "spearman_rho":
        return "muy débil" if value < 0.1 else "pequeño" if value < 0.3 else "moderado"
    if kind == "epsilon_squared":
        return "muy pequeño" if value < 0.01 else "pequeño" if value < 0.06 else "moderado"
    if kind == "probability_superiority":
        distance = abs(value - 0.5)
        return "muy pequeño" if distance < 0.06 else "pequeño" if distance < 0.14 else "moderado"
    if kind in {"odds_ratio", "geometric_mean_ratio"}:
        distance = abs(value - 1.0)
        return "muy pequeño" if distance < 0.1 else "pequeño" if distance < 0.3 else "moderado"
    return "no clasificado"


def evidence_summary(result: pd.Series) -> str:
    """Traduce una fila sin ocultar significación, magnitud ni sensibilidad."""

    adjusted = float(result["p_value_adjusted"])
    significance = (
        "hay evidencia estadística al 5%"
        if adjusted < 0.05
        else "no hay evidencia estadística suficiente al 5%"
    )
    magnitude = _effect_magnitude(result["effect_type"], float(result["estimate"]))
    sensitivity = canonical_evidence_status(result.get("sensitivity_status"))
    return (
        f"{significance}; efecto {magnitude}; sensibilidad {sensitivity}. "
        "La asociación no implica causalidad ni demuestra demanda, ocupación o ingresos."
    )


def evidence_table(
    dataset: DashboardDataset,
    statistics: pd.DataFrame,
) -> pd.DataFrame:
    """Proyecta evidencia con etiquetas y sin claves técnicas."""

    segment_context = dataset.opportunities[
        ["segment_key", "neighborhood_key", "room_type_key"]
    ].drop_duplicates("segment_key")
    labeled = (
        statistics.merge(segment_context, on="segment_key", how="left", validate="many_to_one")
        .merge(
            dataset.cities[["city_key", "city_label_es"]],
            on="city_key",
            how="left",
            validate="many_to_one",
        )
        .merge(
            dataset.neighborhoods[["neighborhood_key", "neighborhood_label"]],
            on="neighborhood_key",
            how="left",
            validate="many_to_one",
        )
        .merge(
            dataset.room_types[["room_type_key", "room_type_label_es"]],
            on="room_type_key",
            how="left",
            validate="many_to_one",
        )
    )
    columns = [column for column in EVIDENCE_COLUMNS if column in labeled]
    return labeled[columns].rename(columns=EVIDENCE_COLUMNS).reset_index(drop=True)
