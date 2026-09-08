from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pytest


def _copy_exports(source: Path, destination: Path) -> Path:
    shutil.copytree(source, destination)
    return destination


def _rewrite(path: Path, transform) -> None:
    frame = pd.read_csv(path)
    transform(frame)
    frame.to_csv(path, index=False)


def test_dashboard_rejects_a_missing_required_file(powerbi_export_fixture, tmp_path: Path) -> None:
    from dashboard.data import DashboardDataError, load_dashboard_dataset

    export_dir = _copy_exports(powerbi_export_fixture.directory, tmp_path / "exports")
    (export_dir / "dim_city.csv").unlink()

    with pytest.raises(DashboardDataError) as caught:
        load_dashboard_dataset(export_dir)

    assert caught.value.code == "missing_file"
    assert caught.value.artifact == "dim_city.csv"


@pytest.mark.parametrize(
    ("column", "value", "code"),
    [
        ("schema_version", "2.0.0", "unsupported_schema"),
        ("release_gate_status", "fail", "release_gate_failed"),
        ("build_id", "OTHER", "mixed_build"),
    ],
)
def test_dashboard_rejects_invalid_build_control(
    powerbi_export_fixture,
    tmp_path: Path,
    column: str,
    value: str,
    code: str,
) -> None:
    from dashboard.data import DashboardDataError, load_dashboard_dataset

    export_dir = _copy_exports(powerbi_export_fixture.directory, tmp_path / code)

    def corrupt(frame: pd.DataFrame) -> None:
        frame.loc[0, column] = value

    _rewrite(export_dir / "build_control.csv", corrupt)

    with pytest.raises(DashboardDataError) as caught:
        load_dashboard_dataset(export_dir)

    assert caught.value.code == code


def test_dashboard_rejects_a_recorded_row_count_mismatch(
    powerbi_export_fixture,
    tmp_path: Path,
) -> None:
    from dashboard.data import DashboardDataError, load_dashboard_dataset

    export_dir = _copy_exports(powerbi_export_fixture.directory, tmp_path / "counts")

    def corrupt(frame: pd.DataFrame) -> None:
        row = frame["output_file"].eq("fact_listings.csv")
        frame.loc[row, "output_row_count"] = 99

    _rewrite(export_dir / "build_control.csv", corrupt)

    with pytest.raises(DashboardDataError) as caught:
        load_dashboard_dataset(export_dir)

    assert caught.value.code == "row_count_mismatch"
    assert caught.value.artifact == "fact_listings.csv"


def test_dashboard_rejects_duplicate_dimension_keys(powerbi_export_fixture, tmp_path: Path) -> None:
    from dashboard.data import DashboardDataError, load_dashboard_dataset

    export_dir = _copy_exports(powerbi_export_fixture.directory, tmp_path / "duplicates")
    city_path = export_dir / "dim_city.csv"
    city = pd.read_csv(city_path)
    pd.concat([city, city], ignore_index=True).to_csv(city_path, index=False)

    def preserve_count(frame: pd.DataFrame) -> None:
        row = frame["output_file"].eq("dim_city.csv")
        frame.loc[row, "output_row_count"] = 2

    _rewrite(export_dir / "build_control.csv", preserve_count)

    with pytest.raises(DashboardDataError) as caught:
        load_dashboard_dataset(export_dir)

    assert caught.value.code == "duplicate_dimension_key"
    assert caught.value.artifact == "dim_city.csv"


def test_dashboard_rejects_orphan_fact_keys(powerbi_export_fixture, tmp_path: Path) -> None:
    from dashboard.data import DashboardDataError, load_dashboard_dataset

    export_dir = _copy_exports(powerbi_export_fixture.directory, tmp_path / "orphans")

    def corrupt(frame: pd.DataFrame) -> None:
        frame.loc[0, "city_key"] = "unknown-city"

    _rewrite(export_dir / "fact_listings.csv", corrupt)

    with pytest.raises(DashboardDataError) as caught:
        load_dashboard_dataset(export_dir)

    assert caught.value.code == "orphan_dimension_key"
    assert caught.value.artifact == "fact_listings.csv"
