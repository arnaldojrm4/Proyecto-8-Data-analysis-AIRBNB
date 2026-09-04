# Bloques de trabajo posteriores a US2

Cada bloque usa una rama corta, commits atómicos, pruebas antes de implementación y una PR contra
`main`. No se inicia Power BI hasta aceptar por completo el Nivel Esencial.

## Bloque 1 — Contratos de reproducibilidad US3

- **Rama**: `feat/us3-repro-contracts`
- **Tareas**: T070–T074.
- **Commit sugerido**: `test: define essential reproducibility contracts`.
- **Entrega**: tests de notebooks, comando `all`, documentación y rendimiento inicialmente fallidos.

## Bloque 2 — Orquestación reproducible US3

- **Rama**: `feat/us3-pipeline-orchestration`
- **Tareas**: T075–T079.
- **Commits sugeridos**: uno para ejecución de notebooks, otro para `test/validate/all`.
- **Entrega**: CLI Esencial completa, idempotente y con fallo cerrado.

## Bloque 3 — Aceptación del Nivel Esencial

- **Rama**: `docs/us3-essential-acceptance`
- **Tareas**: T080–T085.
- **Commits sugeridos**: documentación reproducible; evidencia de rendimiento; aceptación final.
- **Entrega**: README y quickstart comprobados, evidencia Docker/rendimiento y puerta Esencial.

## Bloque 4 — Contratos y exportación Power BI

- **Rama**: `feat/us4-powerbi-data-contract`
- **Tareas**: T086–T094 y T102.
- **Commits sugeridos**: tests de ocho tablas; exportador estrella; documentación/tema/verificador.
- **Entrega**: CSV seguros, conciliados y listos para Power BI Desktop gratuito.

## Bloque 5 — Construcción del informe Power BI

- **Rama**: `feat/us4-powerbi-report`
- **Tareas**: T095–T101.
- **Commits sugeridos**: modelo y medidas; páginas e interacciones; plantilla `.pbit`.
- **Entrega**: informe de tres páginas con filtros, ranking, detalle y accesibilidad.

## Bloque 6 — Aceptación del Nivel Medio

- **Rama**: `test/us4-powerbi-acceptance`
- **Tareas**: T103–T105.
- **Commits sugeridos**: conciliación; UAT/accesibilidad; cierre Medio.
- **Entrega**: refresh limpio, prueba de tres minutos y puerta Medio aprobada.

## Bloque 7 — Pulido y release

- **Rama**: `chore/final-release`
- **Tareas**: T106–T110.
- **Commits sugeridos**: roadmap; validación de quickstart; evidencia final y conciliación Kanban.
- **Entrega**: release documentada sin iniciar trabajo Avanzado/Experto.
