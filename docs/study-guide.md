# Guía de estudio del proyecto hasta US2

## 1. Problema de negocio

El objetivo es priorizar qué combinaciones de ciudad, barrio y tipología conviene investigar para
captar oferta. La fuente permite estudiar anuncios y actividad histórica de reseñas. No permite
observar directamente resultados comerciales.

## 2. Arquitectura

El flujo es `raw CSV → inventario → auditoría → dataset canónico → estadística → matriz de
oportunidades → notebooks/figuras`. Python 3.13 y `uv.lock` fijan el entorno. Docker y Compose
describen el contenedor reproducible. Los artefactos regenerables no se versionan, salvo sus
manifiestos.

## 3. Base de datos

Se preservan 220.031 filas de seis ciudades: Londres 85.068, Nueva York 48.895, Sídney 36.662,
Madrid 19.618, Milán 18.322 y Tokio 11.466. Los SHA-256 y `.gitattributes` impiden cambios
accidentales en las fuentes.

Las decisiones ETL más importantes son:

1. no imputar nombres ni fechas con textos o ceros;
2. conservar como nulas las columnas no disponibles en una ciudad;
3. excluir valores inválidos solo de la métrica afectada, sin borrar la fila;
4. derivar actividad cero únicamente cuando faltan reseñas mensuales y el total de reseñas es cero;
5. mantener desconocidas 123 tasas ausentes con reseñas positivas.

El resultado conserva las 220.031 filas y una clave única `ciudad + listing_id`.

## 4. Diseño estadístico

- **Kruskal-Wallis** pregunta si las distribuciones de actividad difieren entre tipologías dentro de
  una ciudad. `epsilon_squared` mide la magnitud; no basta con mirar el valor p.
- **Mann-Whitney y probabilidad de superioridad** comparan un segmento con el resto de su misma
  ciudad y tipología. Un efecto de 0,60 significa que, al tomar una observación de cada grupo, la del
  segmento supera a la referencia aproximadamente el 60 % de las veces, contando empates a medias.
- **Bootstrap por anfitrión** remuestrea anfitriones para no tratar anuncios del mismo propietario
  como observaciones totalmente independientes.
- **Holm** controla contrastes confirmatorios múltiples. **Benjamini-Hochberg** controla la tasa
  esperada de falsos descubrimientos en la exploración de muchos barrios.
- **Spearman** mide asociación monotónica y resiste mejor la asimetría; no demuestra causalidad.
- **Modelo en dos partes** separa la posibilidad de actividad positiva de su intensidad cuando es
  positiva.

## 5. Regla de oportunidad

Un `candidate` debe cumplir todas las reglas visibles: muestra suficiente, efecto mínimo 0,56,
intervalo por encima de 0,5, `q<0,05`, sensibilidades coherentes y menor cuota de la tipología en el
barrio que en la ciudad. `consolidated` tiene evidencia robusta pero no baja cuota; `watch` no supera
todas las reglas; `insufficient_evidence` no alcanza la muestra mínima.

## 6. Resultado principal

Hay 28 candidatos: Madrid 1, Milán 1, Nueva York 12, Sídney 13 y Tokio 1. Los primeros por escala son
Justicia-habitación privada, CENTRALE-alojamiento completo, Bedford-Stuyvesant-alojamiento completo,
Leichhardt-habitación privada y Nakano Ku-habitación privada. Londres no supera todos los filtros.

El aprendizaje central es que una tipología ganadora a nivel de ciudad no identifica por sí sola la
mejor zona de captación. La decisión útil aparece al combinar actividad relativa, barrio, escala,
cuota de oferta, incertidumbre y robustez.

## 7. Cómo reproducir y estudiar el código

1. Revisar `config/source-manifest.json` y `config/analysis.yml`.
2. Leer `etl.py` junto con `tests/unit/test_etl.py`.
3. Leer `statistics.py` junto con los cuatro archivos de pruebas estadísticas.
4. Revisar `opportunity.py` y comprobar cómo cada condición cambia la etiqueta.
5. Ejecutar `airbnb-supply inventory`, `audit`, `build` y `analyze`.
6. Recorrer los notebooks 01, 02 y 03 en ese orden.

## 8. Límites que deben acompañar cualquier presentación

La fecha, moneda, procedencia original y representatividad son desconocidas. Una reseña mensual es
un proxy histórico, no una reserva. Las recomendaciones son hipótesis de priorización que deben
validarse con fuentes internas vigentes.
