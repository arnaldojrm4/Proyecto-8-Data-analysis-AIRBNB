from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest


@pytest.mark.full_data
def test_cli_inventory_audit_and_build_publish_reconciled_outputs(project_root, tmp_path) -> None:
    artifacts = tmp_path / "artifacts"
    processed = tmp_path / "processed"
    common = [
        "--raw-dir",
        str(project_root / "data/raw"),
        "--source-manifest",
        str(project_root / "config/source-manifest.json"),
        "--artifacts-dir",
        str(artifacts),
        "--processed-dir",
        str(processed),
        "--log-format",
        "json",
    ]
    for command in ("inventory", "audit", "build"):
        result = subprocess.run(
            [sys.executable, "-m", "airbnb_supply_analysis.cli", command, *common],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr or result.stdout
        assert json.loads(result.stdout.strip().splitlines()[-1])["status"] == "success"

    listings = pd.read_parquet(processed / "listings.parquet")
    reconciliation = json.loads(
        (artifacts / "quality/row-reconciliation.json").read_text(encoding="utf-8")
    )
    assert len(listings) == 220_031
    assert reconciliation["source_rows"] == reconciliation["canonical_rows"] == 220_031
    assert (artifacts / "quality/source-profile.parquet").exists()
    assert (artifacts / "quality/findings.parquet").exists()
    assert (artifacts / "quality/transformations.parquet").exists()


@pytest.mark.full_data
def test_cli_analyze_publishes_statistics_opportunities_and_summary(project_root, tmp_path) -> None:
    processed = tmp_path / "processed"
    artifacts = tmp_path / "artifacts"
    build = subprocess.run(
        [
            sys.executable,
            "-m",
            "airbnb_supply_analysis.cli",
            "build",
            "--raw-dir",
            str(project_root / "data/raw"),
            "--source-manifest",
            str(project_root / "config/source-manifest.json"),
            "--processed-dir",
            str(processed),
            "--artifacts-dir",
            str(artifacts),
            "--log-format",
            "json",
        ],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert build.returncode == 0, build.stderr or build.stdout
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "airbnb_supply_analysis.cli",
            "analyze",
            "--processed-dir",
            str(processed),
            "--artifacts-dir",
            str(artifacts),
            "--log-format",
            "json",
        ],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert (processed / "statistical_results.parquet").exists()
    assert (processed / "opportunity_segments.parquet").exists()
    assert (artifacts / "quality/analysis-summary.json").exists()
