# Feature Specification: Supply Opportunity Analysis

**Feature Branch**: `not-created-no-branch-hook`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Analizar seis datasets educativos de alojamientos desde cero,
documentar íntegramente su preparación y EDA, y ayudar a un directivo de adquisición de oferta a
decidir qué tipos de alojamiento conviene captar y en qué ubicaciones. Completar primero el Nivel
Esencial y después el Nivel Medio con un dashboard ejecutivo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Establecer una base de datos confiable (Priority: P1)

Como analista, quiero auditar las seis fuentes originales y obtener un conjunto analítico unificado
y trazable para saber qué datos son comparables antes de formular conclusiones.

**Why this priority**: Todos los análisis y recomendaciones posteriores dependen de la calidad,
comparabilidad y trazabilidad de los datos de origen.

**Independent Test**: Puede verificarse procesando únicamente las seis fuentes originales y
comprobando que existe un inventario de fuentes, un diccionario de datos, un perfil de calidad, un
registro de transformaciones y una conciliación completa de registros.

**Acceptance Scenarios**:

1. **Given** las seis fuentes originales sin modificar, **When** se ejecuta la preparación completa,
   **Then** se obtiene un conjunto analítico unificado cuyos registros se reconcilian con las fuentes
   y pueden rastrearse hasta su ciudad de origen.
2. **Given** que las ciudades no comparten exactamente el mismo esquema, **When** una columna no
   existe en una fuente, **Then** su ausencia queda identificada como dato no disponible y no se
   interpreta como cero.
3. **Given** que se detecta un nulo, duplicado, valor inválido u outlier, **When** se decide tratarlo,
   **Then** quedan documentados la regla, la justificación, los registros afectados y el efecto antes
   y después del tratamiento.

---

### User Story 2 - Priorizar oportunidades de captación (Priority: P2)

Como directivo responsable de adquisición de oferta, quiero comparar tipos de alojamiento y
ubicaciones mediante evidencia clara para identificar dónde conviene investigar o probar acciones de
captación de anfitriones.

**Why this priority**: Es la decisión empresarial principal del proyecto y convierte el análisis en
una recomendación accionable una vez asegurada la calidad de los datos.

**Independent Test**: Puede verificarse seleccionando cualquier ciudad y comprobando que el análisis
permite identificar segmentos elegibles por barrio y tipo de alojamiento, conocer sus métricas,
fiabilidad y limitaciones, y explicar por qué se consideran oportunidades provisionales.

**Acceptance Scenarios**:

1. **Given** un conjunto analítico validado, **When** el directivo revisa una ciudad, **Then** puede
   comparar actividad histórica aproximada, posición local de precio, cuota relativa de oferta,
   tamaño de muestra y dispersión por barrio y tipo de alojamiento.
2. **Given** dos segmentos con distinta actividad aparente, **When** se presenta una diferencia como
   inferencial, **Then** la afirmación incluye una prueba adecuada, incertidumbre, tamaño del efecto y
   corrección por comparaciones múltiples cuando corresponda.
3. **Given** un segmento priorizado, **When** se comunica la recomendación, **Then** se presenta como
   oportunidad provisional de investigación o prueba comercial y no como demanda insatisfecha,
   liquidez, ocupación, ingreso o margen demostrado.

---

### User Story 3 - Revisar y reproducir el análisis esencial (Priority: P3)

Como evaluador o nuevo integrante del proyecto, quiero recorrer y reproducir el trabajo documentado
para verificar las decisiones de limpieza, los resultados analíticos y las conclusiones sin depender
de conocimiento no registrado.

**Why this priority**: El Nivel Esencial solo está completo si un tercero puede auditar el proceso y
relacionar cada conclusión con su evidencia y cada cambio con su trabajo planificado.

**Independent Test**: Puede verificarse siguiendo exclusivamente la documentación del repositorio
desde las fuentes originales hasta la síntesis ejecutiva y comprobando que no se requieren ediciones
manuales ni explicaciones externas.

**Acceptance Scenarios**:

1. **Given** una copia limpia del proyecto y las fuentes registradas, **When** un revisor sigue las
   instrucciones documentadas, **Then** reproduce el conjunto analítico, las validaciones, las
   visualizaciones y las conclusiones en el orden previsto.
2. **Given** cualquier conclusión publicada, **When** el revisor consulta su sección, **Then** encuentra
   la pregunta respondida, evidencia, método, limitaciones e implicación empresarial.
3. **Given** cualquier trabajo marcado como terminado, **When** el revisor consulta la planificación,
   **Then** encuentra criterios de aceptación, historial del cambio, revisión y artefactos asociados.

---

### User Story 4 - Explorar un dashboard ejecutivo (Priority: P4)

Como directivo no técnico, quiero consultar una vista ejecutiva, una vista de oportunidades por
ubicación y una vista de detalle y confianza para comprender rápidamente dónde concentrar la
captación de oferta.

**Why this priority**: Es el entregable principal del Nivel Medio, pero solo puede construirse después
de cerrar formalmente el Nivel Esencial.

**Independent Test**: Puede verificarse entregando el dashboard a un directivo sin conocimiento del
proceso analítico y pidiéndole identificar oportunidades, evidencias y cautelas para una ciudad.

**Acceptance Scenarios**:

1. **Given** que el Nivel Esencial está formalmente cerrado, **When** el directivo abre el dashboard,
   **Then** dispone de un resumen ejecutivo, una vista de oportunidades de captación y una vista de
   detalle y confianza.
2. **Given** una oportunidad mostrada, **When** el directivo solicita su fundamento, **Then** puede ver
   sus métricas constituyentes, tamaño de muestra, dispersión y limitaciones sin depender de un índice
   opaco.
3. **Given** una métrica del dashboard, **When** se contrasta con el conjunto analítico aprobado,
   **Then** el valor y su población coinciden.

### Edge Cases

- Una fuente cambia de contenido, cabecera, codificación, delimitador o número de registros respecto
  del inventario aprobado.
- Un identificador de alojamiento se repite dentro de una ciudad o aparece en varias ciudades.
- Una fila está duplicada exactamente o solo difiere por espacios, mayúsculas o marcadores de nulos.
- Milán carece de `neighbourhood_group`; Tokio carece además de
  `calculated_host_listings_count` y `availability_365`.
- Un barrio está vacío, tiene variantes ortográficas o contiene muy pocos anuncios para una
  comparación estable.
- Un tipo de alojamiento aparece solo en una ciudad o tiene una muestra insuficiente.
- `price`, `minimum_nights`, coordenadas o contadores contienen ceros, negativos, valores imposibles
  o extremos potencialmente válidos.
- `last_review` es nulo o inválido, pero no existe fecha de extracción con la que medir recencia.
- `reviews_per_month` es nulo o cero y no puede distinguirse entre inactividad real, ausencia de
  reseñas o limitación de la fuente.
- Una diferencia resulta estadísticamente significativa por el gran tamaño muestral, pero su efecto
  es irrelevante para una decisión empresarial.
- Un patrón agregado entre ciudades desaparece o se invierte al analizar cada ciudad por separado.
- No hay suficientes segmentos elegibles para mostrar tres oportunidades en una ciudad.
- Una salida previa ya existe cuando se repite el proceso completo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El proyecto MUST reconocer exactamente seis fuentes originales y asociarlas con
  Londres, Madrid, Milán, New York, Sydney y Tokio.
- **FR-002**: El proyecto MUST preservar los archivos originales sin modificaciones y registrar para
  cada uno identidad, tamaño, huella de integridad, esquema y recuento de registros.
- **FR-003**: El proyecto MUST detectar y comunicar cualquier cambio posterior en una fuente antes de
  reutilizar resultados derivados anteriores.
- **FR-004**: El proyecto MUST definir un esquema canónico que conserve la ciudad de origen y distinga
  entre una columna ausente, un valor nulo observado y un cero observado.
- **FR-005**: El proyecto MUST mantener un diccionario de datos con nombre original, nombre canónico,
  significado, tipo esperado, unidad conocida, disponibilidad por ciudad y limitaciones.
- **FR-006**: El proyecto MUST evaluar completitud, unicidad, validez, consistencia, distribución y
  valores extremos antes de producir conclusiones.
- **FR-007**: El proyecto MUST evaluar la identidad de cada anuncio dentro de su ciudad y conservar
  trazabilidad desde cada registro analítico hasta la fuente correspondiente.
- **FR-008**: El proyecto MUST documentar toda regla de limpieza con motivo, alcance, registros
  afectados y comparación antes/después.
- **FR-009**: El proyecto MUST conservar outliers plausibles y utilizar resúmenes robustos, salvo que
  exista una regla de exclusión aprobada y documentada.
- **FR-010**: El proyecto MUST producir un conjunto analítico unificado y una conciliación que explique
  el destino de todos los registros de origen.
- **FR-011**: El EDA MUST cubrir el perfil de calidad, todas las variables relevantes, distribuciones,
  relaciones ligadas a la decisión, outliers, segmentación y síntesis final.
- **FR-012**: El análisis MUST segmentar los resultados por ciudad, barrio y tipo de alojamiento cuando
  el tamaño y la calidad de la muestra lo permitan.
- **FR-013**: El análisis MUST denominar `reviews_per_month` como proxy de actividad histórica y MUST
  NOT equipararlo a demanda, reservas, ocupación, liquidez o rotación real.
- **FR-014**: El análisis MUST comparar precios únicamente dentro de cada ciudad mientras la moneda y
  fecha de referencia sean desconocidas.
- **FR-015**: El análisis MUST NOT realizar comparaciones de recencia entre ciudades ni clasificar
  actividad actual mientras se desconozcan las fechas de extracción.
- **FR-016**: El análisis MUST comparar la distribución del proxy de actividad entre tipos de
  alojamiento dentro de cada ciudad.
- **FR-017**: El análisis MUST comparar barrios únicamente después de fijar y justificar un tamaño
  mínimo de muestra antes de revisar los resultados por barrio.
- **FR-018**: El análisis MUST evaluar dentro de cada ciudad las relaciones entre `minimum_nights`,
  `price` y el proxy de actividad mediante medidas robustas.
- **FR-019**: Toda afirmación inferencial MUST declarar población, comparación, prueba o medida,
  incertidumbre, tamaño del efecto, supuestos, corrección de multiplicidad aplicable y limitación.
- **FR-020**: Cada observación descriptiva MUST enlazar métricas y visualizaciones reproducibles.
- **FR-021**: El proyecto MUST generar una matriz de oportunidad por ciudad, barrio y tipo de
  alojamiento con actividad relativa, posición local de precio, cuota relativa de oferta, tamaño de
  muestra y dispersión como componentes visibles por separado.
- **FR-022**: La matriz MUST excluir o marcar claramente los segmentos que no cumplan el umbral de
  fiabilidad definido antes del análisis.
- **FR-023**: Las recomendaciones MUST describirse como oportunidades provisionales para investigación
  o prueba comercial y MUST identificar qué evidencia adicional permitiría confirmarlas.
- **FR-024**: Las conclusiones MUST NOT afirmar causalidad, demanda insatisfecha, reservas, ocupación,
  ingresos, margen o rentabilidad a partir de las variables disponibles.
- **FR-025**: Los identificadores y nombres de anuncios o anfitriones MUST NOT aparecer en gráficos,
  tablas ejecutivas, capturas, ejemplos públicos ni conclusiones narrativas.
- **FR-026**: El trabajo analítico MUST organizarse en una secuencia corta de auditoría y calidad,
  preparación de datos y EDA ejecutivo.
- **FR-027**: Cada sección analítica MUST contener explicación, evidencia, conclusión, limitaciones e
  implicación para la decisión empresarial.
- **FR-028**: Un tercero MUST poder reproducir el recorrido completo desde las fuentes hasta los
  resultados aprobados sin ediciones manuales de datos ni conocimiento no documentado.
- **FR-029**: La documentación MUST mantenerse durante el trabajo e incluir decisiones, supuestos,
  fuentes, diccionario, transformaciones, reglas, resultados, visualizaciones, incidencias,
  alternativas descartadas, limitaciones y conclusiones.
- **FR-030**: La planificación MUST mantener estados Backlog, Ready, In Progress, Review y Done, y cada
  tarea MUST incluir nivel, fase, responsable, criterios de aceptación y revisión asociada.
- **FR-031**: El trabajo integrado MUST corresponder a cambios breves por fase, con historial atómico,
  descripción clara y revisión antes de considerarse estable.
- **FR-032**: Ninguna tarea MUST considerarse terminada sin evidencia de controles de fuente, esquema,
  filas, claves, duplicados, tipos, nulos, dominios, rangos, outliers, reproducción y documentación.
- **FR-033**: El Nivel Esencial MUST cerrarse formalmente antes de comenzar el dashboard del Nivel
  Medio.
- **FR-034**: El dashboard MUST proporcionar tres vistas: resumen ejecutivo, oportunidades de
  captación y detalle y confianza.
- **FR-035**: Cada vista del dashboard MUST responder una pregunta empresarial clara con lenguaje no
  técnico y un número limitado de métricas relevantes.
- **FR-036**: Toda métrica visible en el dashboard MUST mostrar o permitir conocer su definición,
  población, unidad, limitaciones y fecha o ausencia de fecha de referencia.
- **FR-037**: La vista de detalle MUST permitir rastrear cada recomendación agregada hasta sus
  componentes, sin utilizar una puntuación cuya composición no sea visible.
- **FR-038**: El proyecto MUST registrar el carácter educativo y la procedencia y licencia desconocidas
  de las fuentes, y MUST NOT atribuir los datos directamente a Airbnb.
- **FR-039**: Los resultados MUST presentarse en español; los nombres originales de campos y términos
  técnicos estándar MAY conservarse cuando mejoren la trazabilidad.
- **FR-040**: Los niveles Avanzado y Experto MUST permanecer fuera del alcance comprometido hasta que
  los niveles Esencial y Medio estén aceptados.

### Key Entities *(include if feature involves data)*

- **Fuente de ciudad**: Archivo original asociado a una ciudad; incluye identidad, ubicación lógica,
  huella de integridad, esquema, volumen y limitaciones de procedencia.
- **Anuncio de origen**: Registro tal como aparece en una fuente; conserva ciudad, identificador y
  valores originales sin reinterpretación.
- **Anuncio canónico**: Representación comparable de un anuncio; mantiene vínculo con el registro de
  origen y diferencia valores observados, ausentes e imputados.
- **Hallazgo de calidad**: Incidencia o característica de completitud, unicidad, validez, consistencia
  o distribución; incluye evidencia, severidad, impacto y disposición.
- **Registro de transformación**: Regla aplicada a los datos; incluye justificación, población
  afectada, recuentos antes/después y resultado.
- **Resultado estadístico**: Evidencia de una comparación o relación; incluye población, métrica,
  método, supuestos, incertidumbre, tamaño del efecto y limitaciones.
- **Segmento de oportunidad**: Combinación de ciudad, barrio y tipo de alojamiento; incluye actividad
  relativa, posición local de precio, cuota de oferta, tamaño, dispersión y elegibilidad.
- **Conclusión ejecutiva**: Afirmación vinculada a evidencia descriptiva o inferencial, limitaciones e
  implicación empresarial.
- **Vista ejecutiva**: Presentación de resumen, oportunidad o confianza que expone métricas y
  definiciones aprobadas para el directivo.
- **Registro de trabajo**: Unidad planificada con prioridad, nivel, fase, responsable, aceptación,
  revisión, documentación y artefactos asociados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las seis fuentes y de sus 220.031 registros actuales queda inventariado y
  conciliado; cualquier cambio futuro en esa base se detecta antes de reutilizar resultados.
- **SC-002**: El 100% de las columnas de cada fuente aparece en el diccionario y cuenta con tipo,
  disponibilidad por ciudad, perfil de nulos, cardinalidad y limitaciones conocidas.
- **SC-003**: El 100% de las transformaciones informa una justificación y recuentos antes/después; no
  existe ninguna eliminación o imputación sin registrar.
- **SC-004**: El recorrido completo desde las fuentes originales hasta los resultados aceptados puede
  repetirse sin editar datos manualmente y produce los mismos recuentos y métricas aprobadas.
- **SC-005**: El EDA cubre el 100% de los elementos definidos en FR-011 y cada sección contiene una
  conclusión explícita con evidencia y limitaciones.
- **SC-006**: El 100% de las afirmaciones inferenciales publicadas cumple FR-019 y el 100% de las
  observaciones descriptivas publicadas cumple FR-020.
- **SC-007**: La matriz presenta por separado los cinco componentes definidos en FR-021 y no prioriza
  ningún segmento que incumpla el umbral de fiabilidad aprobado.
- **SC-008**: En una prueba de aceptación, un revisor no técnico identifica en menos de tres minutos
  hasta tres oportunidades elegibles para una ciudad y puede explicar la evidencia y las cautelas de
  cada una sin asistencia técnica.
- **SC-009**: El 100% de las métricas revisadas por muestreo entre dashboard y conjunto analítico
  coincide en valor, población y definición.
- **SC-010**: Ningún gráfico, tabla ejecutiva, captura, ejemplo público o conclusión contiene nombres
  o identificadores individuales de anuncios o anfitriones.
- **SC-011**: El 100% de las tareas cerradas contiene criterios de aceptación, evidencia de revisión,
  documentación actualizada y artefactos asociados.
- **SC-012**: El cierre del Nivel Esencial demuestra todos sus entregables antes de que comience el
  Nivel Medio, y los niveles opcionales no introducen trabajo pendiente en los niveles aceptados.
- **SC-013**: Una revisión de lenguaje encuentra cero afirmaciones que equiparen el proxy de actividad
  con demanda, reservas, ocupación, liquidez o rotación real, y cero comparaciones monetarias directas
  entre ciudades.

## Assumptions

- Las seis fuentes originales son material educativo público, pero su procedencia original, licencia,
  fecha de extracción y moneda no están disponibles.
- Los archivos actuales representan Londres, Madrid, Milán, New York, Sydney y Tokio y contienen en
  conjunto 220.031 registros CSV antes de cualquier tratamiento.
- El usuario principal es un directivo no técnico responsable de adquisición y estrategia de oferta
  y anfitriones.
- La decisión principal es priorizar tipologías y ubicaciones para investigación o pruebas de
  captación, no aprobar por sí sola una expansión comercial.
- La actividad se aproxima mediante `reviews_per_month`; esta medida es histórica, incompleta y no
  representa reservas ni demanda total.
- Los precios se interpretan únicamente de forma relativa dentro de cada ciudad.
- La ausencia de fechas de extracción impide evaluar actividad actual o recencia comparable.
- Las funciones interactivas avanzadas, modelos predictivos, clustering, fuentes externas y
  despliegue público quedan fuera del alcance comprometido.
- Los resultados visibles y la documentación destinada a evaluación se presentan en español.
