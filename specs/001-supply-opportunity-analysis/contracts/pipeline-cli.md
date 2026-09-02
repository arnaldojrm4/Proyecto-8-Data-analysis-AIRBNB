# Contract: Pipeline Command Interface

**Version**: 1.0.0

**Owner**: analytical pipeline

**Consumers**: developer, reviewer, container workflow, acceptance checks

## Invocation

Host invocation:

```text
uv run --locked airbnb-supply <command> [options]
```

Container invocation:

```text
docker compose run --rm pipeline <command> [options]
```

The container invocation delegates to the same application entry point. Commands run from the
repository root and resolve project-relative paths from configuration. No command requires a
developer-specific absolute path.

## Global options

| Option | Default | Contract |
|---|---|---|
| `--config` | `config/analysis.yml` | Versioned analysis thresholds and deterministic settings |
| `--source-manifest` | `config/source-manifest.json` | Approved six-file source contract |
| `--raw-dir` | `data/raw` | Must resolve below the configured project root; read-only in container |
| `--processed-dir` | `data/processed` | Canonical Parquet outputs |
| `--powerbi-dir` | `data/powerbi` | Stable report-facing CSV outputs |
| `--artifacts-dir` | `artifacts` | Quality, figures, manifests, and executed notebooks |
| `--build-id` | derived | Optional explicit reproducible build identifier; otherwise derived from inputs/config/schema |
| `--log-format` | `human` | `human` or `json`; neither format may contain names or raw identifiers |

Unknown options, missing values, or paths outside permitted roots fail before data is read.

## Commands

### `inventory`

Validates file presence, filename, byte size, SHA-256, parsed row count, encoding, delimiter, and exact
ordered header against the approved source manifest.

**Outputs**:

- `artifacts/quality/source-inventory.json`
- one summary record on stdout

**Postcondition**: all six sources are `identity_verified` or the command fails.

### `audit`

Requires a passing inventory. Applies permissive raw schemas and profiles completeness, uniqueness,
validity, consistency, domains, ranges, distributions, cross-field rules, and outliers.

**Outputs**:

- `artifacts/quality/source-profile.parquet`
- `artifacts/quality/findings.parquet`
- `artifacts/quality/audit-summary.json`

**Postcondition**: all mandatory raw checks pass or findings identify the release blocker.

### `build`

Requires a passing audit. Canonicalizes names and types, assigns lineage and availability flags,
derives the activity proxy under its explicit rule, records all transformations, and validates the
strict canonical schema.

**Outputs**:

- `data/processed/listings.parquet`
- `artifacts/quality/transformations.parquet`
- `artifacts/quality/row-reconciliation.json`

**Postcondition**: every raw record is canonical, quarantined, or rejected with a documented reason;
accepted listing keys are unique.

### `analyze`

Requires a valid canonical dataset. Produces descriptive summaries, statistical result families,
sensitivity results, and the transparent opportunity matrix.

**Outputs**:

- `data/processed/statistical_results.parquet`
- `data/processed/opportunity_segments.parquet`
- `artifacts/figures/`
- `artifacts/quality/analysis-summary.json`

**Postcondition**: each inferential output has effect, interval, multiplicity status, assumption
status, and proxy-safe Spanish interpretation.

### `export`

Requires valid canonical and analysis outputs. Writes the stable Power BI star tables and a control
manifest atomically.

**Outputs**: every file defined in [analytical-outputs.md](analytical-outputs.md).

**Postcondition**: schemas, keys, privacy exclusions, row counts, and hashes pass before the build is
published under `data/powerbi/`.

### `notebooks`

Executes `01_data_audit.ipynb`, `02_etl.ipynb`, and `03_executive_eda.ipynb` in that exact order, each
in a fresh kernel with errors disallowed.

**Outputs**:

- `artifacts/executed_notebooks/01_data_audit.ipynb`
- `artifacts/executed_notebooks/02_etl.ipynb`
- `artifacts/executed_notebooks/03_executive_eda.ipynb`

**Postcondition**: all cells execute and every required conclusion block is present.

### `test`

Runs automated checks selected by `--suite unit|contract|integration|all`. The default is `all`.
Full-data integration checks use temporary output roots and MUST NOT replace accepted artifacts.

**Postcondition**: every selected test passes; the completion summary reports passed, failed,
skipped, and total counts.

### `validate`

Validates existing canonical, analysis, report-export, quality, and documentation artifacts without
rebuilding them. It checks schemas, hashes, reconciliation, language guardrails, and notebook
execution evidence.

**Postcondition**: emits one release-gate result and fails on any unexplained variance.

### `all`

Runs `inventory -> audit -> build -> analyze -> export -> test --suite all -> notebooks -> validate`.
It is the mandatory Essential acceptance entry point. Partial success never publishes a new accepted
build.

## Completion output

Every command emits a final machine-readable summary containing:

```text
command, status, build_id, schema_version, started_at_utc, finished_at_utc,
input_rows, output_rows, warning_count, error_count, artifact_paths
```

Human logs precede the summary only when `--log-format human` is selected. Timestamps are operational
metadata and do not enter deterministic analytical tables.

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Success; all applicable contracts pass |
| 2 | Invalid command, option, configuration, or path |
| 3 | Source identity or raw-schema contract failure |
| 4 | Canonical data-quality or reconciliation failure |
| 5 | Statistical, sensitivity, or opportunity-analysis failure |
| 6 | Output schema, privacy, hash, or atomic-publication failure |
| 7 | Notebook execution or documentation-contract failure |
| 8 | Unexpected internal failure with safe diagnostic output |

## Behavioral guarantees

- Commands are idempotent for the same source, configuration, schema, and dependency identities.
- Writes use a temporary build directory and replace accepted outputs only after validation.
- Mandatory failures are visible and return non-zero status.
- Raw files are never opened for write.
- Logs and errors never print listing names, host names, or raw identifiers.
- A failed build preserves the most recent accepted build and its control manifest.
