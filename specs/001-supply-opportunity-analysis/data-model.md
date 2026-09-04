# Data Model: Supply Opportunity Analysis

**Date**: 2026-09-02

**Schema version**: `1.0.0`

**Canonical grain**: one parsed listing record per `city_key + listing_id`

## Conventions

- Technical names use English `snake_case`; reader-facing labels use Spanish.
- Nullable integers and floats preserve missing values; missing is never encoded as zero.
- Dates use ISO `YYYY-MM-DD` where valid and remain nullable when absent or invalid.
- Processing timestamps use UTC ISO 8601 and live in manifests, not analytical observations.
- Stable data tables are sorted by their documented keys before export.
- `listing_name`, `host_name`, `listing_id`, and `host_id` are restricted fields. They support
  lineage and aggregate analysis but never appear in reader-facing outputs.
- Every output includes `schema_version` and `build_id`, either as columns or manifest metadata.

## Entity: SourceFile

Represents one immutable city CSV and its approved identity.

| Field | Type | Required | Validation |
|---|---|---:|---|
| `source_id` | string | yes | Stable unique slug, one per source |
| `city_key` | string | yes | One of `london`, `madrid`, `milan`, `new_york`, `sydney`, `tokyo` |
| `display_city_es` | string | yes | Londres, Madrid, Milán, Nueva York, Sídney, Tokio |
| `file_name` | string | yes | Exact approved filename |
| `relative_path` | string | yes | Must resolve below `data/raw/` |
| `sha256` | fixed string | yes | 64 uppercase hexadecimal characters |
| `byte_size` | integer | yes | Positive and equal to observed file size |
| `parsed_row_count` | integer | yes | Positive and equal to CSV-parser result |
| `column_names` | list[string] | yes | Exact ordered raw header |
| `encoding` | string | yes | Approved input encoding |
| `delimiter` | string | yes | One character; comma for baseline sources |
| `provenance_status` | enum | yes | `unknown_public_educational` for baseline |
| `license_status` | enum | yes | `unknown` for baseline |
| `snapshot_date` | date | no | Null for baseline sources |
| `currency` | string | no | Null until sourced metadata exists |

### Baseline state

| `source_id` | `file_name` | `parsed_row_count` | Raw columns |
|---|---|---:|---:|
| `london` | `london_airbnb.csv` | 85,068 | 16 |
| `madrid` | `madrid_airbnb.csv` | 19,618 | 16 |
| `milan` | `milan_airbnb.csv` | 18,322 | 15 |
| `new_york` | `NY_airbnb.csv` | 48,895 | 16 |
| `sydney` | `sydney_airbnb.csv` | 36,662 | 16 |
| `tokyo` | `tokyo_airbnb.csv` | 11,466 | 14 |

The exact byte sizes, ordered headers, and SHA-256 values are defined in
[research.md](research.md#3-source-inventory-and-immutable-input-contract) and become the initial
`config/source-manifest.json` contract.

## Entity: RawListing

Represents one parsed CSV record before canonical conversion. Values remain source strings until
validated.

| Source field | Expected semantic type | Availability | Raw validation |
|---|---|---|---|
| `id` | integer identifier | all cities | Present, parseable, unique within city |
| `name` | text | all cities | Nullable; restricted from visible outputs |
| `host_id` | integer identifier | all cities | Present and parseable |
| `host_name` | text | all cities | Nullable; restricted from visible outputs |
| `neighbourhood_group` | text | except Milan; entirely null in some sources | Absence and all-null state preserved separately |
| `neighbourhood` | text | all cities | Nullable values flagged and excluded from segment eligibility |
| `latitude` | decimal degrees | all cities | Parseable; within `[-90, 90]` |
| `longitude` | decimal degrees | all cities | Parseable; within `[-180, 180]` |
| `room_type` | category | all cities | Observed set registered; new values fail strict output validation |
| `price` | local published price | all cities | Numeric; nonpositive and extreme values flagged |
| `minimum_nights` | count | all cities | Integral; values below 1 invalid, extremes flagged |
| `number_of_reviews` | count | all cities | Integral and nonnegative |
| `last_review` | date | all cities | Nullable; valid values parse as ISO date |
| `reviews_per_month` | rate | all cities | Nullable and nonnegative when present |
| `calculated_host_listings_count` | count | except Tokyo | Nullable, integral, nonnegative when source field exists |
| `availability_365` | day count | except Tokyo | Nullable, integral, within `[0, 365]` when source field exists |

Additional lineage fields assigned at read time:

- `source_id`
- `source_record_number`: one-based parsed data-record position, independent of physical line count
- `raw_record_hash`: stable hash of the normalized parsed field sequence for duplicate evidence

## Entity: CanonicalListing

Represents the validated common schema. Invalid metric values remain present in the raw lineage but
become null in the typed analytical field with a corresponding quality finding and validity flag.

| Field | Type | Nullable | Rule |
|---|---|---:|---|
| `listing_key` | string | no | `{city_key}:{listing_id}`; unique |
| `city_key` | category | no | Foreign key to `City` |
| `listing_id` | nullable integer | no | Original value; restricted |
| `listing_name` | string | yes | Original `name`; restricted |
| `host_id` | nullable integer | no | Original host identifier; restricted |
| `host_name` | string | yes | Original value; restricted |
| `neighborhood_group` | string | yes | Original value or unavailable/null, never fabricated |
| `neighborhood` | string | yes | Trimmed canonical display value; original retained in lineage |
| `neighborhood_key` | string | yes | City-qualified key; null when neighborhood invalid/missing |
| `latitude` | float | yes | Decimal degrees when valid |
| `longitude` | float | yes | Decimal degrees when valid |
| `room_type` | category | yes | `entire_home_apt`, `private_room`, `shared_room`, `hotel_room` |
| `price` | float | yes | Original numeric price when valid for analysis |
| `price_is_valid` | boolean | no | False for missing, nonnumeric, zero, or negative price |
| `minimum_nights` | nullable integer | yes | At least 1 when valid |
| `minimum_nights_is_valid` | boolean | no | Explicit metric eligibility |
| `number_of_reviews` | nullable integer | yes | Nonnegative when valid |
| `last_review` | date | yes | Parsed original; never filled with sentinel values |
| `reviews_per_month_observed` | float | yes | Original nonnegative rate only |
| `has_historical_activity` | boolean | yes | `number_of_reviews > 0` when count is valid |
| `activity_proxy` | float | yes | Observed rate, or derived zero under the documented rule |
| `activity_proxy_derived_zero` | boolean | no | True only when rate is missing and review count is exactly zero |
| `activity_proxy_is_analyzable` | boolean | no | False when neither observed nor validly derived |
| `calculated_host_listings_count` | nullable integer | yes | Unavailable for Tokyo |
| `availability_365` | nullable integer | yes | Unavailable for Tokyo; not interpreted as occupancy |
| `neighborhood_group_source_available` | boolean | no | Source-schema availability |
| `host_listing_count_source_available` | boolean | no | False for Tokyo |
| `availability_365_source_available` | boolean | no | False for Tokyo |
| `coordinate_is_valid` | boolean | no | Both coordinates parse and pass global range checks |
| `source_id` | string | no | Foreign key to `SourceFile` |
| `source_record_number` | integer | no | Parsed record lineage |
| `raw_record_hash` | string | no | Raw duplicate evidence |

### Cross-field validation

- A non-null `last_review` with `number_of_reviews == 0` is a consistency finding.
- A missing observed rate with positive reviews remains unknown; it is never derived as zero.
- A derived activity zero requires a missing observed rate and exactly zero valid reviews.
- Source-unavailable fields are null and have their availability flag set to false.
- Source-available null values have availability true and remain analytically distinct.
- Listing, host, or location identifiers never enter visible labels or chart tooltips.

## Entity: DataQualityFinding

Represents one detected issue or documented data characteristic.

| Field | Type | Required | Validation |
|---|---|---:|---|
| `finding_id` | string | yes | Unique within build |
| `build_id` | string | yes | Foreign key to build manifest |
| `source_id` | string | no | Present for source-scoped findings |
| `entity` | string | yes | Affected table/entity |
| `field` | string | no | Affected field when applicable |
| `check_id` | string | yes | Stable validation-rule identifier |
| `dimension` | enum | yes | completeness, uniqueness, validity, consistency, integrity, distribution |
| `severity` | enum | yes | critical, high, medium, low |
| `failed_count` | integer | yes | Nonnegative |
| `evaluated_count` | integer | yes | At least `failed_count` |
| `failed_rate` | float | yes | Within `[0, 1]` |
| `evidence_path` | string | no | Relative path to safe evidence |
| `impact` | string | yes | Downstream analytical risk |
| `disposition` | enum | yes | open, accepted_valid, treated, excluded, blocked |
| `rationale` | string | no | Required unless disposition is open |

## Entity: TransformationRecord

Records every value-level or row-level transformation.

| Field | Type | Required | Validation |
|---|---|---:|---|
| `transformation_id` | string | yes | Stable rule identifier |
| `build_id` | string | yes | Build foreign key |
| `input_entity` | string | yes | Source/canonical table |
| `output_entity` | string | yes | Derived table |
| `field` | string | no | Field affected, if applicable |
| `rule` | string | yes | Human-readable deterministic rule |
| `rationale` | string | yes | Why the rule is acceptable |
| `rows_evaluated` | integer | yes | Nonnegative |
| `rows_changed` | integer | yes | Between zero and evaluated count |
| `rows_rejected` | integer | yes | Between zero and evaluated count |
| `before_summary` | object/string | yes | Safe aggregate evidence |
| `after_summary` | object/string | yes | Safe aggregate evidence |

## Entity: StatisticalResult

Stores one reproducible descriptive, contrast, correlation, or model result.

| Field | Type | Required | Validation |
|---|---|---:|---|
| `result_id` | string | yes | Unique within build |
| `build_id` | string | yes | Build foreign key |
| `analysis_family` | enum | yes | room_type, segment, association, sensitivity |
| `city_key` | string | yes | All inferential results are within-city |
| `segment_key` | string | no | Present for segment results |
| `metric` | string | yes | Metric and population clearly identified |
| `comparison` | string | yes | Groups/reference described |
| `method` | string | yes | Test, interval, correlation, or model |
| `sample_size` | integer | yes | Analyzable observations |
| `positive_sample_size` | integer | no | Required for positive-part results |
| `estimate` | float | no | Effect or association estimate |
| `effect_type` | string | no | Probability superiority, rho, ratio, percentage points, etc. |
| `ci_low` / `ci_high` | float | no | 95% interval when defined |
| `p_value_raw` | float | no | Within `[0, 1]` |
| `p_value_adjusted` | float | no | Within `[0, 1]` when family correction applies |
| `correction_method` | string | no | Holm or Benjamini-Hochberg family identifier |
| `assumption_status` | enum | yes | pass, caution, fail, not_applicable |
| `sensitivity_status` | enum | yes | robust, fragile, conflicting, not_run |
| `interpretation_es` | string | yes | Non-causal, proxy-safe reader wording |

## Entity: OpportunitySegment

One row per `city_key + neighborhood_key + room_type`, used by analysis and Power BI.

| Field group | Fields |
|---|---|
| Identity | `segment_key`, `city_key`, `neighborhood_key`, `room_type`, `build_id` |
| Supply scale | `listing_count`, `city_supply_share`, `neighborhood_supply_share`, `room_type_city_share` |
| Activity | `activity_analyzable_count`, `positive_activity_count`, `active_listing_share`, `activity_median`, `activity_iqr`, `positive_activity_median`, `activity_p90`, `activity_p99` |
| Local price context | `valid_price_count`, `price_median`, `price_iqr`, `price_position_percentile_within_city_room_type` |
| Stay context | `valid_minimum_nights_count`, `minimum_nights_median`, `minimum_nights_p90` |
| Evidence | `probability_superiority`, `effect_ci_low`, `effect_ci_high`, `median_difference`, `p_value_raw`, `q_value`, `sensitivity_status` |
| Geography | `centroid_latitude`, `centroid_longitude`, `coordinate_coverage` |
| Decision | `eligibility_status`, `eligibility_reason`, `opportunity_label`, `candidate_rank`, `quality_flag_count` |

### Eligibility and classification validation

- `eligible` requires at least 30 analyzable listings and 10 positive-activity listings.
- `candidate` requires probability superiority at least 0.56, `q < 0.05`, a 95% interval excluding
  no difference, robust sensitivity direction/label, and neighborhood room-type share below the
  same room type's citywide share.
- `consolidated` satisfies the robust activity evidence but not the low-supply condition.
- `watch` is eligible but does not satisfy every candidate/consolidated rule.
- `insufficient_evidence` fails an eligibility or required-data rule.
- Candidate rank is assigned within city by descending listing scale, then effect magnitude, then
  stable segment key. Significance alone never controls rank.

## Entity: BuildControl

One disconnected record per published build plus child control totals.

| Field | Type | Required | Validation |
|---|---|---:|---|
| `build_id` | string | yes | Deterministic identifier from source/config/schema identities |
| `schema_version` | string | yes | Semantic version |
| `generated_at_utc` | timestamp | yes | Informational, excluded from deterministic content checks |
| `source_manifest_hash` | string | yes | SHA-256 |
| `analysis_config_hash` | string | yes | SHA-256 |
| `source_file_count` | integer | yes | Exactly 6 |
| `source_row_count` | integer | yes | Exactly 220,031 for baseline |
| `canonical_row_count` | integer | yes | Reconciled with documented rejections/quarantine |
| `distinct_listing_key_count` | integer | yes | Equals canonical rows for an accepted build |
| `segment_count` | integer | yes | Matches opportunity output |
| `output_file` | string | yes | One row per published file in child table |
| `output_row_count` | integer | yes | Parsed rows for that output |
| `output_sha256` | string | yes | Stable export hash |
| `release_gate_status` | enum | yes | pass or fail |

## Power BI Semantic Model

### Dimensions

- **DimCity**: one row per city; key, Spanish label, source availability, currency/snapshot warnings.
- **DimNeighborhood**: one row per city-qualified neighborhood; Spanish/display label and aggregate
  centroid. Relationship to city is explicit.
- **DimRoomType**: one row per canonical room type with Spanish label and stable sort order.
- **Measures**: a display table containing explicit measures only; it has no data relationship.

### Facts

- **FactListings**: one privacy-safe row per canonical listing. It retains a hidden technical
  `listing_key`, dimension keys, eligible numeric metrics and flags; it excludes listing/host names,
  raw identifiers, last-review dates, and listing-level coordinates.
- **FactOpportunitySegments**: one row per opportunity segment with all separate decision components.
- **FactStatisticalResults**: report-safe selected results and interpretations.
- **FactQualitySummary**: aggregate quality counts/rates with no record-level evidence.
- **BuildControl**: disconnected build and reconciliation totals.

All relationships from dimensions to facts are one-to-many and single-direction. No relationship is
created from `BuildControl`; reconciliation measures explicitly compare its constants to
filter-independent fact totals.

## Relationships

```text
SourceFile 1 ---- * RawListing 1 ---- 1 CanonicalListing
                                |
                                +---- * DataQualityFinding
                                +---- * TransformationRecord

City 1 --------- * CanonicalListing * --------- 1 RoomType
  |                         |
  |                         *
  |                  OpportunitySegment 1 ---- * StatisticalResult
  |                         |
  +---- * Neighborhood -----+

BuildControl 1 ---- * generated datasets/findings/results
```

## State Transitions

### Source lifecycle

```text
discovered -> identity_verified -> schema_verified -> ingested
     |                |                  |
     `--------------> rejected <--------'
```

Any hash, parsed-row, header, or mandatory raw-contract failure moves the source to `rejected` and
blocks derived-data reuse.

### Build lifecycle

```text
started -> sources_validated -> canonical_validated -> analysis_validated
   |               |                    |                    |
   +---------------+--------------------+--------------------+--> failed

analysis_validated -> exports_validated -> tests_validated -> notebooks_validated
                              |                 |                  |
                              +-----------------+------------------+--> failed

notebooks_validated -> essential_accepted

essential_accepted -> report_refreshed -> report_reconciled -> medium_accepted
                              |                   |
                              +-------------------+--> failed
```

Only `essential_accepted` permits report implementation. A failed build never replaces the latest
accepted outputs.

### Finding lifecycle

```text
open -> accepted_valid -> verified
  |  -> treated ------> verified
  |  -> excluded -----> verified
  `-------------------> blocked
```

Every non-open disposition requires rationale and before/after evidence. Critical or high unresolved
findings block release unless the project owner approves a constitutional exception.
