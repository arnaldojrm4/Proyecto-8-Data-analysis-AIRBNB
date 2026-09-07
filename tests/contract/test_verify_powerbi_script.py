from __future__ import annotations

from pathlib import Path


SCRIPT = Path("scripts/verify_powerbi.ps1")


def test_external_powerbi_verifier_covers_release_contract() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    required_evidence = {
        "build_control.csv",
        "ExpectedSchemaMajor",
        "Get-FileHash",
        "output_row_count",
        "release_gate_status",
        "restrictedHeaders",
        "listing_key",
        "reconciliation_difference",
        "Diferencia de conciliación",
    }
    assert all(token in source for token in required_evidence)
    for filename in (
        "dim_city.csv",
        "dim_neighborhood.csv",
        "dim_room_type.csv",
        "fact_listings.csv",
        "fact_opportunity_segments.csv",
        "fact_statistical_results.csv",
        "fact_quality_summary.csv",
    ):
        assert filename in source


def test_verifier_has_no_machine_specific_path() -> None:
    source = SCRIPT.read_text(encoding="utf-8").casefold()
    assert "users\\arnal" not in source
    assert "proyectosf5" not in source
