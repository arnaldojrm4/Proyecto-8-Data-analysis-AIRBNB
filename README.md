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

Los comandos ejecutables se documentarán al cerrar la infraestructura y el flujo Esencial.
