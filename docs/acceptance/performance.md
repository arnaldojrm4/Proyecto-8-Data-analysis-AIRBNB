# Rendimiento de US3

## Datos y límites

Medición host del 2026-09-03 sobre seis fuentes y 220.031 filas. Los límites son ETL ≤60 s, flujo
completo ≤5 min y RSS pico ≤2 GB; el contenedor declara 2 vCPU y 4 GB.

| Recorrido | Resultado | Límite | Estado |
|---|---:|---:|---|
| ETL `build` | prueba aprobada | ≤60 s y ≤2 GB RSS | Aprobado |
| Análisis `analyze` | 58,42 s | registrado sobre build aceptado | Aprobado |
| Flujo `all` | 4 min 38 s | ≤5 min | Aprobado |
| RSS del flujo `all` | ≤2 GB | ≤2 GB | Aprobado |
| Suite completa | 64 aprobadas en 7 min 19 s | sin fallos | Aprobado |

La primera variante superó el RSS por solapamiento entre análisis y pytest. La versión aceptada aísla
las etapas pesadas en procesos independientes. La medición de contenedor está bloqueada y se registra
en [docker-reproduction.md](docker-reproduction.md).
