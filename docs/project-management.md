# Gestión del proyecto

GitHub Projects es la fuente única de verdad de la planificación. El tablero debe usar, en este
orden, `Backlog`, `Ready`, `In Progress`, `Review` y `Done`.

## Convenciones

- Cada unidad de trabajo tiene issue con nivel, fase, responsable y aceptación.
- Cada fase usa una rama corta desde una base estable.
- `main` solo recibe trabajo revisado mediante pull request, incluso con una sola persona.
- Los commits siguen Conventional Commits y contienen un cambio atómico verificable.
- Un issue pasa a `Done` únicamente tras integrar su PR y enlazar la evidencia.

## Registro

| Nivel | Fase | Issue | Rama | PR | Estado |
|---|---|---|---|---|---|
| Esencial | Preparación y fundamentos | [#2](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/2) | `feat/essential-foundation` | [#1](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/1) | Review |
| Esencial | Base confiable | [#3](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/3) | `feat/essential-foundation`¹ | [#1](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/1) | Review |
| Esencial | Análisis de oportunidad | [#4](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/4) | `feat/essential-foundation`¹ | [#1](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/1) | In Progress |
| Esencial | Reproducibilidad | [#5](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/5) | `feat/essential-reproducibility` | Pendiente | Backlog |
| Medio | Power BI | [#6](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/issues/6) | `feat/medium-powerbi-report` | Pendiente | Backlog |

¹ US1 y la parte implementada de US2 se consolidaron en la rama autorizada
`feat/essential-foundation`; se conserva la desviación para no fingir ramas retrospectivas.

## Incidencias de entorno

- 2026-09-03: Git y las operaciones de repositorio de GitHub CLI funcionan. El token carece del
  alcance `read:project`, por lo que crear o conciliar el tablero requiere
  `gh auth refresh -s read:project,project`.
- 2026-09-02: Docker CLI está instalado, pero el daemon no permite conexión desde la sesión actual.
- 2026-09-02: Power BI Desktop no se detectó en la ruta de instalación estándar.

## Estado de sincronización (2026-09-03)

- Trabajo local y remoto consolidado en `feat/essential-foundation`.
- Pull request borrador [#1](https://github.com/arnaldojrm4/Proyecto-8-Data-analysis-AIRBNB/pull/1)
  abierta y enlazada con los issues #2 a #6.
- `tasks.md` refleja 57 tareas terminadas y 53 pendientes; no se cierran tareas sin toda su
  evidencia.
- La suite acumulada aprobó 36 pruebas y Ruff terminó sin incidencias antes de publicar.
- El tablero GitHub Projects es el único elemento remoto pendiente por alcance insuficiente del
  token; los issues, la rama y la PR sí están sincronizados.
