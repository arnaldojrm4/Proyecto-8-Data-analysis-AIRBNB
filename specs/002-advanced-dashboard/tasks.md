# Tasks: Panel avanzado interactivo y portable

**Input**: Design documents from `/specs/002-advanced-dashboard/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Se aplica TDD. Las pruebas de cada historia se escriben y se observan fallar antes de su
implementación.

**Organization**: Las tareas se agrupan por historia para permitir incrementos demostrables y pruebas
independientes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo sin editar los mismos archivos ni depender de trabajo incompleto.
- **[Story]**: historia de usuario servida por la tarea.
- Cada tarea incluye una ruta exacta.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar rama, dependencias y esqueleto sin implementar comportamiento.

- [X] T001 Crear el issue de la feature, añadirlo al GitHub Project en `Ready`, moverlo a `In Progress` y registrar URL, nivel, fase, propietario y criterios en `docs/project-management.md`
- [X] T002 Añadir Streamlit 1.63.x y actualizar el bloqueo reproducible en `pyproject.toml` y `uv.lock`
- [X] T003 [P] Crear el paquete y módulos vacíos definidos por el plan en `dashboard/__init__.py` y `dashboard/views/__init__.py`
- [X] T004 [P] Definir tema, telemetría deshabilitada y opciones seguras de servidor en `.streamlit/config.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Contrato de datos, modelos, carga, errores y shell requeridos por todas las historias.

**⚠️ CRITICAL**: Ninguna historia puede comenzar hasta completar esta fase.

- [X] T005 [P] Escribir pruebas fallidas de modelos inmutables y estados de build en `tests/unit/test_dashboard_data.py`
- [X] T006 [P] Escribir pruebas contractuales fallidas de archivos, columnas y privacidad en `tests/contract/test_dashboard_contract.py`
- [X] T007 Implementar `DashboardDataError`, `BuildMetadata`, `DashboardDataset` y lectura sin caché en `dashboard/data.py`
- [X] T008 Implementar la validación de archivos, versión, estado, build, recuentos, claves y relaciones en `dashboard/data.py`
- [X] T009 [P] Escribir pruebas fallidas de selección normalizada y poblaciones filtradas en `tests/unit/test_dashboard_filters.py`
- [X] T010 Implementar `FilterSelection`, opciones dependientes y filtros puros por hecho en `dashboard/filters.py`
- [X] T011 [P] Escribir prueba fallida del shell, navegación y estado bloqueado mediante AppTest en `tests/integration/test_dashboard_app.py`
- [X] T012 Implementar configuración, carga cacheada por `build_id`, navegación y puerta global en `dashboard/app.py`

**Checkpoint**: El panel puede cargar o rechazar un build y mantener una selección válida sin mostrar
todavía las vistas analíticas.

---

## Phase 3: User Story 1 - Explorar oportunidades con filtros coordinados (Priority: P1) 🎯 MVP

**Goal**: Entregar resumen y oportunidades filtrables con ranking alternativo y descargas seguras.

**Independent Test**: Seleccionar ciudad y tipologías, verificar que indicadores, gráficos, ranking y
tabla comparten población, cambiar barrio y restablecer toda la selección.

### Tests for User Story 1

- [X] T013 [P] [US1] Escribir pruebas fallidas de indicadores y figuras con datos normales y vacíos en `tests/unit/test_dashboard_charts.py`
- [X] T014 [P] [US1] Escribir pruebas fallidas de etiquetas, unidades y proyección de descarga segura en `tests/unit/test_dashboard_presentation.py`
- [X] T015 [US1] Ampliar AppTest con recorridos fallidos de filtros, persistencia y restablecimiento en `tests/integration/test_dashboard_app.py`
- [X] T016 [P] [US1] Escribir conciliación fallida de indicadores y ranking contra los CSV en `tests/integration/test_dashboard_reconciliation.py`

### Implementation for User Story 1

- [X] T017 [P] [US1] Implementar indicadores, ranking, distribución y mapa con fallback tabular en `dashboard/charts.py`
- [X] T018 [P] [US1] Implementar etiquetas españolas, formatos, cautelas y descargas seguras en `dashboard/presentation.py`
- [X] T019 [US1] Implementar filtros coordinados, población visible e indicadores ejecutivos en `dashboard/views/summary.py`
- [X] T020 [US1] Implementar comparación de componentes, ranking, mapa, estados vacíos y descarga en `dashboard/views/opportunities.py`
- [X] T021 [US1] Integrar ambas vistas y su estado compartido en `dashboard/app.py`

**Checkpoint**: US1 funciona de forma independiente como MVP y permite identificar un candidato con su
cautela aunque el mapa no esté disponible.

---

## Phase 4: User Story 2 - Comprender y contrastar evidencia estadística (Priority: P2)

**Goal**: Rastrear las tres hipótesis y la sensibilidad hasta evidencia completa y honesta.

**Independent Test**: Abrir un resultado de tipología, segmento y asociación y comprobar población,
método, muestra, efecto, intervalo, ajuste, sensibilidad y limitación sin recálculo por filtros.

### Tests for User Story 2

- [X] T022 [P] [US2] Escribir pruebas fallidas de selección de resultados por familia y población publicada en `tests/unit/test_dashboard_filters.py`
- [X] T023 [P] [US2] Escribir pruebas fallidas de interpretación, magnitud y términos prohibidos en `tests/unit/test_dashboard_presentation.py`
- [X] T024 [US2] Añadir recorrido AppTest fallido para las tres hipótesis y sensibilidad en `tests/integration/test_dashboard_app.py`
- [X] T025 [P] [US2] Añadir conciliación fallida de evidencia visible contra resultados publicados en `tests/integration/test_dashboard_reconciliation.py`

### Implementation for User Story 2

- [X] T026 [P] [US2] Implementar figuras de efectos, intervalos y asociaciones sin inferencia nueva en `dashboard/charts.py`
- [X] T027 [P] [US2] Implementar resúmenes de hipótesis, significación ajustada, efecto y sensibilidad en `dashboard/presentation.py`
- [X] T028 [US2] Implementar navegación y detalle de tipología, segmento, asociación y sensibilidad en `dashboard/views/evidence.py`
- [X] T029 [US2] Integrar la vista de evidencia respetando filtros aplicables y poblaciones fijas en `dashboard/app.py`

**Checkpoint**: US2 permite defender cada conclusión estadística sin convertir asociación en causalidad
ni significación en relevancia práctica.

---

## Phase 5: User Story 3 - Reproducir y ejecutar el panel de forma portable (Priority: P3)

**Goal**: Abrir el panel desde un build existente o recién generado mediante un servicio contenido sano.

**Independent Test**: Desde un checkout limpio, construir, generar datos, arrancar el panel, consultar su
salud y detenerlo siguiendo solo el quickstart.

### Tests for User Story 3

- [X] T030 [P] [US3] Escribir prueba fallida de configuración, puerto, volumen de solo lectura, recursos y salud en `tests/integration/test_docker_smoke.py`
- [X] T031 [P] [US3] Escribir prueba fallida del comando host documentado en `tests/contract/test_documentation.py`

### Implementation for User Story 3

- [X] T032 [US3] Adaptar la imagen única para admitir CLI y panel con usuario no privilegiado en `Dockerfile`
- [X] T033 [US3] Añadir servicio `dashboard`, puerto configurable, montaje de solo lectura, límite de 1 GiB y healthcheck en `compose.yaml`
- [X] T034 [US3] Documentar los recorridos host y Docker y la convivencia con Power BI en `README.md` y `powerbi/README.md`
- [X] T035 [US3] Ejecutar el recorrido contenido completo y registrar tiempos, salud y resultados en `docs/acceptance/advanced-dashboard-docker.md`

**Checkpoint**: US3 reproduce el panel sin rutas personales, licencias BI ni ejecución implícita del
pipeline al iniciar la interfaz.

---

## Phase 6: User Story 4 - Detectar datos no publicables o incompatibles (Priority: P4)

**Goal**: Bloquear de forma accionable todos los builds que no cumplan el contrato.

**Independent Test**: Simular archivo ausente, gate rechazado, versión incompatible, mezcla de builds,
recuento incorrecto, clave duplicada y relación huérfana y comprobar bloqueo sin métricas.

### Tests for User Story 4

- [X] T036 [P] [US4] Completar casos contractuales fallidos para cada código de rechazo en `tests/contract/test_dashboard_contract.py`
- [X] T037 [P] [US4] Añadir recorridos AppTest fallidos de bloqueo, mensaje y recuperación en `tests/integration/test_dashboard_app.py`

### Implementation for User Story 4

- [X] T038 [US4] Completar validaciones y códigos estables de `DashboardDataError` en `dashboard/data.py`
- [X] T039 [P] [US4] Implementar mensajes españoles seguros y pasos de recuperación por código en `dashboard/presentation.py`
- [X] T040 [US4] Integrar estados `blocked`, `empty` e `insufficient` sin trazas ni métricas residuales en `dashboard/app.py`

**Checkpoint**: US4 rechaza cada entrada inválida de forma visible, determinista y recuperable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Accesibilidad, rendimiento, documentación y puertas finales del nivel Avanzado.

- [X] T041 [P] Ampliar la guía educativa con filtros e interpretación de hipótesis en `docs/study-guide.md`
- [X] T042 [P] Documentar cumplimiento de requisitos y trazabilidad FR/SC/pruebas en `docs/acceptance/advanced-level.md`
- [X] T043 Ejecutar y registrar la revisión de teclado, foco, contraste, orden de lectura y comportamiento estrecho en `dashboard/app.py`, `.streamlit/config.toml` y `docs/acceptance/advanced-level.md`
- [X] T044 Medir carga inicial y acciones de filtro y optimizar solo incumplimientos reproducibles en `dashboard/data.py` y `docs/acceptance/advanced-level.md`
- [X] T045 Ejecutar unitarias, contractuales, integración, AppTest y Ruff y registrar evidencia en `docs/acceptance/advanced-level.md`
- [X] T046 Ejecutar build, pipeline y smoke test Docker desde cero y registrar evidencia en `docs/acceptance/advanced-dashboard-docker.md`
- [X] T047 Conciliar muestras del panel con CSV y Power BI y registrar diferencias cero en `docs/acceptance/advanced-level.md`
- [X] T048 Crear el PR, mover el issue a `Review`, registrar commits y revisión y moverlo a `Done` solo tras integrar en `docs/project-management.md`
- [X] T049 Ejecutar con un usuario de prueba el recorrido cronometrado de SC-001 y registrar tiempo, éxito y observaciones en `docs/acceptance/advanced-level.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup y bloquea todas las historias.
- **US1 (Phase 3)**: depende de Foundational y constituye el MVP.
- **US2 (Phase 4)**: depende de Foundational; integra navegación con US1 al final.
- **US3 (Phase 5)**: depende de Foundational y de una entrada web arrancable; puede avanzar en paralelo
  con US2 después de T012.
- **US4 (Phase 6)**: depende de Foundational; sus pruebas pueden avanzar en paralelo, y su integración
  final requiere el shell de US1.
- **Polish (Phase 7)**: depende de las historias incluidas en la entrega.

### User Story Dependencies

```text
Setup → Foundation → US1 (MVP) ─┬→ Polish
                    ├→ US2 ─────┤
                    ├→ US3 ─────┤
                    └→ US4 ─────┘
```

- **US1** no depende de otra historia después de Foundation.
- **US2** es comprobable con la vista de evidencia aunque reutiliza el shell común.
- **US3** es comprobable con cualquier vista mínima arrancable después de Foundation.
- **US4** es comprobable inyectando builds inválidos en el shell común.

### Within Each User Story

1. Escribir pruebas y confirmar que fallan por la capacidad ausente.
2. Implementar funciones puras antes de la vista que las consume.
3. Integrar la vista y ejecutar sus pruebas unitarias, contractuales y de recorrido.
4. Detenerse en el checkpoint y conservar evidencia antes de la siguiente prioridad.

### Parallel Opportunities

- T003 y T004 pueden avanzar en paralelo después de T002.
- T005, T006, T009 y T011 escriben archivos de prueba diferentes y pueden avanzar en paralelo.
- En US1, T013, T014 y T016 pueden avanzar en paralelo; T017 y T018 también.
- En US2, T022, T023 y T025 pueden avanzar en paralelo; T026 y T027 también.
- US2, infraestructura de US3 y pruebas de US4 pueden avanzar en paralelo tras Foundation si se evita
  editar simultáneamente `dashboard/app.py`.
- T041 y T042 pueden ejecutarse en paralelo al comenzar el pulido.

## Parallel Example: User Story 1

```text
Task T013: pruebas de figuras en tests/unit/test_dashboard_charts.py
Task T014: pruebas de presentación en tests/unit/test_dashboard_presentation.py
Task T016: conciliación en tests/integration/test_dashboard_reconciliation.py

Después:
Task T017: figuras en dashboard/charts.py
Task T018: presentación en dashboard/presentation.py
```

## Parallel Example: User Story 2

```text
Task T022: selección estadística en tests/unit/test_dashboard_filters.py
Task T023: interpretación en tests/unit/test_dashboard_presentation.py
Task T025: conciliación estadística en tests/integration/test_dashboard_reconciliation.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Setup.
2. Completar Foundation.
3. Implementar US1 con TDD.
4. Ejecutar el checkpoint de US1.
5. Demostrar filtrado coordinado, ranking y fallback antes de ampliar el alcance.

### Incremental Delivery

1. Setup + Foundation → build validado y shell seguro.
2. US1 → panel exploratorio útil.
3. US2 → evidencia estadística defendible.
4. US3 → reproducción contenida.
5. US4 → rechazo completo de entradas inválidas.
6. Polish → aceptación integral y trazabilidad.

## Notes

- Cada tarea de implementación comienza después de observar fallar sus pruebas asociadas.
- `[P]` solo marca trabajo en archivos distintos y sin dependencia incompleta.
- No se modifica el archivo temporal `output/presentation/~$airbnb-oportunidades-captacion-ejecutiva.pptx`.
- Los artefactos de esta feature SDD se versionan para que especificación, plan, tareas, revisión y PR
  conserven trazabilidad conjunta.
- Cada grupo lógico usa commits convencionales y no mueve el issue a `Done` sin PR y evidencia.
