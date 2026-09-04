# ETL, calidad y decisiones de tratamiento

## Fuentes y límites

Se preservan seis CSV públicos de uso educativo. Su procedencia original, licencia, moneda, fecha
de extracción y representatividad son desconocidas. Cada copia se acepta solo si coincide en
nombre, bytes, filas, cabecera y SHA-256 con `config/source-manifest.json`.

## Conciliación observada

| Ciudad | Filas raw | Filas canónicas |
|---|---:|---:|
| Londres | 85.068 | 85.068 |
| Madrid | 19.618 | 19.618 |
| Milán | 18.322 | 18.322 |
| Nueva York | 48.895 | 48.895 |
| Sídney | 36.662 | 36.662 |
| Tokio | 11.466 | 11.466 |
| **Total** | **220.031** | **220.031** |

No se rechazó ni eliminó ninguna fila. La clave `city_key + listing_id` es única en el build
aceptado.

## Reglas aplicadas

1. Se normalizan nombres de columnas al esquema canónico y se preserva el origen.
2. Nombres de anuncio/anfitrión permanecen nulos cuando faltan; no se usa `sin nombre`.
3. Columnas ausentes por ciudad permanecen nulas y llevan indicador `source_available = false`.
4. `last_review` se parsea como fecha o queda nula; nunca se usa el sentinela `0`.
5. Precio no numérico, cero o negativo queda fuera de métricas de precio, sin eliminar la fila.
6. Coordenadas fuera del rango global quedan fuera de geografía, sin eliminar la fila.
7. Los outliers se señalan con IQR y se conservan; las conclusiones usan mediana, IQR y
   sensibilidades robustas.
8. `activity_proxy` conserva la tasa observada. Solo deriva cero si falta la tasa y el anuncio tiene
   exactamente cero reseñas.

## Impacto observado de tratamientos

- 54.248 ceros derivados con respaldo en `number_of_reviews == 0`.
- 123 filas con reseñas positivas y tasa mensual ausente permanecen desconocidas.
- 50 precios no positivos quedan fuera de cálculos de precio.
- No se encontraron noches mínimas inválidas ni coordenadas fuera de rango en estas fuentes.

## Alternativas rechazadas

- Imputar todos los nulos de actividad con cero: confundiría 123 tasas desconocidas con inactividad.
- Imputar fechas con `0`: destruiría el tipo fecha e induciría una falsa cronología.
- Eliminar outliers por regla global: podría borrar anuncios válidos y de alto precio/estancia.
- Comparar precios absolutos entre ciudades: la moneda y fecha de referencia son desconocidas.

## Relevancia para la decisión

La base permite comparar composición y actividad histórica dentro de cada ciudad. No puede medir
reservas, ocupación, margen, demanda actual ni el tamaño completo del mercado; las recomendaciones
de captación serán provisionales.
