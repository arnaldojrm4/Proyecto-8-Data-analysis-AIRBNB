# Implementation Plan: Panel avanzado interactivo y portable

**Branch**: `002-advanced-dashboard` | **Date**: 2026-09-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-advanced-dashboard/spec.md`

## Summary

Añadir un panel web interactivo de tres vistas que consuma exclusivamente el conjunto de exportaciones
aprobado, permita explorar ciudad, tipología, barrio y evidencia, y presente las tres familias de
hipótesis sin recalcular inferencia sobre filtros arbitrarios. El panel se ejecutará como un segundo
servicio del entorno contenido actual, mantendrá Power BI como consumidor paralelo y separará la
lógica de carga, filtrado, presentación y gráficos de la capa de interfaz.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Streamlit 1.63.x, Pandas 2.2.x, Plotly 6.x, PyArrow 19-23

**Storage**: Ocho CSV versionados por build bajo `data/powerbi/`, montados en solo lectura

**Testing**: pytest 8-9, Streamlit `AppTest`, Ruff y pruebas de Docker Compose

**Target Platform**: Contenedor Linux y navegador moderno en escritorio o pantalla estrecha

**Project Type**: Aplicación analítica Python con CLI existente y nueva interfaz web

**Performance Goals**: El 95% de las interacciones de filtro del conjunto de aceptación se refleja en
menos de 2 segundos; primera vista utilizable en menos de 10 segundos con el build de referencia

**Constraints**: Sin rutas personales, sin escritura en datos, sin servicio BI de pago, sin
autenticación pública, sin inferencia dinámica, máximo 1 GiB para el servicio web y conservación de la
frontera de privacidad existente

**Scale/Scope**: 220.031 anuncios seguros, aproximadamente 1.500 segmentos, tres vistas, cuatro
dimensiones de filtrado y uso local o en una red controlada

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle or constraint | Pre-research | Post-design | Evidence |
|---|---|---|---|
| I. Essential First | PASS | PASS | Esencial y Medio están cerrados; esta feature es una extensión independiente. |
| II. Immutable Raw Data and Lineage | PASS | PASS | El panel solo lee exportaciones; no accede ni escribe en `data/raw/`. |
| III. Data Quality Before Analysis | PASS | PASS | Un build no aprobado o incompatible bloquea la publicación. |
| IV. Statistical Rigor | PASS | PASS | Se muestran efectos, intervalos, valores ajustados y sensibilidad ya calculados; no hay inferencia ad hoc. |
| V. Auditable Deliverables | PASS | PASS | No se duplica lógica analítica de notebooks; la guía reproduce el recorrido completo. |
| VI. Decision-First Communication | PASS | PASS | Tres vistas, componentes visibles, español y recomendaciones provisionales. |
| VII. Git and Kanban Governance | PASS | PASS | Rama `002-advanced-dashboard`; issue, estados Kanban y PR son puertas de ejecución. |
| VIII. Contemporary Documentation | PASS | PASS | README, guía, contratos y evidencia se actualizan junto a la implementación. |
| Required analytical stack | PASS | PASS | Streamlit amplía el stack; Pandas y Plotly existentes se reutilizan con versiones bloqueadas. |
| Power BI Medium deliverable | PASS | PASS | El informe existente se conserva sin dependencia de Power BI Service. |
| Docker reproducibility | PASS | PASS | Pipeline y panel son servicios separados de una misma imagen bloqueada. |
| Spanish and privacy | PASS | PASS | Etiquetas en español y descargas limitadas a campos aprobados. |

No existen violaciones constitucionales que requieran excepción.

## Project Structure

### Documentation (this feature)

```text
specs/002-advanced-dashboard/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dashboard-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # generado en la fase de tareas
```

### Source Code (repository root)

```text
dashboard/
├── __init__.py
├── app.py
├── charts.py
├── data.py
├── filters.py
├── presentation.py
└── views/
    ├── __init__.py
    ├── evidence.py
    ├── opportunities.py
    └── summary.py

src/airbnb_supply_analysis/
├── config.py
├── schemas.py
└── ...                      # pipeline y estadística existentes

tests/
├── unit/
│   ├── test_dashboard_charts.py
│   ├── test_dashboard_data.py
│   ├── test_dashboard_filters.py
│   └── test_dashboard_presentation.py
├── contract/
│   └── test_dashboard_contract.py
└── integration/
    ├── test_dashboard_app.py
    ├── test_dashboard_reconciliation.py
    └── test_docker_smoke.py

Dockerfile
compose.yaml
pyproject.toml
uv.lock
README.md
```

**Structure Decision**: Mantener el pipeline como paquete instalado bajo `src/` y añadir una aplicación
`dashboard/` pequeña en la raíz. Los módulos de dominio de la interfaz no importan Streamlit salvo
`app.py` y `views/`, de modo que carga, filtros, presentación y gráficos admiten pruebas unitarias
directas. Una sola imagen evita dos entornos de dependencias; Compose cambia el comando de entrada y
los montajes por servicio.

## Phase 0: Research Decisions

Las decisiones y alternativas se documentan en [research.md](research.md). No quedan decisiones
técnicas abiertas.

## Phase 1: Design and Contracts

- [data-model.md](data-model.md) define el build, conjunto de datos, selección, población filtrada,
  segmento, resultado estadístico y descarga segura.
- [contracts/dashboard-contract.md](contracts/dashboard-contract.md) fija entradas, validaciones,
  semántica de filtros, vistas, errores, privacidad y salud.
- [quickstart.md](quickstart.md) define la validación reproducible de host y contenedor.

La revisión constitucional posterior al diseño permanece en PASS: el diseño no añade persistencia,
servicios externos, inferencia dinámica ni exposición pública y conserva las puertas existentes.

## Complexity Tracking

No hay violaciones que justificar.
