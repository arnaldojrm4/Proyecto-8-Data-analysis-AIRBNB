# Hallazgos ejecutivos — oportunidades de captación

**Build analizado**: `FDAAB53F8317CAD7`  
**Unidad de decisión**: ciudad + barrio + tipología  
**Métrica principal**: actividad histórica de reseñas, no un resultado comercial

## Recomendación

Investigar primero los segmentos etiquetados como `candidate`. La etiqueta exige simultáneamente
muestra suficiente, efecto mínimo, intervalo bootstrap por anfitrión por encima de la ausencia de
diferencia, valor ajustado inferior a 0,05, sensibilidades coherentes y una cuota local de la
tipología inferior a su cuota en la ciudad. No se utiliza una puntuación opaca.

| Ciudad | Primer segmento | N | Mediana | Superioridad | IC 95 % | q ajustado | Cuota barrio / ciudad |
|---|---|---:|---:|---:|---:|---:|---:|
| Madrid | Justicia · habitación privada | 281 | 0,280 | 0,565 | [0,524; 0,613] | 0,0203 | 29,5 % / 39,8 % |
| Milán | CENTRALE · alojamiento completo | 495 | 0,490 | 0,590 | [0,558; 0,622] | <0,00001 | 71,8 % / 74,3 % |
| Nueva York | Bedford-Stuyvesant · alojamiento completo | 1.591 | 1,000 | 0,609 | [0,593; 0,622] | <0,00001 | 42,8 % / 52,0 % |
| Sídney | Leichhardt · habitación privada | 290 | 0,355 | 0,589 | [0,554; 0,626] | <0,00001 | 29,0 % / 35,8 % |
| Tokio | Nakano Ku · habitación privada | 55 | 2,730 | 0,704 | [0,629; 0,777] | 0,00243 | 19,0 % / 26,2 % |

Londres no tiene un segmento que supere todas las reglas. No se relajan umbrales para producir una
recomendación artificial.

## Qué aporta cada ciudad

- **Madrid**: el alojamiento completo presenta mayor mediana global de actividad (0,410), pero la
  oportunidad local prioritaria es la habitación privada en Justicia. Esto demuestra por qué una
  decisión de captación debe combinar tipología y barrio.
- **Milán**: CENTRALE-alojamiento completo reúne escala y evidencia consistente. El build contiene
  un candidato y un segmento consolidado en esta ciudad.
- **Nueva York**: concentra 12 de los 28 candidatos. Después de Bedford-Stuyvesant destacan Hell's
  Kitchen-habitación privada y East Flatbush-alojamiento completo.
- **Sídney**: concentra 13 candidatos. Leichhardt, Ryde y Parramatta forman el primer bloque de
  investigación por escala dentro de sus segmentos elegibles.
- **Tokio**: Nakano Ku-habitación privada tiene el mayor efecto del primer candidato de cada ciudad,
  pero una muestra de 55 anuncios; la precisión visible impide equipararlo automáticamente a un
  segmento de gran escala.
- **Londres**: las diferencias globales entre tipologías son estadísticamente detectables pero
  prácticamente minúsculas (`epsilon_squared=0,0004`); se mantiene en observación.

## Tipología y actividad

Los contrastes globales de tipología son significativos en las seis ciudades, pero el tamaño del
efecto varía mucho: Tokio 0,0893; Madrid 0,0497; Milán 0,0163; Sídney 0,0061; Londres 0,0004 y Nueva
York 0,0001. Con muestras grandes, un valor p pequeño no equivale a una diferencia relevante.

Las medianas más altas corresponden a alojamiento completo en Londres, Madrid, Milán, Sídney y
Tokio. Nueva York presenta medianas próximas entre habitación compartida (0,405), privada (0,400) y
alojamiento completo (0,350). Estas cifras son descriptivas y siempre se interpretan dentro de cada
ciudad.

## Patrones geográficos descriptivos

Entre barrios con al menos 30 observaciones analizables, las tres mayores medianas son:

| Ciudad | Barrios |
|---|---|
| Londres | Westminster, Camden, Southwark |
| Madrid | Casco Histórico de Barajas, Cortes, Sol |
| Milán | DUOMO, CENTRALE, BICOCCA |
| Nueva York | East Elmhurst, Springfield Gardens, Queens Village |
| Sídney | Auburn, Penrith, Fairfield |
| Tokio | Bunkyo Ku, Shibuya Ku, Nakano Ku |

Este ranking describe barrios completos. No sustituye la matriz barrio-tipología ni sus pruebas.

## Asociaciones

La asociación de precio publicado con actividad es débil: negativa en cinco ciudades y positiva en
Tokio (`rho=0,115`, IC 95 % [0,096; 0,133]). Las noches mínimas se asocian negativamente con la
actividad en las seis ciudades; la mayor magnitud aparece en Sídney (`rho=-0,335`, IC 95 %
[-0,344; -0,326]). Son asociaciones monotónicas, no efectos causales.

## Decisión y límites

### Nuevas conclusiones de la exploración geográfica

La revisión del 2026-09-08 concilia **28 candidatos**, corrigiendo el recuento de 29 que figuraba
en el resumen del notebook. Los 28 disponen de centroides. Nueva York y Sídney reúnen 25 (89,3 %).
Esta distribución describe las fuentes analizadas y no demuestra dónde se concentra la demanda.

La brecha de cuota se calcula como `100 × (cuota ciudad − cuota barrio)` para una misma tipología.
Entre los primeros candidatos por ciudad es 10,3 puntos porcentuales en Justicia, 2,4 en CENTRALE,
9,1 en Bedford-Stuyvesant, 6,7 en Leichhardt y 7,2 en Nakano Ku. Una brecha pequeña como la de
CENTRALE puede coexistir con evidencia robusta. La brecha por sí sola no determina la captación.

El mapa incluye todos los candidatos con coordenadas y la matriz muestra hasta tres por ciudad,
según el rango oficial. Las combinaciones ausentes quedan vacías. Se retira el score geográfico
ad hoc que mezclaba actividad, efecto, cuota y tamaño entre ciudades. Los segmentos `watch` no
se presentan como candidatos y los centroides no representan inmuebles individuales.

La superioridad y su IC usan medianas de actividad por anfitrión. N en la tabla cuenta anuncios.
El rango de candidatos prioriza el número de anuncios dentro de ciudad, seguido del efecto y
una clave de desempate. No es un ranking de rentabilidad.

La acción recomendada es una investigación comercial focalizada, empezando por los cinco primeros
segmentos de la tabla y ampliando después por el ranking de cada ciudad. Antes de ejecutar una
campaña debe contrastarse la oportunidad con datos internos y vigentes. Las fuentes no contienen
fecha de extracción, moneda comparable, universo completo del mercado ni resultados de negocio.

Evidencia reproducible: [notebook ejecutivo](../../notebooks/03_executive_eda.ipynb),
[reglas versionadas](../../config/analysis.yml) y
[aceptación estadística](../acceptance/statistical-rigor.md).
