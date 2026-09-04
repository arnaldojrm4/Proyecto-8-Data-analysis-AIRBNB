# Airbnb Supply Opportunity Analysis

Proyecto educativo y reproducible para responder qué tipologías de alojamiento conviene investigar
para captación de anfitriones y en qué ciudades y barrios. El público principal es un directivo no
técnico responsable de estrategia de oferta.

## Alcance comprometido

1. **Nivel Esencial**: auditoría, ETL, EDA, estadística, notebooks, documentación, Git y Kanban.
2. **Nivel Medio**: informe interactivo de Power BI Desktop sin licencia de pago.

El Nivel Esencial debe quedar aceptado antes de iniciar Power BI. Los niveles Avanzado y Experto no
forman parte del compromiso actual.

## Advertencias de interpretación

- Son seis datasets públicos de uso educativo, con procedencia original y licencia desconocidas.
  No se presentan como datos oficiales ni cedidos directamente por Airbnb.
- `reviews_per_month` es solo un **proxy de actividad histórica de reseñas**. No mide demanda,
  reservas, ocupación, liquidez ni rotación real.
- `price` es el precio publicado en moneda local desconocida; no representa ingreso ni margen y no
  permite rankings monetarios entre ciudades.
- Las fechas de extracción son desconocidas, por lo que no se harán afirmaciones de actualidad ni
  comparaciones de recencia.

## Diseño y ejecución

- [Especificación](specs/001-supply-opportunity-analysis/spec.md)
- [Plan técnico](specs/001-supply-opportunity-analysis/plan.md)
- [Tareas](specs/001-supply-opportunity-analysis/tasks.md)
- [Guía reproducible](specs/001-supply-opportunity-analysis/quickstart.md)
- [Gestión y trazabilidad](docs/project-management.md)
- [Kanban GitHub Projects](https://github.com/users/arnaldojrm4/projects/2)
- [Hallazgos ejecutivos US2](docs/analysis/executive-findings.md)
- [Guía de estudio](docs/study-guide.md)
- [Próximos bloques de trabajo](docs/next-work-blocks.md)

Los comandos ejecutables se documentarán al cerrar la infraestructura y el flujo Esencial.

## Reproducción host y Docker

Requisitos: las seis fuentes bajo `data/raw/`, Git y Docker Desktop con daemon activo para la ruta
contenedorizada. Para host se requiere Python 3.13 y `uv`.

```powershell
uv sync --locked --group dev
uv run --locked airbnb-supply all --log-format json
```

La ruta equivalente en contenedor es:

```powershell
docker compose build
docker compose run --rm pipeline all --log-format json
```

El servicio limita el contenedor a 2 vCPU y 4 GB y monta `data/raw/` como solo lectura. Los resultados
se publican en `data/processed/`, `data/powerbi/` y `artifacts/` solo tras validar el flujo.

La suite final aprobó 65 pruebas (una prueba Docker omitida dentro del propio contenedor); los flujos
host y Docker aprobaron el presupuesto de cinco minutos y 2 GB de RSS.
Esta evidencia acredita reproducción técnica, no demanda, reservas, ocupación ni rentabilidad. Consulta
la [guía paso a paso](specs/001-supply-opportunity-analysis/quickstart.md), el
[rendimiento](docs/acceptance/performance.md) y la [puerta Esencial](docs/acceptance/essential-level.md).
