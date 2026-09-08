# Contract: Panel avanzado

**Version**: 1.0.0

**Producer**: pipeline analítico existente

**Consumer**: panel web avanzado

## Archivos de entrada obligatorios

El consumidor requiere los ocho CSV definidos en el contrato analítico 1.0.0 bajo `data/powerbi/`.
`build_control.csv` se valida primero. El panel no lee `data/raw/` ni los Parquet canónicos.

## Puerta de apertura

Antes de representar una métrica, el consumidor MUST comprobar:

1. archivos obligatorios presentes;
2. versión mayor `1` compatible;
3. estado de publicación `pass`;
4. una identidad de build coherente;
5. recuentos de filas registrados;
6. claves dimensionales únicas; y
7. relaciones de hechos resolubles.

Cualquier fallo produce `DashboardDataError` con código estable, mensaje español, artefacto afectado y
acción de recuperación. Códigos: `missing_file`, `unsupported_schema`, `release_gate_failed`,
`mixed_build`, `row_count_mismatch`, `duplicate_dimension_key`, `orphan_dimension_key` y
`restricted_export_field`.

## Semántica de filtros

| Filtro | Resumen | Oportunidades | Evidencia |
|---|---|---|---|
| Ciudad única | obligatorio | obligatorio | obligatorio |
| Tipologías múltiples | sí | sí | cuando la familia lo permite |
| Barrios múltiples | no | sí | solo resultados de segmento |
| Estado de evidencia | candidatos mostrados | sí | sí |

La interfaz muestra qué filtros no aplican a una métrica. No se reducirá silenciosamente una población
estadística a un subconjunto distinto del usado por el pipeline.

El estado de evidencia se deriva únicamente de `sensitivity_status`: `robust` → `robusta`, `fragile`
→ `frágil`, `conflicting` → `conflictiva` y `not_run`, vacío o desconocido → `no evaluada`.
`eligibility_status` y `assumption_status` se presentan como dimensiones distintas y nunca se fusionan
con ese filtro.

## Contrato de vistas

### Resumen ejecutivo

Debe mostrar identidad/estado del build, población filtrada, un máximo inicial de seis indicadores,
candidatos prioritarios y cautela principal. No presenta una puntuación compuesta.

### Oportunidades

Debe mostrar ranking tabular, representación geográfica opcional y componentes separados de cada
segmento. La tabla constituye el fallback completo del mapa.

### Evidencia estadística

Debe organizar resultados por hipótesis y distinguir contraste global, comparaciones posteriores,
segmentos, asociaciones y sensibilidad. Toda ficha inferencial incluye población, método, muestra,
efecto, intervalo, valor crudo, valor ajustado, corrección y limitación.

## Contrato de descargas

Las descargas se derivan de la selección activa mediante listas positivas. Cualquier campo no incluido
queda prohibido.

**Oportunidades**: `city_label_es`, `neighborhood_label`, `room_type_label_es`, `listing_count`,
`city_supply_share`, `neighborhood_supply_share`, `neighborhood_room_type_share`,
`room_type_city_share`, `active_listing_share`, `activity_median`, `activity_iqr`, `price_median`,
`price_iqr`, `minimum_nights_median`, `probability_superiority`, `effect_ci_low`, `effect_ci_high`,
`median_difference`, `q_value`, `sensitivity_status`, `coordinate_coverage`, `quality_flag_count`,
`price_position_percentile_within_city_room_type`, `eligibility_status`, `eligibility_reason`,
`opportunity_label`, `candidate_rank`.

**Evidencia**: `city_label_es`, `neighborhood_label`, `room_type_label_es`, `analysis_family`, `metric`,
`comparison`, `method`, `sample_size`, `positive_sample_size`, `estimate`, `effect_type`,
`median_difference`, `ci_low`, `ci_high`, `p_value_raw`, `p_value_adjusted`, `correction_method`,
`assumption_status`, `sensitivity_status`, `interpretation_es`.

**Calidad**: `source_id`, `quality_metric`, `field`, `evaluated_count`, `failed_count`, `failure_rate`,
`severity`, `status`, `interpretation_es`.

Se prohíben expresamente claves técnicas, nombres, `listing_id`, `host_id` y cualquier coordenada en las
descargas, aunque el archivo fuente contenga centroides agregados autorizados para el mapa.

## Estados de interfaz

- `ready`: build aprobado y vistas disponibles.
- `empty`: filtro válido sin filas; se ofrece restablecer.
- `insufficient`: existen descriptivos, pero no evidencia inferencial publicable.
- `blocked`: falla una validación obligatoria; no se muestran métricas.

## Salud

El endpoint `/_stcore/health` prueba disponibilidad del proceso. La aplicación muestra por separado el
estado del build; un proceso sano con datos bloqueados es un estado operativo válido y diagnosticable.

## Compatibilidad

Cambios aditivos compatibles en la versión 1.x se aceptan si no alteran campos consumidos. Un cambio de
versión mayor bloquea la apertura hasta actualizar este contrato y sus pruebas.
