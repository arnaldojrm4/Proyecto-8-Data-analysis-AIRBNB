# Evidencia contractual Power BI — T087–T090

## Estado

**Contrato aprobado en rojo el 2026-09-06.** Este bloque define el comportamiento requerido antes de
modificar la exportación. No contiene implementación de producción.

## Alcance fijado

- Ocho CSV exactos con columnas ordenadas, claves, tipos semánticos, UTF-8 sin BOM, finales LF y
  orden estable.
- Frontera de privacidad comprobada por nombre de columna y por valores centinela: nombres, IDs
  crudos y coordenadas de anuncio no pueden aparecer en ninguna celda publicada.
- Relaciones dimensión-hecho sin huérfanos y claves únicas/no nulas.
- `build_control.csv` conciliado mediante conteos y SHA-256 recalculados de forma independiente.
- Checklist manual para refresh, tres páginas, filtros, fallback sin mapa, accesibilidad, medidas
  muestreadas y prueba no asistida de tres minutos.

## Ejecución RED

```powershell
python -m pytest tests/contract/test_powerbi_exports.py `
  tests/contract/test_powerbi_privacy.py `
  tests/integration/test_powerbi_reconciliation.py -q
```

Resultado observado: **7 fallos esperados y 2 pruebas aprobadas**.

| Deuda demostrada | Evidencia del fallo |
|---|---|
| Dimensiones incompletas | `dim_city.csv` solo contiene `city_key`; faltan etiquetas y cautelas |
| Tipos y geografía agregada | faltan `coordinate_coverage` y centroides agregados en la dimensión |
| Esquema/control incompleto | faltan `generated_at_utc`, hashes de entrada y `segment_count` |
| Privacidad de identificadores | el `listing_key` exportado todavía incorpora el ID crudo |
| Relaciones | falta `room_type_key` en hechos y dimensión |
| Conciliación | el manifiesto no declara todos los campos necesarios para recomputar el control |

Las dos pruebas ya aprobadas confirman que los encabezados restringidos explícitos no se publican y
que no salen columnas de coordenadas de anuncio. Se mantienen como regresión.

## Criterio de continuación

T091 implementará el modelo estrella y la exportación mínima necesaria para convertir este rojo en
verde. T092 conectará las validaciones con `export`, `validate` y `all`. Ningún fallo de este bloque
se trata como incidencia inesperada ni se relaja para obtener verde.

La aceptación manual queda preparada en
[`powerbi/acceptance-checklist.md`](../../powerbi/acceptance-checklist.md), con estado `BLOCKED` hasta
disponer de los artefactos `.pbix` y `.pbit` de T095–T101.

## Implementación GREEN — T091

**Contrato convertido a verde el 2026-09-07.** La exportación implementa las siete tablas del
modelo estrella y `build_control.csv` con:

- claves sustitutas deterministas mediante SHA-256 para anuncios y tipologías;
- dimensiones con etiquetas de negocio en español y estados explícitos para fecha y moneda
  desconocidas;
- coordenadas exclusivamente agregadas, con supresión del centroide en grupos de menos de tres
  anuncios;
- columnas y orden de filas estables, CSV UTF-8 sin BOM y finales de línea LF;
- hashes de entradas y salidas, conteos conciliables y versión de esquema en el control de build;
- normalización del resumen de calidad desde el esquema canónico real de auditoría.

La verificación específica aprobó Ruff y **9 pruebas contractuales/de integración**. Una primera
regresión completa detectó que el fixture de calidad no representaba los campos reales
`failed_rate` y `disposition`; se corrigió el contrato de prueba y la normalización del exportador.
La exportación real posterior publicó los ocho CSV desde **220.031 anuncios**, y la regresión final
aprobó **76 pruebas en 276,85 s**.

T092 es la siguiente tarea: completar las puertas de validación de `export`, `validate` y `all` sin
alterar el contrato de datos aprobado en T091.
