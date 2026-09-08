from __future__ import annotations

import json
import shutil
import subprocess

import pytest


@pytest.mark.docker
def test_compose_configuration_is_valid() -> None:
    if shutil.which("docker") is None:
        pytest.skip("Docker CLI no está instalado")
    result = subprocess.run(
        ["docker", "compose", "config", "--quiet"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.docker
def test_dashboard_service_is_read_only_limited_and_health_checked() -> None:
    if shutil.which("docker") is None:
        pytest.skip("Docker CLI no está instalado")
    result = subprocess.run(
        ["docker", "compose", "config", "--format", "json"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    services = json.loads(result.stdout)["services"]
    service = services["dashboard"]

    assert service["image"] == services["pipeline"]["image"]
    assert service["ports"][0]["target"] == 8501
    powerbi_mount = next(
        mount for mount in service["volumes"] if mount["target"] == "/workspace/data/powerbi"
    )
    assert powerbi_mount["read_only"] is True
    assert service["deploy"]["resources"]["limits"]["memory"] == "1073741824"
    assert "/_stcore/health" in " ".join(service["healthcheck"]["test"])
