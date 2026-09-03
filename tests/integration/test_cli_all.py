from __future__ import annotations

import importlib
import json
from pathlib import Path

STAGE_ORDER = (
    "inventory",
    "audit",
    "build",
    "analyze",
    "export",
    "test",
    "notebooks",
    "validate",
)


def _arguments(tmp_path: Path) -> list[str]:
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    config = tmp_path / "analysis.yml"
    config.write_text("{}", encoding="utf-8")
    return [
        "all",
        "--source-manifest",
        str(manifest),
        "--config",
        str(config),
        "--raw-dir",
        str(tmp_path / "raw"),
        "--processed-dir",
        str(tmp_path / "processed"),
        "--powerbi-dir",
        str(tmp_path / "powerbi"),
        "--artifacts-dir",
        str(tmp_path / "artifacts"),
        "--log-format",
        "json",
    ]


def test_all_runs_stages_in_contract_order_and_is_idempotent(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    cli = importlib.import_module("airbnb_supply_analysis.cli")
    calls: list[str] = []

    def successful_stage(name: str, args):
        del args
        calls.append(name)
        return {"command": name, "status": "success", "artifact_paths": []}

    monkeypatch.setattr(cli, "_run_stage", successful_stage)

    first_code = cli.main(_arguments(tmp_path))
    first_payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    second_code = cli.main(_arguments(tmp_path))
    second_payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    assert first_code == second_code == 0
    assert calls == [*STAGE_ORDER, *STAGE_ORDER]
    assert first_payload["status"] == second_payload["status"] == "success"
    assert first_payload["command"] == second_payload["command"] == "all"


def test_all_fails_closed_and_removes_partial_staging(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    cli = importlib.import_module("airbnb_supply_analysis.cli")
    processed = tmp_path / "processed"
    processed.mkdir()
    accepted = processed / "accepted-build.txt"
    accepted.write_text("stable", encoding="utf-8")
    calls: list[str] = []

    def staged_runner(name: str, args):
        calls.append(name)
        if name != "analyze":
            return {"command": name, "status": "success", "artifact_paths": []}
        partial = Path(args.processed_dir) / "partial.parquet"
        partial.parent.mkdir(parents=True, exist_ok=True)
        partial.write_text("partial", encoding="utf-8")
        raise cli.PipelineCommandError("fallo estadístico deliberado", 5)

    monkeypatch.setattr(cli, "_run_stage", staged_runner)

    exit_code = cli.main(_arguments(tmp_path))
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    assert exit_code == 5
    assert payload["status"] == "failed"
    assert calls == ["inventory", "audit", "build", "analyze"]
    assert accepted.read_text(encoding="utf-8") == "stable"
    assert not (processed / "partial.parquet").exists()


def test_staged_figure_manifest_does_not_publish_temporary_paths(tmp_path: Path) -> None:
    cli = importlib.import_module("airbnb_supply_analysis.cli")
    manifest = tmp_path / "artifacts" / "figures" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps(
            {
                "artifacts": [
                    {
                        "path": (
                            "C:/Users/Arnal/AppData/Local/Temp/build/artifacts/figures/chart.png"
                        ),
                        "type": "png",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    cli.normalize_staged_figure_manifest(manifest)

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["artifacts"][0]["path"] == "artifacts/figures/chart.png"
