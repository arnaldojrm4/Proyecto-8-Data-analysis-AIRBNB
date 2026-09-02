# Quickstart Validation Guide: Supply Opportunity Analysis

**Purpose**: Prove the planned feature end to end after implementation.

**Feature**: [spec.md](spec.md)

**Contracts**: [pipeline CLI](contracts/pipeline-cli.md),
[analytical outputs](contracts/analytical-outputs.md),
[Power BI report](contracts/powerbi-report.md)

This is a validation/run guide, not implementation code. Commands describe the interfaces that the
implementation must provide.

## Prerequisites

- Git.
- Docker Engine with Compose support.
- The six approved educational CSV files.
- Windows 10 or later with free Power BI Desktop only for the Medium-level report validation.
- Enough local resources for the reference workflow: 2 vCPU, 4 GB RAM, and space for raw, processed,
  report, and execution artifacts.

The Python toolchain is provided by the locked container. A host Python installation is optional.

## 1. Confirm repository and feature state

From the repository root:

```powershell
git branch --show-current
git status --short
```

Expected:

- work occurs on the approved phase branch rather than directly on stable `main`;
- the active GitHub Project item is in `In Progress` or `Review`;
- unrelated local changes are identified before validation.

## 2. Place and verify immutable sources

The required layout is:

```text
data/raw/london_airbnb.csv
data/raw/madrid_airbnb.csv
data/raw/milan_airbnb.csv
data/raw/NY_airbnb.csv
data/raw/sydney_airbnb.csv
data/raw/tokyo_airbnb.csv
```

The expected identities and counts are recorded in
[research.md](research.md#3-source-inventory-and-immutable-input-contract). After the files are in
place, build the locked image and verify sources:

```powershell
docker compose build
docker compose run --rm pipeline inventory
```

Expected:

- six verified source files;
- exactly 220,031 parsed CSV records in total;
- exact filename, header, size, and SHA-256 matches;
- no source file is opened for write;
- `artifacts/quality/source-inventory.json` records `identity_verified` for all six.

A mismatch is an expected hard failure. Do not update the approved manifest until the source change
has been reviewed and documented.

## 3. Run fast development checks

```powershell
docker compose run --rm pipeline test --suite unit
docker compose run --rm pipeline test --suite contract
```

Expected:

- unit checks cover parsing, canonicalization, conditional activity derivation, statistical helpers,
  opportunity rules, and safe wording;
- contract checks cover the six-source manifest, schemas, keys, output names, privacy exclusions, and
  deterministic configuration;
- the command returns zero only when all selected checks pass.

The implementation may expose pytest directly inside the container, but these stable acceptance
aliases must remain documented.

## 4. Execute the complete Essential workflow

```powershell
docker compose run --rm pipeline all
```

Expected order:

```text
inventory -> audit -> build -> analyze -> export -> test -> notebooks -> validate
```

Expected artifacts:

- `data/processed/listings.parquet`
- `data/processed/opportunity_segments.parquet`
- `data/processed/statistical_results.parquet`
- all files in the Power BI export set
- quality profiles, findings, transformation log, row reconciliation, and figures
- three successfully executed notebook copies
- a passing build control manifest

Acceptance budgets on the reference machine:

- ETL at most 60 seconds;
- full audit-to-export analytical workflow at most 5 minutes;
- peak resident memory at most 2 GB.

The run fails if a mandatory validation fails. Failed outputs must not replace the latest accepted
build.

## 5. Validate documentation and notebook evidence

```powershell
docker compose run --rm pipeline notebooks
docker compose run --rm pipeline validate
```

Inspect the executed copies under `artifacts/executed_notebooks/`.

Expected:

- notebook order is audit, ETL, executive EDA;
- each starts in a fresh kernel and completes without ignored errors;
- every analytical section has Spanish explanation, evidence, conclusion, limitation, and business
  implication;
- all calculations call the package's tested functions rather than duplicate logic;
- no conclusion uses prohibited demand, booking, occupancy, liquidity, revenue, margin, causal,
  cross-city price, or unsupported recency language.

## 6. Verify core analytical scenarios

### Scenario A: source and row reconciliation

1. Compare per-file parsed counts to the approved source manifest.
2. Compare their sum to the canonical count plus explicitly quarantined/rejected rows.
3. Confirm accepted `listing_key` values are unique.
4. Confirm raw hashes are unchanged after the workflow.

Expected: zero unexplained rows and zero changed raw hashes.

### Scenario B: missing activity rate

1. Locate rows with missing observed rate and zero cumulative reviews.
2. Confirm `activity_proxy` is zero and `activity_proxy_derived_zero` is true.
3. Locate rows with missing observed rate and positive cumulative reviews.
4. Confirm their activity proxy remains null and their analyzable flag is false.

Expected: no unknown positive-review rate is silently converted to zero.

### Scenario C: unavailable city fields

1. Inspect Milan's neighborhood-group availability.
2. Inspect Tokyo's host-listing-count and availability fields.
3. Confirm canonical nulls and source-availability flags.

Expected: missing source columns are unavailable, never zero-filled.

### Scenario D: opportunity classification

For one city, select one segment of each available label.

Expected:

- candidate and consolidated segments meet sample, positive-count, effect, adjusted-value, interval,
  and sensitivity rules;
- candidate alone meets the low-relative-supply rule;
- watch segments are eligible but show the unmet condition;
- insufficient-evidence segments remain visible without inferential claims;
- all components are visible and no weighted score exists.

### Scenario E: statistical traceability

Trace one room-type result, one segment result, and one association result.

Expected: each records population, sample, missing/zero share, method, effect, 95% interval, raw and
adjusted value, correction family, assumptions, sensitivity, and proxy-safe Spanish interpretation.

## 7. Close the Essential gate

Do not start Power BI work until all of the following are evidenced in the phase PR and GitHub item:

- full container workflow passes;
- source, schema, row, key, privacy, and output contracts pass;
- three notebooks execute cleanly and meet the narrative contract;
- required EDA and statistical families are complete;
- every published conclusion is linked to evidence and limitations;
- README, data dictionary, decision records, and Kanban evidence are current;
- the project owner records Essential acceptance.

## 8. Refresh the Power BI Desktop report

After Essential acceptance:

1. Open `powerbi/airbnb-supply-opportunity.pbit` in the recorded minimum supported Power BI Desktop
   version.
2. Set `DataRoot` to the absolute host path of this checkout's `data/powerbi/` directory.
3. Refresh all report queries.
4. Save the populated result as `powerbi/airbnb-supply-opportunity.pbix`.
5. Follow the page and semantic contract in [powerbi-report.md](contracts/powerbi-report.md).

Expected:

- all stable export files load in Import mode;
- the model schema and relationships match the contract;
- the report contains exactly the three required decision pages;
- no Power BI Service sign-in or paid license is required for local use.

## 9. Reconcile and accept the Medium report

On Page 3:

1. Confirm displayed build and schema versions match `build_control.csv`.
2. Clear slicers and verify imported row/control totals.
3. Apply slicers and confirm the global reconciliation difference remains zero.
4. Sample displayed metrics and compare them with accepted analytical outputs.
5. Test keyboard navigation, tab order, contrast, alt text, non-color cues, drillthrough, and Back.
6. Disable network access or block the map and confirm the ranked fallback remains decision-usable.
7. Ask a non-technical reviewer to identify up to three eligible opportunities for a selected city
   and explain their evidence and cautions.

Expected:

- zero unexplained reconciliation variance;
- sampled metrics match exactly in value, population, and definition;
- restricted fields are absent from visible/report-export surfaces;
- the review task finishes in under three minutes without assistance;
- the minimum tested Desktop version and refresh steps are recorded.

## 10. Failure recovery

- **Source mismatch**: stop; restore the approved file or review and version a manifest change.
- **Schema/quality failure**: use the finding ID and safe evidence path; never bypass silently.
- **Statistical diagnostic failure**: retain descriptive results and downgrade the affected
  interpretation; do not force a model result.
- **Notebook failure**: fix the package, configuration, or narrative dependency and rerun from a
  fresh kernel.
- **Partial output**: inspect the temporary build; the last accepted build remains authoritative.
- **Power BI path failure**: update only `DataRoot`, confirm filenames, then refresh.
- **Map unavailable**: use the ranked fallback; the page must remain complete without map tiles.
- **Reconciliation difference**: block report release until the export/model mismatch is explained.

## 11. Completion evidence

The final acceptance record links:

- GitHub Project item and acceptance criteria;
- phase branch, atomic commits, and reviewed PR;
- source and build manifests;
- test and performance summaries;
- executed notebooks and figures;
- data dictionary and decision records;
- `.pbix`, `.pbit`, report refresh guide, and reconciliation evidence;
- Essential and Medium owner approvals recorded separately.
