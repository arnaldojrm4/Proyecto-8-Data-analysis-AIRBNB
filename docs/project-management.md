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
| Esencial | Preparación y fundamentos | [#2](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/2) | `feat/essential-foundation` | [#7](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/7) | Done |
| Esencial | Base confiable | [#3](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/3) | `feat/essential-foundation`¹ | [#7](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/7) | Done |
| Esencial | Análisis de oportunidad | [#4](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/4) | `feat/essential-opportunity-analysis` | [#7](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/7) | Done |
| Esencial | Reproducibilidad | [#5](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/5) | `feat/essential-reproducibility` | [#8](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/8) | Done |
| Medio | Power BI | [#6](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/6) | `feat/medium-powerbi-report` | Pendiente | Backlog |

¹ US1 se construyó en la rama autorizada `feat/essential-foundation`; sus commits son la base de la
rama específica de US2. Se conserva la desviación para no fingir una rama retrospectiva.

## Incidencias de entorno

- 2026-09-03: se renovó la autorización de GitHub CLI con alcance `project`; se creó y vinculó el
  Project #2 sin modificar el Project #1, que pertenece a otro repositorio.
- 2026-09-04: Docker Desktop quedó accesible; T082 aprobó con Engine 29.7.2 y Compose 5.5.0.
- 2026-09-02: Power BI Desktop no se detectó en la ruta de instalación estándar.

## Estado de sincronización (2026-09-04)

- Los PR [#7](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/7) y
  [#8](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/8) están integrados en
  `main`; el árbol final coincide con el árbol verificado de US3.
- `tasks.md` refleja T070–T085 terminadas y la puerta Esencial aprobada.
- La suite Docker aprobó 65 pruebas, omitió una comprobación Docker anidada y no tuvo fallos. Ruff y
  las 67 pruebas locales también aprobaron.
- Los issues #2–#5 y los PR #7–#8 están cerrados y conciliados con `Done` en GitHub Projects.
- US4 deja de estar bloqueada por la puerta Esencial; el issue #6 permanece en `Backlog` hasta iniciar
  T086 y crear su rama de trabajo.
