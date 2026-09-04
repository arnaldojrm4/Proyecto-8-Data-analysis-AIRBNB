# Aceptación de rigor estadístico

**Fecha**: 2026-09-03  
**Build**: `FDAAB53F8317CAD7`

## Contratos comprobados

- 690 resultados: 6 Kruskal-Wallis, 27 comparaciones posteriores, 633 segmentos, 12 correlaciones
  y 12 resultados de modelos ajustados.
- Cero ausencias en efecto, IC 95 %, valor p crudo, valor ajustado, método de corrección, diagnóstico
  e interpretación.
- Holm se aplica a los contrastes de tipología; Benjamini-Hochberg a segmentos dentro de ciudad y a
  la familia de 12 correlaciones.
- Los segmentos usan anfitrión como unidad inferencial. El IC percentil emplea 500 remuestras
  deterministas por conglomerado.
- Los resultados se contrastan además con efecto por anuncio, casos completos, winsorización p1/p99
  y umbral reforzado de 50 observaciones.
- El modelo en dos partes separa presencia de actividad e intensidad positiva, ajustando por
  tipología y barrios elegibles.

## Validación automática

`validate_statistical_results` bloquea la publicación si falta algún componente de evidencia o si
una interpretación atribuye al proxy resultados que la fuente no mide. El comando `analyze` devuelve
código 5 y no publica artefactos cuando falla este contrato.

Pruebas asociadas:

- `tests/unit/test_room_type_statistics.py`
- `tests/unit/test_segment_statistics.py`
- `tests/unit/test_correlations.py`
- `tests/unit/test_sensitivity_models.py`
- `tests/contract/test_statistical_evidence.py`
- `tests/integration/test_full_analysis.py`

## Resultado

**PASS**. Los resultados inferenciales del build cumplen el contrato. La aceptación acredita
coherencia estadística y trazabilidad, no actualidad, causalidad ni representatividad externa.
