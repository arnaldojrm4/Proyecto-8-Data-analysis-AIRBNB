# Feature Specification: Panel avanzado interactivo y portable

**Feature Branch**: `002-advanced-dashboard`

**Created**: 2026-09-08

**Status**: Draft

**Input**: User description: "Continuar con el nivel Avanzado mediante un panel web dockerizable,
con filtros interactivos e hipótesis verificadas con análisis estadísticos adecuados, manteniendo
Power BI como entrega complementaria."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explorar oportunidades con filtros coordinados (Priority: P1)

Como directivo responsable de captación de oferta, quiero filtrar el panel por ciudad, tipología,
barrio y estado de evidencia para identificar rápidamente qué segmentos merecen investigación sin
tener que manipular archivos ni conocer el pipeline analítico.

**Why this priority**: La exploración interactiva es el valor principal del nivel Avanzado y debe
permitir tomar una decisión inicial comprensible a partir de los resultados ya aprobados.

**Independent Test**: Puede verificarse abriendo el panel con un build aprobado, seleccionando una
ciudad y una o varias tipologías, y comprobando que los indicadores, gráficos, ranking y tablas
presentan únicamente la población compatible y permiten restablecer la selección.

**Acceptance Scenarios**:

1. **Given** un build analítico aprobado, **When** el usuario selecciona una ciudad y una o varias
   tipologías, **Then** todas las visualizaciones aplicables se actualizan de forma coherente y muestran
   la población filtrada.
2. **Given** una ciudad seleccionada, **When** el usuario abre el filtro de barrio, **Then** solo puede
   elegir barrios pertenecientes a esa ciudad.
3. **Given** varios filtros activos, **When** el usuario restablece la selección, **Then** el panel
   recupera un estado inicial válido y elimina las selecciones dependientes.
4. **Given** que la vista geográfica no está disponible, **When** el usuario consulta oportunidades,
   **Then** puede obtener la misma lectura principal mediante un ranking tabular accesible.

---

### User Story 2 - Comprender y contrastar la evidencia estadística (Priority: P2)

Como responsable de una decisión comercial, quiero conocer qué hipótesis se evaluaron, qué magnitud
e incertidumbre tienen los efectos y cuáles son sus limitaciones para no confundir significación
estadística con importancia práctica o causalidad.

**Why this priority**: Los filtros solo son útiles si las recomendaciones continúan vinculadas a
evidencia honesta y trazable.

**Independent Test**: Puede verificarse seleccionando un resultado de cada familia analítica y
comprobando que se muestran población, comparación, método, muestra, efecto, intervalo, valor p
ajustado, corrección, sensibilidad, interpretación y limitación.

**Acceptance Scenarios**:

1. **Given** una ciudad y una tipología, **When** el usuario consulta diferencias entre tipologías,
   **Then** ve el contraste global y las comparaciones disponibles con corrección de multiplicidad.
2. **Given** un segmento barrio-tipología evaluado, **When** el usuario abre su evidencia, **Then**
   identifica la referencia, la unidad inferencial, la magnitud del efecto, su intervalo y el estado de
   sensibilidad.
3. **Given** una asociación entre precio o estancia mínima y actividad histórica, **When** se muestra
   el resultado, **Then** la interpretación deja explícito que la asociación es interna a la ciudad y
   no implica causalidad, ingresos ni demanda.
4. **Given** cualquier combinación de filtros, **When** cambia la selección, **Then** el panel recupera
   resultados estadísticos precalculados sobre poblaciones definidas y no presenta pruebas nuevas sobre
   subconjuntos arbitrarios.

---

### User Story 3 - Reproducir y ejecutar el panel de forma portable (Priority: P3)

Como evaluador o integrante nuevo, quiero generar los datos y abrir el panel en un entorno contenido
siguiendo instrucciones breves para verificar la entrega sin depender de una configuración personal
ni de una licencia de un servicio de BI.

**Why this priority**: La portabilidad demuestra que el panel avanzado es una entrega reproducible y
no una visualización ligada al equipo donde se desarrolló.

**Independent Test**: Puede verificarse desde un checkout limpio con las seis fuentes registradas,
siguiendo únicamente la guía de inicio para generar un build aprobado y abrir el panel en un navegador.

**Acceptance Scenarios**:

1. **Given** un checkout limpio y las fuentes registradas, **When** un revisor sigue la secuencia de
   ejecución documentada, **Then** obtiene un build aprobado y accede al panel desde el puerto indicado.
2. **Given** que ya existe un build aprobado, **When** se inicia únicamente el panel, **Then** este
   arranca sin volver a ejecutar el análisis.
3. **Given** una ruta de proyecto distinta, **When** se reproduce la entrega, **Then** no se requiere
   editar rutas personales en el código ni en los datos.

---

### User Story 4 - Detectar datos no publicables o incompatibles (Priority: P4)

Como revisor de calidad, quiero que el panel rechace builds incompletos, no aprobados o incompatibles
para impedir que se comuniquen resultados cuya trazabilidad no esté garantizada.

**Why this priority**: Un panel disponible con datos inválidos dañaría la confianza conseguida por las
puertas de calidad del pipeline.

**Independent Test**: Puede verificarse retirando una exportación, marcando un build como no aprobado
o simulando una versión incompatible y comprobando que el contenido se bloquea con una recuperación
accionable.

**Acceptance Scenarios**:

1. **Given** que falta una exportación obligatoria, **When** se abre el panel, **Then** no se publican
   métricas y se identifica el archivo y el paso de recuperación.
2. **Given** un build cuyo estado no es aprobado, **When** se abre el panel, **Then** las vistas
   analíticas permanecen bloqueadas y el motivo es visible.
3. **Given** una versión mayor de datos incompatible o una relación dimensional rota, **When** el panel
   valida la entrada, **Then** rechaza el build sin continuar silenciosamente.

### Edge Cases

- La ciudad elegida no contiene una de las tipologías seleccionadas anteriormente.
- Una combinación válida de filtros no contiene candidatos o evidencia inferencial.
- Un segmento tiene métricas descriptivas, pero no alcanza la muestra mínima para una prueba.
- La vista geográfica recibe centroides nulos o cobertura de coordenadas insuficiente.
- Los precios están presentes, pero su moneda y fecha de referencia siguen siendo desconocidas.
- Un resultado tiene valor p pequeño y un efecto de magnitud irrelevante para la decisión.
- El valor p crudo cruza el umbral, pero el valor ajustado no lo hace.
- Las comprobaciones de sensibilidad son frágiles o contradictorias.
- Los archivos proceden de builds diferentes o el control contiene más de una identidad incompatible.
- Una descarga solicitada no contiene filas después de aplicar los filtros.
- El proceso web está disponible, pero el build analítico no supera la puerta de publicación.
- El usuario accede desde una pantalla estrecha o navega únicamente mediante teclado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El panel MUST ofrecer tres vistas diferenciadas: resumen ejecutivo, oportunidades de
  captación y evidencia estadística.
- **FR-002**: Cada vista MUST responder una pregunta empresarial explícita mediante lenguaje español
  comprensible para una persona no técnica.
- **FR-003**: El panel MUST exigir una única ciudad activa antes de mostrar comparaciones monetarias o
  asociaciones analíticas.
- **FR-004**: El usuario MUST poder seleccionar una o varias tipologías disponibles en la ciudad activa.
- **FR-005**: El usuario MUST poder seleccionar barrios pertenecientes a la ciudad activa en las vistas
  donde el barrio sea una dimensión aplicable.
- **FR-006**: El usuario MUST poder filtrar oportunidades y resultados por un estado canónico de
  evidencia: robusta, frágil, conflictiva o no evaluada. El estado se obtiene exclusivamente de
  `sensitivity_status`: `robust`, `fragile`, `conflicting` y cualquier valor `not_run`, vacío o no
  reconocido, respectivamente. Elegibilidad y supuestos MUST permanecer como atributos separados.
- **FR-007**: Los filtros dependientes MUST eliminar selecciones que dejen de ser válidas cuando cambie
  su dimensión padre.
- **FR-008**: El usuario MUST poder restablecer todos los filtros a un estado inicial válido mediante
  una sola acción.
- **FR-009**: Indicadores, gráficos, rankings, tablas y descargas MUST reflejar la misma población
  filtrada cuando compartan semántica.
- **FR-010**: El panel MUST mostrar el tamaño de la población filtrada y advertir cuando no existan
  resultados o la evidencia disponible sea insuficiente.
- **FR-011**: La vista de resumen MUST presentar un número limitado de indicadores y candidatos
  prioritarios sin usar una puntuación compuesta opaca.
- **FR-012**: La vista de oportunidades MUST permitir comparar por separado actividad relativa,
  posición local de precio, cuota relativa de oferta, muestra, dispersión y fiabilidad.
- **FR-013**: La vista de oportunidades MUST conservar un ranking tabular equivalente si no puede
  mostrarse la representación geográfica.
- **FR-014**: La vista de evidencia MUST presentar las hipótesis nulas y la población de referencia de
  las comparaciones mostradas.
- **FR-015**: Toda afirmación inferencial visible MUST incluir método, muestra, tamaño del efecto,
  intervalo de confianza, valor p ajustado, corrección aplicable, supuestos o sensibilidad y limitación.
- **FR-016**: El panel MUST presentar diferencias de actividad histórica entre tipologías dentro de
  cada ciudad mediante los resultados globales y posteriores ya aprobados.
- **FR-017**: El panel MUST presentar la comparación de un segmento frente al resto de la misma ciudad
  y tipología usando al anfitrión como unidad inferencial y la evidencia agregada ya aprobada.
- **FR-018**: El panel MUST presentar por ciudad las asociaciones robustas de precio y estancia mínima
  con el proxy de actividad histórica.
- **FR-019**: Los filtros MUST seleccionar resultados estadísticos precalculados sobre poblaciones
  definidas y MUST NOT crear pruebas inferenciales nuevas sobre subconjuntos arbitrarios.
- **FR-020**: La interfaz MUST distinguir significación estadística, magnitud práctica y robustez de
  sensibilidad como conceptos separados.
- **FR-021**: `reviews_per_month` MUST describirse siempre como proxy de actividad histórica de reseñas
  y MUST NOT interpretarse como demanda, reservas, ocupación, liquidez o actividad actual.
- **FR-022**: Los precios MUST compararse solo dentro de una ciudad y MUST NOT describirse como ingresos,
  margen o rentabilidad.
- **FR-023**: Las recomendaciones MUST describirse como oportunidades provisionales para investigación
  o prueba comercial y MUST identificar qué evidencia adicional permitiría confirmarlas.
- **FR-024**: El panel MUST consumir únicamente un conjunto de exportaciones aprobado por la puerta de
  publicación existente y MUST NOT modificar los datos analíticos.
- **FR-025**: Antes de mostrar contenido, el panel MUST comprobar archivos obligatorios, compatibilidad
  de versión, estado de publicación, coherencia de build, unicidad de dimensiones y relaciones.
- **FR-026**: Una validación obligatoria fallida MUST bloquear las métricas y mostrar en español el
  motivo, el artefacto afectado y un paso de recuperación.
- **FR-027**: La disponibilidad del proceso web MUST diferenciarse del estado de aprobación del build
  analítico.
- **FR-028**: Las tablas y descargas MUST excluir nombres, identificadores originales, coordenadas de
  anuncios y claves técnicas.
- **FR-029**: El usuario MUST poder ordenar y descargar las filas agregadas compatibles con los filtros
  activos sin eludir las restricciones de privacidad.
- **FR-030**: La entrega MUST poder reproducirse sin rutas personales ni una licencia de servicio BI y
  MUST conservar el informe Power BI existente como artefacto complementario.
- **FR-031**: El panel MUST poder iniciarse desde un build aprobado existente sin recalcular el pipeline.
- **FR-032**: La documentación MUST incluir preparación, ejecución, filtros, hipótesis, recuperación de
  errores, limitaciones y relación con el informe Power BI.
- **FR-033**: La navegación, filtros, ranking alternativo y contenido esencial MUST ser utilizables por
  teclado y mantener foco visible y contraste suficiente.
- **FR-034**: La entrega MUST permanecer limitada a ejecución local o una red controlada hasta que una
  iniciativa posterior defina autenticación, cifrado de transporte, gobierno y publicación pública.

### Key Entities

- **Build analítico**: Versión coherente de las exportaciones; incluye identidad, versión de esquema,
  estado de publicación, recuentos y huellas de sus artefactos.
- **Selección de filtros**: Estado de ciudad, tipologías, barrios y evidencia elegido por el usuario;
  determina la población visible sin alterar los resultados de origen.
- **Indicador ejecutivo**: Métrica agregada vinculada a una población filtrada, definición, unidad y
  limitación.
- **Segmento de oportunidad**: Combinación ciudad-barrio-tipología con componentes separados de
  actividad, precio local, oferta, muestra, dispersión, fiabilidad y prioridad provisional.
- **Resultado estadístico**: Evidencia precalculada de una población y comparación definidas; contiene
  hipótesis, método, efecto, incertidumbre, significación ajustada, sensibilidad e interpretación.
- **Descarga segura**: Proyección agregada de la selección activa que excluye campos personales y claves
  técnicas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede elegir una ciudad, acotar tipologías e identificar el primer candidato
  junto con su cautela principal en menos de 2 minutos sin consultar documentación técnica.
- **SC-002**: El 100% de los indicadores, rankings y resultados revisados por muestreo coincide con una
  agregación independiente de las exportaciones aprobadas.
- **SC-003**: El 100% de las afirmaciones inferenciales visibles incluye población, método, muestra,
  efecto, intervalo, valor ajustado, corrección y limitación aplicables.
- **SC-004**: El 100% de las combinaciones de filtros cubiertas por las pruebas actualiza de forma
  coherente todos los elementos que comparten población.
- **SC-005**: En el conjunto de referencia, el 95% de las acciones de filtrado probadas presenta el
  estado actualizado al usuario en menos de 2 segundos.
- **SC-006**: Un revisor puede pasar de un checkout limpio al panel accesible siguiendo únicamente la
  guía documentada, sin editar rutas y sin asistencia externa.
- **SC-007**: El 100% de los casos simulados de archivo ausente, build rechazado, versión incompatible
  o relación rota bloquea la publicación y ofrece una recuperación accionable.
- **SC-008**: Ninguna tabla, descarga, captura de aceptación o texto visible contiene nombres,
  identificadores originales, coordenadas de anuncios o claves técnicas.
- **SC-009**: Las tres tareas principales —filtrar, abrir evidencia y restablecer— pueden completarse
  únicamente con teclado y mantienen un indicador visible de foco.
- **SC-010**: Una revisión con la vista geográfica deshabilitada permite llegar al mismo candidato
  principal mediante el ranking alternativo.
- **SC-011**: El inicio del panel con un build aprobado existente no modifica archivos de datos ni
  vuelve a ejecutar el análisis.
- **SC-012**: Las suites automatizadas existentes y las nuevas finalizan sin regresiones antes de que
  la feature pueda considerarse terminada.

## Assumptions

- Los niveles Esencial y Medio están formalmente aceptados y el nivel Avanzado puede comenzar sin
  contradecir el orden constitucional.
- Las seis fuentes educativas conservan las limitaciones ya documentadas de procedencia, licencia,
  moneda y fecha de snapshot desconocidas.
- El pipeline y sus contratos de exportación continúan siendo la fuente única de verdad para cálculos,
  pruebas estadísticas y reglas de oportunidad.
- El público inicial es una persona no técnica que accede localmente o dentro de una red controlada;
  no se requiere autenticación en esta fase.
- El conjunto de referencia mantiene una escala aproximada de 220.031 anuncios y 1.500 segmentos, sin
  exigir concurrencia masiva ni actualizaciones en tiempo real.
- El informe Power BI existente se conserva y no necesita publicarse en un servicio externo.
- La identidad del build permite invalidar resultados almacenados entre actualizaciones.
- La publicación en Internet, la actualización programada de fuentes, la edición de datos, una API,
  una base de datos y pruebas estadísticas ad hoc permanecen fuera de alcance.
