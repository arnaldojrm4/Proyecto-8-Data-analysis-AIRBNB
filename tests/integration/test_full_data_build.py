from __future__ import annotations

import json

import pytest


@pytest.mark.full_data
def test_full_build_reconciles_all_sources_and_preserves_hashes(project_root) -> None:
    from airbnb_supply_analysis.etl import build_canonical
    from airbnb_supply_analysis.io import inventory_sources

    manifest_path = project_root / "config/source-manifest.json"
    assert manifest_path.exists(), "Falta copiar y manifestar las seis fuentes"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    before = inventory_sources(project_root / "data/raw", manifest)

    canonical, transformations = build_canonical(project_root / "data/raw", manifest, "test")
    after = inventory_sources(project_root / "data/raw", manifest)

    assert sum(item["parsed_row_count"] for item in before) == 220_031
    assert len(canonical) == 220_031
    assert canonical["listing_key"].is_unique
    assert [item["sha256"] for item in before] == [item["sha256"] for item in after]
    assert transformations["rows_evaluated"].max() > 0
