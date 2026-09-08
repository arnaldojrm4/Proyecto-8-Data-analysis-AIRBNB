# Data Model: Panel avanzado interactivo y portable

## BuildAnalitico

Representa una publicación coherente del pipeline.

| Campo | Tipo | Regla |
|---|---|---|
| `build_id` | texto | No nulo; una identidad activa por sesión. |
| `schema_version` | versión semántica | La versión mayor debe ser compatible. |
| `generated_at_utc` | fecha-hora | Informativa; no prueba actualidad de las fuentes. |
| `release_gate_status` | categoría | Debe ser `pass` antes de mostrar métricas. |
| `output_file` | texto | Un registro por archivo publicado. |
| `output_row_count` | entero | Debe coincidir con el archivo leído. |
| `output_sha256` | texto | Identidad registrada por el pipeline. |

Estados: `no disponible` → `detectado` → `validado` o `rechazado`. Solo `validado` alimenta vistas.

## DashboardDataset

Colección inmutable en memoria formada por las dimensiones de ciudad, barrio y tipología, los hechos de
anuncios seguros, oportunidades, resultados estadísticos, calidad y el control de build.

Reglas:

- cada clave dimensional es única y no nula;
- toda clave de hechos resuelve en su dimensión;
- las tablas con `build_id` coinciden con el build activo;
- los recuentos coinciden con el control;
- no contiene columnas restringidas en superficies descargables.

## FilterSelection

| Campo | Cardinalidad | Regla |
|---|---|---|
| ciudad | exactamente una | Debe pertenecer a la dimensión de ciudad; inicialmente es la primera por etiqueta española en orden alfabético. |
| tipologías | una o más | Solo valores presentes en la ciudad. |
| barrios | cero o más | Solo valores presentes en ciudad y tipologías activas. |
| evidencias | cero o más | `robusta`, `frágil`, `conflictiva` o `no evaluada`, derivados solo de `sensitivity_status`. |

Transición: al cambiar ciudad se recalculan tipologías y barrios; al cambiar tipologías se recalculan
barrios; los valores ya no elegibles se eliminan. Restablecer crea la selección inicial válida.

La correspondencia de evidencia es `robust` → `robusta`, `fragile` → `frágil`, `conflicting` →
`conflictiva` y `not_run`, nulo o desconocido → `no evaluada`. `eligibility_status` y
`assumption_status` no modifican esta clasificación y se muestran por separado.

## FilteredPopulation

Resultado derivado de aplicar `FilterSelection` a un hecho concreto. Incluye filas, recuento, etiquetas
de alcance y estado `con datos`, `vacío` o `insuficiente`. Dos elementos visuales solo comparten una
población si las dimensiones seleccionadas existen con la misma semántica en ambos hechos.

## ExecutiveIndicator

Métrica agregada de una población filtrada. Contiene nombre español, valor, unidad, población,
definición y cautela. No persiste y no crea una puntuación compuesta.

## OpportunitySegment

Reutiliza el grano `ciudad + barrio + tipología` del contrato actual. Sus componentes visibles son
muestra, cuota de oferta, actividad histórica, dispersión, posición local de precio, efecto, intervalo,
valor ajustado, sensibilidad, elegibilidad, etiqueta y rango provisional.

Un segmento puede estar `candidato`, `observación`, `no elegible` o `sin evidencia suficiente`. El
estado procede del pipeline y la interfaz no lo recalifica.

## StatisticalResult

Resultado inferencial precalculado identificado por `result_id`. Pertenece a las familias `room_type`,
`segment`, `association` o `sensitivity`. Contiene población, comparación, método, muestra, efecto,
intervalo, valores p, corrección, supuestos, sensibilidad e interpretación.

Relaciones:

- una ciudad tiene muchos resultados;
- un segmento puede enlazar uno o más resultados publicados;
- los resultados de tipología y asociación no requieren `segment_key`;
- cambiar filtros selecciona resultados compatibles, nunca crea resultados nuevos.

## SafeDownload

Proyección efímera de una `FilteredPopulation`. Incluye solo etiquetas y métricas agregadas aprobadas.
Excluye claves técnicas, nombres, identificadores originales y coordenadas de anuncios. Una descarga
vacía se representa como estado informativo y no genera un archivo engañoso.
