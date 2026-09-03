# Tareas: Airbnb Supply Opportunity Analysis

**Entrada**: artefactos de diseño de `specs/001-supply-opportunity-analysis/`

**Prerrequisitos**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md` y `contracts/`

**Pruebas**: son obligatorias por la constitución, la especificación y el plan. En cada historia se escriben primero y deben fallar por la razón esperada antes de implementar.

**Organización**: las tareas se agrupan por historia de usuario. La puerta Esencial se cierra al terminar US3; solo entonces comienza US4 (Nivel Medio).

## Formato: `[ID] [P?] [Historia] Descripción con ruta exacta`

- **[P]**: puede ejecutarse en paralelo porque afecta archivos distintos y no depende de otra tarea incompleta del mismo bloque.
- **[US1]...[US4]**: trazabilidad directa con las historias de `spec.md`.
- Cada tarea incluye la ruta exacta del archivo que crea o modifica.

---

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: inicializar el repositorio, el entorno reproducible y la gobernanza mínima antes de desarrollar la solución.

- [ ] T001 Crear la rama corta `feat/setup-foundation`, vincularla a su issue de GitHub Projects y registrar issue, rama y PR previstos en `docs/project-management.md`
- [X] T002 Definir Python `>=3.13,<3.14`, dependencias obligatorias, grupos de desarrollo, entry point `airbnb-supply` y configuración de pytest en `pyproject.toml`
- [X] T003 [P] Fijar Python 3.13 para herramientas locales en `.python-version`
- [X] T004 [P] Crear el paquete instalable y exponer su versión inicial en `src/airbnb_supply_analysis/__init__.py`
- [X] T005 [P] Definir exclusiones de entorno y artefactos regenerables sin excluir la constitución, especificaciones ni fuentes aprobadas en `.gitignore`
- [X] T006 [P] Crear el entorno reproducible y el servicio `pipeline`, montando `data/raw/` como solo lectura, en `Dockerfile` y `compose.yaml`
- [X] T007 [P] Crear la plantilla de issues con nivel, fase, responsable, criterios de aceptación y PR vinculado en `.github/ISSUE_TEMPLATE/feature.yml`
- [X] T008 [P] Crear la plantilla de pull request con puertas de pruebas, documentación, privacidad, datos y evidencia en `.github/pull_request_template.md`
- [X] T009 Documentar columnas Kanban, ramas por fase, Conventional Commits, PR incluso en trabajo individual y definición de Done en `docs/project-management.md`
- [X] T010 Crear el README inicial con propósito, alcance Esencial/Medio, estructura, advertencia de procedencia/licencia desconocidas y enlaces a los artefactos de diseño en `README.md`

**Punto de control**: el repositorio tiene entorno, estructura de gobierno y una rama/issue trazables.

---

## Fase 2: Fundamentos (prerrequisitos bloqueantes)

**Propósito**: fijar contratos compartidos de configuración, esquemas, CLI, escritura atómica y pruebas.

**CRÍTICO**: ninguna historia de usuario comienza hasta cerrar esta fase.

### Pruebas y contratos fundacionales

- [X] T011 Crear fixtures sintéticas, directorios temporales aislados y fábricas de DataFrame reutilizables en `tests/conftest.py`
- [X] T012 [P] Escribir pruebas de contrato inicialmente fallidas para comandos, opciones, códigos de salida y resumen final de la CLI en `tests/contract/test_cli_contract.py`
- [X] T013 [P] Escribir pruebas de contrato inicialmente fallidas para nombres, columnas, tipos, claves y privacidad de salidas canónicas y Power BI en `tests/contract/test_output_schemas.py`
- [X] T014 [P] Escribir una prueba inicialmente fallida del arranque del servicio y del montaje de fuentes como solo lectura en `tests/integration/test_docker_smoke.py`

### Implementación fundacional

- [X] T015 [P] Versionar umbrales, alfa 0.05, intervalos 95 %, semillas, correcciones, elegibilidad y reglas de oportunidad en `config/analysis.yml`
- [X] T016 [P] Definir nombres canónicos, tipos, nulabilidad, disponibilidad, privacidad y etiquetas españolas en `config/data-dictionary.yml`
- [X] T017 [P] Definir el contrato JSON del manifiesto de seis fuentes en `config/source-manifest.schema.json`
- [X] T018 Implementar carga tipada de configuración, resolución segura de rutas bajo la raíz y logging sin nombres ni identificadores crudos en `src/airbnb_supply_analysis/config.py`
- [X] T019 [P] Implementar modelos Pandera compartidos para entidades, claves, dominios y metadatos de versión en `src/airbnb_supply_analysis/schemas.py`
- [X] T020 Implementar lectura determinista, SHA-256, conteos y utilidades de directorios temporales sin escritura sobre raw en `src/airbnb_supply_analysis/io.py`
- [X] T021 Implementar publicación atómica, orden estable, CSV UTF-8/LF y control de hashes en `src/airbnb_supply_analysis/exports.py`
- [X] T022 Implementar el esqueleto Click/argparse de `inventory`, `audit`, `build`, `analyze`, `export`, `test`, `notebooks`, `validate` y `all` en `src/airbnb_supply_analysis/cli.py`
- [X] T023 [P] Implementar la interfaz base de ejecución de notebooks con kernel limpio, orden fijo y errores prohibidos en `src/airbnb_supply_analysis/notebooks.py`
- [X] T024 Ejecutar las pruebas fundacionales, corregir solo la infraestructura compartida y registrar comandos y resultados en `docs/acceptance/foundation.md`

**Punto de control**: configuración, contratos, escritura segura y CLI base están listos para todas las historias.

---

## Fase 3: Historia de usuario 1 — Establecer una base de datos confiable (Prioridad: P1) 🎯

**Objetivo**: auditar las seis fuentes originales, preservar su identidad y generar un dataset canónico con trazabilidad y conciliación completas.

**Prueba independiente**: con las seis fuentes en `data/raw/`, `uv run --locked airbnb-supply inventory && uv run --locked airbnb-supply audit && uv run --locked airbnb-supply build` produce inventario, perfil, hallazgos, transformaciones y conciliación de las 220.031 filas, sin modificar ningún hash raw.

### Pruebas para US1 — escribir primero y comprobar el fallo esperado

- [ ] T025 [US1] Crear la rama `feat/essential-data-foundation` desde la base estable y registrar issue, rama y PR de US1 en `docs/project-management.md`
- [X] T026 [P] [US1] Escribir pruebas de presencia, nombre, cabecera ordenada, tamaño, SHA-256, delimitador, codificación y filas del inventario en `tests/contract/test_source_inventory.py`
- [X] T027 [P] [US1] Escribir pruebas de esquemas permisivos por ciudad, columnas ausentes explícitas, dominios y clave candidata `city + listing_id` en `tests/unit/test_raw_schemas.py`
- [X] T028 [P] [US1] Escribir pruebas de perfilado de nulos, duplicados, rangos, reglas cruzadas, outliers y severidades bloqueantes en `tests/unit/test_quality.py`
- [X] T029 [P] [US1] Escribir pruebas de estandarización y de `activity_proxy`: cero solo si faltan `reviews_per_month` y hay cero reseñas; mantener desconocido si existen reseñas positivas en `tests/unit/test_etl.py`
- [X] T030 [US1] Escribir la prueba full-data de inmutabilidad, 220.031 filas conciliadas, unicidad de `listing_key` y explicación de toda cuarentena/rechazo en `tests/integration/test_full_data_build.py`
- [X] T031 [P] [US1] Crear CSV mínimos por caso de borde sin datos personales reales en `tests/fixtures/raw_edge_cases.csv`

### Implementación para US1

- [X] T032 [US1] Copiar sin transformar `C:/proyectosF5/Proyecto8/data/raw/london_airbnb.csv`, `C:/proyectosF5/Proyecto8/data/raw/madrid_airbnb.csv`, `C:/proyectosF5/Proyecto8/data/raw/milan_airbnb.csv`, `C:/proyectosF5/Proyecto8/data/raw/NY_airbnb.csv`, `C:/proyectosF5/Proyecto8/data/raw/sydney_airbnb.csv` y `C:/proyectosF5/Proyecto8/data/raw/tokyo_airbnb.csv` a `data/raw/london_airbnb.csv`, `data/raw/madrid_airbnb.csv`, `data/raw/milan_airbnb.csv`, `data/raw/NY_airbnb.csv`, `data/raw/sydney_airbnb.csv` y `data/raw/tokyo_airbnb.csv`, respectivamente, y verificar que cada origen y copia conservan exactamente el mismo SHA-256
- [X] T033 [US1] Registrar para las seis fuentes nombre, ciudad, hash, bytes, cabecera, filas esperadas, codificación y delimitador en `config/source-manifest.json`
- [X] T034 [US1] Implementar inventario estricto y generación de `source-inventory.json` en `src/airbnb_supply_analysis/io.py`
- [X] T035 [US1] Implementar esquemas raw por ciudad y esquema canónico estricto con indicadores de disponibilidad en `src/airbnb_supply_analysis/schemas.py`
- [X] T036 [US1] Implementar perfil de calidad, hallazgos, reglas cruzadas y análisis robusto de outliers sin eliminación automática en `src/airbnb_supply_analysis/quality.py`
- [X] T037 [US1] Implementar normalización de columnas/tipos, claves, linaje, campos ausentes, fechas desconocidas y derivación documentada de actividad en `src/airbnb_supply_analysis/etl.py`
- [X] T038 [US1] Publicar `listings.parquet`, perfiles, hallazgos, transformaciones y conciliación con metadatos estables desde `src/airbnb_supply_analysis/exports.py`
- [X] T039 [US1] Completar el comando `inventory` con fallo cerrado y resumen legible/machine-readable en `src/airbnb_supply_analysis/cli.py`
- [X] T040 [US1] Completar el comando `audit` con dependencia explícita de inventario aprobado en `src/airbnb_supply_analysis/cli.py`
- [X] T041 [US1] Completar el comando `build` con validación canónica y publicación solo tras conciliación aprobada en `src/airbnb_supply_analysis/cli.py`
- [X] T042 [P] [US1] Crear el notebook narrado de auditoría, con Markdown antes de cada bloque y conclusiones/evidencia/limitaciones/impacto al final de cada sección, en `notebooks/01_data_audit.ipynb`
- [X] T043 [P] [US1] Crear el notebook narrado de ETL, con decisiones, conteos antes/después, rechazos y conclusiones explícitas, en `notebooks/02_etl.ipynb`
- [X] T044 [P] [US1] Publicar el diccionario legible en español, conservando identificadores técnicos en inglés, en `docs/data-dictionary.md`
- [X] T045 [P] [US1] Documentar cada regla ETL, alternativas rechazadas, filas afectadas y limitaciones de fecha/moneda/procedencia en `docs/etl-and-quality.md`
- [X] T046 [US1] Ejecutar la prueba independiente de US1, enlazar evidencias al issue/PR y registrar hashes, conteos y resultado en `docs/acceptance/us1-data-foundation.md`

**Punto de control**: US1 entrega una base auditable y puede demostrarse sin ejecutar el análisis ejecutivo.

---

## Fase 4: Historia de usuario 2 — Priorizar oportunidades de captación (Prioridad: P2)

**Objetivo**: producir EDA, pruebas estadísticas y una matriz transparente que señale qué tipologías investigar en cada ciudad y barrio.

**Prueba independiente**: para cualquier ciudad se identifican segmentos elegibles `city + neighborhood + room_type`, con actividad histórica relativa, precio local, cuota de oferta, tamaño, dispersión, efecto, IC 95 %, valor ajustado, sensibilidad, etiqueta y limitaciones reproducibles.

### Pruebas para US2 — escribir primero y comprobar el fallo esperado

- [X] T047 [US2] Crear la rama `feat/essential-opportunity-analysis` desde US1 aceptada y registrar issue, rama y PR de US2 en `docs/project-management.md`
- [X] T048 [P] [US2] Escribir pruebas de Kruskal-Wallis por ciudad, comparaciones posteriores, corrección Holm, efecto e IC 95 % con empates y muestras degeneradas en `tests/unit/test_room_type_statistics.py`
- [X] T049 [P] [US2] Escribir pruebas de segmento frente al resto de la misma ciudad/tipología, corrección Benjamini-Hochberg por ciudad y agrupación por host en `tests/unit/test_segment_statistics.py`
- [X] T050 [P] [US2] Escribir pruebas de Spearman intra-ciudad para precio/estancia mínima, sus 12 correcciones y casos con datos insuficientes en `tests/unit/test_correlations.py`
- [X] T051 [P] [US2] Escribir pruebas del modelo ajustado en dos partes, intervalos, diagnósticos y variantes de sensibilidad en `tests/unit/test_sensitivity_models.py`
- [X] T052 [P] [US2] Escribir pruebas de elegibilidad (`n>=30`, positivos `>=10`) y de `candidate` (`probability_superiority>=0.56`, `q<0.05`, IC 95 % excluye ausencia de diferencia, sensibilidades robustas y cuota de tipología del barrio inferior a la ciudad), además de `consolidated`, `watch` e `insufficient_evidence`, sin puntuación opaca, en `tests/unit/test_opportunity.py`
- [X] T053 [P] [US2] Escribir pruebas de títulos/leyendas seguros, ausencia de PII, comparaciones monetarias solo intra-ciudad y exportación de Plotly autocontenida en `tests/unit/test_visualization.py`
- [X] T054 [US2] Escribir la prueba de integración que reconcilia resultados estadísticos, matriz de oportunidad y figuras con el dataset canónico en `tests/integration/test_full_analysis.py`

### Implementación para US2

- [X] T055 [US2] Implementar utilidades comunes de remuestreo agrupado por host, probabilidad de superioridad, IC 95 %, tamaños de efecto, diagnósticos y multiplicidad en `src/airbnb_supply_analysis/statistics.py`
- [X] T056 [US2] Implementar Kruskal-Wallis y comparaciones post hoc de actividad por `room_type` dentro de cada ciudad con corrección Holm en `src/airbnb_supply_analysis/statistics.py`
- [X] T057 [US2] Implementar comparaciones de cada barrio-tipología contra el resto equivalente de su ciudad con Benjamini-Hochberg en `src/airbnb_supply_analysis/statistics.py`
- [X] T058 [US2] Implementar correlaciones Spearman intra-ciudad de actividad con precio publicado y noches mínimas, sin interpretarlas causalmente, en `src/airbnb_supply_analysis/statistics.py`
- [X] T059 [US2] Implementar el modelo de sensibilidad en dos partes para actividad positiva y magnitud condicional en `src/airbnb_supply_analysis/statistics.py`
- [X] T060 [US2] Implementar sensibilidades a tratamiento de nulos, umbrales de muestra, outliers válidos y concentración por host en `src/airbnb_supply_analysis/statistics.py`
- [X] T061 [US2] Implementar la matriz por ciudad+barrio+tipología y sus etiquetas transparentes usando todos los criterios bloqueados en `src/airbnb_supply_analysis/opportunity.py`
- [X] T062 [P] [US2] Implementar gráficos Matplotlib/Seaborn y Plotly para distribución, outliers, segmentación, efectos, correlaciones y oportunidades en `src/airbnb_supply_analysis/visualization.py`
- [X] T063 [US2] Publicar `statistical_results.parquet`, `opportunity_segments.parquet` y el resumen analítico con esquema/metadatos estables en `src/airbnb_supply_analysis/exports.py`
- [X] T064 [US2] Completar `analyze` con prerrequisitos, familias de pruebas, sensibilidades, guardas terminológicas y códigos de salida contractuales en `src/airbnb_supply_analysis/cli.py`
- [X] T065 [US2] Crear el notebook ejecutivo completo, con EDA uni/bivariada, segmentación, outliers, estadística, gráficos interactivos y cierre de evidencia/limitaciones/decisión en `notebooks/03_executive_eda.ipynb`
- [X] T066 [US2] Generar y versionar el índice reproducible de figuras estáticas e interactivas en `artifacts/figures/manifest.json`
- [X] T067 [P] [US2] Redactar hallazgos provisionales y recomendaciones de captación, citando métricas y evitando demanda, liquidez, ocupación, margen, actualidad o causalidad, en `docs/analysis/executive-findings.md`
- [X] T068 [US2] Validar automáticamente que toda conclusión inferencial tenga prueba/efecto/IC/corrección y documentar el resultado en `docs/acceptance/statistical-rigor.md`
- [X] T069 [US2] Ejecutar la prueba independiente de US2, enlazar evidencias al issue/PR y registrar segmentos seleccionados y cautelas en `docs/acceptance/us2-opportunity-analysis.md`

**Punto de control**: US2 responde la decisión principal con evidencia estadística y sin sobreinterpretar las fuentes.

---

## Fase 5: Historia de usuario 3 — Revisar y reproducir el análisis Esencial (Prioridad: P3)

**Objetivo**: permitir que otra persona reproduzca el flujo completo, audite las conclusiones y verifique la gobernanza sin edición manual de datos.

**Prueba independiente**: desde un entorno limpio, `docker compose run --rm pipeline all` ejecuta inventario → auditoría → ETL → análisis → exportación → pruebas → notebooks → validación, y el revisor encuentra trazabilidad issue-rama-commits-PR-evidencia para cada entrega.

### Pruebas para US3 — escribir primero y comprobar el fallo esperado

- [X] T070 [US3] Crear la rama `feat/essential-reproducibility` desde US2 aceptada y registrar issue, rama y PR de US3 en `docs/project-management.md`
- [X] T071 [P] [US3] Escribir pruebas NBClient de ejecución en kernels frescos, orden y contrato de bloques Markdown/conclusión en `tests/integration/test_notebooks.py`
- [X] T072 [P] [US3] Escribir la prueba de integración del orden, idempotencia, fallo cerrado y no publicación parcial del comando `all` en `tests/integration/test_cli_all.py`
- [X] T073 [P] [US3] Escribir pruebas de documentación, español visible, términos prohibidos, enlaces locales y ausencia de PII en `tests/contract/test_documentation.py`
- [X] T074 [P] [US3] Escribir la prueba full-data de presupuestos ETL ≤60 s, flujo completo ≤5 min y RSS pico ≤2 GB en 2 vCPU/4 GB en `tests/integration/test_performance.py`

### Implementación para US3

- [X] T075 [US3] Completar ejecución ordenada y aislada de los tres notebooks y validar sus bloques narrativos en `src/airbnb_supply_analysis/notebooks.py`
- [X] T076 [US3] Completar `test --suite unit|contract|integration|all` con resumen de aprobadas/fallidas/omitidas en `src/airbnb_supply_analysis/cli.py`
- [X] T077 [US3] Completar `notebooks` con kernel fresco, salidas en `artifacts/executed_notebooks/` y código de salida 7 ante incumplimiento en `src/airbnb_supply_analysis/cli.py`
- [X] T078 [US3] Completar `validate` para esquemas, hashes, conciliación, terminología, privacidad y evidencia de notebooks en `src/airbnb_supply_analysis/cli.py`
- [X] T079 [US3] Completar `all` con el orden contractual, idempotencia y conservación del último build aceptado en `src/airbnb_supply_analysis/cli.py`
- [ ] T080 [P] [US3] Completar instalación, comandos host/Docker, estructura, pruebas, resultados, límites y reproducción paso a paso en `README.md`
- [ ] T081 [P] [US3] Actualizar y ejecutar desde cero la guía canónica de reproducción, dejando todos los pasos libres de rutas personales, en `specs/001-supply-opportunity-analysis/quickstart.md`
- [ ] T082 [US3] Verificar el flujo completo con límites 2 vCPU/4 GB y documentar versión de Docker, comandos, duración y salidas en `docs/acceptance/docker-reproduction.md`
- [ ] T083 [US3] Medir ETL, flujo analítico y RSS pico sobre las seis fuentes y registrar evidencia o desviación explicada en `docs/acceptance/performance.md`
- [ ] T084 [US3] Conciliar GitHub Projects con issues, estados, ramas, commits atómicos, PR y criterios de Done de las fases Esenciales en `docs/project-management.md`
- [ ] T085 [US3] Ejecutar `airbnb-supply all`, revisar manualmente notebooks/documentación, cerrar la puerta Esencial y enlazar toda evidencia en `docs/acceptance/essential-level.md`

**Punto de control obligatorio — NIVEL ESENCIAL**: US1, US2 y US3 están completas, probadas, documentadas, fusionadas y en `Done`. No comenzar US4 antes de este punto.

---

## Fase 6: Historia de usuario 4 — Explorar un informe ejecutivo Power BI (Prioridad: P4)

**Objetivo**: entregar un informe Power BI Desktop gratuito, claro e interactivo que permita explorar oportunidades, evidencia y cautelas.

**Prueba independiente**: con un `DataRoot` limpio, el informe refresca las ocho tablas, mantiene `Diferencia de conciliación = 0`, permite identificar hasta tres oportunidades válidas y sus cautelas en menos de tres minutos, y funciona sin mapa mediante la vista de ranking.

### Pruebas para US4 — escribir primero y comprobar el fallo esperado

- [ ] T086 [US4] Crear la rama `feat/medium-powerbi-report` solo después del cierre Esencial y registrar issue, rama y PR de US4 en `docs/project-management.md`
- [ ] T087 [P] [US4] Ampliar el contrato automatizado de las ocho tablas estrella, sus claves, tipos, orden, formato CSV y versión de esquema en `tests/contract/test_powerbi_exports.py`
- [ ] T088 [P] [US4] Escribir pruebas de exclusión de nombres, IDs crudos, coordenadas por anuncio y claves técnicas visibles en `tests/contract/test_powerbi_privacy.py`
- [ ] T089 [P] [US4] Escribir pruebas de filas, hashes, relaciones y control de build sin diferencias inexplicadas en `tests/integration/test_powerbi_reconciliation.py`
- [ ] T090 [P] [US4] Crear la lista de aceptación manual para refresh, tres páginas, filtros, fallback, accesibilidad, métricas muestreadas y prueba de tres minutos en `powerbi/acceptance-checklist.md`

### Implementación para US4

- [ ] T091 [US4] Implementar dimensiones, hechos, claves sustitutas, privacidad, orden estable y `build_control.csv` en `src/airbnb_supply_analysis/exports.py`
- [ ] T092 [US4] Completar `export` y conectar su validación con `validate` y `all` en `src/airbnb_supply_analysis/cli.py`
- [ ] T093 [P] [US4] Documentar Power BI Desktop gratuito, versión mínima probada, parámetro `DataRoot`, refresh, modelo, limitaciones y resolución de errores en `powerbi/README.md`
- [ ] T094 [P] [US4] Crear el tema accesible con contraste ≥4,5:1 y estados diferenciados también por texto/icono en `powerbi/theme.json`
- [ ] T095 [US4] Construir en `powerbi/airbnb-supply-opportunity.pbix` las consultas parametrizadas por `DataRoot`, validación de release gate y modelo estrella con relaciones uno-a-muchos unidireccionales
- [ ] T096 [US4] Crear en `powerbi/airbnb-supply-opportunity.pbix` las medidas explícitas requeridas, denominadores, tooltips explicativos y `Diferencia de conciliación`
- [ ] T097 [US4] Construir la página 1 `Resumen ejecutivo` con hasta tres candidatos, evidencia separada, recomendación provisional y avisos visibles en `powerbi/airbnb-supply-opportunity.pbix`
- [ ] T098 [US4] Construir la página 2 `Oportunidades de captación` con slicers globales, ranking siempre disponible, mapa agregado opcional y drillthrough en `powerbi/airbnb-supply-opportunity.pbix`
- [ ] T099 [US4] Construir la página 3 `Detalle y confianza` con muestra, dispersión, efecto, IC, valores ajustados, sensibilidad, calidad, control de build y retorno en `powerbi/airbnb-supply-opportunity.pbix`
- [ ] T100 [US4] Configurar sincronización limitada de filtros, reset, navegación, orden de tabulación, alt text dinámico y ocultación de claves técnicas en `powerbi/airbnb-supply-opportunity.pbix`
- [ ] T101 [US4] Exportar la plantilla sin datos y comprobar que solicita `DataRoot` en la primera apertura en `powerbi/airbnb-supply-opportunity.pbit`
- [ ] T102 [US4] Implementar verificación externa de archivos, schema major, hashes, filas, privacidad y diferencia de conciliación en `scripts/verify_powerbi.ps1`
- [ ] T103 [US4] Refrescar `.pbix` desde una ruta limpia, cotejar una muestra de medidas con Parquet/CSV y registrar capturas y resultados en `docs/acceptance/powerbi-reconciliation.md`
- [ ] T104 [US4] Realizar la prueba no asistida de tres minutos y la revisión de accesibilidad/fallback, registrando incidencias y correcciones en `docs/acceptance/powerbi-uat.md`
- [ ] T105 [US4] Ejecutar la aceptación independiente, cerrar la puerta Medio y enlazar exportaciones, `.pbix`, `.pbit`, pruebas, issue y PR en `docs/acceptance/medium-level.md`

**Punto de control — NIVEL MEDIO**: informe funcional, interactivo, accesible, conciliado, reproducible localmente y sin licencia de pago.

---

## Fase 7: Pulido y controles transversales

**Propósito**: comprobar coherencia final sin ampliar el alcance comprometido.

- [ ] T106 [P] Documentar únicamente como backlog posterior las opciones Avanzado/Experto —modelos, clustering, datos externos y publicación— en `docs/roadmap.md`
- [ ] T107 [P] Revisar que decisiones, supuestos, incidentes, alternativas rechazadas, resultados y limitaciones estén contemporáneamente enlazados desde `README.md`
- [ ] T108 Ejecutar todos los comandos de `specs/001-supply-opportunity-analysis/quickstart.md` en un checkout limpio y registrar cualquier corrección en `docs/acceptance/quickstart-validation.md`
- [ ] T109 Ejecutar pruebas unitarias, contractuales e integración, notebooks y validaciones Power BI en Docker; archivar el resumen final en `docs/acceptance/final-release.md`
- [ ] T110 Conciliar GitHub Projects con `main`, confirmar PR integradas y elementos en `Done`, y registrar la instantánea final y el historial de release en `docs/project-management.md`

---

## Dependencias y orden de ejecución

### Dependencias de fases

```text
Fase 1 Preparación
        ↓
Fase 2 Fundamentos (bloquea todas las historias)
        ↓
US1 Base confiable
        ↓
US2 Oportunidades y estadística
        ↓
US3 Reproducción y cierre Esencial
        ↓  PUERTA ESENCIAL OBLIGATORIA
US4 Power BI y cierre Medio
        ↓
Fase 7 Pulido y release
```

- **Fase 1**: no tiene dependencias.
- **Fase 2**: depende de la Fase 1 y bloquea todas las historias.
- **US1**: depende de la Fase 2; entrega por sí sola una base de datos confiable y auditable.
- **US2**: depende del dataset canónico aceptado de US1; se prueba independientemente sobre ese contrato estable.
- **US3**: depende de US1 y US2 porque reproduce y cierra todo el Nivel Esencial.
- **US4**: depende del cierre formal de US3; la constitución prohíbe iniciarla antes.
- **Fase 7**: depende de las cuatro historias para el release comprometido; T106 solo documenta backlog y no inicia alcance avanzado.

### Dependencias internas por historia

- Escribir las pruebas de cada historia y verificar que fallan por la ausencia del comportamiento esperado.
- Implementar primero esquemas/entidades y utilidades comunes; después servicios analíticos y CLI.
- Generar artefactos antes de construir documentación que los reconcilia.
- Ejecutar la prueba independiente y actualizar issue/PR solo después de pasar las pruebas aplicables.
- Mantener raw inmutable y publicar salidas únicamente después de validar el build completo.

### Oportunidades de paralelización

- **Preparación**: T003–T008 pueden repartirse después de T001; T009 consolida la gobernanza y T010 integra los enlaces.
- **Fundamentos**: T012–T014 y T015–T017 afectan archivos distintos; T018–T023 requieren coordinar los contratos compartidos.
- **US1**: T026–T029 y T031 pueden escribirse en paralelo; tras estabilizar contratos, T042–T045 pueden desarrollarse en paralelo.
- **US2**: T048–T053 pueden escribirse en paralelo; T062 y T067 pueden avanzar en paralelo después de fijar los resultados y el vocabulario.
- **US3**: T071–T074 pueden escribirse en paralelo; T080 y T081 pueden actualizarse en paralelo tras estabilizar la CLI.
- **US4**: T087–T090 pueden escribirse en paralelo; T093 y T094 pueden avanzar en paralelo. T095–T101 son secuenciales porque modifican el mismo archivo Power BI o derivan de él.
- **Pulido**: T106 y T107 pueden ejecutarse en paralelo; T108–T110 son secuenciales por ser controles de release.

---

## Ejemplos de ejecución paralela

### US1

```text
En paralelo: T026 test_source_inventory.py | T027 test_raw_schemas.py | T028 test_quality.py | T029 test_etl.py
Después: T030 integración full-data → T032 copia verificada → T033 manifiesto → T034–T041 implementación
En paralelo tras el build: T042 notebook auditoría | T043 notebook ETL | T044 diccionario | T045 documentación ETL
```

### US2

```text
En paralelo: T048 room types | T049 segmentos | T050 correlaciones | T051 sensibilidad | T052 oportunidad | T053 visualización
Después: T055 utilidades → T056–T060 análisis → T061 matriz → T063 publicación → T064 CLI → T065 notebook
En paralelo tras resultados estables: T062 visualizaciones | T067 hallazgos ejecutivos
```

### US3

```text
En paralelo: T071 notebooks | T072 CLI all | T073 documentación | T074 rendimiento
Después: T075 runner → T076–T079 CLI → T082–T085 aceptación Esencial
```

### US4

```text
En paralelo: T087 esquema export | T088 privacidad | T089 conciliación | T090 checklist manual
Después: T091 exportación → T092 CLI → T095 modelo → T096 medidas → T097–T100 páginas/interacciones → T101 plantilla
En paralelo tras fijar el contrato visual: T093 guía Power BI | T094 tema accesible
```

---

## Estrategia de implementación

### Primer incremento técnico — US1

1. Completar Fases 1 y 2.
2. Completar US1.
3. Detenerse y ejecutar su prueba independiente.
4. Demostrar inventario, calidad, ETL, trazabilidad y conciliación sin depender de estadísticas ni Power BI.

US1 es el primer incremento demostrable, pero **no** satisface por sí solo el listón mínimo evaluable.

### Release mínimo obligatorio — Nivel Esencial

1. Aceptar US1: base confiable.
2. Aceptar US2: EDA, estadística y recomendación provisional.
3. Aceptar US3: reproducción, documentación y gobernanza.
4. Ejecutar T085 y cerrar formalmente la puerta Esencial.
5. Solo entonces comenzar US4.

### Entrega incremental completa

1. Preparación + Fundamentos → infraestructura estable.
2. US1 → datos auditables.
3. US2 → decisión respaldada.
4. US3 → Nivel Esencial reproducible y cerrado.
5. US4 → Nivel Medio interactivo y cerrado.
6. Pulido → release final; Avanzado/Experto permanece en backlog.

---

## Reglas de ejecución y Done

- Una tarea no está terminada si sus pruebas, documentación contemporánea o evidencia de aceptación están pendientes.
- Verificar que las pruebas nuevas fallan por la razón esperada antes de implementar y que pasan después.
- Usar un commit Conventional Commit atómico por tarea o grupo inseparable; no mezclar fases ni historias.
- Actualizar README y documentación afectada dentro del mismo cambio material.
- Mantener GitHub Projects como única fuente de verdad con `Backlog → Ready → In Progress → Review → Done`.
- No mover un issue a `Done` hasta integrar su PR y enlazar evidencia.
- No editar archivos de `data/raw/`; cualquier limpieza se implementa en código versionado.
- No mostrar nombres, IDs crudos ni coordenadas individuales en salidas públicas.
- No llamar a `reviews_per_month` demanda, liquidez, reservas u ocupación, ni a `price` ingreso o margen.
- No comparar importes monetarios entre ciudades ni afirmar actualidad/recencia con fechas de extracción desconocidas.
- Ningún trabajo Avanzado o Experto puede retrasar o sustituir las puertas Esencial y Medio.
