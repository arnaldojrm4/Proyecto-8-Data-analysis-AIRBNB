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

    def stage(name: str):
        def run(args):
            calls.append(name)
            return {"command": name, "status": "success", "artifact_paths": []}

        return run

    for name in STAGE_ORDER:
        monkeypatch.setattr(cli, f"_{name}", stage(name), raising=False)

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

    def successful(name: str):
        def run(args):
            calls.append(name)
            return {"command": name, "status": "success", "artifact_paths": []}

        return run

    def failed_analysis(args):
        calls.append("analyze")
        partial = Path(args.processed_dir) / "partial.parquet"
        partial.parent.mkdir(parents=True, exist_ok=True)
        partial.write_text("partial", encoding="utf-8")
        raise ValueError("fallo estadístico deliberado")

    for name in STAGE_ORDER:
        monkeypatch.setattr(cli, f"_{name}", successful(name), raising=False)
    monkeypatch.setattr(cli, "_analyze", failed_analysis)

    exit_code = cli.main(_arguments(tmp_path))
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    assert exit_code == 5
    assert payload["status"] == "failed"
    assert calls == ["inventory", "audit", "build", "analyze"]
    assert accepted.read_text(encoding="utf-8") == "stable"
    assert not (processed / "partial.parquet").exists()
