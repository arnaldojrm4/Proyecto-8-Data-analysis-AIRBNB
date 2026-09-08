# Revisión de los notebooks y conclusiones

Revisión iniciada el 2026-09-08 y cerrada el 2026-09-09, zona Europe/Madrid.
Build de referencia: `FDAAB53F8317CAD7`.

## Evaluación

El análisis permite priorizar investigación comercial con cautelas explícitas. Los tres notebooks
se ejecutaron de principio a fin en kernels limpios, sin errores de celda. Las fuentes no permiten
inferir demanda actual, reservas, ocupación, ingresos ni rentabilidad. La fecha de extracción,
moneda comparable, licencia y representatividad siguen sin conocerse.

## Correcciones

- **Recuento:** el resumen del EDA indicaba 29 candidatos. La matriz contiene 28, distribuidos en
  Sídney 13, Nueva York 12 y Madrid, Milán y Tokio uno cada una. Londres tiene cero.
- **Regeneración:** la exploración geográfica existía solo en el notebook y se perdía al ejecutar
  el generador. Ahora las celdas y conclusiones forman parte de `scripts/generate_notebooks.py`.
  Una prueba compara el contenido generado con el versionado, ignorando IDs y salidas.
- **Selección geográfica:** se sustituye el score ad hoc entre ciudades por la brecha de cuota
  en puntos porcentuales. La matriz toma hasta tres candidatos por ciudad según el rango oficial.
  Se elimina el corte global de 12 filas tras ordenar por ciudad, que podía ocultar ciudades.
- **Lectura de ausencias:** una combinación no seleccionada queda vacía en el mapa de calor.
  No se convierte una ausencia en cero ni se presenta un estado `watch` como candidato.
- **Evidencia visible:** la tabla de candidatos incluye los dos extremos del IC 95 % y el
  recuento por ciudad muestra también Londres con cero.
- **Precisión metodológica:** N cuenta anuncios, pero la superioridad y el contraste local usan
  medianas por anfitrión. La documentación distingue ambos conceptos y corrige el recuento de
  segmentos consolidados de Milán a uno.
- **Mantenimiento:** se corrigen mensajes con problemas de codificación y el orden de imports.

## Conciliación independiente

Se contrastaron directamente los tres Parquet procesados y las reglas del código:

| Control | Resultado |
| --- | ---: |
| Anuncios y claves únicas | 220.031 |
| Anuncios con actividad analizable | 219.908 |
| Ceros derivados con respaldo en ausencia de reseñas | 54.248 |
| Tasas de actividad desconocidas | 123 |
| Precios no válidos | 50 |
| Segmentos | 1.497 |
| Resultados estadísticos | 690 |
| Candidatos con q < 0,05, superioridad ≥ 0,56, IC inferior > 0,50 y brecha > 0 | 28 |
| Candidatos con centroides disponibles | 28 |

Los resultados estadísticos y la matriz comparten el build indicado. La validación del pipeline
comprueba además los hashes y la coherencia de las exportaciones. La instantánea de evidencia
de la presentación está en [technical-evidence.json](../presentation/technical-evidence.json).

## Nuevas conclusiones

Nueva York y Sídney reúnen el 89,3 % de los candidatos. La brecha de cuota del primer candidato
es 10,3 puntos en Justicia, 2,4 en CENTRALE, 9,1 en Bedford-Stuyvesant, 6,7 en Leichhardt y 7,2
en Nakano Ku. La presencia local relativa y el efecto deben leerse conjuntamente: una brecha
pequeña puede coexistir con evidencia robusta y una grande no basta para recomendar captación.

Los 28 centroides permiten localizar los candidatos sin publicar direcciones individuales.
La concentración observada describe las fuentes y los criterios utilizados. No permite concluir
que los barrios con menor cuota tengan necesidades comerciales sin cubrir.

## Reproducción

Desde la raíz, con el entorno Python 3.13 preparado y el build generado:

```powershell
.venv/Scripts/python.exe -m airbnb_supply_analysis.cli notebooks
.venv/Scripts/python.exe -m airbnb_supply_analysis.cli validate
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pytest -q --basetemp=tmp/pytest-notebook-review
```

El comando `notebooks` guarda las copias ejecutadas en `artifacts/executed_notebooks/`, que el
repositorio excluye de Git por ser salidas reproducibles. Los notebooks fuente versionados
conservan sus celdas explicativas y el código. El mapa interactivo requiere el recurso geográfico
de Plotly en el navegador. La matriz y las tablas mantienen una lectura útil sin ese recurso.

Los números narrativos y la presentación corresponden al build revisado. Si cambian las fuentes
o las reglas, es necesario revisar la instantánea y las conclusiones antes de volver a compartirlas.

## Entregables

Verificación final del 2026-09-09: **142 pruebas aprobadas** en 308,91 segundos, incluidos los
controles de Docker y el flujo completo con las seis fuentes. Ruff y la validación de artefactos
aprobaron. Los notebooks ejecutados contienen respectivamente 2, 3 y 7 celdas de código, todas
ejecutadas y sin errores. El comando de la suite final fue:

```powershell
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp=tmp/pytest-final-technical-review
```

- [Notebook de auditoría](../../notebooks/01_data_audit.ipynb)
- [Notebook de ETL](../../notebooks/02_etl.ipynb)
- [Notebook ejecutivo y geográfico](../../notebooks/03_executive_eda.ipynb)
- [Hallazgos ejecutivos actualizados](executive-findings.md)
- [Presentación técnica](../../output/presentation/airbnb-desarrollo-tecnico.pptx)
- [Guion para la exposición](../presentation/technical-presentation.md)
