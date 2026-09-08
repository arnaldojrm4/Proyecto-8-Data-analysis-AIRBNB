# Research: Panel avanzado interactivo y portable

## Decision 1: Marco de aplicación web

**Decision**: Usar Streamlit 1.63.x sobre Python 3.13 y conservar Plotly 6.x para las figuras.

**Rationale**: El repositorio ya usa Pandas y Plotly; Streamlit permite convertir esas estructuras en
una aplicación de datos interactiva con poca capa incidental. La versión 1.63.0 declara compatibilidad
con Python 3.13 y se fijará en `uv.lock`. La aplicación sigue siendo gratuita y no exige una cuenta de
servicio BI.

**Alternatives considered**: Dash ofrece control fino, pero requiere más código de callbacks y layout;
Superset o Metabase introducirían base de datos y operación adicionales; Power BI Embedded mantendría
una dependencia externa de capacidad y licencias.

**Sources**: [Streamlit en PyPI](https://pypi.org/project/streamlit/),
[documentación de despliegue](https://docs.streamlit.io/deploy/tutorials/docker).

## Decision 2: Fuente de datos y frontera de privacidad

**Decision**: Leer únicamente los ocho CSV de `data/powerbi/` y reutilizar sus dimensiones y hechos.

**Rationale**: Son la frontera de publicación existente, están conciliados con Power BI, excluyen
identificadores y nombres originales y contienen todas las métricas necesarias. Leer los Parquet
canónicos expondría columnas que la interfaz no necesita y duplicaría reglas de proyección segura.

**Alternatives considered**: Leer Parquet sería más rápido, pero ampliaría la superficie de privacidad;
generar otro conjunto de exportaciones produciría dos contratos públicos que podrían divergir.

## Decision 3: Validación y caché

**Decision**: Validar primero `build_control.csv`, después archivos, columnas, claves y relaciones, y
almacenar en caché el conjunto cargado usando la identidad del build como clave explícita.

**Rationale**: La identidad del build permite reutilizar datos inmutables durante las interacciones e
invalidarlos cuando el pipeline publica una nueva ejecución. Las funciones de lectura y validación
permanecen independientes de la caché para poder probar fallos deterministas.

**Alternatives considered**: Cachear solo por ruta no detecta un archivo reemplazado en el mismo lugar;
recargar los 47 MB de anuncios en cada interacción incumpliría el objetivo de respuesta.

**Source**: [caché de datos de Streamlit](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data).

## Decision 4: Navegación y estado

**Decision**: Una entrada registra tres vistas y conserva en estado de sesión una selección normalizada.
La ciudad es única y obligatoria; tipologías y barrios son selecciones múltiples dependientes; el estado
de evidencia se aplica solo a hechos con esa semántica.

**Rationale**: Una selección compartida evita discrepancias entre páginas. Normalizar después de cada
cambio elimina opciones huérfanas. Los filtros no se aplican a métricas cuya población no comparte la
misma dimensión.

**Alternatives considered**: Filtros independientes por página facilitan la implementación, pero hacen
que el usuario compare poblaciones distintas sin advertirlo; parámetros de URL públicos quedan fuera
por no existir requisito de enlaces compartibles.

## Decision 5: Evidencia precalculada

**Decision**: Mostrar solo filas existentes en `fact_statistical_results.csv` y enlazar evidencia de
segmento mediante `segment_key`; no ejecutar pruebas al cambiar filtros.

**Rationale**: Los resultados publicados ya fijan población, unidad inferencial, correcciones e
intervalos. Recalcular tras cada combinación convertiría la interfaz en una herramienta exploratoria de
inferencia múltiple sin control y podría contradecir los resultados aprobados.

**Alternatives considered**: La inferencia dinámica parece flexible, pero cambia hipótesis y familias de
comparaciones en función de acciones del usuario y no cumple la constitución estadística.

## Decision 6: Estrategia de pruebas

**Decision**: Probar funciones puras con pytest, recorridos de widgets con `AppTest`, conciliación con
agregaciones independientes y el proceso real mediante salud HTTP y Docker Compose.

**Rationale**: Las pruebas puras localizan fallos de datos y semántica; `AppTest` permite inspeccionar e
interactuar programáticamente con una aplicación multipágina; el smoke test cubre empaquetado, puerto y
montaje, aspectos que las pruebas en proceso no observan.

**Alternatives considered**: Solo capturas manuales no detectan regresiones de filtros; automatización
exclusiva de navegador añade coste y fragilidad sin mejorar la cobertura de la lógica tabular.

**Source**: [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).

## Decision 7: Contenedor y operación

**Decision**: Reutilizar una única imagen bloqueada, sobrescribir la entrada del servicio `dashboard`,
publicar `8501`, montar `data/powerbi` como solo lectura y comprobar `/_stcore/health`. El panel no
depende de ejecutar `pipeline` en el mismo `compose up`.

**Rationale**: Un build aprobado puede reutilizarse muchas veces; acoplar ambos procesos al arranque
aumenta latencia y disponibilidad conjunta. El endpoint recomendado verifica que el proceso web atiende,
mientras la interfaz comunica por separado la validez del build.

**Alternatives considered**: Dos imágenes duplican resolución de dependencias; `depends_on` con el
pipeline lo ejecutaría innecesariamente y no representa que los datos son un artefacto persistente.

**Sources**: [Streamlit con Docker](https://docs.streamlit.io/deploy/tutorials/docker),
[healthchecks en Compose](https://docs.docker.com/reference/compose-file/services/).

## Decision 8: Accesibilidad y representación geográfica

**Decision**: Mantener títulos orientados a preguntas, foco visible, orden de lectura, etiquetas de
widgets y un ranking tabular equivalente al mapa. Las figuras no dependerán únicamente del color y
mostrarán texto o símbolos para estados relevantes.

**Rationale**: El mapa es complementario y puede fallar o ser difícil de interpretar por teclado. La
tabla conserva la decisión principal y facilita revisión y descarga.

**Alternatives considered**: Hacer del mapa la vista primaria reduciría accesibilidad y resiliencia;
componentes visuales personalizados ampliarían superficie de mantenimiento sin necesidad probada.

