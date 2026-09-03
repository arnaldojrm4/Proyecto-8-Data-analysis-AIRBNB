from __future__ import annotations

import json

import pandas as pd

import airbnb_supply_analysis.cli as cli


def test_analyze_fails_with_code_five_before_publishing_invalid_evidence(
    canonical_frame, tmp_path, monkeypatch, capsys
) -> None:
    processed = tmp_path / "processed"
    artifacts = tmp_path / "artifacts"
    processed.mkdir()
    canonical_frame.to_parquet(processed / "listings.parquet", index=False)
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    config = tmp_path / "analysis.yml"
    config.write_text("sensitivity:\n  bootstrap_iterations: 10\n", encoding="utf-8")
    invalid = pd.DataFrame(
        {
            "result_id": ["invalid"],
            "estimate": [0.6],
            "ci_low": [pd.NA],
            "ci_high": [0.7],
            "p_value_raw": [0.01],
            "p_value_adjusted": [0.02],
            "correction_method": ["holm"],
            "assumption_status": ["pass"],
            "interpretation_es": ["Actividad histórica; no implica causalidad."],
        }
    )
    monkeypatch.setattr(cli, "run_statistical_analysis", lambda *args, **kwargs: invalid)

    exit_code = cli.main(
        [
            "analyze",
            "--processed-dir",
            str(processed),
            "--artifacts-dir",
            str(artifacts),
            "--source-manifest",
            str(manifest),
            "--config",
            str(config),
            "--log-format",
            "json",
        ]
    )

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert exit_code == 5
    assert payload["status"] == "failed"
    assert not (processed / "statistical_results.parquet").exists()


def test_analyze_requires_canonical_dataset(tmp_path, capsys) -> None:
    exit_code = cli.main(
        ["analyze", "--processed-dir", str(tmp_path), "--log-format", "json"]
    )

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert exit_code == 5
    assert "ejecute build" in payload["error"]
