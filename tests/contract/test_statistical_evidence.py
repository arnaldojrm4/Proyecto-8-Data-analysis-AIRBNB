from __future__ import annotations

import pandas as pd
import pytest

from airbnb_supply_analysis.statistics import validate_statistical_results


def test_statistical_evidence_requires_effect_interval_and_multiplicity() -> None:
    valid = pd.DataFrame(
        {
            "result_id": ["result-1"],
            "estimate": [0.6],
            "ci_low": [0.55],
            "ci_high": [0.65],
            "p_value_raw": [0.01],
            "p_value_adjusted": [0.02],
            "correction_method": ["holm"],
            "assumption_status": ["pass"],
            "interpretation_es": ["Asociación de actividad histórica; no implica causalidad."],
        }
    )

    validate_statistical_results(valid)
    with pytest.raises(ValueError, match="ci_low"):
        validate_statistical_results(valid.assign(ci_low=pd.NA))


@pytest.mark.parametrize("forbidden", ["demanda", "liquidez", "ocupación", "margen"])
def test_statistical_evidence_rejects_unsupported_business_terms(forbidden: str) -> None:
    frame = pd.DataFrame(
        {
            "result_id": ["result-1"],
            "estimate": [0.6],
            "ci_low": [0.55],
            "ci_high": [0.65],
            "p_value_raw": [0.01],
            "p_value_adjusted": [0.02],
            "correction_method": ["holm"],
            "assumption_status": ["pass"],
            "interpretation_es": [f"Este resultado demuestra {forbidden}."],
        }
    )

    with pytest.raises(ValueError, match="Terminología"):
        validate_statistical_results(frame)
