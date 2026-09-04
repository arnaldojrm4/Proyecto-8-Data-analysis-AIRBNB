from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import psutil
import pytest
import yaml


def _run_monitored(command: list[str], cwd: Path, timeout: int) -> tuple[int, float, float, str]:
    started = time.perf_counter()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    peak_rss = 0
    while process.poll() is None:
        try:
            parent = psutil.Process(process.pid)
            processes = [parent, *parent.children(recursive=True)]
            current_rss = 0
            for child in processes:
                try:
                    current_rss += child.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            peak_rss = max(peak_rss, current_rss)
        except psutil.NoSuchProcess:
            break
        if time.perf_counter() - started > timeout:
            process.kill()
            raise AssertionError(f"El proceso superó {timeout} segundos")
        time.sleep(0.05)
    output = process.communicate()[0]
    return process.returncode, time.perf_counter() - started, peak_rss / 1024**2, output


def _common_args(project_root: Path, tmp_path: Path) -> list[str]:
    return [
        "--raw-dir",
        str(project_root / "data/raw"),
        "--source-manifest",
        str(project_root / "config/source-manifest.json"),
        "--config",
        str(project_root / "config/analysis.yml"),
        "--processed-dir",
        str(tmp_path / "processed"),
        "--powerbi-dir",
        str(tmp_path / "powerbi"),
        "--artifacts-dir",
        str(tmp_path / "artifacts"),
        "--log-format",
        "json",
    ]


@pytest.mark.full_data
def test_etl_stays_within_sixty_seconds_and_two_gb(project_root: Path, tmp_path: Path) -> None:
    code, elapsed, peak_rss, output = _run_monitored(
        [
            sys.executable,
            "-m",
            "airbnb_supply_analysis.cli",
            "build",
            *_common_args(project_root, tmp_path),
        ],
        project_root,
        timeout=65,
    )

    assert code == 0, output
    assert elapsed <= 60
    assert peak_rss <= 2048


@pytest.mark.full_data
@pytest.mark.skipif(
    os.environ.get("AIRBNB_SUPPLY_IN_ALL") == "1",
    reason="evita recursión cuando all ejecuta la suite completa",
)
def test_full_workflow_budget_and_container_limits(project_root: Path, tmp_path: Path) -> None:
    compose = yaml.safe_load((project_root / "compose.yaml").read_text(encoding="utf-8"))
    limits = compose["services"]["pipeline"]["deploy"]["resources"]["limits"]
    assert str(limits["cpus"]) == "2.0"
    assert limits["memory"] == "4G"

    code, elapsed, peak_rss, output = _run_monitored(
        [
            sys.executable,
            "-m",
            "airbnb_supply_analysis.cli",
            "all",
            *_common_args(project_root, tmp_path),
        ],
        project_root,
        timeout=305,
    )

    assert code == 0, output
    assert elapsed <= 300
    assert peak_rss <= 2048
