from __future__ import annotations

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
