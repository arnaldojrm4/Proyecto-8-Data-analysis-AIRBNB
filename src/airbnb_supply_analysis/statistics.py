"""Estadística no paramétrica y sensibilidad para la actividad histórica."""

from __future__ import annotations

import warnings
from itertools import combinations
from math import atanh, sqrt, tanh

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

RESULT_COLUMNS = [
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
    "ci_low",
    "ci_high",
    "p_value_raw",
    "p_value_adjusted",
    "correction_method",
    "assumption_status",
    "sensitivity_status",
    "interpretation_es",
]


def adjust_pvalues(pvalues: list[float] | pd.Series, method: str) -> np.ndarray:
    if not len(pvalues):
        return np.array([], dtype=float)
    normalized = "fdr_bh" if method in {"bh", "benjamini-hochberg"} else method
    return multipletests(np.asarray(pvalues, dtype=float), method=normalized)[1]


def probability_superiority(first: pd.Series, second: pd.Series) -> float:
    first = pd.to_numeric(first, errors="coerce").dropna()
    second = pd.to_numeric(second, errors="coerce").dropna()
    if first.empty or second.empty:
        return float("nan")
    statistic = stats.mannwhitneyu(first, second, alternative="two-sided").statistic
    return float(statistic / (len(first) * len(second)))


def probability_ci(effect: float, n_first: int, n_second: int) -> tuple[float, float]:
    """Intervalo normal aproximado de AUC/Vargha-Delaney, acotado a [0, 1]."""

    if not np.isfinite(effect) or n_first < 2 or n_second < 2:
        return float("nan"), float("nan")
    q1 = effect / (2 - effect) if effect < 1 else 1.0
    q2 = 2 * effect**2 / (1 + effect) if effect > 0 else 0.0
    variance = (
        effect * (1 - effect)
        + (n_first - 1) * (q1 - effect**2)
        + (n_second - 1) * (q2 - effect**2)
    ) / (n_first * n_second)
    margin = 1.96 * sqrt(max(variance, 0.0))
    return max(0.0, effect - margin), min(1.0, effect + margin)


def _row(**values) -> dict[str, object]:
    base = {column: None for column in RESULT_COLUMNS}
    base.update(
        {
            "assumption_status": "not_applicable",
            "sensitivity_status": "not_run",
        }
    )
    base.update(values)
    return base


def _room_type_ratio(model) -> tuple[float, float, float, float, str]:
    """Extrae un contraste de tipología y lo expresa como razón multiplicativa."""

    candidates = [name for name in model.params.index if name.startswith("C(room_type)")]
    preferred = [name for name in candidates if "[T.private_room]" in name]
    if not candidates:
        return (float("nan"),) * 4 + ("sin contraste estimable",)
    term = preferred[0] if preferred else candidates[0]
    interval = model.conf_int().loc[term]
    values = np.exp(
        np.clip(
            [model.params.loc[term], interval.iloc[0], interval.iloc[1]],
            -700,
            700,
        )
    )
    return (
        float(values[0]),
        float(values[1]),
        float(values[2]),
        float(model.pvalues.loc[term]),
        term,
    )


def room_type_tests(frame: pd.DataFrame, build_id: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for city, city_frame in frame.dropna(subset=["activity_proxy", "room_type"]).groupby(
        "city_key", observed=True
    ):
        grouped = {
            str(name): group["activity_proxy"].astype(float)
            for name, group in city_frame.groupby("room_type", observed=True)
            if len(group) >= 2
        }
        if len(grouped) < 2:
            continue
        try:
            statistic, pvalue = stats.kruskal(*grouped.values())
        except ValueError:
            statistic, pvalue = 0.0, 1.0
        rows.append(
            _row(
                result_id=f"room_type:{city}:omnibus",
                build_id=build_id,
                analysis_family="room_type",
                city_key=city,
                metric="activity_proxy",
                comparison="tipologías dentro de la ciudad",
                method="kruskal_wallis",
                sample_size=len(city_frame),
                estimate=float(statistic),
                effect_type="kruskal_h",
                p_value_raw=float(pvalue),
                correction_method="holm_across_cities",
                interpretation_es=(
                    "Contraste global de actividad histórica entre tipologías dentro de la ciudad; "
                    "no implica causalidad."
                ),
            )
        )
        ordered = sorted(grouped, key=lambda name: grouped[name].median(), reverse=True)
        for first_name, second_name in combinations(ordered, 2):
            first, second = grouped[first_name], grouped[second_name]
            test = stats.mannwhitneyu(first, second, alternative="two-sided")
            effect = probability_superiority(first, second)
            low, high = probability_ci(effect, len(first), len(second))
            rows.append(
                _row(
                    result_id=f"room_type:{city}:{first_name}:{second_name}",
                    build_id=build_id,
                    analysis_family="room_type",
                    city_key=city,
                    metric="activity_proxy",
                    comparison=f"{first_name} frente a {second_name}",
                    method="mann_whitney_u",
                    sample_size=len(first) + len(second),
                    estimate=effect,
                    effect_type="probability_superiority",
                    ci_low=low,
                    ci_high=high,
                    p_value_raw=float(test.pvalue),
                    correction_method="holm_pairwise_family",
                    interpretation_es=(
                        "Probabilidad de superioridad de actividad histórica; "
                        "no implica causalidad."
                    ),
                )
            )
    result = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    for method in ("kruskal_wallis", "mann_whitney_u"):
        mask = result["method"].eq(method)
        if mask.any():
            result.loc[mask, "p_value_adjusted"] = adjust_pvalues(
                result.loc[mask, "p_value_raw"].tolist(), "holm"
            )
    return result


def segment_tests(
    frame: pd.DataFrame,
    build_id: str,
    minimum_n: int = 30,
    minimum_positive: int = 10,
) -> pd.DataFrame:
    usable = frame.dropna(subset=["activity_proxy", "city_key", "room_type", "neighborhood_key"])
    rows: list[dict[str, object]] = []
    for (city, room_type), population in usable.groupby(["city_key", "room_type"], observed=True):
        for neighborhood, segment in population.groupby("neighborhood_key", observed=True):
            values = segment["activity_proxy"].astype(float)
            if len(values) < minimum_n or int(values.gt(0).sum()) < minimum_positive:
                continue
            reference = population.loc[population["neighborhood_key"] != neighborhood]
            reference_values = reference["activity_proxy"].astype(float)
            if len(reference_values) < minimum_n:
                continue
            test = stats.mannwhitneyu(values, reference_values, alternative="two-sided")
            effect = probability_superiority(values, reference_values)
            low, high = probability_ci(effect, len(values), len(reference_values))
            segment_hosts = segment.groupby("host_id", observed=True)["activity_proxy"].median()
            reference_hosts = reference.groupby("host_id", observed=True)["activity_proxy"].median()
            host_effect = probability_superiority(segment_hosts, reference_hosts)
            complete_segment = segment.loc[
                ~segment.get(
                    "activity_proxy_derived_zero",
                    pd.Series(False, index=segment.index),
                ).astype(bool),
                "activity_proxy",
            ]
            complete_reference = reference.loc[
                ~reference.get(
                    "activity_proxy_derived_zero",
                    pd.Series(False, index=reference.index),
                ).astype(bool),
                "activity_proxy",
            ]
            complete_effect = probability_superiority(complete_segment, complete_reference)
            lower, upper = population["activity_proxy"].quantile([0.01, 0.99])
            winsor_effect = probability_superiority(
                values.clip(lower, upper), reference_values.clip(lower, upper)
            )
            sensitivity_effects = [effect, host_effect, complete_effect, winsor_effect]
            robust = len(values) >= max(minimum_n, 50) and all(
                np.isfinite(candidate) and candidate >= 0.56
                for candidate in sensitivity_effects
            )
            segment_key = f"{neighborhood}:{room_type}"
            rows.append(
                _row(
                    result_id=f"segment:{segment_key}",
                    build_id=build_id,
                    analysis_family="segment",
                    city_key=city,
                    segment_key=segment_key,
                    metric="activity_proxy",
                    comparison="segmento frente al resto de la misma ciudad y tipología",
                    method="mann_whitney_u",
                    sample_size=len(values) + len(reference_values),
                    positive_sample_size=int(values.gt(0).sum()),
                    estimate=effect,
                    effect_type="probability_superiority",
                    ci_low=low,
                    ci_high=high,
                    p_value_raw=float(test.pvalue),
                    correction_method="benjamini_hochberg_within_city",
                    assumption_status="caution",
                    sensitivity_status="robust" if robust else "fragile",
                    interpretation_es=(
                        "Actividad histórica del segmento frente al resto de la misma ciudad y "
                        "tipología; asociación no causal."
                    ),
                )
            )
    result = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    if result.empty:
        return result
    for city, indexes in result.groupby("city_key", observed=True).groups.items():
        del city
        result.loc[indexes, "p_value_adjusted"] = adjust_pvalues(
            result.loc[indexes, "p_value_raw"].tolist(), "fdr_bh"
        )
    return result


def association_tests(frame: pd.DataFrame, build_id: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    metrics = {"price": "price_vs_activity", "minimum_nights": "minimum_nights_vs_activity"}
    for city, city_frame in frame.groupby("city_key", observed=True):
        for field, metric in metrics.items():
            sample = city_frame[[field, "activity_proxy"]].dropna()
            if len(sample) < 4 or sample[field].nunique() < 2:
                continue
            result = stats.spearmanr(sample[field], sample["activity_proxy"])
            rho = float(result.statistic)
            if len(sample) > 3 and abs(rho) < 1:
                margin = 1.96 / sqrt(len(sample) - 3)
                low, high = tanh(atanh(rho) - margin), tanh(atanh(rho) + margin)
            else:
                low, high = rho, rho
            rows.append(
                _row(
                    result_id=f"association:{city}:{field}",
                    build_id=build_id,
                    analysis_family="association",
                    city_key=city,
                    metric=metric,
                    comparison=f"{field} y actividad histórica dentro de ciudad",
                    method="spearman",
                    sample_size=len(sample),
                    estimate=rho,
                    effect_type="spearman_rho",
                    ci_low=low,
                    ci_high=high,
                    p_value_raw=float(result.pvalue),
                    correction_method="benjamini_hochberg_across_12",
                    interpretation_es=(
                        "Asociación monotónica dentro de ciudad; no implica causalidad ni ingresos."
                    ),
                )
            )
    output = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    if not output.empty:
        output["p_value_adjusted"] = adjust_pvalues(output["p_value_raw"].tolist(), "fdr_bh")
    return output


def two_part_summary(frame: pd.DataFrame, build_id: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for city, city_frame in frame.dropna(subset=["activity_proxy", "room_type"]).groupby(
        "city_key", observed=True
    ):
        model_frame = city_frame.copy()
        if model_frame["room_type"].nunique() < 2:
            continue
        predictors = "C(room_type)"
        if "neighborhood_key" in model_frame:
            eligible = model_frame["neighborhood_key"].value_counts()
            eligible = eligible.loc[eligible >= 30]
            model_frame = model_frame.loc[
                model_frame["neighborhood_key"].isin(eligible.index)
            ].copy()
            if model_frame["neighborhood_key"].nunique() > 1:
                predictors += " + C(neighborhood_key)"
        model_frame["activity_present"] = model_frame["activity_proxy"].gt(0).astype(int)
        model_frame["log_positive_activity"] = np.log1p(model_frame["activity_proxy"])
        presence = (float("nan"),) * 4 + ("sin contraste estimable",)
        intensity = (float("nan"),) * 4 + ("sin contraste estimable",)
        status = "fragile"
        assumption = "caution"
        if len(model_frame) >= 20:
            try:
                presence_model = smf.glm(
                    f"activity_present ~ {predictors}",
                    data=model_frame,
                    family=sm.families.Binomial(),
                ).fit(maxiter=100, disp=0)
                presence = _room_type_ratio(presence_model)
                positive = model_frame.loc[model_frame["activity_proxy"].gt(0)].copy()
                if len(positive) >= 20:
                    covariance = (
                        {"cov_type": "cluster", "cov_kwds": {"groups": positive["host_id"]}}
                        if "host_id" in positive and positive["host_id"].nunique() > 1
                        else {}
                    )
                    intensity_model = smf.ols(
                        f"log_positive_activity ~ {predictors}", data=positive
                    ).fit(**covariance)
                    intensity = _room_type_ratio(intensity_model)
                    directions_agree = (presence[0] - 1) * (intensity[0] - 1) > 0
                    both_significant = presence[3] < 0.05 and intensity[3] < 0.05
                    if directions_agree and both_significant:
                        status = "robust"
                    elif not directions_agree:
                        status = "conflicting"
                    assumption = (
                        "pass"
                        if np.isfinite([*presence[:3], *intensity[:3]]).all()
                        else "caution"
                    )
            except (ValueError, np.linalg.LinAlgError):
                status = "conflicting"
        specifications = (
            (
                "activity_presence",
                *presence,
                "binomial_glm_adjusted",
                "odds_ratio",
            ),
            (
                "positive_activity_intensity",
                *intensity,
                "ols_log_positive_adjusted",
                "geometric_mean_ratio",
            ),
        )
        for metric, estimate, low, high, pvalue, term, method, effect_type in specifications:
            rows.append(
                _row(
                    result_id=f"sensitivity:{city}:{metric}",
                    build_id=build_id,
                    analysis_family="sensitivity",
                    city_key=city,
                    metric=metric,
                    comparison=f"{term}; ajustado por barrio elegible dentro de ciudad",
                    method=method,
                    sample_size=len(model_frame),
                    estimate=estimate,
                    effect_type=effect_type,
                    ci_low=low,
                    ci_high=high,
                    p_value_raw=pvalue,
                    p_value_adjusted=pvalue,
                    correction_method="not_applicable_sensitivity",
                    assumption_status=assumption,
                    sensitivity_status=status,
                    interpretation_es=(
                        "Modelo ajustado por tipología y barrio elegible; sensibilidad no causal."
                    ),
                )
            )
    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


def run_statistical_analysis(frame: pd.DataFrame, build_id: str) -> pd.DataFrame:
    parts = [
        room_type_tests(frame, build_id),
        segment_tests(frame, build_id),
        association_tests(frame, build_id),
        two_part_summary(frame, build_id),
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        return pd.concat(parts, ignore_index=True)[RESULT_COLUMNS]
