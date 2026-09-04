from __future__ import annotations

import json
import subprocess
import sys


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "airbnb_supply_analysis.cli", *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_help_lists_every_contract_command() -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    for command in (
        "inventory",
        "audit",
        "build",
        "analyze",
        "export",
        "test",
        "notebooks",
        "validate",
        "all",
    ):
        assert command in result.stdout


def test_invalid_command_returns_contract_exit_code_2() -> None:
    result = run_cli("does-not-exist", "--log-format", "json")

    assert result.returncode == 2


def test_version_is_machine_readable() -> None:
    result = run_cli("version", "--log-format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["command"] == "version"
    assert payload["status"] == "success"
    assert payload["schema_version"] == "1.0.0"
