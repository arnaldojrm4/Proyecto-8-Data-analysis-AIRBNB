from __future__ import annotations

import json
import os
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


@pytest.mark.docker
@pytest.mark.skipif(
    os.environ.get("AIRBNB_SUPPLY_IN_ALL") == "1",
    reason="evita iniciar Docker de forma recursiva durante el comando all",
)
def test_dashboard_package_is_importable_from_streamlit_script_context() -> None:
    if shutil.which("docker") is None:
        pytest.skip("Docker CLI no está instalado")
    result = subprocess.run(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            "--no-deps",
            "--entrypoint",
            "python",
            "dashboard",
            "-c",
            (
                "import sys; "
                "sys.path[0] = '/workspace/dashboard'; "
                "import dashboard; "
                "print(dashboard.__file__)"
            ),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "/workspace/dashboard/__init__.py"
