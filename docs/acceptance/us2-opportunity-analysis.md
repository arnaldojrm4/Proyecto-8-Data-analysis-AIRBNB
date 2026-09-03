# Aceptación US2 — análisis de oportunidades

**Fecha**: 2026-09-03  
**Build**: `FDAAB53F8317CAD7`  
**Issue**: [#4](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/4)  
**PR**: [#1](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/1)

## Prueba independiente

`airbnb-supply analyze --log-format json` finalizó con estado `success` sobre 220.031 anuncios.
Publicó 690 resultados estadísticos, 1.497 segmentos y cinco visualizaciones reproducibles.

| Etiqueta | Segmentos |
|---|---:|
| `candidate` | 28 |
| `consolidated` | 19 |
| `watch` | 586 |
| `insufficient_evidence` | 864 |

Los candidatos se distribuyen entre Madrid (1), Milán (1), Nueva York (12), Sídney (13) y Tokio
(1). Londres queda sin candidato bajo las reglas bloqueadas.

## Evidencias

- La matriz aplica los umbrales `n>=30`, positivos `>=10`, superioridad `>=0,56`, `q<0,05`, IC por
  encima de 0,5, sensibilidad robusta y cuota local inferior a la urbana.
- Los efectos e intervalos de segmento emplean anfitrión como unidad inferencial.
- Los resultados estadísticos no contienen componentes de evidencia ausentes.
- El manifiesto de figuras usa rutas portables e incluye distribución, mezcla de tipologías,
  ranking geográfico, asociaciones e interacción de oportunidades.
- El notebook 03 contiene Markdown antes de cada bloque, conclusiones, límites e implicación para la
  decisión.

## Cautelas

La selección prioriza dónde investigar captación. No prueba resultados comerciales futuros. Precio,
fecha de extracción, procedencia original y cobertura del mercado siguen siendo desconocidos.

## Estado

**US2 aceptada localmente**. La rama consolidada se documenta como desviación de la rama prevista.
Tras la verificación final, el issue pasa a revisión y la PR queda lista contra `main`.
