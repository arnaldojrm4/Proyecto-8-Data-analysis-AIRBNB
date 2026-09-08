# Presentación técnica del análisis de oferta Airbnb

18 diapositivas. Guion para una exposición técnica de unos 20 minutos.

[Descargar PowerPoint](../../output/presentation/airbnb-desarrollo-tecnico.pptx)

Build: FDAAB53F8317CAD7. Revisión: 2026-09-08. Las cifras describen estas fuentes históricas, de fecha de extracción desconocida.

## 1. Análisis de oferta Airbnb



Presentación técnica del proyecto educativo. El resultado es una priorización reproducible para investigación comercial. Las fuentes no permiten estimar demanda actual ni resultados económicos.

Fuentes: README.md; pyproject.toml.

## 2. Objetivos y unidad de decisión

Identificar qué combinaciones de ciudad, barrio y tipología conviene investigar para captar nueva oferta.

reviews_per_month es una señal histórica de reseñas. No equivale a reservas.

La pregunta combina ciudad, barrio y tipología. El trabajo integra fuentes heterogéneas, conserva su trazabilidad, estudia la actividad histórica y comunica la incertidumbre. La decisión final requiere investigación comercial con datos vigentes.

Fuentes: README.md; config/analysis.yml.

## 3. Fuentes y cobertura

- Londres: 85068
- Madrid: 19618
- Milán: 18322
- Nueva York: 48895
- Sídney: 36662
- Tokio: 11466

Seis CSV públicos. Comparaciones dentro de ciudad y conservación de todas las filas.

Las seis fuentes contienen 220.031 anuncios. Sus tamaños son desiguales. No se conoce la fecha de extracción ni la representatividad del mercado completo. El SHA-256 valida la identidad de la copia recibida, no su actualidad.

Fuentes: config/source-manifest.json; notebooks/01_data_audit.ipynb.

## 4. Desarrollo del pipeline

| Etapa | Resultado |
| --- | --- |
| Inventario y auditoría | Identidad, esquema, nulos y hallazgos por fuente |
| ETL y modelo canónico | Tipos armonizados, linaje y Parquet de anuncios |
| EDA y estadística | Contrastes, sensibilidades y matriz de segmentos |
| Exportación y validación | Ocho CSV para Power BI y Streamlit |
| Comunicación | Notebooks, visualizaciones y presentación |

Build analizado: FDAAB53F8317CAD7. Clave del anuncio: ciudad + identificador.

La CLI coordina las etapas inventory, audit, build, analyze y export. La publicación pasa por validación y los consumidores leen resultados ya calculados. Los notebooks documentan y visualizan el build. Los datos raw permanecen inmutables.

Fuentes: src/airbnb_supply_analysis/cli.py; README.md.

## 5. Tecnologías utilizadas

| Función | Tecnologías |
| --- | --- |
| Entorno y procesamiento | Python 3.13, uv, pandas, NumPy |
| Contratos y almacenamiento | Pandera, PyArrow, Parquet, CSV, SHA-256 |
| Estadística | SciPy y statsmodels |
| Exploración y gráficos | Jupyter, nbformat, nbclient, Matplotlib, Seaborn, Plotly |
| Consumo analítico | Power BI Desktop, modelo semántico y Streamlit |
| Calidad y distribución | pytest, Ruff, Git, GitHub, Docker y Compose |

La lista describe dependencias y componentes presentes en el repositorio. Python 3.13 y uv.lock fijan el entorno. Pandera valida datos y PyArrow permite Parquet. SciPy y statsmodels implementan estadística. El panel Streamlit utiliza las exportaciones seguras del pipeline.

Fuentes: pyproject.toml; uv.lock; Dockerfile; powerbi/README.md.

## 6. ETL sin pérdida de registros

| Control | Resultado | Tratamiento |
| --- | --- | --- |
| Conciliación de filas | 220.031 / 220.031 | Ningún anuncio eliminado |
| Actividad derivada a cero | 54.248 | Solo cuando no hay reseñas |
| Actividad desconocida | 123 | Permanece ausente |
| Precio no válido | 50 | Excluir solo de métricas de precio |

219.908 anuncios tienen actividad analizable. Los nulos estructurales siguen siendo nulos.

Se conservan 220.031 entradas. La clave listing_key es única. Se derivan ceros únicamente cuando falta la tasa y el número de reseñas es cero. Las 123 tasas desconocidas tienen reseñas positivas. Los precios no positivos quedan fuera solo de métricas de precio y los outliers se conservan con indicadores.

Fuentes: notebooks/02_etl.ipynb; src/airbnb_supply_analysis/etl.py.

## 7. Notebooks y reproducibilidad

| Notebook | Pregunta y evidencia |
| --- | --- |
| 01 · Auditoría | ¿Qué contienen las fuentes y qué calidad tienen? |
| 02 · ETL | ¿Cómo se armonizan y concilian las 220.031 filas? |
| 03 · EDA ejecutivo | ¿Qué segmentos cumplen las reglas y dónde están? |

El generador conserva las nuevas celdas geográficas.
Cada ejecución usa los artefactos del build y un kernel limpio.

Los notebooks consumen los artefactos del pipeline. La ejecución se realiza en orden y en kernels separados. El generador conserva ahora la exploración geográfica y las conclusiones revisadas. Una prueba compara su contenido con los notebooks versionados para evitar pérdidas al regenerar.

Fuentes: notebooks/; scripts/generate_notebooks.py; src/airbnb_supply_analysis/notebooks.py.

## 8. Métodos estadísticos

| Pregunta | Método | Lectura |
| --- | --- | --- |
| H1 · Tipología | Kruskal-Wallis + Holm | Diferencia global y epsilon² |
| H2 · Segmento local | Mann-Whitney + BH | Superioridad e IC 95 % por anfitrión |
| H3 · Asociaciones | Spearman + BH | Precio y noches mínimas frente a actividad |

Sensibilidad: casos completos, outliers y unidad anfitrión. El modelo en dos partes separa presencia e intensidad de actividad.

H1 compara tipologías por ciudad con Kruskal-Wallis y epsilon cuadrado, ajustando por Holm. H2 compara las medianas de actividad por anfitrión del segmento y del resto de la misma ciudad y tipología mediante Mann-Whitney, superioridad e IC bootstrap por anfitrión, con BH. H3 estudia asociaciones de Spearman. El modelo en dos partes complementa la sensibilidad, sin interpretación causal. Un mismo anfitrión podría aparecer en ambos grupos locales y merece revisión adicional de dependencia.

Fuentes: src/airbnb_supply_analysis/statistics.py; config/analysis.yml.

## 9. Reglas para clasificar un segmento

Muestra: ≥ 30 anuncios analizables y ≥ 10 positivos
Evidencia: superioridad ≥ 0,56, IC inferior > 0,50, q < 0,05
Estabilidad: sensibilidades robustas

| Estado | Interpretación | Segmentos |
| --- | --- | --- |
| candidate | Evidencia robusta y menor cuota local | 28 |
| consolidated | Evidencia robusta sin menor cuota local | 19 |
| watch | Muestra elegible, evidencia incompleta | 586 |
| insufficient_evidence | Muestra insuficiente | 864 |

La matriz contiene 1.497 segmentos. Las etiquetas no estiman rentabilidad.

La clasificación exige al menos 30 anuncios analizables y 10 con actividad positiva. La evidencia exige superioridad de al menos 0,56, límite inferior del IC mayor que 0,5, q menor que 0,05 y sensibilidades robustas. Una cuota local menor que la de ciudad distingue candidate de consolidated. El orden entre candidatos se basa primero en número de anuncios, después en efecto y clave de desempate.

Fuentes: src/airbnb_supply_analysis/opportunity.py; config/analysis.yml.

## 10. 28 candidatos en cinco ciudades

- Londres: 0
- Madrid: 1
- Milán: 1
- Nueva York: 12
- Sídney: 13
- Tokio: 1

Nueva York y Sídney reúnen el 89,3 %. Londres no supera simultáneamente todas las reglas.

El recuento actualizado es 28 y corrige el 29 del resumen anterior del notebook. Sídney aporta 13 y Nueva York 12. Juntas representan 25/28, el 89,3 %. La concentración describe las fuentes y las reglas aplicadas, no una cuota de mercado ni una comparación causal entre ciudades.

Fuentes: data/processed/opportunity_segments.parquet; notebooks/03_executive_eda.ipynb.

## 11. Primer candidato por ciudad

| Ciudad y barrio | Tipología | N | Superioridad | IC 95 % |
| --- | --- | --- | --- | --- |
| Madrid<br>Justicia | Habitación privada | 281 | 0,565 | 0,524–0,613 |
| Milán<br>CENTRALE | Alojamiento completo | 495 | 0,590 | 0,558–0,622 |
| Nueva York<br>Bedford-Stuyvesant | Alojamiento completo | 1.591 | 0,609 | 0,593–0,622 |
| Sídney<br>Leichhardt | Habitación privada | 290 | 0,589 | 0,554–0,626 |
| Tokio<br>Nakano Ku | Habitación privada | 55 | 0,704 | 0,629–0,777 |

Rango por escala dentro de ciudad. Superioridad = comparación de medianas por anfitrión, con empates a medias.

La selección usa el rango oficial dentro de cada ciudad. N cuenta anuncios, mientras que el contraste y la superioridad usan medianas por anfitrión. Los cinco candidatos cumplen q menor que 0,05 y sensibilidades robustas. El efecto de Nakano Ku es mayor, pero su N de 55 y el IC más ancho deben permanecer visibles.

Fuentes: data/processed/opportunity_segments.parquet; src/airbnb_supply_analysis/statistics.py.

## 12. Nueva lectura: brecha de cuota local

- Justicia: 10.3
- CENTRALE: 2.4
- Bedford- Stuyvesant: 9.1
- Leichhardt: 6.7
- Nakano Ku: 7.2

Puntos porcentuales = cuota de la tipología en la ciudad menos cuota en el barrio. CENTRALE cumple con una brecha de 2,4 puntos.

La brecha compara la cuota de una tipología entre los anuncios de toda la ciudad con su cuota entre los anuncios del barrio. Se resta cuota barrio a cuota ciudad y se multiplica por 100. Los valores exactos provienen del Parquet. Una menor presencia relativa no prueba escasez de oferta, saturación o necesidades comerciales sin cubrir.

Fuentes: notebooks/03_executive_eda.ipynb, sección 6; data/processed/opportunity_segments.parquet.

## 13. Exploración geográfica de los candidatos

Los estados watch mantienen su categoría. Las celdas vacías de la matriz no equivalen a cero.

El notebook incorpora una matriz de brechas de hasta tres candidatos por ciudad y un mapa interactivo de los 28 centroides disponibles. Cada centroide se obtiene de coordenadas válidas agregadas mediante mediana. Las combinaciones no seleccionadas permanecen vacías en la matriz. La nueva selección elimina el sesgo de ordenar por ciudad y aplicar head(12) globalmente. Se retira el score ad hoc porque mezclaba actividad, cuota, efecto y tamaño sin validación.

Fuentes: notebooks/03_executive_eda.ipynb, secciones 6 y 7; src/airbnb_supply_analysis/opportunity.py.

## 14. Significación y tamaño del efecto

- Londres: 0.0004
- Madrid: 0.0497
- Milán: 0.0163
- Nueva York: 0.0001
- Sídney: 0.0061
- Tokio: 0.0893

Un valor p pequeño no garantiza relevancia práctica. La decisión local necesita barrio y tipología.

Los contrastes globales por tipología tienen p ajustada inferior a 0,05 en las seis ciudades. Sin embargo, epsilon cuadrado es casi nulo en Londres y Nueva York. Los resultados globales no sustituyen los contrastes locales: Nueva York conserva 12 candidatos pese al efecto global mínimo. Epsilon cuadrado se muestra como magnitud descriptiva de efecto, sin convertirlo en explicación causal.

Fuentes: data/processed/statistical_results.parquet, method=kruskal_wallis.

## 15. Precio y estancia mínima: asociaciones

| Ciudad | Precio / actividad | Noches mínimas / actividad |
| --- | --- | --- |
| Londres | -0,064 | -0,169 |
| Madrid | -0,074 | -0,042 |
| Milán | -0,220 | -0,136 |
| Nueva York | -0,060 | -0,248 |
| Sídney | -0,079 | -0,335 |
| Tokio | 0,115 | -0,026 |

Coeficiente rho de Spearman. Son asociaciones históricas, sin interpretación causal.

Las correlaciones son de Spearman y se calculan dentro de cada ciudad. El precio tiene asociación negativa en cinco ciudades y positiva en Tokio. Las noches mínimas se asocian negativamente en las seis, con mayor magnitud en Sídney. La tabla no estima cambios de reservas provocados por reducir precio o estancia mínima.

Fuentes: data/processed/statistical_results.parquet, method=spearman.

## 16. Dashboard y distribución del análisis

Docker Compose distribuye el pipeline y el panel.
El dashboard lee data/powerbi/ en modo de solo lectura.

Power BI Desktop utiliza ocho CSV y un modelo estrella. Streamlit lee las mismas exportaciones seguras con filtros coordinados y vistas de resumen, oportunidad y evidencia. El panel no recalcula pruebas sobre selecciones arbitrarias. Docker Compose separa pipeline y dashboard y monta data/powerbi en solo lectura para el panel.

Fuentes: powerbi/README.md; dashboard/app.py; compose.yaml.

## 17. Reproducir y mantener el proyecto

| Paso | Comando |
| --- | --- |
| Preparar entorno | uv sync --locked --group dev |
| Ejecutar el pipeline | uv run --locked airbnb-supply all --log-format json |
| Repetir notebooks | uv run --locked airbnb-supply notebooks |
| Verificar código | uv run --locked pytest -q<br>uv run --locked ruff check . |

Conservar fuentes, configuración, uv.lock y build. Revisar las cifras narrativas cuando cambie el build.

Para repetir todo el flujo hacen falta Python 3.13, uv y las seis fuentes en data/raw. uv sync usa el lockfile. all ejecuta el flujo integrado. notebooks vuelve a ejecutar los tres notebooks sobre artefactos existentes. pytest incluye pruebas de datos completos y comprobaciones Docker que requieren su entorno operativo. El generador se conserva junto con la prueba de paridad de contenido.

Fuentes: README.md; pyproject.toml; tests/; scripts/generate_notebooks.py.

## 18. Conclusiones y límites

Investigar los candidatos con evidencia robusta, empezando por el rango de cada ciudad.

Fuentes de fecha y representatividad desconocidas. Los resultados priorizan investigación comercial.

La entrega identifica 28 candidatos mediante reglas explícitas. La nueva exploración geográfica añade ubicación y brecha de cuota sin modificar el criterio estadístico. La captación debe contrastarse con información interna actual sobre búsquedas, reservas, conversión, ocupación, costes y capacidad real. No se conoce moneda comparable, fecha de extracción, licencia ni universo completo. El precio solo se compara dentro de ciudad.

Fuentes: README.md; docs/analysis/executive-findings.md; notebooks/03_executive_eda.ipynb.

## Regeneración del entregable

El script `scripts/create_technical_presentation.mjs` lee `docs/presentation/technical-evidence.json`, una instantánea agregada del build. Requiere el runtime de presentaciones de Codex y las variables `RUNTIME_NODE_MODULES`, `PRESENTATION_SKILL_DIR` y `RUNTIME_PYTHON`. Ejecutar desde la raíz con el Node de ese runtime. El finalizador exige que el archivo de salida todavía no exista. Para otro build, actualizar primero la instantánea y revisar todas las cifras y conclusiones.
