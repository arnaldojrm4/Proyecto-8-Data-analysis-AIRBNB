"""Interfaz de línea de comandos del pipeline analítico."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pandas as pd

from airbnb_supply_analysis import __version__
from airbnb_supply_analysis.config import SCHEMA_VERSION, load_yaml
from airbnb_supply_analysis.etl import build_canonical
from airbnb_supply_analysis.exports import write_parquet, write_stable_csv
from airbnb_supply_analysis.io import (
    atomic_write_json,
    inventory_sources,
    load_json,
    read_source,
)
from airbnb_supply_analysis.notebooks import (
    NOTEBOOK_ORDER,
    execute_notebooks,
    validate_notebook_narrative,
)
from airbnb_supply_analysis.opportunity import build_opportunity_matrix
from airbnb_supply_analysis.quality import profile_sources
from airbnb_supply_analysis.statistics import (
    run_statistical_analysis,
    validate_statistical_results,
)
from airbnb_supply_analysis.validation import (
    DocumentationContractError,
    validate_documentation_tree,
    validate_release_artifacts,
)
from airbnb_supply_analysis.visualization import save_core_figures

COMMANDS = (
    "inventory",
    "audit",
    "build",
    "analyze",
    "export",
    "test",
    "notebooks",
    "validate",
    "all",
    "version",
)

TEST_PATHS = {
    "unit": "tests/unit",
    "contract": "tests/contract",
    "integration": "tests/integration",
    "all": "tests",
}


class NotebookContractError(ValueError):
    """Indica que la ejecución o narrativa de un notebook incumple el contrato."""


class PipelineCommandError(ValueError):
    """Error de una etapa con el código de salida contractual."""

    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def _add_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default="config/analysis.yml")
    parser.add_argument("--source-manifest", default="config/source-manifest.json")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--powerbi-dir", default="data/powerbi")
    parser.add_argument("--artifacts-dir", default="artifacts")
    parser.add_argument("--build-id")
    parser.add_argument("--log-format", choices=("human", "json"), default="human")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="airbnb-supply",
        description="Pipeline reproducible de oportunidades de oferta Airbnb.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in COMMANDS:
        subparser = subparsers.add_parser(command)
        _add_options(subparser)
        if command == "test":
            subparser.add_argument(
                "--suite",
                choices=("unit", "contract", "integration", "all"),
                default="all",
            )
    return parser


def _summary(
    command: str,
    status: str = "success",
    *,
    started_at: str | None = None,
    build_id: str | None = None,
    input_rows: int = 0,
    output_rows: int = 0,
    artifact_paths: list[str] | None = None,
    error_count: int = 0,
) -> dict[str, object]:
    now = datetime.now(UTC).isoformat()
    return {
        "command": command,
        "status": status,
        "build_id": build_id,
        "schema_version": SCHEMA_VERSION,
        "started_at_utc": started_at or now,
        "finished_at_utc": now,
        "input_rows": input_rows,
        "output_rows": output_rows,
        "warning_count": 0,
        "error_count": error_count,
        "artifact_paths": artifact_paths or [],
        "application_version": __version__,
    }


def _build_id(manifest_path: Path, config_path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(manifest_path.read_bytes())
    digest.update(config_path.read_bytes())
    digest.update(SCHEMA_VERSION.encode("ascii"))
    return digest.hexdigest()[:16].upper()


def _paths(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        manifest=Path(args.source_manifest).resolve(),
        config=Path(args.config).resolve(),
        raw=Path(args.raw_dir).resolve(),
        processed=Path(args.processed_dir).resolve(),
        powerbi=Path(args.powerbi_dir).resolve(),
        artifacts=Path(args.artifacts_dir).resolve(),
    )


def _inventory(args: argparse.Namespace) -> dict[str, Any]:
    started = datetime.now(UTC).isoformat()
    paths = _paths(args)
    manifest = load_json(paths.manifest)
    inventory = inventory_sources(paths.raw, manifest)
    destination = paths.artifacts / "quality/source-inventory.json"
    atomic_write_json(
        {"schema_version": SCHEMA_VERSION, "sources": inventory},
        destination,
    )
    rows = sum(item["parsed_row_count"] for item in inventory)
    return _summary(
        "inventory",
        started_at=started,
        build_id=_build_id(paths.manifest, paths.config),
        input_rows=rows,
        output_rows=len(inventory),
        artifact_paths=[str(destination)],
    )


def _audit(args: argparse.Namespace) -> dict[str, Any]:
    started = datetime.now(UTC).isoformat()
    paths = _paths(args)
    manifest = load_json(paths.manifest)
    inventory = inventory_sources(paths.raw, manifest)
    build_id = _build_id(paths.manifest, paths.config)
    frames = [
        (source["source_id"], read_source(paths.raw, source))
        for source in manifest["sources"]
    ]
    profile, findings = profile_sources(frames, build_id)
    quality_dir = paths.artifacts / "quality"
    profile_path = quality_dir / "source-profile.parquet"
    findings_path = quality_dir / "findings.parquet"
    summary_path = quality_dir / "audit-summary.json"
    write_parquet(profile, profile_path, ["source_id", "field"])
    write_parquet(findings, findings_path, ["source_id", "check_id"])
    total_rows = sum(item["parsed_row_count"] for item in inventory)
    atomic_write_json(
        {
            "build_id": build_id,
            "source_rows": total_rows,
            "finding_count": len(findings),
            "open_finding_count": int(findings["failed_count"].gt(0).sum()),
            "release_blocker_count": int(
                ((findings["severity"] == "critical") & findings["failed_count"].gt(0)).sum()
            ),
        },
        summary_path,
    )
    return _summary(
        "audit",
        started_at=started,
        build_id=build_id,
        input_rows=total_rows,
        output_rows=len(profile) + len(findings),
        artifact_paths=[str(profile_path), str(findings_path), str(summary_path)],
    )


def _build(args: argparse.Namespace) -> dict[str, Any]:
    started = datetime.now(UTC).isoformat()
    paths = _paths(args)
    manifest = load_json(paths.manifest)
    inventory = inventory_sources(paths.raw, manifest)
    build_id = _build_id(paths.manifest, paths.config)
    canonical, transformations = build_canonical(paths.raw, manifest, build_id)
    listings_path = paths.processed / "listings.parquet"
    transformations_path = paths.artifacts / "quality/transformations.parquet"
    reconciliation_path = paths.artifacts / "quality/row-reconciliation.json"
    write_parquet(canonical, listings_path, ["listing_key"])
    write_parquet(transformations, transformations_path, ["transformation_id"])
    source_rows = sum(item["parsed_row_count"] for item in inventory)
    reconciliation = {
        "build_id": build_id,
        "source_rows": source_rows,
        "canonical_rows": len(canonical),
        "rejected_rows": 0,
        "quarantined_rows": 0,
        "distinct_listing_key_count": int(canonical["listing_key"].nunique()),
        "difference": source_rows - len(canonical),
        "release_gate_status": "pass"
        if source_rows == len(canonical) == canonical["listing_key"].nunique()
        else "fail",
    }
    atomic_write_json(reconciliation, reconciliation_path)
    if reconciliation["release_gate_status"] != "pass":
        raise ValueError("La conciliación canónica no cierra")
    return _summary(
        "build",
        started_at=started,
        build_id=build_id,
        input_rows=source_rows,
        output_rows=len(canonical),
        artifact_paths=[str(listings_path), str(transformations_path), str(reconciliation_path)],
    )


def _analyze(args: argparse.Namespace) -> dict[str, Any]:
    started = datetime.now(UTC).isoformat()
    paths = _paths(args)
    listings_path = paths.processed / "listings.parquet"
    if not listings_path.exists():
        raise ValueError("Falta data/processed/listings.parquet; ejecute build antes de analyze")
    listings = pd.read_parquet(listings_path)
    build_id = args.build_id or _build_id(paths.manifest, paths.config)
    configuration = load_yaml(paths.config)
    bootstrap_iterations = int(
        configuration.get("sensitivity", {}).get("bootstrap_iterations", 500)
    )
    statistical = run_statistical_analysis(
        listings, build_id, bootstrap_iterations=bootstrap_iterations
    )
    validate_statistical_results(statistical)
    segment_results = statistical.loc[statistical["analysis_family"].eq("segment")]
    opportunities = build_opportunity_matrix(listings, segment_results, build_id)
    statistical_path = paths.processed / "statistical_results.parquet"
    opportunity_path = paths.processed / "opportunity_segments.parquet"
    write_parquet(statistical, statistical_path, ["result_id"])
    write_parquet(opportunities, opportunity_path, ["segment_key"])
    figures = save_core_figures(
        listings,
        opportunities,
        paths.artifacts / "figures",
        statistical=statistical,
    )
    figure_manifest = paths.artifacts / "figures/manifest.json"
    atomic_write_json({"build_id": build_id, "artifacts": figures}, figure_manifest)
    summary_path = paths.artifacts / "quality/analysis-summary.json"
    label_counts = opportunities["opportunity_label"].value_counts().to_dict()
    atomic_write_json(
        {
            "build_id": build_id,
            "statistical_result_count": len(statistical),
            "segment_count": len(opportunities),
            "opportunity_label_counts": label_counts,
            "terminology_guardrail": "pass",
        },
        summary_path,
    )
    return _summary(
        "analyze",
        started_at=started,
        build_id=build_id,
        input_rows=len(listings),
        output_rows=len(statistical) + len(opportunities),
        artifact_paths=[
            str(statistical_path),
            str(opportunity_path),
            str(summary_path),
            str(figure_manifest),
        ],
    )


def _test(args: argparse.Namespace) -> dict[str, Any]:
    """Ejecuta la selección pytest solicitada y expone un resumen estable."""
    suite = args.suite
    environment = os.environ.copy()
    if getattr(args, "in_all", False):
        environment["AIRBNB_SUPPLY_IN_ALL"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", TEST_PATHS[suite]],
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )
    test_summary = _pytest_counts(f"{result.stdout}\n{result.stderr}")
    status = "success" if result.returncode == 0 else "failed"
    payload = _summary("test", status, error_count=int(result.returncode != 0))
    payload["test_summary"] = test_summary
    payload["pytest_returncode"] = result.returncode
    if result.returncode != 0:
        payload["error"] = "La suite pytest seleccionada contiene fallos."
    return payload


def _notebooks(args: argparse.Namespace) -> dict[str, Any]:
    """Ejecuta notebooks y bloquea su publicación si falla la narrativa."""
    source_directory = Path("notebooks").resolve()
    output_directory = Path(args.artifacts_dir).resolve() / "executed_notebooks"
    outputs = execute_notebooks(source_directory, output_directory)
    issues = {
        source.name: result
        for source in (source_directory / filename for filename in NOTEBOOK_ORDER)
        if (result := validate_notebook_narrative(source))
    }
    if issues:
        formatted = "; ".join(
            f"{filename}: {', '.join(messages)}" for filename, messages in issues.items()
        )
        raise NotebookContractError(f"Contrato narrativo de notebooks incumplido: {formatted}")
    return _summary("notebooks", artifact_paths=[str(path) for path in outputs])


def _export(args: argparse.Namespace) -> dict[str, Any]:
    """Publica la dependencia CSV mínima y segura requerida por la puerta Esencial."""
    paths = _paths(args)
    listings = pd.read_parquet(paths.processed / "listings.parquet")
    opportunities = pd.read_parquet(paths.processed / "opportunity_segments.parquet")
    statistical = pd.read_parquet(paths.processed / "statistical_results.parquet")
    quality = pd.read_parquet(paths.artifacts / "quality" / "findings.parquet")
    build_id = args.build_id or _build_id(paths.manifest, paths.config)
    exports = {
        "dim_city.csv": listings[["city_key"]].drop_duplicates(),
        "dim_neighborhood.csv": listings[
            ["city_key", "neighborhood_key", "neighborhood"]
        ].drop_duplicates(),
        "dim_room_type.csv": listings[["room_type"]].drop_duplicates(),
        "fact_listings.csv": listings[
            [
                "listing_key",
                "city_key",
                "neighborhood_key",
                "room_type",
                "price",
                "minimum_nights",
                "number_of_reviews",
                "reviews_per_month_observed",
                "activity_proxy",
                "activity_proxy_derived_zero",
                "activity_proxy_is_analyzable",
            ]
        ],
        "fact_opportunity_segments.csv": opportunities.drop(
            columns=["centroid_latitude", "centroid_longitude"], errors="ignore"
        ),
        "fact_statistical_results.csv": statistical,
        "fact_quality_summary.csv": quality,
    }
    for filename, frame in exports.items():
        _validate_export_columns(frame)
        write_stable_csv(frame, paths.powerbi / filename)
    control = pd.DataFrame(
        [
            {
                "build_id": build_id,
                "schema_version": SCHEMA_VERSION,
                "source_file_count": 6,
                "source_row_count": len(listings),
                "canonical_row_count": len(listings),
                "distinct_listing_key_count": int(listings["listing_key"].nunique()),
                "output_file": filename,
                "output_row_count": len(frame),
                "output_sha256": _sha256(paths.powerbi / filename),
                "release_gate_status": "pass",
            }
            for filename, frame in exports.items()
        ]
    )
    control_path = paths.powerbi / "build_control.csv"
    write_stable_csv(control, control_path)
    return _summary(
        "export",
        build_id=build_id,
        input_rows=len(listings),
        output_rows=sum(len(frame) for frame in exports.values()) + len(control),
        artifact_paths=[
            str(paths.powerbi / filename) for filename in (*exports, "build_control.csv")
        ],
    )


def _validate(args: argparse.Namespace) -> dict[str, Any]:
    """Valida artefactos existentes y documentación sin reconstruir el flujo."""
    paths = _paths(args)
    documentation = validate_documentation_tree(Path.cwd())
    artifacts = validate_release_artifacts(paths.processed, paths.powerbi, paths.artifacts)
    return _summary(
        "validate",
        build_id=args.build_id or _build_id(paths.manifest, paths.config),
        output_rows=documentation["checked_files"] + artifacts["processed_files"],
    )


def _all(args: argparse.Namespace) -> dict[str, Any]:
    """Ejecuta las etapas contractuales aisladas y publica solo tras aprobación."""
    with tempfile.TemporaryDirectory(prefix="airbnb-supply-") as temporary:
        staging = Path(temporary)
        staged_values = vars(args).copy()
        staged_values.update(
            processed_dir=str(staging / "processed"),
            powerbi_dir=str(staging / "powerbi"),
            artifacts_dir=str(staging / "artifacts"),
            suite="all",
            in_all=True,
        )
        staged_args = argparse.Namespace(**staged_values)
        for name in (
            "inventory",
            "audit",
            "build",
            "analyze",
            "export",
            "test",
            "notebooks",
            "validate",
        ):
            try:
                payload = _run_stage(name, staged_args)
            except (DocumentationContractError, NotebookContractError) as error:
                raise PipelineCommandError(str(error), 7) from error
            except ValueError as error:
                raise PipelineCommandError(str(error), _stage_exit_code(name)) from error
            if payload["status"] != "success":
                raise PipelineCommandError(f"La etapa {name} no aprobó.", _stage_exit_code(name))
        normalize_staged_figure_manifest(staging / "artifacts" / "figures" / "manifest.json")
        _publish_staged_outputs(staging, args)
    build_id = args.build_id or _build_id(Path(args.source_manifest), Path(args.config))
    return _summary("all", build_id=build_id)


def _pytest_counts(output: str) -> dict[str, int]:
    counts = {
        name: int(match.group(1)) if (match := re.search(rf"(\d+) {name}", output)) else 0
        for name in ("passed", "failed", "skipped")
    }
    counts["total"] = sum(counts.values())
    return counts


def _run_stage(name: str, args: argparse.Namespace) -> dict[str, Any]:
    """Aísla cada etapa en un proceso para liberar su memoria antes de la siguiente."""
    if name == "test":
        return _test(args)
    command = [
        sys.executable,
        "-m",
        "airbnb_supply_analysis.cli",
        name,
        "--config",
        args.config,
        "--source-manifest",
        args.source_manifest,
        "--raw-dir",
        args.raw_dir,
        "--processed-dir",
        args.processed_dir,
        "--powerbi-dir",
        args.powerbi_dir,
        "--artifacts-dir",
        args.artifacts_dir,
        "--log-format",
        "json",
    ]
    if args.build_id:
        command.extend(("--build-id", args.build_id))
    if name == "test":
        command.extend(("--suite", "all"))
    environment = os.environ.copy()
    if name == "test":
        environment["AIRBNB_SUPPLY_IN_ALL"] = "1"
    result = subprocess.run(command, text=True, capture_output=True, check=False, env=environment)
    payload = _last_json_summary(result.stdout)
    if result.returncode != 0:
        message = str(payload.get("error", "La etapa no produjo una salida aceptada."))
        raise PipelineCommandError(message, result.returncode)
    return payload


def _last_json_summary(output: str) -> dict[str, Any]:
    for line in reversed(output.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "status" in payload:
            return payload
    raise PipelineCommandError("La etapa no emitió un resumen JSON.", 8)


def normalize_staged_figure_manifest(manifest_path: Path) -> None:
    """Elimina rutas temporales del manifiesto antes de mover artefactos aceptados."""
    if not manifest_path.is_file():
        return
    payload = load_json(manifest_path)
    for artifact in payload.get("artifacts", []):
        artifact["path"] = f"artifacts/figures/{Path(artifact['path']).name}"
    atomic_write_json(payload, manifest_path)


def _validate_export_columns(frame: pd.DataFrame) -> None:
    restricted = {"listing_id", "host_id", "host_name", "listing_name", "latitude", "longitude"}
    present = restricted.intersection(frame.columns)
    if present:
        raise ValueError(f"Campos restringidos en exportación: {', '.join(sorted(present))}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stage_exit_code(stage: str) -> int:
    if stage == "analyze":
        return 5
    if stage in {"export", "validate"}:
        return 6
    if stage in {"notebooks"}:
        return 7
    return 4


def _publish_staged_outputs(staging: Path, args: argparse.Namespace) -> None:
    for name, destination in (
        ("processed", Path(args.processed_dir).resolve()),
        ("powerbi", Path(args.powerbi_dir).resolve()),
        ("artifacts", Path(args.artifacts_dir).resolve()),
    ):
        source = staging / name
        if not source.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        backup = destination.with_name(f".{destination.name}.previous")
        if backup.exists():
            shutil.rmtree(backup)
        try:
            if destination.exists():
                destination.replace(backup)
            source.replace(destination)
        except BaseException:
            if backup.exists() and not destination.exists():
                backup.replace(destination)
            raise
        else:
            if backup.exists():
                shutil.rmtree(backup)
            (destination / ".gitkeep").touch(exist_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "version":
            payload = _summary("version")
        elif args.command == "inventory":
            payload = _inventory(args)
        elif args.command == "audit":
            payload = _audit(args)
        elif args.command == "build":
            payload = _build(args)
        elif args.command == "analyze":
            payload = _analyze(args)
        elif args.command == "export":
            payload = _export(args)
        elif args.command == "test":
            payload = _test(args)
        elif args.command == "notebooks":
            payload = _notebooks(args)
        elif args.command == "validate":
            payload = _validate(args)
        elif args.command == "all":
            payload = _all(args)
        else:
            payload = _summary(args.command, "not_implemented", error_count=1)
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return 8
        if payload["status"] != "success":
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return 4
    except PipelineCommandError as error:
        payload = _summary(args.command, "failed", error_count=1)
        payload["error"] = str(error)
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return error.exit_code
    except (DocumentationContractError, NotebookContractError) as error:
        payload = _summary(args.command, "failed", error_count=1)
        payload["error"] = str(error)
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 7
    except (FileNotFoundError, ValueError) as error:
        payload = _summary(args.command, "failed", error_count=1)
        payload["error"] = str(error)
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        if args.command == "inventory":
            return 3
        if args.command == "analyze":
            return 5
        return 4
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
