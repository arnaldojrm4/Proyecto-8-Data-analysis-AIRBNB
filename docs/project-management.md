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
| Esencial | Preparación y fundamentos | [#2](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/2) | `feat/essential-foundation` | [#7](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/7) | Review |
| Esencial | Base confiable | [#3](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/3) | `feat/essential-foundation`¹ | [#7](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/7) | Review |
| Esencial | Análisis de oportunidad | [#4](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/4) | `feat/essential-opportunity-analysis` | [#7](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/7) | Review |
| Esencial | Reproducibilidad | [#5](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/5) | `feat/essential-reproducibility` | [#8](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/8) | Review |
| Medio | Power BI | [#6](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/6) | `feat/medium-powerbi-report` | Pendiente | Backlog |

¹ US1 se construyó en la rama autorizada `feat/essential-foundation`; sus commits son la base de la
rama específica de US2. Se conserva la desviación para no fingir una rama retrospectiva.

## Incidencias de entorno

- 2026-09-03: se renovó la autorización de GitHub CLI con alcance `project`; se creó y vinculó el
  Project #2 sin modificar el Project #1, que pertenece a otro repositorio.
- 2026-09-02: Docker CLI está instalado, pero el daemon no permite conexión desde la sesión actual.
- 2026-09-02: Power BI Desktop no se detectó en la ruta de instalación estándar.

## Estado de sincronización (2026-09-03)

- Trabajo de US2 local y remoto consolidado en `feat/essential-opportunity-analysis`.
- Pull request [#7](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/7) abierta
  contra `main` y enlazada con los issues #2 a #6. La PR borrador #1 fue cerrada por solapamiento.
- `tasks.md` refleja T070–T074 como contratos terminados; no se cierran tareas de implementación sin
  toda su evidencia.
- La suite acumulada aprobó 49 pruebas y Ruff terminó sin incidencias antes de publicar.
- El tablero contiene los issues #2–#6 y la PR #7. Preparación, US1, US2 y la PR están en `Review`;
  El bloque contractual T070–T074 de US3 está en `Review` mediante la PR #8; la historia US3 sigue
  abierta y US4 permanece en `Backlog` hasta cerrar el Nivel Esencial.
