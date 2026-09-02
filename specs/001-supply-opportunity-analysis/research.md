# Research: Supply Opportunity Analysis

**Date**: 2026-09-02

**Status**: Complete; no unresolved technical clarifications

## 1. Runtime and dependency management

**Decision**: Use standard CPython 3.13, constrained to `>=3.13,<3.14`, with the tested patch
recorded in `.python-version`. Declare project metadata and direct dependencies in `pyproject.toml`
and commit `uv.lock`. Local, test, and container workflows use locked synchronization.

**Rationale**: Python 3.13 offers a conservative compatibility baseline for the required analytics
stack while remaining within its supported lifecycle. A project manifest plus a universal lockfile
gives one declared dependency graph for Windows development and Linux containers.

**Alternatives considered**:

- Python 3.14: already present in the empty local virtual environment, but offers less compatibility
  margin across the complete notebook, validation, and statistics toolchain.
- Python 3.12: mature, but has a shorter remaining support horizon.
- `requirements.txt` only: familiar, but duplicates project metadata and provides a weaker project
  workflow than a manifest plus lock.
- Conda, Poetry, or PDM: capable, but add no required benefit for this wheel-based project.

**Risks/constraints**: Package versions are exact only after `uv.lock` is generated and verified.
Dependency upgrades require a deliberate lockfile change and the full acceptance workflow. Do not
use a free-threaded Python build unless the entire stack is tested against it.

**Sources**: [CPython version status](https://devguide.python.org/versions/),
[PyPA pyproject guidance](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/),
[uv project layout](https://docs.astral.sh/uv/concepts/projects/layout/),
[uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)

## 2. Package architecture and notebook boundaries

**Decision**: Use a single installable `src`-layout package. Reusable ingestion, validation, ETL,
statistics, opportunity classification, and output logic lives in modules. Three ordered notebooks
provide the Spanish audit trail and narrative: source audit, ETL, and executive EDA.

**Rationale**: Thin notebooks remain readable and independently executable while tested modules own
computational behavior. A `src` layout prevents accidental imports from the repository root.

**Alternatives considered**:

- All logic in one notebook: rejected because it creates hidden state, duplication, and weak tests.
- One notebook per city: rejected because common transformations would diverge.
- A workflow orchestrator or distributed engine: rejected as unnecessary for three steps and
  220,031 rows.

**Risks/constraints**: Notebook order is explicit, not inferred from wildcard ordering. Notebook
outputs never become undocumented inputs. Executed copies are artifacts and do not overwrite source
notebooks.

**Sources**: [PyPA src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/),
[NBClient notebook execution](https://nbclient.readthedocs.io/en/latest/client.html),
[nbconvert execution](https://nbconvert.readthedocs.io/en/latest/execute_api.html)

## 3. Source inventory and immutable input contract

**Decision**: Copy the exact six provided files into the repository's `data/raw/` layer, verify the
following baseline, and then mount that directory read-only during container execution. Parsed CSV
records, not physical line counts, are authoritative because quoted text contains embedded newlines.

| City | File | Parsed rows | Bytes | Columns | SHA-256 |
|---|---:|---:|---:|---:|---|
| London | `london_airbnb.csv` | 85,068 | 11,578,155 | 16 | `766A8AB23C1A469F8C95F5DDE0DD21FF8583C676AFF33E6806CDD872CFFD5977` |
| Madrid | `madrid_airbnb.csv` | 19,618 | 2,801,783 | 16 | `5F8012389BFFF705B0B8F2B2A19FAC4D80C6EEE52B6694FE99A5F63FAE2D3799` |
| Milan | `milan_airbnb.csv` | 18,322 | 2,375,246 | 15 | `F815FA5F93265AEE95CB61479B123D77A52A7E46162010A780EF4E9F666E04F7` |
| New York | `NY_airbnb.csv` | 48,895 | 7,077,973 | 16 | `E420DB40FF10FCB40EFC1B5B1648EE0B18A48F4E4537155CECC59FE95D18783A` |
| Sydney | `sydney_airbnb.csv` | 36,662 | 5,504,518 | 16 | `2ABC21647378F06EF6225805152BF87F5819A66D4AE6BFFEDD87D92FA3FD90D3` |
| Tokyo | `tokyo_airbnb.csv` | 11,466 | 1,738,173 | 14 | `33D049A365D820E111125A1D56937A81999AFAD9BFB5FDB59DBECAC01E305AAE` |
| **Total** | **6 files** | **220,031** | **31,075,848** | **14-16** | **Per-file hashes above** |

The common schema has 14 fields. Milan lacks `neighbourhood_group`. Tokyo lacks
`calculated_host_listings_count` and `availability_365`; those canonical fields remain nullable and
carry source-availability flags.

**Rationale**: File hashes, sizes, schemas, and parsed record counts detect accidental source changes
before stale derived results are reused.

**Alternatives considered**: Copying raw data into a container image was rejected because it obscures
source ownership. Ignoring source hashes was rejected because filenames alone do not establish
identity.

**Risks/constraints**: Provenance, license, currency, and extraction dates are unknown. Documentation
must retain those limitations and must not label the files official Airbnb data.

**Sources**: local inspection of the six user-provided CSV files;
[Docker read-only bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)

## 4. Canonical storage and interoperability outputs

**Decision**: Make typed, sorted Parquet files the canonical derived outputs. Generate stable UTF-8
CSV tables in `data/powerbi/` solely as the Power BI interoperability contract. Use explicit null,
date, decimal, float-format, delimiter, encoding, column-order, and row-sort conventions.

**Rationale**: Parquet preserves types and compresses the reusable analytical layer. Deliberate CSV
exports remain transparent, inspectable, and portable for the desktop report.

**Alternatives considered**: CSV-only loses type fidelity; a database adds operational complexity;
Power BI reading pipeline intermediates couples the report to unstable data.

**Risks/constraints**: Logical contents and control totals are release evidence; Parquet byte hashes
alone are not, because writer metadata can vary. Export schemas are versioned contracts.

**Sources**: [Pandas Parquet output](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html),
[Pandas scaling guidance](https://pandas.pydata.org/docs/user_guide/scale.html)

## 5. Schema validation and quality evidence

**Decision**: Use versioned Pandera models with permissive raw schemas and strict canonical/output
schemas. Run lazy validation to report all failures. Supplement schema checks with explicit source
hashes, row reconciliation, composite-key checks, cross-field rules, referential integrity, and
privacy/export checks.

**Rationale**: Dataframe-native contracts make expected types, nullability, domains, ranges, and
joint uniqueness inspectable without introducing a full data-observability platform.

**Alternatives considered**: Great Expectations is heavier than this local six-file workflow;
row-by-row validation is inefficient; plain assertions lack structured failure cases.

**Risks/constraints**: Raw coercion must never conceal invalid values. Failed mandatory checks return
a non-zero process status and preserve a machine-readable failure report. Outliers are flagged, not
silently deleted.

**Sources**: [Pandera dataframe models](https://pandera.readthedocs.io/en/stable/dataframe_models.html),
[strict schemas](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html),
[lazy validation](https://pandera.readthedocs.io/en/stable/lazy_validation.html)

## 6. Historical activity representation

**Decision**: Preserve the original nullable `reviews_per_month` as
`reviews_per_month_observed`. Derive `has_historical_activity` from `number_of_reviews > 0`. Derive
`activity_proxy` as the observed rate when present and as zero only when the rate is missing and
`number_of_reviews == 0`; set `activity_proxy_derived_zero = true` for those rows. A missing rate with
positive cumulative reviews remains unknown.

Run primary summaries on `activity_proxy` and publish complete-case sensitivity results using only
observed rates. Model positive intensity only where an observed positive rate exists.

**Rationale**: Local profiling found perfect alignment between missing rate, missing last-review date,
and zero reviews in five cities. Sydney has 123 rows with positive cumulative reviews but missing
both rate and last-review date; those values cannot be treated as zero. The dual-field design keeps
the assumption visible and testable.

**Alternatives considered**: Filling every missing rate with zero changes unknown values into facts;
dropped complete cases exclude all no-review listings and bias activity summaries upward.

**Risks/constraints**: The derived rate remains a historical-review proxy. It does not establish
bookings, demand, occupancy, listing age, or current activity.

**Sources**: local cross-field profiling of all 220,031 rows.

## 7. Descriptive and inferential statistical design

**Decision**:

1. Report count, missing share, zero share, median, IQR, p90, p99, and positive-only median before
   inferential analysis.
2. Compare room types within each city using tie-corrected Kruskal-Wallis tests. Apply Holm correction
   to the six omnibus tests and prespecified within-city pairwise rank comparisons. Report probability
   of superiority and 95% intervals alongside raw median differences.
3. For every eligible `city + neighborhood + room_type` segment, compare its activity distribution
   with the remaining listings of the same city and room type. Control the neighborhood-screening
   family within city with Benjamini-Hochberg FDR at 0.05. Report raw and adjusted p-values,
   probability of superiority, median difference, and clustered bootstrap intervals.
4. Report within-city Spearman correlations for `price` and `minimum_nights` against activity. Correct
   the 12 primary coefficients as one Benjamini-Hochberg family.
5. Fit a two-part adjusted sensitivity model: activity present versus absent, then positive activity
   intensity. Adjust for room type and eligible neighborhood; express effects per doubling or
   interquartile-range change. Downgrade conclusions when diagnostics are inadequate.

**Rationale**: Rank methods resist skew and outliers; two-part modeling distinguishes the probability
of activity from its positive intensity. Effect sizes and intervals prevent large samples from
turning negligible differences into executive recommendations.

**Alternatives considered**: t-tests, ANOVA, Pearson correlation, and ordinary least squares are not
primary because the variables are skewed, tied, zero-heavy, and heteroskedastic. Count models are not
used for `reviews_per_month` because it is a continuous derived rate.

**Risks/constraints**: Rank tests compare distributions, not automatically medians. Host portfolios
create dependence, so bootstrap resampling and model covariance cluster on `host_id` when available.
All associations remain non-causal.

**Sources**: [SciPy Kruskal-Wallis](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html),
[SciPy Spearman correlation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html),
[statsmodels rank comparison](https://www.statsmodels.org/stable/generated/statsmodels.stats.nonparametric.rank_compare_2indep.html),
[statsmodels multiple testing](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html),
[SciPy BCa bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)

## 8. Eligibility, sensitivity, and opportunity classification

**Decision**: A segment is inferentially eligible when it has at least 30 analyzable listings and at
least 10 positive-activity listings. Smaller segments remain visible as descriptive-only. Repeat key
results at thresholds of 20 and 50, with complete-case versus derived-zero activity, raw-valid versus
p1/p99-winsorized sensitivity, listing versus host-clustered inference, and common six-city versus
enriched five-city fields.

The opportunity matrix keeps every component separate. It assigns deterministic labels:

- `candidate`: eligible; activity superiority at least 0.56 with adjusted `q < 0.05`; the 95%
  interval excludes no difference; direction and label survive the prespecified sensitivity checks;
  and the room type's neighborhood supply share is below its citywide share.
- `consolidated`: satisfies the robust activity criteria but not the low-relative-supply condition.
- `watch`: eligible but the activity, supply, precision, or sensitivity conditions do not all support
  action.
- `insufficient_evidence`: fails an eligibility or required-data rule.

Price position, listing scale, active share, positive intensity, minimum-night distribution,
uncertainty, and quality flags remain visible context and are never summed into a score. Candidate
rankings use business scale first, then effect magnitude; p-values never determine ordering alone.

**Rationale**: Explicit labels expose the exact trade-offs and let an executive understand why an
area is prioritized. A fixed score would conceal value judgments and create false precision.

**Alternatives considered**: Top-N before eligibility invites selection bias; pooling small
neighborhoods hides geography; a weighted composite score obscures assumptions; significance-only
ranking favors large samples.

**Risks/constraints**: The sample thresholds are operational stability rules, not guarantees of
power. If fewer than three candidates exist for a city, the report shows fewer and does not weaken
the rules. A candidate is a hypothesis for commercial investigation, not proven unmet demand.

**Sources**: [Vargha-Delaney effect size](https://doi.org/10.3102/10769986025002101),
[Benjamini-Hochberg FDR](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x),
[Holm correction](https://doi.org/10.2307/4615733)

## 9. Power BI Desktop report contract

**Decision**: Deliver a three-page Power BI Desktop report in Import mode. The executive handoff
includes a populated `.pbix`, a data-free `.pbit`, the versioned analytical exports, checksums, the
minimum tested Desktop version, and refresh instructions. One text parameter, `DataRoot`, points to
the host-side `data/powerbi/` directory; all source paths derive from it.

Use a star schema with single-direction one-to-many relationships. The pipeline owns row-level
features, opportunity labels, confidence fields, and provenance. A dedicated Measures table owns
filter-context aggregations; visual objects contain no duplicated business logic.

**Rationale**: Power Query parameters make local refresh configurable. The PBIX is immediately
viewable, while the PBIT preserves report structure, model, measures, queries, and parameters without
embedded data.

**Alternatives considered**: A hard-coded absolute path is not portable. PBIX-only weakens
reproducibility. Power BI Service, Embedded, Premium, and paid sharing are outside scope.

**Risks/constraints**: In Microsoft terminology this is a multipage report, not a service dashboard.
Without Power BI Service there is no browser sharing, scheduled refresh, service audit, secure
per-user enforcement, or true one-page dashboard. Report relocation requires updating `DataRoot` and
refreshing; there is no promised automatic PBIX-relative path.

**Sources**: [Power Query parameters](https://learn.microsoft.com/en-us/power-query/power-query-query-parameters),
[Power BI templates](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-templates),
[Import mode](https://learn.microsoft.com/en-us/power-bi/connect-data/service-dataset-modes-understand),
[dashboards versus reports](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards),
[star schema guidance](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)

## 10. Executive report experience and geography

**Decision**: Page 1 contains decision-ready KPIs, the acquisition message, and a small ranked set of
opportunities. Page 2 contains an aggregated Azure Maps view plus an accessible ranked table or bar
fallback. Page 3 contains confidence, methodology, provenance, data-quality flags, and supporting
detail. Use consistent geography, room-type, and evidence-status slicers; locked filters enforce
eligibility. Page 3 is the drillthrough target.

Use aggregate neighborhood or segment centroids, not 220,031 listing points. Apply at least 4.5:1
text contrast, alt text, deliberate tab order, plain-language titles, and non-color status cues.

**Rationale**: The layout matches the executive decision path: recommendation, location, then proof.
An accessible non-map view preserves the core decision if map services are unavailable.

**Alternatives considered**: Plotting all listings harms clarity and exceeds visual limits. Critical
evidence in tooltips is inaccessible. A dense analytical canvas contradicts the target audience.

**Risks/constraints**: Azure Maps requires network access to Microsoft endpoints and has location-data
and regional considerations. The fallback ranking must remain usable offline. Tooltips carry only
supplementary information.

**Sources**: [Power BI accessibility](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports),
[Azure Maps visual](https://learn.microsoft.com/en-us/azure/azure-maps/power-bi-visual-get-started),
[drillthrough guidance](https://learn.microsoft.com/en-us/power-bi/guidance/report-drillthrough),
[report tooltips](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-tooltips)

## 11. Report reconciliation and control manifest

**Decision**: Every pipeline run emits a disconnected control table with build ID, schema version,
UTC generation time, source hashes and rows, output rows, distinct keys, additive control totals,
date bounds, and output hashes. Page 3 compares filter-independent model totals with this manifest;
zero unexplained variance is a release gate.

**Rationale**: A successful refresh proves only that data loaded, not that the imported model matches
the approved build.

**Alternatives considered**: Visual spot checks and refresh-success status alone are insufficient.
The report displays hashes for provenance, but external validation computes them.

**Risks/constraints**: Desktop has no centralized refresh history. Filter-independent reconciliation
measures must not change with slicers.

**Sources**: [Power BI refresh](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data),
[COUNTROWS](https://learn.microsoft.com/en-us/dax/countrows-function-dax),
[REMOVEFILTERS](https://learn.microsoft.com/en-us/dax/removefilters-function-dax)

## 12. Automated testing, containerization, and budgets

**Decision**: Use pytest with unit, contract, and integration suites. A dedicated NBClient runner
executes the three notebooks in fresh kernels with errors disallowed. The container uses a
digest-pinned `python:3.13-slim` base, locked dependencies, a non-root user, read-only raw mount, and
writable processed/artifact mounts. One `all` command runs audit, ETL, analysis, exports, tests, and
notebook validation.

Mark full-data and notebook tests `slow`, but always run them in the containerized acceptance gate.
Use a documented reference budget of ETL at most 60 seconds, the complete analytical workflow at most
5 minutes, and peak memory at most 2 GB on 2 vCPU and 4 GB RAM. Recalibrate only from recorded
measurements.

**Rationale**: Layered tests diagnose failures quickly; full-data integration and notebook execution
prove the actual deliverable. Digests, lockfiles, stable sorting, locale, timezone, and seeds reduce
environment drift.

**Alternatives considered**: Manual notebook execution is not evidence. Tag-only base images are
mutable. Dask, Spark, or Polars add complexity without a scale need.

**Risks/constraints**: Architecture-specific wheels can produce different image bytes; acceptance is
based on logical tables, hashes of stable exports, and approved metrics, not identical container
digests across architectures.

**Sources**: [pytest good practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html),
[Docker image digests](https://docs.docker.com/dhi/explore/security-concepts/digests/),
[uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/),
[Pandas memory usage](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.memory_usage.html)
