from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace


def test_test_command_runs_selected_suite_and_reports_pytest_counts(monkeypatch) -> None:
    cli = importlib.import_module("airbnb_supply_analysis.cli")
    command: list[str] = []

    class Completed:
        returncode = 0
        stdout = ".... 4 passed, 1 skipped in 0.10s\n"
        stderr = ""

    def fake_run(arguments, **kwargs):
        nonlocal command
        del kwargs
        command = arguments
        return Completed()

    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    result = cli._test(SimpleNamespace(suite="unit"))

    assert command[-1] == "tests/unit"
    assert result["status"] == "success"
    assert result["test_summary"] == {
        "passed": 4,
        "failed": 0,
        "skipped": 1,
        "total": 5,
    }


def test_test_command_excludes_redundant_full_data_checks_inside_all(monkeypatch) -> None:
    cli = importlib.import_module("airbnb_supply_analysis.cli")
    command: list[str] = []

    class Completed:
        returncode = 0
        stdout = "10 passed, 5 deselected in 0.10s\n"
        stderr = ""

    def fake_run(arguments, **kwargs):
        nonlocal command
        del kwargs
        command = arguments
        return Completed()

    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    result = cli._test(SimpleNamespace(suite="all", in_all=True))

    assert command[-3:] == ["-m", "not full_data", "tests"]
    assert result["status"] == "success"


def test_notebooks_command_writes_contract_outputs_and_rejects_bad_narrative(
    tmp_path: Path, monkeypatch
) -> None:
    cli = importlib.import_module("airbnb_supply_analysis.cli")
    output = tmp_path / "artifacts"
    executed: list[Path] = []

    def fake_execute(source: Path, destination: Path):
        del source
        destination.mkdir(parents=True, exist_ok=True)
        paths = [destination / name for name in cli.NOTEBOOK_ORDER]
        for path in paths:
            path.write_text("executed", encoding="utf-8")
        executed.extend(paths)
        return paths

    monkeypatch.setattr(cli, "execute_notebooks", fake_execute)
    monkeypatch.setattr(cli, "validate_notebook_narrative", lambda path: [])
    result = cli._notebooks(SimpleNamespace(artifacts_dir=str(output)))

    assert result["status"] == "success"
    assert result["artifact_paths"] == [str(path) for path in executed]
    assert all(path.parent.name == "executed_notebooks" for path in executed)

    monkeypatch.setattr(cli, "validate_notebook_narrative", lambda path: ["sin conclusión"])
    try:
        cli._notebooks(SimpleNamespace(artifacts_dir=str(output)))
    except cli.NotebookContractError as error:
        assert "sin conclusión" in str(error)
    else:
        raise AssertionError("Una narrativa inválida debe bloquear notebooks")
