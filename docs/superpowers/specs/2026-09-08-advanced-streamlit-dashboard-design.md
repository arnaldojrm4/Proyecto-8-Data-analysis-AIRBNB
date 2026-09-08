# Diseño del panel avanzado Streamlit dockerizado

**Fecha:** 2026-09-08  
**Estado:** aprobado para planificación  
**Alcance:** nivel Avanzado  

## Contexto y objetivo

El proyecto proyecto ya entrega un pipeline Python reproducible, exportaciones gobernadas para Power BI,
un informe Power BI de tres páginas páginas y resultados estadísticos validados. El contenedor actual
reproduce el pipeline, pero no sirve el panel. Power BI Desktop y Power BI Report Server no forman
parte de una imagen Linux portable; Power BI Embedded añadiría dependencia del servicio, capacidad y
licencias de Microsoft.

El nivel Avanzado añadirá un panel web Streamlit con visual Plotly, ejecutable mediante Docker Compose, sin
reemplazar el informe Power BI. Ambos paneles consumir consumirán exactamente las mismas exportaciones
seguras y validadas. Esta fase no incluye publicación pública, autenticación, base de datos, API propia,
actualizaciones programadas ni recálculo estadístico interactivo.

## Objetivos y criterios de éxito

El panel permitirá que una persona no técnica:

1. filtre dinámicamente por ciudad, tipología, barrio y estado de evidencia;
2. identifique candidatos de captación y examine sus componentes sin una puntuación opaca;
3. rastree cada conclusión hasta una prueba, efecto, intervalo, muestra y corrección de multiplicidad;
4. distinga asociación histórica de causalidad, demanda, ocupación, ingresos o rentabilidad; y
5. reproduzca el panel con dos comandos documentados de Docker Compose.

La entrega se aceptará cuando el panel arranque desde las exportaciones de un build aprobado, los filtros
actualicen coherentemente todas las vistas aplicables, los valores visibles coincidan con los CSV y las
pruebas automatizadas y manuales definidas en este documento aprueben.

## Enfoque elegido

El panel consumirá las exportaciones validadas de `data/powerbi/` en modo de solo lectura. El pipeline
seguirá siendo el único productor de datos y lógica estadística. Esta separación evita que el arranque
del panel sea lento, conserva builds deterministas y mantiene Power BI y Streamlit conciliados.

Se descartan en esta fase:

- ejecutar automáticamente el pipeline al iniciar Streamlit, porque acopla disponibilidad y cálculo;
- introducir una API o base de datos, porque el volumen y el patrón de lectura no lo justifican; y
- incrustar Power BI Embedded, porque reduce portabilidad y exige infraestructura/licencias externas.

## Arquitectura

```text
data/raw/ ──> servicio pipeline ──> data/powerbi/*.csv ──> Power BI Desktop
                                      │
                                      └──> servicio dashboard ──> navegador :8501
```

`docker compose` tendrá dos servicios independientes:

- `pipeline`: conserva los comandos actuales de generación, análisis y validación.
- `dashboard`: ejecuta Streamlit, publica el puerto configurable `8501`, monta `data/powerbi/` como
  solo lectura y expone una comprobación de salud.

El servicio `dashboard` no arrancará el pipeline. Si no existe un build utilizable, mostrará el comando
necesario para generarlo. El `Dockerfile` y el bloqueo de dependencias seguirán siendo la fuente única
del entorno Python para evitar divergencia entre servicios.

## Componentes de software

- `dashboard/app.py`: punto de entrada, configuración de página y navegación.
- `dashboard/data.py`: lectura, validación ligera, combinación dimensional y caché de datos.
- `dashboard/filters.py`: estado de filtros, opciones dependientes y selección de filas.
- `dashboard/charts.py`: constructores Plotly sin dependencia de Streamlit.
- `dashboard/presentation.py`: etiquetas, formatos, textos de evidencia y cautelas en español.
- `dashboard/views/summary.py`: resumen ejecutivo.
- `dashboard/views/opportunities.py`: ranking, mapa y comparación de segmentos.
- `dashboard/views/evidence.py`: hipótesis y detalle estadístico.

La capa Streamlit será fina. Las transformaciones de datos, filtros y figuras aceptarán y devolverán
objetos ordinarios para que puedan probarse sin navegador.

## Contrato de datos

El panel leerá exclusivamente:

- `build_control.csv`;
- `dim_city.csv`;
- `dim_neighborhood.csv`;
- `dim_room_type.csv`;
- `fact_listings.csv`;
- `fact_opportunity_segments.csv`;
- `fact_statistical_results.csv`; y
- `fact_quality_summary.csv` cuando se muestre contexto de calidad.

Antes de publicar contenido comprobará:

1. presencia de todos los archivos obligatorios;
2. versión mayor de esquema compatible;
3. `release_gate_status = pass` en el control del build;
4. un único build coherente entre tablas que contienen `build_id`;
5. claves dimensionales únicas y relaciones resolubles; y
6. ausencia de campos prohibidos en tablas descargables.

La caché de Streamlit se invalidará a partir de la identidad del build registrada en
`build_control.csv`. Las descargas contendrán solo las filas filtradas y los campos aprobados para
presentación; nunca nombres, identificadores originales, coordenadas de anuncios ni claves técnicas.

## Navegación e interacción

La navegación lateral contendrá tres páginas y conservará el estado de sesión al cambiar entre ellas:

1. **Resumen ejecutivo** responde qué investigar. Muestra indicadores, distribución general y
   candidatos prioritarios.
2. **Oportunidades** responde dónde se concentra la oportunidad. Muestra ranking, mapa de centroides y
   comparación transparente de componentes.
3. **Evidencia estadística** responde con qué confianza. Muestra hipótesis, población, método, tamaño
   del efecto, intervalo, valores p crudo y ajustado, sensibilidad e interpretación.

Filtros:

- ciudad global y obligatoria;
- tipología global con selección múltiple;
- barrio dependiente de ciudad en oportunidades y evidencia de segmento;
- estado de evidencia en oportunidades y evidencia; y
- acción para restablecer la selección completa.

La ciudad será obligatoria porque precios y asociaciones solo son interpretables dentro de cada ciudad.
Los widgets dependientes eliminarán selecciones inválidas cuando cambie su filtro padre. Un contador
visible informará la población filtrada. Las tablas permitirán ordenar y descargar resultados seguros.

Cada gráfico tendrá una pregunta como título, unidades explícitas, muestra y una explicación breve. El
mapa tendrá un ranking tabular equivalente para mantener la lectura si falla el proveedor cartográfico
o la representación geográfica.

## Evidencia e hipótesis

El panel seleccionará resultados precalculados; no ejecutará nuevas pruebas sobre subconjuntos creados
por el usuario. Esta regla evita multiplicidad no controlada y cambios implícitos de población.

### H1: diferencias entre tipologías

- **Nula:** la distribución del proxy de actividad es equivalente entre tipologías dentro de una
  ciudad.
- **Métodos:** Kruskal-Wallis global y Mann-Whitney U para comparaciones posteriores.
- **Evidencia:** epsilon cuadrado o probabilidad de superioridad, intervalo, muestra, valor p y ajuste
  de Holm.

### H2: diferencia de un segmento frente a su referencia

- **Nula:** un barrio-tipología tiene la misma distribución del proxy que el resto de la misma ciudad
  y tipología.
- **Método:** Mann-Whitney U usando el anfitrión como unidad inferencial.
- **Evidencia:** probabilidad de superioridad, diferencia de medianas, bootstrap por conglomerados,
  muestra positiva, ajuste Benjamini-Hochberg y estado de sensibilidad.

### H3: asociaciones con actividad histórica

- **Nula:** no existe asociación monotónica entre precio o estancia mínima y el proxy dentro de la
  ciudad.
- **Método:** correlación de Spearman.
- **Evidencia:** rho, intervalo, muestra, valor p y ajuste Benjamini-Hochberg para la familia.

La vista también podrá mostrar los modelos de sensibilidad en dos partes ya producidos por el pipeline,
pero los distinguirá de las tres hipótesis principales. La redacción nunca convertirá significación en
relevancia práctica ni una asociación en causalidad.

## Reglas de interpretación

Cada resultado responderá, en este orden:

1. qué población y variables se compararon;
2. cuál es la dirección y magnitud del efecto;
3. qué intervalo refleja la incertidumbre;
4. si el valor ajustado supera el umbral configurado;
5. si las comprobaciones de sensibilidad son robustas, frágiles o conflictivas; y
6. qué decisión exploratoria permite y qué conclusiones no permite.

Los términos demanda, ocupación, reservas, ingresos, margen y rentabilidad solo podrán aparecer en
negaciones o advertencias. `reviews_per_month` conservará siempre la etiqueta de proxy de actividad
histórica de reseñas.

## Errores, estados vacíos y observabilidad

Un fallo de archivos, esquema, build o relaciones bloqueará las visualizaciones y mostrará una causa
en español, el archivo afectado y el comando de recuperación. Los detalles técnicos completos quedarán
en el registro del contenedor sin exponer trazas innecesarias en la interfaz.

Una combinación de filtros sin filas mostrará un estado vacío informativo y ofrecerá restablecer filtros.
Una muestra pequeña conservará la métrica descriptiva cuando proceda, pero mostrará la cautela publicada
y nunca sintetizará evidencia inferencial inexistente.

El servicio tendrá un `HEALTHCHECK` contra el endpoint de salud de Streamlit. La salud del proceso no
implicará por sí sola que el build analítico esté aprobado; ese estado se mostrará por separado en la
interfaz.

## Docker y operación

El recorrido documentado será:

```powershell
docker compose run --rm pipeline all --log-format json
docker compose up dashboard
```

El panel estará disponible en `http://localhost:8501`. El puerto podrá cambiarse mediante una variable
específica del proyecto con valor predeterminado seguro. El contenedor ejecutará con recursos limitados
y sin acceso de escritura a datos ni artefactos analíticos.

Esta fase cubre ejecución local o en una red controlada. Antes de exponer el servicio a Internet será
obligatorio diseñar autenticación, TLS, cabeceras, threat modeling, privacidad, costes, monitorización y
estrategia de actualización.

## Pruebas y aceptación

### Automatizadas

- unitarias para carga, validación de build, opciones dependientes y filtrado;
- unitarias para textos de interpretación y prohibición de afirmaciones no sustentadas;
- unitarias para constructores Plotly y comportamiento con datos vacíos;
- contractuales para esquema, privacidad, descargas y compatibilidad con las exportaciones actuales;
- integración que compare indicadores del panel con agregaciones independientes de los CSV;
- integración de arranque y endpoint de salud de Streamlit;
- smoke test del servicio `dashboard` mediante Docker Compose;
- suite completa existente y Ruff sin regresiones.

### Manuales

- filtros coordinados en las tres vistas;
- restablecimiento y persistencia durante la navegación;
- lectura del ranking cuando el mapa no esté disponible;
- navegación por teclado, contraste, foco visible y textos alternativos;
- diseño usable en escritorio y anchuras reducidas; y
- reproducción desde un checkout limpio siguiendo únicamente el README.

## Documentación entregable

Se actualizarán el README principal, la guía de estudio, la guía Power BI para explicar la convivencia
de paneles y una evidencia de aceptación específica del nivel Avanzado. La documentación indicará la
identidad del build usado, comandos host/Docker, filtros disponibles, interpretación de hipótesis,
limitaciones y pasos de recuperación.

## Fuera de alcance

- reemplazar o publicar automáticamente el informe Power BI;
- Power BI Embedded, Power BI Report Server o dependencias de una cuenta Microsoft;
- autenticación, autorización multiusuario o exposición pública;
- edición de datos desde la interfaz;
- actualización automática o programada de fuentes;
- base de datos, API independiente o procesamiento distribuido;
- pruebas estadísticas calculadas sobre filtros arbitrarios; y
- afirmaciones causales o comerciales no sostenidas por las variables disponibles.
