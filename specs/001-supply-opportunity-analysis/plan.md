# Implementation Plan: Supply Opportunity Analysis

**Branch**: `001-supply-opportunity-analysis` (planned; current checkout is `main`) | **Date**:
2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-supply-opportunity-analysis/spec.md`

## Summary

Build a reproducible six-city analytical workflow that preserves and fingerprints the original CSV
files, validates and canonicalizes all 220,031 listings, produces a fully documented executive EDA,
and identifies transparent host-acquisition opportunities at city, neighborhood, and room-type
grain. The committed delivery closes the Essential level before creating a three-page Power BI
Desktop report for the Medium level.

The technical approach is a single Python package with three thin ordered notebooks, typed Parquet
analytical outputs, stable CSV report exports, explicit data and CLI contracts, rigorous nonparametric
and sensitivity analysis, layered automated tests, and a locked Linux container workflow. Power BI
Desktop imports a star-shaped set of generated files through one configurable host path; it is not
run inside the container and does not require Power BI Service.

## Technical Context

**Language/Version**: Standard CPython 3.13 (`>=3.13,<3.14`), with one tested patch pinned in
`.python-version` and the container

**Primary Dependencies**: Pandas, NumPy, Matplotlib, Seaborn, Plotly, SciPy, statsmodels, Jupyter,
PyArrow, Pandera, NBClient, pytest, and uv; exact compatible versions committed in `uv.lock`

**Storage**: Immutable CSV sources; typed Parquet canonical and aggregate datasets; stable UTF-8 CSV
exports for Power BI; JSON/CSV manifests and quality evidence; `.pbix` and `.pbit` report artifacts

**Testing**: pytest unit, contract, and integration suites; Pandera schema checks; full-data
reconciliation; fresh-kernel NBClient execution; Dockerized acceptance workflow; Power BI control
totals and manual visual/accessibility review

**Target Platform**: Linux container for all Python processing and validation; Windows 10 or later
with free Power BI Desktop for report authoring and consumption

**Project Type**: Single-project batch analytics pipeline with reproducible notebooks and a local
desktop BI report

**Performance Goals**: On a documented 2-vCPU/4-GB reference container, ETL completes in at most
60 seconds, the complete audit-to-export analytical workflow in at most 5 minutes, and peak resident
memory remains at or below 2 GB

**Constraints**: Raw sources read-only; no paid Power BI service; no absolute machine paths; no
cross-city monetary comparisons; no recency claims; no PII in visible outputs; deterministic seeds,
sorting, locale, timezone, and export formatting; mandatory Spanish narrative documentation

**Scale/Scope**: Six CSV files, 220,031 listing rows, 14 common source fields and up to 16 fields,
three ordered notebooks, one canonical listing fact, segment and statistical aggregates, three Power
BI report pages, and Essential then Medium delivery gates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-design gate

| Constitutional obligation | Status | Plan evidence |
|---|---|---|
| Essential closes before Medium | PASS | Separate delivery phases and an explicit Essential acceptance gate precede Power BI work. |
| Raw data remains immutable and traceable | PASS | Source manifest, SHA-256 checks, read-only raw mount, and row-level lineage are mandatory. |
| Quality precedes analysis | PASS | Raw and canonical schema validation, reconciliation, quality reports, and explicit treatment logs gate EDA. |
| Statistical claims are rigorous and honest | PASS | Within-city rank tests, effect sizes, confidence intervals, corrections, sensitivity checks, and proxy labels are designed. |
| Notebooks are auditable deliverables | PASS | Three ordered fresh-kernel notebooks contain Spanish narrative while package modules own calculations. |
| Executive communication is decision-first | PASS | Separate opportunity components, deterministic labels, three decision pages, and no opaque score support the acquisition decision. |
| Git and Kanban govern completion | PASS | Phase branches, issues, PR evidence, and status gates remain required implementation controls. |
| All work remains contemporaneously documented | PASS | Research, contracts, manifests, decision records, notebooks, report guidance, and README updates are first-class artifacts. |
| Required stack and portability constraints hold | PASS | Mandatory analytics libraries, Power BI Desktop, Docker, pinned dependencies, Spanish outputs, and comparison restrictions are preserved. |

No constitutional violation requires justification. Phase 0 research resolves all technical choices;
there are no unresolved research questions.

## Architecture

The system is a deterministic artifact pipeline:

```text
raw CSV files (read-only)
        |
        v
source inventory + permissive raw validation
        |
        v
canonicalization + treatment log + strict schema validation
        |
        +-----------------------> quality/reconciliation artifacts
        |
        v
descriptive EDA + statistical analysis
        |
        v
transparent opportunity segments + sensitivity status
        |
        +-----------------------> executed notebooks + figures
        |
        v
versioned Parquet datasets + stable Power BI CSV star exports
        |
        v
Power BI Desktop report + disconnected control manifest
```

The command interface is the only orchestration entry point. It calls pure, focused modules and
returns non-zero status when a mandatory contract fails. Notebooks call the same public package
functions; they do not implement alternative transformations. Every build receives a build ID and
schema version recorded across the control manifest and generated tables.

### Key design decisions

- The canonical listing grain is `city + listing_id`; `source_file` and `source_row_number` retain
  row lineage.
- Original nullable review rate is preserved. A separate activity proxy uses a derived zero only
  when cumulative reviews are zero, and always carries a derivation flag.
- Six-city common-core outputs exclude unavailable host and availability fields from required
  comparisons. Five-city enrichment keeps those measures and shows Tokyo as unavailable.
- Opportunity labels are rule outcomes, not scores. Each input, threshold, effect, interval,
  multiplicity-adjusted value, and sensitivity flag remains visible.
- Power BI receives presentation-ready facts and dimensions. Transformation and statistical logic
  remain owned and tested in the pipeline; DAX owns only filter-context aggregations and
  reconciliation measures.
- The geographic page uses aggregated segment centroids and an accessible ranked fallback, never
  individual listing points.

## Statistical Analysis Plan

### Populations and estimands

- Run all monetary and inferential comparisons within city.
- Treat `reviews_per_month` as historical review activity only.
- Report the probability of any historical activity separately from positive activity intensity.
- Cluster resampling and applicable model covariance by `host_id` to account for multi-listing hosts.
- Keep invalid values out of the affected metric calculation without deleting their listing rows;
  report all exclusions and affected counts.

### Confirmatory and exploratory families

1. Room type: tie-corrected Kruskal-Wallis per city, Holm-corrected across six omnibus tests;
   prespecified pairwise rank comparisons within qualifying cities, also Holm-corrected.
2. Neighborhood/type segments: compare each eligible segment with the rest of the same city and room
   type; apply Benjamini-Hochberg correction within each city's exploratory family.
3. Associations: within-city Spearman coefficients for price and minimum nights against activity;
   apply Benjamini-Hochberg correction across the 12 primary coefficients.
4. Adjusted sensitivity: two-part model for activity presence and positive intensity, adjusted for
   room type and eligible neighborhood; downgrade interpretation when diagnostics fail.

Every inferential output includes raw and adjusted p-values, a scale-appropriate effect size, a 95%
interval, sample size, missing/zero share, test family, assumptions, and interpretation guardrail.

### Eligibility and sensitivity

A segment requires at least 30 analyzable listings and 10 positive-activity listings for inferential
eligibility. Smaller segments remain descriptive-only. Sensitivity runs repeat key conclusions at
20/30/50 listing thresholds, complete-case versus derived-zero activity, raw-valid versus p1/p99
winsorized metrics, listing versus host-clustered inference, and common-core versus five-city
enrichment. Robustness means the effect direction and action label persist, not merely that a
p-value remains below 0.05.

## Opportunity Matrix Rules

Each row represents one `city + neighborhood + room_type` segment and exposes listing count, city and
neighborhood supply shares, active-listing share, median activity, positive-only median activity,
within-city/room-type price position, minimum-night distribution, effect size, interval, adjusted
q-value, sensitivity status, and quality flags.

Labels are deterministic:

- `candidate`: eligible; probability of superiority is at least 0.56 with adjusted `q < 0.05`; its
  95% interval excludes no difference; direction and label survive required sensitivity checks; and
  the room type's neighborhood share is below its citywide share.
- `consolidated`: satisfies the robust activity conditions but not low relative supply.
- `watch`: eligible, but activity, supply, precision, or robustness conditions do not all support
  action.
- `insufficient_evidence`: fails an eligibility or required-data condition.

Price and statistical significance never form a hidden combined score. Candidate ordering uses
listing scale first and effect magnitude second. If a city has fewer than three candidates, the
report shows fewer rather than weakening the rules.

## Power BI Design

Deliver both an imported-data `.pbix` and a data-free `.pbit`. A single text parameter named
`DataRoot` points to the host `data/powerbi/` directory. Stable filenames are derived from that
parameter. The model uses one-to-many, single-direction relationships from dimensions to facts and a
dedicated Measures table.

- **Page 1 — Resumen ejecutivo**: selected-city context, candidate count, eligible inventory,
  prioritized segments, one plain-language recommendation, and visible proxy/source cautions.
- **Page 2 — Oportunidades de captación**: aggregated Azure Maps view, ranked accessible fallback,
  and consistent city, room-type, and evidence-status slicers.
- **Page 3 — Detalle y confianza**: drillthrough detail, component metrics, effect and interval,
  adjusted value, sensitivity, quality flags, build/schema version, source hashes, and reconciliation
  controls.

The report uses at least 4.5:1 text contrast, alt text, intentional tab order, non-color cues, and
plain-language titles. Azure Maps is optional at runtime: the ranked view remains useful without
network access. Without Power BI Service, the deliverable is technically a multipage report rather
than a service dashboard and has no scheduled refresh, centralized sharing, or service-side access
control.

## Project Structure

### Documentation (this feature)

```text
specs/001-supply-opportunity-analysis/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- pipeline-cli.md
|   |-- analytical-outputs.md
|   `-- powerbi-report.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md                         # Created later by $speckit-tasks
```

### Source Code (repository root)

```text
data/
|-- raw/                             # Six immutable, versioned CSV sources
|-- processed/                       # Canonical and aggregate Parquet outputs
`-- powerbi/                         # Stable CSV star-schema exports

src/
`-- airbnb_supply_analysis/
    |-- __init__.py
    |-- config.py                    # Paths, schema/build version, deterministic settings
    |-- io.py                        # Source inventory and typed readers/writers
    |-- schemas.py                   # Raw, canonical, and output contracts
    |-- quality.py                   # Profiles, findings, and reconciliation
    |-- etl.py                       # Canonicalization and treatment records
    |-- statistics.py                # Tests, intervals, corrections, sensitivity
    |-- opportunity.py               # Segment metrics and transparent labels
    |-- visualization.py             # Shared chart preparation and styling
    |-- exports.py                   # Parquet, Power BI CSV, and manifest outputs
    |-- notebooks.py                 # Ordered fresh-kernel notebook runner
    `-- cli.py                       # Audit/build/analyze/export/validate/all commands

notebooks/
|-- 01_data_audit.ipynb
|-- 02_etl.ipynb
`-- 03_executive_eda.ipynb

tests/
|-- fixtures/                        # Small synthetic edge-case datasets
|-- unit/                            # Pure transformation/statistical rule tests
|-- contract/                        # Source, schema, output, and privacy contracts
`-- integration/                     # Full pipeline, notebooks, Docker, reconciliation

config/
|-- source-manifest.json             # Approved raw identities and schemas
|-- analysis.yml                     # Thresholds, test families, seeds, labels
`-- data-dictionary.yml              # Canonical definitions and availability

artifacts/
|-- quality/                         # Profiles, findings, treatment and reconciliation
|-- figures/                         # Approved static and interactive EDA outputs
`-- executed_notebooks/              # Clean-kernel execution evidence

powerbi/
|-- airbnb-supply-opportunity.pbix
|-- airbnb-supply-opportunity.pbit
|-- README.md                        # DataRoot, refresh, tested version, reconciliation
`-- theme.json                       # Accessible report theme

scripts/
`-- verify_powerbi.ps1               # Documented report/export reconciliation helper

pyproject.toml
uv.lock
.python-version
Dockerfile
compose.yaml
README.md
```

**Structure Decision**: A single Python project owns all computation and exports. Notebooks are
narrative clients of the package; Power BI is a local consumer of versioned output contracts.
Separate services, databases, distributed processing, and deployment infrastructure are rejected
because neither scale nor scope requires them.

## Delivery Phases

### Phase A — Foundation and governance

Establish the phase branch, GitHub Project fields and statuses, issue/PR templates, tracked
constitution, source inventory, package metadata, locked runtime, deterministic configuration,
container shell, and documentation skeleton.

### Phase B — Source audit and quality

Bring the six exact raw files under `data/raw/`, verify hashes and parsed counts, implement raw schema
and cross-field checks, produce the data dictionary and quality artifacts, and complete the first
documented notebook.

### Phase C — Canonical ETL

Implement canonical types, availability flags, conditional activity derivation, treatment logging,
row reconciliation, privacy-safe outputs, canonical Parquet, and the second documented notebook.

### Phase D — Executive EDA and statistics

Implement descriptive profiles, required hypothesis families, clustered intervals, sensitivity
analysis, transparent opportunity labels, figures, statistical output contracts, and the third
documented notebook.

### Phase E — Essential acceptance gate

Run the complete locked container workflow, all tests, all notebooks, documentation review, language
guardrails, manifest reconciliation, and GitHub evidence. No Medium work starts until every Essential
criterion passes.

### Phase F — Power BI report

Generate the star exports and control manifest, author the three-page report and template, configure
`DataRoot`, measures, navigation, accessibility, offline ranking fallback, and metric reconciliation.

### Phase G — Medium acceptance gate

Refresh from a clean host path, reconcile all controls, inspect every page and interaction, verify the
nontechnical three-minute scenario, record the tested Desktop version, and complete the final
documentation and PR evidence.

## Post-design Constitution Check

**Status**: PASS

| Phase 1 artifact | Constitutional evidence | Result |
|---|---|---|
| `data-model.md` | Models immutable source identity, row lineage, source-unavailable fields, activity derivation flags, restricted fields, findings, treatments, effects, sensitivity, and release states. | PASS |
| `contracts/pipeline-cli.md` | Makes source checks, quality, ETL, statistics, tests, notebooks, exports, validation, non-zero failures, atomic publication, and safe logs executable through one interface. | PASS |
| `contracts/analytical-outputs.md` | Fixes typed canonical outputs, Power BI schemas, privacy exclusions, row/hash reconciliation, semantic guardrails, and versioning. | PASS |
| `contracts/powerbi-report.md` | Enforces three decision-first pages, visible components, proxy cautions, accessibility, no paid service, portable `DataRoot`, and zero-variance reconciliation. | PASS |
| `quickstart.md` | Proves raw immutability, 220,031-row reconciliation, clean notebooks, statistical traceability, documentation, Essential-before-Medium gating, and report acceptance. | PASS |

All eight principles and the technical constraints remain satisfied after design. No complexity
exception or constitutional amendment is required.
