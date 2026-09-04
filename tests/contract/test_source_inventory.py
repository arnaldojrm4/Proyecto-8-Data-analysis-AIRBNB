from __future__ import annotations

import json
from pathlib import Path

import pytest

import airbnb_supply_analysis.io as source_io


def test_inventory_accepts_exact_file_identity(tmp_path: Path) -> None:
    source = tmp_path / "sample.csv"
    source.write_text("id,name\n1,A\n", encoding="utf-8", newline="")
    manifest = {
        "sources": [
            {
                "source_id": "sample",
                "city_key": "madrid",
                "file_name": "sample.csv",
                "relative_path": "sample.csv",
                "sha256": source_io.sha256_file(source),
                "byte_size": source.stat().st_size,
                "parsed_row_count": 1,
                "column_names": ["id", "name"],
                "encoding": "utf-8",
                "delimiter": ",",
            }
        ]
    }
    inventory = getattr(source_io, "inventory_sources", None)
    assert inventory is not None, "Falta implementar inventory_sources"

    observed = inventory(tmp_path, manifest)

    assert observed[0]["identity_status"] == "identity_verified"


def test_inventory_rejects_hash_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "sample.csv"
    source.write_text("id\n1\n", encoding="utf-8", newline="")
    inventory = getattr(source_io, "inventory_sources", None)
    assert inventory is not None, "Falta implementar inventory_sources"
    manifest = {
        "sources": [
            {
                "source_id": "sample",
                "file_name": "sample.csv",
                "relative_path": "sample.csv",
                "sha256": "0" * 64,
                "byte_size": source.stat().st_size,
                "parsed_row_count": 1,
                "column_names": ["id"],
                "encoding": "utf-8",
                "delimiter": ",",
            }
        ]
    }

    with pytest.raises(ValueError, match="SHA-256"):
        inventory(tmp_path, manifest)


def test_approved_manifest_has_six_sources(project_root: Path) -> None:
    path = project_root / "config/source-manifest.json"
    assert path.exists(), "El manifiesto aprobado todavía no existe"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert len(payload["sources"]) == 6
    assert sum(source["parsed_row_count"] for source in payload["sources"]) == 220_031
