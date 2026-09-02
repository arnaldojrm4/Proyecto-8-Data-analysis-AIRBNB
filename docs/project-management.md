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
| Esencial | Preparación y fundamentos | Pendiente de renovar autenticación de GitHub CLI | `feat/essential-foundation` | Pendiente | In Progress |
| Esencial | Base confiable | Pendiente | `feat/essential-data-foundation` | Pendiente | Backlog |
| Esencial | Análisis de oportunidad | Pendiente | `feat/essential-opportunity-analysis` | Pendiente | Backlog |
| Esencial | Reproducibilidad | Pendiente | `feat/essential-reproducibility` | Pendiente | Backlog |
| Medio | Power BI | Pendiente | `feat/medium-powerbi-report` | Pendiente | Backlog |

## Incidencias de entorno

- 2026-09-02: GitHub CLI detectado con credencial inválida. La sincronización remota de issues,
  tablero y PR queda bloqueada hasta ejecutar `gh auth login -h github.com`.
- 2026-09-02: Docker CLI está instalado, pero el daemon no permite conexión desde la sesión actual.
- 2026-09-02: Power BI Desktop no se detectó en la ruta de instalación estándar.

## Estado de sincronización (2026-09-02)

- Trabajo local consolidado en `feat/essential-foundation`.
- `tasks.md` refleja 57 tareas terminadas y 53 pendientes; no se cierran tareas sin toda su
  evidencia.
- La suite acumulada aprobó 35 pruebas antes de preparar la sincronización.
- La publicación de rama, issues, tablero y pull request sigue condicionada a renovar la sesión de
  GitHub CLI con `gh auth login -h github.com`.
