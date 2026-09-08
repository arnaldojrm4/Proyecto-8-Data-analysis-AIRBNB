# Gestión del proyecto

GitHub Projects es la fuente única de verdad de la planificación. El tablero debe usar, en este
orden, `Backlog`, `Ready`, `In Progress`, `Review` y `Done`.

**Tablero activo**:
[Airbnb Supply Opportunity Analysis — Proyecto 8A](https://github.com/users/arnaldojrm4/projects/2)

El campo `Estado Kanban` contiene las cinco columnas acordadas. Los campos `Nivel` y `Prioridad`
permiten filtrar el alcance. El campo nativo `Status` se mantiene compatible con la vista inicial de
GitHub (`Todo`, `In Progress`, `Done`).

## Convenciones

- Cada unidad de trabajo tiene issue con nivel, fase, responsable y aceptación.
- Cada fase usa una rama corta desde una base estable.
- `main` solo recibe trabajo revisado mediante pull request, incluso con una sola persona.
- Los commits siguen Conventional Commits y contienen un cambio atómico verificable.
- Un issue pasa a `Done` únicamente tras integrar su PR y enlazar la evidencia.

## Registro

| Nivel | Fase | Issue | Rama | PR | Estado |
|---|---|---|---|---|---|
| Esencial | Preparación y fundamentos | [#2](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/issues/2) | `feat/essential-foundation` | [#7](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/7) | Done |
| Esencial | Base confiable | [#3](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/issues/3) | `feat/essential-foundation`¹ | [#7](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/7) | Done |
| Esencial | Análisis de oportunidad | [#4](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/issues/4) | `feat/essential-opportunity-analysis` | [#7](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/7) | Done |
| Esencial | Reproducibilidad | [#5](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/issues/5) | `feat/essential-reproducibility` | [#8](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/8) | Done |
| Medio | Power BI | [#6](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/issues/6) | `feat/medium-powerbi-report` | [#10](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/10) | Done |

¹ US1 se construyó en la rama autorizada `feat/essential-foundation`; sus commits son la base de la
rama específica de US2. Se conserva la desviación para no fingir una rama retrospectiva.

## Incidencias de entorno

- 2026-09-03: se renovó la autorización de GitHub CLI con alcance `project`; se creó y vinculó el
  Project #2 sin modificar el Project #1, que pertenece a otro repositorio.
- 2026-09-04: Docker Desktop quedó accesible; T082 aprobó con Engine 29.7.2 y Compose 5.5.0.
- 2026-09-02: Power BI Desktop no se detectó en la ruta de instalación estándar.
- 2026-09-07: Power BI Desktop x64 `2.157.879.0 (26.08)` quedó disponible y permitió construir,
  refrescar y validar localmente el informe sin Power BI Service ni licencia de pago.
- 2026-09-07: el checkout limpio reveló que Docker no empaquetaba `powerbi/`, `.pbix` ni `.pbit`;
  los commits `048bcb1` y `706c96d` corrigieron las dos causas y 43/43 contratos aprobaron.
- 2026-09-07: un pase de rendimiento midió 302,99 s bajo contención de varias instancias Desktop;
  tras cerrarlas con autorización, el test aislado aprobó en 298,37 s y la suite final completa
  aprobó sin ampliar el límite.

## Estado de sincronización (2026-09-07)

- Los PR [#7](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/7) y
  [#8](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/8) están integrados en
  `main`; el árbol final coincide con el árbol verificado de US3.
- `tasks.md` refleja T070–T085 terminadas y la puerta Esencial aprobada.
- La suite Docker aprobó 65 pruebas, omitió una comprobación Docker anidada y no tuvo fallos. Ruff y
  las 67 pruebas locales también aprobaron.
- Los issues #2–#5 y los PR #7–#8 están cerrados y conciliados con `Done` en GitHub Projects.
- T086 inició US4 desde `origin/main` en la rama `feat/medium-powerbi-report` y abrió el PR borrador
  [#10](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/10).
- La línea base de la rama aprobó Ruff y 67 pruebas en 290,18 s antes de cualquier cambio funcional.
- T087–T090 fijaron los contratos de exportación, privacidad y conciliación, además del checklist
  manual. La ejecución inicial registró 7 fallos esperados y 2 pruebas aprobadas, sin modificar
  producción; la evidencia está en
  [powerbi-contracts-red.md](acceptance/powerbi-contracts-red.md).
- T091 implementó las siete tablas del modelo estrella y `build_control.csv`, con claves
  sustitutas, privacidad, geografía agregada, orden estable, hashes y conteos conciliables.
- T092 conectó una única puerta de archivos, esquemas, claves, relaciones, privacidad, conteos,
  hashes, identidad de build y versión con `export`, `validate` y `all`; `export` conserva la entrega
  previa ante cualquier fallo.
- Ruff y 17 pruebas específicas aprobaron. La regresión completa terminó con 81 pruebas aprobadas en
  290,82 s, y la exportación real validó 8 archivos y 222.834 filas desde 220.031 anuncios.
- T093 documentó Power BI Desktop gratuito, el entorno x64 `2.157.879.0 (26.08)` detectado,
  `DataRoot`, refresh, modelo estrella, límites y resolución de errores. La compatibilidad mínima
  real del informe queda explícitamente pendiente de la prueba de refresh de T103.
- T094–T109 completaron tema, informe, plantilla, aceptación, quickstart limpio y release técnico;
  su integración final se registra a continuación.

## Instantánea final (2026-09-07)

- El PR [#10](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/pull/10) se integró en
  `main` mediante merge commit `12466b3abd73d13f685546183aafbb0ad21f8c01`.
- El issue [#6](https://github.com/arnaldojrm4/Proyecto8-DataAnalyst-Arnaldo/issues/6) está cerrado.
- Issue #6 y PR #10 figuran `Done` tanto en `Estado Kanban` como en el campo nativo `Status` del
  [Project #2](https://github.com/users/arnaldojrm4/projects/2).
- La suite del HEAD integrado aprobó 94 pruebas, omitió únicamente el smoke de Docker anidado y no
  tuvo fallos. Ruff, tres notebooks, `all`, `validate`, el verificador Power BI y el validador PBIR
  también aprobaron.
- T001–T110 quedan completadas. Esencial y Medio están cerrados; Avanzado/Experto permanecen solo
  como backlog en `docs/roadmap.md`.

## Historial de release

| Hito | Referencia | Resultado |
|---|---|---|
| Fundación, US1 y US2 | PR #7 | Integrado |
| Reproducibilidad US3 | PR #8 | Integrado |
| Cierre Esencial | PR #9 | Integrado |
| Informe Power BI US4 | PR #10 / merge `12466b3` | Integrado |
| Reconciliación final | `docs/final-release-reconciliation` | Esta actualización |
