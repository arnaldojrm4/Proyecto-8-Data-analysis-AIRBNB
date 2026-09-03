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
    "median_difference",
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


def epsilon_squared(statistic: float, sample_size: int, group_count: int) -> float:
    """Tamaño de efecto acotado para Kruskal-Wallis."""

    if sample_size <= group_count:
        return float("nan")
    return float(np.clip((statistic - group_count + 1) / (sample_size - group_count), 0, 1))


def bounded_effect_ci(effect: float, sample_size: int) -> tuple[float, float]:
    """Intervalo normal aproximado para un efecto acotado en [0, 1]."""

    if not np.isfinite(effect) or sample_size < 2:
        return float("nan"), float("nan")
    margin = 1.96 * sqrt(max(effect * (1 - effect) / sample_size, 0.0))
    return max(0.0, effect - margin), min(1.0, effect + margin)


def clustered_probability_ci(
    first: pd.DataFrame,
    second: pd.DataFrame,
    *,
    iterations: int = 500,
    seed: int = 20260902,
) -> tuple[float, float]:
    """IC percentil remuestreando anfitriones, no anuncios individuales.

    Cada anfitrión aporta la mediana de sus anuncios. El cálculo multinomial sobre los valores
    únicos reproduce el bootstrap por conglomerados sin construir matrices de pares gigantes.
    """

    def host_values(frame: pd.DataFrame) -> np.ndarray:
        usable = frame.dropna(subset=["activity_proxy"]).copy()
        if usable.empty:
            return np.array([], dtype=float)
        if "host_id" not in usable or usable["host_id"].isna().all():
            return usable["activity_proxy"].to_numpy(dtype=float)
        return (
            usable.groupby("host_id", observed=True)["activity_proxy"]
            .median()
            .to_numpy(dtype=float)
        )

    first_values = host_values(first)
    second_values = host_values(second)
    if len(first_values) < 2 or len(second_values) < 2 or iterations < 2:
        return float("nan"), float("nan")
    support = np.union1d(first_values, second_values)
    first_unique, first_frequency = np.unique(first_values, return_counts=True)
    second_unique, second_frequency = np.unique(second_values, return_counts=True)
    first_counts = np.zeros(len(support), dtype=int)
    second_counts = np.zeros(len(support), dtype=int)
    first_counts[np.searchsorted(support, first_unique)] = first_frequency
    second_counts[np.searchsorted(support, second_unique)] = second_frequency
    rng = np.random.default_rng(seed)
    first_boot = rng.multinomial(
        len(first_values), first_counts / len(first_values), size=iterations
    )
    second_boot = rng.multinomial(
        len(second_values), second_counts / len(second_values), size=iterations
    )
    second_less = np.cumsum(second_boot, axis=1) - second_boot
    numerators = (first_boot * (second_less + 0.5 * second_boot)).sum(axis=1)
    effects = numerators / (len(first_values) * len(second_values))
    low, high = np.quantile(effects, [0.025, 0.975])
    return float(low), float(high)


FORBIDDEN_INFERENCE_TERMS = ("demanda", "liquidez", "ocupación", "margen")


def validate_statistical_results(frame: pd.DataFrame) -> None:
    """Falla si una salida inferencial carece de evidencia o usa términos no sustentados."""

    required = (
        "result_id",
        "estimate",
        "ci_low",
        "ci_high",
        "p_value_raw",
        "p_value_adjusted",
        "correction_method",
        "assumption_status",
        "interpretation_es",
    )
    missing_columns = [column for column in required if column not in frame]
    if missing_columns:
        raise ValueError(f"Columnas estadísticas ausentes: {', '.join(missing_columns)}")
    for column in required:
        if frame[column].isna().any():
            raise ValueError(f"Evidencia estadística incompleta en {column}")
    interpretations = frame["interpretation_es"].astype(str).str.lower()
    used = [term for term in FORBIDDEN_INFERENCE_TERMS if interpretations.str.contains(term).any()]
    if used:
        raise ValueError(f"Terminología no sustentada: {', '.join(used)}")


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
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                statistic, pvalue = stats.kruskal(*grouped.values())
        except ValueError:
            statistic, pvalue = 0.0, 1.0
        if not np.isfinite(statistic) or not np.isfinite(pvalue):
            statistic, pvalue = 0.0, 1.0
        effect = epsilon_squared(float(statistic), len(city_frame), len(grouped))
        effect_low, effect_high = bounded_effect_ci(effect, len(city_frame))
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
                estimate=effect,
                effect_type="epsilon_squared",
                ci_low=effect_low,
                ci_high=effect_high,
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
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                test = stats.mannwhitneyu(first, second, alternative="two-sided")
            effect = probability_superiority(first, second)
            low, high = probability_ci(effect, len(first), len(second))
            pairwise_pvalue = float(test.pvalue) if np.isfinite(test.pvalue) else 1.0
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
                    p_value_raw=pairwise_pvalue,
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
    bootstrap_iterations: int = 500,
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
            segment_hosts = segment.groupby("host_id", observed=True)["activity_proxy"].median()
            reference_hosts = reference.groupby("host_id", observed=True)["activity_proxy"].median()
            test = stats.mannwhitneyu(segment_hosts, reference_hosts, alternative="two-sided")
            listing_effect = probability_superiority(values, reference_values)
            host_effect = probability_superiority(segment_hosts, reference_hosts)
            effect = host_effect
            seed = int(sum(ord(character) for character in f"{city}:{neighborhood}:{room_type}"))
            low, high = clustered_probability_ci(
                segment,
                reference,
                iterations=bootstrap_iterations,
                seed=seed,
            )
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
            sensitivity_effects = [listing_effect, host_effect, complete_effect, winsor_effect]
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
                    median_difference=float(values.median() - reference_values.median()),
                    ci_low=low,
                    ci_high=high,
                    p_value_raw=float(test.pvalue),
                    correction_method="benjamini_hochberg_within_city",
                    assumption_status="pass" if np.isfinite([low, high]).all() else "caution",
                    sensitivity_status="robust" if robust else "fragile",
                    interpretation_es=(
                        "Actividad histórica del segmento frente al resto de la misma ciudad y "
                        "tipología, con anfitrión como unidad inferencial; asociación no causal."
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


def run_statistical_analysis(
    frame: pd.DataFrame, build_id: str, *, bootstrap_iterations: int = 500
) -> pd.DataFrame:
    parts = [
        room_type_tests(frame, build_id),
        segment_tests(frame, build_id, bootstrap_iterations=bootstrap_iterations),
        association_tests(frame, build_id),
        two_part_summary(frame, build_id),
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        result = pd.concat(parts, ignore_index=True)[RESULT_COLUMNS]
    validate_statistical_results(result)
    return result
