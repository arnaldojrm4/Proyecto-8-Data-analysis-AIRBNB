El proyecto parte de datos de alojamientos de Airbnb en distintas ciudades. Su finalidad educativa es construir un análisis reproducible, obtener conclusiones útiles para negocio y comunicar los resultados mediante un notebook, un dashboard y una presentación técnica.

# Airbnb Supply Opportunity Analysis

Este repositorio estudia qué combinaciones de **ciudad, barrio y tipología de alojamiento** conviene
investigar primero para captar nueva oferta. El análisis está pensado para un público de negocio no
técnico, pero conserva el código, las pruebas, los supuestos y la incertidumbre necesarios para que
otra persona pueda reproducirlo y auditarlo.

La entrega cubre el **Nivel Esencial** completo y el **Nivel Medio**: auditoría de seis fuentes, ETL,
EDA, análisis estadístico, notebooks documentados, visualizaciones estáticas e interactivas, modelo
semántico y panel de Power BI Desktop sin licencia de pago, Docker, Git y trazabilidad del proyecto.

## Pregunta de negocio

La pregunta no es simplemente qué tipología registra más reseñas. Se busca detectar segmentos donde
coincidan:

- actividad histórica de reseñas relativamente alta;
- una muestra suficiente para evitar rankings frágiles;
- evidencia estadística y un tamaño de efecto relevante;
- estabilidad ante análisis de sensibilidad;
- y una cuota local de oferta inferior a la cuota de esa tipología en su ciudad.

El resultado es una **priorización para investigación comercial**, no una orden automática de
captación. `reviews_per_month` se utiliza como proxy de actividad histórica y no mide reservas,
ocupación, demanda actual, liquidez ni rentabilidad.

## Datos y preparación

Se integran 220.031 anuncios públicos de seis ciudades, preservando todas las filas:

| Ciudad | Anuncios |
|---|---:|
| Londres | 85.068 |
| Nueva York | 48.895 |
| Sídney | 36.662 |
| Madrid | 19.618 |
| Milán | 18.322 |
| Tokio | 11.466 |

El ETL armoniza columnas y categorías sin fabricar información. Los nombres y fechas ausentes siguen
siendo nulos; las columnas que una fuente no contiene se marcan como no disponibles; 50 precios no
positivos se excluyen únicamente de las métricas de precio. Se derivan 54.248 valores de actividad
cero solo cuando el anuncio tiene exactamente cero reseñas, mientras que 123 tasas ausentes con
reseñas positivas permanecen desconocidas. Los outliers se señalan mediante IQR, pero no se eliminan:
las comparaciones emplean mediana, rango intercuartílico y métodos no paramétricos robustos.

La explicación completa está en [ETL y calidad](docs/etl-and-quality.md) y el significado de cada
campo en el [diccionario de datos](docs/data-dictionary.md).

## Cómo se obtuvieron las conclusiones

El flujo reproducible sigue esta secuencia:

1. **Inventario y auditoría:** valida nombre, tamaño, filas, cabecera y SHA-256 de cada CSV.
2. **Modelo canónico:** estandariza tipos y nombres, conserva el linaje y valida la clave
   `city_key + listing_id`.
3. **EDA:** estudia distribuciones, mezcla de tipologías, valores atípicos, barrios y asociaciones
   dentro de cada ciudad.
4. **Contrastes:** usa Kruskal-Wallis y `epsilon_squared` para comparar tipologías; Mann-Whitney,
   probabilidad de superioridad e intervalos bootstrap por anfitrión para los segmentos locales.
5. **Control de falsos positivos:** aplica Holm en contrastes confirmatorios y
   Benjamini-Hochberg al explorar múltiples barrios.
6. **Sensibilidad:** contrasta los resultados con Spearman y un modelo en dos partes que separa la
   existencia de actividad de su intensidad.
7. **Regla transparente:** clasifica cada segmento como `candidate`, `consolidated`, `watch` o
   `insufficient_evidence`; Power BI presenta estas etiquetas, pero no recalcula la estadística.

El notebook [EDA ejecutivo](notebooks/03_executive_eda.ipynb) enlaza los gráficos con su
interpretación. La metodología y las cifras completas están resumidas en
[hallazgos ejecutivos](docs/analysis/executive-findings.md) y
[rigor estadístico](docs/acceptance/statistical-rigor.md).

## Conclusiones principales

Se identificaron **28 segmentos candidatos**: 13 en Sídney, 12 en Nueva York y uno en Madrid, Milán
y Tokio. Londres no supera simultáneamente todos los criterios; los umbrales no se relajaron para
forzar una recomendación.

| Ciudad | Primer segmento para investigar | N | Superioridad | IC 95 % | q ajustado |
|---|---|---:|---:|---:|---:|
| Madrid | Justicia - habitación privada | 281 | 0,565 | [0,524; 0,613] | 0,0203 |
| Milán | CENTRALE - alojamiento completo | 495 | 0,590 | [0,558; 0,622] | <0,00001 |
| Nueva York | Bedford-Stuyvesant - alojamiento completo | 1.591 | 0,609 | [0,593; 0,622] | <0,00001 |
| Sídney | Leichhardt - habitación privada | 290 | 0,589 | [0,554; 0,626] | <0,00001 |
| Tokio | Nakano Ku - habitación privada | 55 | 0,704 | [0,629; 0,777] | 0,00243 |

La probabilidad de superioridad compara cada segmento con el resto de anuncios de la misma ciudad y
tipología. Por ejemplo, 0,609 indica que una observación de Bedford-Stuyvesant supera a una de su
referencia aproximadamente el 60,9 % de las veces, contando los empates a medias. El intervalo, el
valor ajustado, la escala y las sensibilidades evitan interpretar ese número de forma aislada.

Otros aprendizajes relevantes:

- La tipología con mayor mediana de actividad es el alojamiento completo en cinco ciudades, pero la
  oportunidad local prioritaria puede ser una habitación privada. Barrio y tipología deben evaluarse
  conjuntamente.
- Nueva York y Sídney concentran 25 de los 28 candidatos, aunque cada segmento mantiene su propia
  muestra, efecto e incertidumbre.
- Tokio presenta el mayor efecto entre los primeros candidatos, pero Nakano Ku solo contiene 55
  anuncios; no debe equipararse automáticamente a un segmento de gran escala.
- En Londres las diferencias globales son detectables por el gran volumen, pero el efecto práctico es
  mínimo (`epsilon_squared = 0,0004`). Significación estadística no equivale a relevancia de negocio.
- El precio muestra una asociación débil con la actividad. Las noches mínimas se asocian
  negativamente en las seis ciudades, con mayor magnitud en Sídney (`rho = -0,335`). Son asociaciones,
  no relaciones causales.

## Notebooks y visualizaciones

Los notebooks se leen y ejecutan en orden:

1. [01_data_audit.ipynb](notebooks/01_data_audit.ipynb): procedencia, esquema, completitud y calidad.
2. [02_etl.ipynb](notebooks/02_etl.ipynb): transformaciones, tratamientos y conciliación de filas.
3. [03_executive_eda.ipynb](notebooks/03_executive_eda.ipynb): EDA, estadística y oportunidades.

Cada bloque de código está precedido por Markdown que explica la pregunta, el método y los supuestos,
y seguido por conclusiones explícitas. Seaborn y Matplotlib producen distribuciones, composiciones y
rankings comparables; Plotly genera el gráfico interactivo de actividad relativa frente a cuota local.

La [guía de estudio](docs/study-guide.md) explica cómo leer y defender el análisis. Su versión lista
para estudiar e imprimir está en [PDF](output/pdf/guia-estudio-airbnb.pdf).

## Dashboard de Power BI

El informe [Power BI Desktop](powerbi/README.md) es gratuito y utiliza ocho CSV públicos generados por
Python. Un modelo estrella separa tres dimensiones, tablas de hechos y control del build. El parámetro
`DataRoot` evita rutas personales y permite refrescar el panel en otro equipo.

Sus tres páginas responden, en orden:

- **qué investigar**, con indicadores y ranking de candidatos;
- **dónde se concentra la oportunidad**, con segmentación por ciudad, barrio y tipología;
- **con qué confianza**, mostrando muestra, efecto, intervalo y evidencia estadística.

Los filtros de ciudad, tipología y estado de evidencia son interactivos. Si el mapa no está disponible,
el ranking agregado conserva la lectura principal. La entrega fue conciliada contra 220.031 anuncios,
1.497 segmentos y 28 candidatos sin diferencias entre los CSV y el modelo.

## Dónde está documentado el código

- `src/airbnb_supply_analysis/`: docstring de los 13 módulos, tipos y lógica de producción; el
  comportamiento de cada función pública se concreta en las pruebas asociadas.
- [ETL y calidad](docs/etl-and-quality.md): reglas de transformación y alternativas descartadas.
- [Diccionario de datos](docs/data-dictionary.md): tipos, grano, campos derivados y restricciones.
- [Hallazgos ejecutivos](docs/analysis/executive-findings.md): resultados, evidencia e implicaciones.
- [Guía Power BI](powerbi/README.md): preparación, modelo semántico, refresh y resolución de errores.
- `tests/`: contratos, pruebas unitarias e integraciones que documentan el comportamiento esperado.
- `config/analysis.yml`: umbrales estadísticos versionados; `config/source-manifest.json`: inventario y
  huellas de las fuentes.
- [Gestión del proyecto](docs/project-management.md): ramas, commits, PR, Kanban y trazabilidad.

## Reproducir el proyecto

Requisitos para host: Python 3.13 y `uv`. Para la ruta contenida: Docker Desktop con el daemon activo.
Las seis fuentes deben estar en `data/raw/`.

```powershell
uv sync --locked --group dev
uv run --locked airbnb-supply all --log-format json
```

Ruta equivalente con Docker:

```powershell
docker compose build
docker compose run --rm pipeline all --log-format json
```

El pipeline publica resultados solo después de validar archivos, esquemas, claves, relaciones,
privacidad, conteos, hashes y versión. Consulta la
[validación del quickstart](docs/acceptance/quickstart-validation.md), la
[puerta Esencial](docs/acceptance/essential-level.md), la
[puerta de Nivel Medio](docs/acceptance/medium-level.md) y la
[evidencia final](docs/acceptance/final-release.md).

## Organización y calidad

El trabajo se organizó mediante ramas por fase, commits atómicos, pull requests y un
[Kanban de GitHub Projects](https://github.com/users/arnaldojrm4/projects/2) como fuente única de
planificación. La verificación host actual registra 95 pruebas aprobadas. En la ejecución dentro del
contenedor se aprobaron 94 y se omitió intencionadamente la prueba que intentaría iniciar Docker desde
el propio contenedor.

## Límites de interpretación

La procedencia original, licencia, moneda, fecha de extracción y representatividad de las fuentes son
desconocidas. Los precios solo se comparan dentro de cada ciudad. No existen reservas, ocupación,
ingresos, costes ni margen; tampoco se conoce el universo completo del mercado. Las conclusiones son
hipótesis de priorización histórica que deben contrastarse con datos internos y actuales antes de una
decisión comercial.
