# Diccionario de datos canónico

**Grano**: una fila por `city_key + listing_id`. Los identificadores y nombres restringidos se
conservan solo para linaje, duplicados y cálculos agregados; nunca se muestran en el informe.

| Campo | Tipo lógico | Uso y regla |
|---|---|---|
| `listing_key` | string | Clave técnica `{city_key}:{listing_id}`, única. |
| `city_key` | categoría | `london`, `madrid`, `milan`, `new_york`, `sydney` o `tokyo`. |
| `listing_id` | entero | Identificador raw restringido. |
| `listing_name` | string nullable | Nombre raw restringido; no se imputa. |
| `host_id` | entero | Identificador raw restringido; permite agrupación estadística. |
| `host_name` | string nullable | Nombre raw restringido; no se imputa. |
| `neighborhood_group` | string nullable | Valor original o nulo; nunca se fabrica. |
| `neighborhood` | string nullable | Barrio con espacios exteriores eliminados. |
| `neighborhood_key` | string nullable | Clave de barrio cualificada por ciudad. |
| `latitude`, `longitude` | float nullable | Coordenadas válidas; solo se publican centroides agregados. |
| `coordinate_is_valid` | boolean | Ambas coordenadas se parsean y están en rango global. |
| `room_type` | categoría | `entire_home_apt`, `private_room`, `shared_room`, `hotel_room`. |
| `price` | float nullable | Precio publicado válido y positivo, solo comparable dentro de ciudad. |
| `price_is_valid` | boolean | Indica elegibilidad para métricas de precio. |
| `minimum_nights` | entero nullable | Estancia mínima integral y al menos uno. |
| `minimum_nights_is_valid` | boolean | Indica elegibilidad para la métrica. |
| `number_of_reviews` | entero nullable | Recuento no negativo de reseñas. |
| `last_review` | fecha nullable | Nunca se rellena con sentinelas ni define recencia. |
| `reviews_per_month_observed` | float nullable | Tasa original no imputada. |
| `has_historical_activity` | boolean nullable | `number_of_reviews > 0` cuando el recuento es válido. |
| `activity_proxy` | float nullable | Tasa observada o cero derivado bajo la regla explícita. |
| `activity_proxy_derived_zero` | boolean | Verdadero solo si falta la tasa y el recuento es cero. |
| `activity_proxy_is_analyzable` | boolean | La tasa es observada o el cero puede derivarse. |
| `calculated_host_listings_count` | entero nullable | No disponible en Tokio. |
| `availability_365` | entero nullable | No disponible en Tokio; no se interpreta como ocupación. |
| `*_source_available` | boolean | Separa ausencia estructural de un valor nulo observado. |
| `source_id` | string | Fuente de origen. |
| `source_record_number` | entero | Posición de registro parseado para linaje. |
| `raw_record_hash` | string | Evidencia técnica de duplicado sin exponer contenido. |

`reviews_per_month` se denomina siempre **proxy de actividad histórica de reseñas**. No equivale a
demanda, reservas, ocupación, liquidez o rotación real.
