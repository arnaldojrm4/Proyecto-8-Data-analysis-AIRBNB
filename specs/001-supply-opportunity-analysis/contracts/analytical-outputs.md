# Contract: Analytical Outputs

**Version**: 1.0.0

**Producer**: analytical pipeline

**Consumers**: notebooks, validation workflow, Power BI Desktop report

The detailed entity fields and validation rules are defined in [data-model.md](../data-model.md).
This contract fixes filenames, grains, keys, formats, privacy boundaries, and release conditions.

## Canonical outputs

| Path | Format | Grain | Key | Consumer |
|---|---|---|---|---|
| `data/processed/listings.parquet` | Parquet | Listing | `listing_key` | EDA, statistics, tests |
| `data/processed/opportunity_segments.parquet` | Parquet | City + neighborhood + room type | `segment_key` | EDA, export |
| `data/processed/statistical_results.parquet` | Parquet | Statistical result | `result_id` | EDA, export |
| `artifacts/quality/source-profile.parquet` | Parquet | Source + field + profile metric | Composite | Audit notebook |
| `artifacts/quality/findings.parquet` | Parquet | Quality finding | `finding_id` | Audit, release gate |
| `artifacts/quality/transformations.parquet` | Parquet | Transformation | `transformation_id` | ETL notebook |
| `artifacts/quality/row-reconciliation.json` | JSON | Build | `build_id` | Acceptance validation |

### Parquet conventions

- PyArrow engine and compression are fixed by locked configuration.
- Tables use the data-model types, stable column order, and stable key sort.
- Schema metadata contains `schema_version`, `build_id`, and logical entity name.
- Validation compares logical schema and values; byte identity is not required across architectures.

## Power BI export set

All files are UTF-8 CSV with comma delimiter, double-quote escaping, LF line endings, ISO dates,
period decimal separator, empty field for null, no index column, fixed float representation, stable
column order, and stable key sort.

| Filename under `data/powerbi/` | Grain | Key | Required content |
|---|---|---|---|
| `dim_city.csv` | City | `city_key` | Spanish label and source/scope cautions |
| `dim_neighborhood.csv` | City-qualified neighborhood | `neighborhood_key` | City key, display label, aggregate centroid |
| `dim_room_type.csv` | Room type | `room_type_key` | Spanish label and sort order |
| `fact_listings.csv` | Privacy-safe listing | `listing_key` | Dimension keys, analyzable numeric metrics and flags |
| `fact_opportunity_segments.csv` | Opportunity segment | `segment_key` | All separate opportunity/evidence components |
| `fact_statistical_results.csv` | Reader-safe statistical result | `result_id` | Selected effects, intervals, corrected values, interpretation |
| `fact_quality_summary.csv` | Aggregate quality metric | Composite | Safe counts/rates and status only |
| `build_control.csv` | Build/output control | Composite | Build identity, source/output totals, hashes, gate status |

### Privacy contract

The Power BI export set MUST NOT contain:

- `listing_name`
- `host_name`
- raw `listing_id`
- raw `host_id`
- listing-level latitude or longitude
- raw rows or examples containing those values

`listing_key` is a hidden technical key and MUST NOT be placed in a visual, tooltip, accessible label,
exported table, or narrative. Host-dependent results are calculated upstream and exported only as
aggregates.

### Key and relationship contract

- Every dimension key is unique and non-null.
- `FactListings` has exactly one row per accepted `listing_key`.
- Every fact dimension key resolves to exactly one dimension row.
- `FactOpportunitySegments.segment_key` equals the canonical city-neighborhood-room-type composition.
- `FactStatisticalResults.segment_key` is nullable only for non-segment analyses.
- Dimension-to-fact relationships are one-to-many and single-direction.
- `BuildControl` remains disconnected from analytical relationships.

## Control manifest contract

`build_control.csv` includes one build summary plus one row per published output. At minimum it
contains:

```text
build_id, schema_version, generated_at_utc, source_manifest_hash,
analysis_config_hash, source_file_count, source_row_count,
canonical_row_count, distinct_listing_key_count, output_file,
output_row_count, output_sha256, release_gate_status
```

For the baseline source set:

- `source_file_count = 6`
- `source_row_count = 220031`
- `canonical_row_count + explicitly_quarantined_or_rejected_rows = 220031`
- `distinct_listing_key_count = canonical_row_count` for an accepted build
- every `output_row_count` equals an independently parsed count
- `release_gate_status = pass` only when every difference is explained and accepted

Power BI displays the manifest values but does not independently compute file hashes. The external
validation command recomputes hashes during release.

## Semantic rules

- All monetary comparisons and price-position fields are within-city.
- No output labels a price as revenue, margin, or profitability.
- No output defines current or recent activity because snapshot dates are unknown.
- `activity_proxy` is always labeled as historical-review activity.
- Source-unavailable values remain null and carry availability/status fields.
- Statistical result families retain raw and adjusted values, effect type, interval, assumptions,
  population, and sensitivity status.
- Opportunity labels follow the exact rules in `data-model.md`; no weighted score exists.

## Versioning and compatibility

- Removing or changing field meaning requires a major schema version.
- Adding an optional backward-compatible field requires a minor schema version.
- Clarifying metadata without changing values requires a patch schema version.
- The report records the supported schema version and refuses refresh on an incompatible major
  version.
- Output filename changes require simultaneous report-contract and refresh-guide changes.

## Release acceptance

The export set is publishable only when:

1. every file exists and passes its strict schema;
2. all primary and foreign keys pass;
3. privacy exclusions pass by field name and content checks;
4. source, canonical, and output row counts reconcile;
5. hashes are recorded after final stable export;
6. no mandatory quality or statistical result is missing;
7. all visible Spanish interpretations pass terminology guardrails; and
8. a fresh report refresh shows zero unexplained control variance.
