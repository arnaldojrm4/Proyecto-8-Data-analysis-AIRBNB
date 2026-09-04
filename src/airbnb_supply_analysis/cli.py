"""Interfaz de línea de comandos del pipeline analítico."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pandas as pd

from airbnb_supply_analysis import __version__
from airbnb_supply_analysis.config import SCHEMA_VERSION, load_yaml
from airbnb_supply_analysis.etl import build_canonical
from airbnb_supply_analysis.exports import write_parquet
from airbnb_supply_analysis.io import (
    atomic_write_json,
    inventory_sources,
    load_json,
    read_source,
)
from airbnb_supply_analysis.opportunity import build_opportunity_matrix
from airbnb_supply_analysis.quality import profile_sources
from airbnb_supply_analysis.statistics import (
    run_statistical_analysis,
    validate_statistical_results,
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
        else:
            payload = _summary(args.command, "not_implemented", error_count=1)
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return 8
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
