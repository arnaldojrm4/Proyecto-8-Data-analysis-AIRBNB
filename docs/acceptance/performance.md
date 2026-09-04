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
| Suite Docker completa | 65 aprobadas y 1 omitida en 8 min 15 s | sin fallos | Aprobado |
| Docker `all` | 3 min 21 s | <=5 min y <=2 GB RSS | Aprobado |

La primera variante superó el RSS por solapamiento entre análisis y pytest. La versión aceptada aísla
las etapas pesadas en procesos independientes. El test Docker de presupuesto confirmó 203,21 s y
RSS <=2 GB; la evidencia completa se registra en [docker-reproduction.md](docker-reproduction.md).
