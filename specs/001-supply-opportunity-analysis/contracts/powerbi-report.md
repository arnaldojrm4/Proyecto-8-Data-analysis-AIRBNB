# Contract: Power BI Desktop Executive Report

**Version**: 1.0.0

**Audience**: non-technical executive responsible for supply and host acquisition

**Artifacts**: `powerbi/airbnb-supply-opportunity.pbix` and
`powerbi/airbnb-supply-opportunity.pbit`

“Dashboard” is the business-facing project term. The technical deliverable is a three-page Power BI
Desktop report. It does not depend on Power BI Service or paid licensing.

## Data connection

- One required text parameter, `DataRoot`, points to the host-side `data/powerbi/` directory.
- Every query builds its stable filename from `DataRoot`; no developer-specific or container-internal
  absolute path is stored.
- The template prompts for `DataRoot` on first use.
- Refresh fails with a clear message when a required file is absent, schema-major version is
  incompatible, or the release gate is not `pass`.
- The report uses Import mode and records the minimum tested Power BI Desktop release in
  `powerbi/README.md`.

## Semantic model

- Dimensions: City, Neighborhood, Room Type, and a disconnected Measures display table.
- Facts: Listings, Opportunity Segments, Statistical Results, Quality Summary, and disconnected
  Build Control.
- Relationships are one-to-many and single-direction from dimensions to facts.
- Auto-generated implicit numeric summaries are disabled or hidden; explicit measures own displayed
  aggregations.
- Pipeline-owned fields include local price position, opportunity label, eligibility, effects,
  intervals, adjusted values, sensitivity, and quality status.
- Visuals contain no duplicated business-rule calculations.

## Required measures

| Business label | Meaning |
|---|---|
| `Anuncios analizables` | Count of privacy-safe listing rows under the current filters |
| `Segmentos candidatos` | Count of segments labeled `candidate` under locked eligibility rules |
| `Cuota activa histórica` | Share with positive historical activity proxy |
| `Actividad histórica mediana` | Median activity proxy; never called demand or occupancy |
| `Precio local mediano` | Median valid published price in the selected city context |
| `Cuota de oferta` | Selected segment listing share using the displayed denominator |
| `Efecto de actividad` | Probability-of-superiority estimate and its 95% interval |
| `Estado de evidencia` | Candidate, consolidated, watch, or insufficient evidence |
| `Diferencia de conciliación` | Filter-independent expected rows minus imported rows; must be zero |

Every measure tooltip or adjacent help text states its population, denominator, exclusions, and
interpretation limitation. Essential evidence never appears only in a hover tooltip.

## Page 1: Resumen ejecutivo

**Question**: ¿Dónde conviene investigar primero la captación de nuevos alojamientos?

Required content:

- selected-city title and scope;
- candidate-segment count and analyzable-listing count;
- up to three ranked candidate segments, or an explicit “fewer than three qualified” state;
- separate activity, supply, price-context, scale, and confidence evidence for each candidate;
- one concise provisional recommendation in Spanish;
- visible disclaimer that reviews approximate historical activity and prices are local published
  values, not demand, bookings, occupancy, revenue, or margin.

No page-level visual may imply a cross-city monetary ranking.

## Page 2: Oportunidades de captación

**Question**: ¿En qué barrios y tipologías se concentra la oportunidad aparente?

Required content:

- aggregated segment centroids in Azure Maps when network access permits;
- an always-available ranked table or bar view conveying the same candidate/consolidated/watch state;
- city, room type, and evidence-status slicers in a consistent location;
- listing count, neighborhood and city supply shares, activity effect, and price position;
- non-color icons or text for status;
- drillthrough affordance to Page 3.

The map never displays individual listing coordinates and remains below its supported point limit.
The ranked fallback must support the page's decision without the map.

## Page 3: Detalle y confianza

**Question**: ¿Qué evidencia respalda esta oportunidad y qué puede cambiar la decisión?

Required content:

- selected segment identity without listing/host identifiers;
- sample size, positive-activity count, missing/zero shares, median/IQR and positive median;
- effect estimate, 95% interval, raw and adjusted values, and correction family;
- sensitivity status across thresholds and data-treatment alternatives;
- quality flags and exclusions;
- definition, population, denominator, and non-causal limitation;
- build ID, schema version, generated time, source row total, imported row total, and reconciliation
  difference;
- Back navigation preserving applicable context.

## Interaction contract

- City, room type, and evidence status are the only global slicers.
- Eligibility rules and invalid-data exclusions are locked report/page filters.
- Neighborhood selection occurs through a ranking/map selection or Page 3 drillthrough.
- Synced slicers are used only where page semantics match.
- Tooltips are supplementary and contain no required conclusion or warning.
- Reset/navigation controls have text labels or accessible names.

## Accessibility and clarity

- Text contrast is at least 4.5:1.
- Every meaningful visual has Spanish alt text, dynamic where the selected context changes meaning.
- Tab order follows reading order and includes slicers, key findings, details, then navigation.
- Color is never the sole status encoding.
- Titles state the takeaway or question; visual-type names are not used as titles.
- Each page has one primary decision and a limited visual count.
- Hidden technical keys cannot be exposed through visuals, tooltips, or normal data export.

## Reconciliation and acceptance

A report release passes only when:

1. `DataRoot` can be changed to a clean host path and all tables refresh;
2. the imported schema version is compatible;
3. the model row count and additive control totals equal `build_control.csv` under removed filters;
4. `Diferencia de conciliación = 0`;
5. sampled displayed measures exactly match accepted analytical outputs;
6. no restricted field appears in the semantic model's visible surface or report exports;
7. the map-offline fallback remains usable;
8. keyboard order, contrast, alt text, labels, and non-color cues pass review; and
9. a non-technical reviewer identifies up to three valid opportunities and their cautions in under
   three minutes without assistance.

## Licensing and distribution boundary

- The report is opened and refreshed in free Power BI Desktop.
- No Power BI Service workspace, app, scheduled refresh, subscription, alert, browser publication,
  centralized audit, or service-side access control is promised.
- The `.pbix` is an editable imported-data snapshot, not a centrally governed read-only publication.
- The `.pbit` contains the report definition without imported data and supports reproducible local
  setup through `DataRoot`.
