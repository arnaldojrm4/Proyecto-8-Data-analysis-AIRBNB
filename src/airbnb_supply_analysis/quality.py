"""Perfilado y hallazgos de calidad previos al análisis."""

from __future__ import annotations

import pandas as pd


def iqr_outlier_mask(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    q1, q3 = numeric.quantile([0.25, 0.75])
    iqr = q3 - q1
    if pd.isna(iqr) or iqr == 0:
        return pd.Series(False, index=values.index)
    return ((numeric < q1 - 1.5 * iqr) | (numeric > q3 + 1.5 * iqr)).fillna(False)


def _finding(
    build_id: str,
    source_id: str,
    check_id: str,
    dimension: str,
    severity: str,
    failed: int,
    evaluated: int,
    field: str | None,
    impact: str,
) -> dict[str, object]:
    return {
        "finding_id": f"{source_id}:{check_id}",
        "build_id": build_id,
        "source_id": source_id,
        "entity": "RawListing",
        "field": field,
        "check_id": check_id,
        "dimension": dimension,
        "severity": severity,
        "failed_count": int(failed),
        "evaluated_count": int(evaluated),
        "failed_rate": float(failed / evaluated) if evaluated else 0.0,
        "evidence_path": "artifacts/quality/source-profile.parquet",
        "impact": impact,
        "disposition": "open" if failed else "accepted_valid",
        "rationale": None if failed else "La regla no encontró incumplimientos.",
    }


def profile_source(
    frame: pd.DataFrame, source_id: str, build_id: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    profiles = []
    for column in frame.columns:
        values = frame[column]
        profiles.append(
            {
                "build_id": build_id,
                "source_id": source_id,
                "field": column,
                "dtype": str(values.dtype),
                "row_count": len(frame),
                "null_count": int(values.isna().sum()),
                "null_rate": float(values.isna().mean()),
                "distinct_count": int(values.nunique(dropna=True)),
            }
        )
    findings = []
    duplicate_count = int(frame["id"].duplicated(keep=False).sum()) if "id" in frame else len(frame)
    findings.append(
        _finding(
            build_id,
            source_id,
            "duplicate_listing_id",
            "uniqueness",
            "critical",
            duplicate_count,
            len(frame),
            "id",
            "Puede duplicar anuncios y sesgar todos los agregados.",
        )
    )
    latitude = pd.to_numeric(frame.get("latitude"), errors="coerce")
    invalid_latitude = int((latitude.isna() | ~latitude.between(-90, 90)).sum())
    findings.append(
        _finding(
            build_id,
            source_id,
            "invalid_latitude",
            "validity",
            "medium",
            invalid_latitude,
            len(frame),
            "latitude",
            "Reduce la cobertura geográfica agregada.",
        )
    )
    longitude = pd.to_numeric(frame.get("longitude"), errors="coerce")
    invalid_longitude = int((longitude.isna() | ~longitude.between(-180, 180)).sum())
    findings.append(
        _finding(
            build_id,
            source_id,
            "invalid_longitude",
            "validity",
            "medium",
            invalid_longitude,
            len(frame),
            "longitude",
            "Reduce la cobertura geográfica agregada.",
        )
    )
    for column in ("price", "minimum_nights", "reviews_per_month"):
        if column not in frame:
            continue
        numeric = pd.to_numeric(frame[column], errors="coerce")
        outliers = int(iqr_outlier_mask(numeric).sum())
        findings.append(
            _finding(
                build_id,
                source_id,
                f"iqr_outlier_{column}",
                "distribution",
                "low",
                outliers,
                int(numeric.notna().sum()),
                column,
                "Puede alterar medias; se conserva y se resume con estadísticos robustos.",
            )
        )
    return pd.DataFrame(profiles), pd.DataFrame(findings)


def profile_sources(
    frames: list[tuple[str, pd.DataFrame]], build_id: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    profile_parts: list[pd.DataFrame] = []
    finding_parts: list[pd.DataFrame] = []
    for source_id, frame in frames:
        profile, finding = profile_source(frame, source_id, build_id)
        profile_parts.append(profile)
        finding_parts.append(finding)
    return pd.concat(profile_parts, ignore_index=True), pd.concat(finding_parts, ignore_index=True)
