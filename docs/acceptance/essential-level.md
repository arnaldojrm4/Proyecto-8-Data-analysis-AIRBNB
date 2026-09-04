# Puerta de aceptación del Nivel Esencial

## Estado

**Aprobado el 2026-09-04.** US1, US2 y US3 disponen de evidencia reproducible y quedaron
integradas en `main`. La puerta Esencial está cerrada y US4 puede comenzar.

## Checklist

- [X] US1: [us1-data-foundation.md](us1-data-foundation.md).
- [X] US2: [us2-opportunity-analysis.md](us2-opportunity-analysis.md).
- [X] US3 técnico: [us3-reproducibility-contracts.md](us3-reproducibility-contracts.md).
- [X] Rendimiento host: [performance.md](performance.md).
- [X] README, guía y gobernanza actualizados.
- [X] Docker `all` aprobado: [docker-reproduction.md](docker-reproduction.md).
- [X] PR #7 y PR #8 integradas en `main` (`f755e7d` y `6d56d0f`).
- [X] Issues Esenciales conciliados con `Done` y evidencia final.

## Evidencia final

- `airbnb-supply all` terminó con estado `success`, build `FDAAB53F8317CAD7` y sin errores.
- La suite local final aprobó 67 pruebas en 288,34 s; Ruff no encontró incidencias.
- La suite Docker aprobó 65 pruebas, omitió únicamente la comprobación Docker anidada y no tuvo
  fallos. El flujo completo terminó en unos 201,34 s bajo 2 vCPU y 4 GB.
- Se revisaron los tres notebooks ejecutados: 2, 3 y 5 celdas de código respectivamente, sin errores
  de ejecución y con conclusiones Markdown explícitas.
- Se comprobaron 3 Parquet procesados, 8 CSV para Power BI, 5 figuras y 7 artefactos de calidad.
- El árbol de `main` tras integrar el PR #8 coincide exactamente con el árbol verificado de
  `feat/essential-reproducibility`.

## Decisión

T085 y el Nivel Esencial quedan aceptados. Puede iniciarse T086 sin relajar los contratos de datos,
estadística, documentación, reproducibilidad o trazabilidad establecidos.
