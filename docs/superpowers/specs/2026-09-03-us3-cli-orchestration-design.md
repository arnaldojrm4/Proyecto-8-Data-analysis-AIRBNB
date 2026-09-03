# Diseño: orquestación CLI y notebooks de US3

## Objetivo

Completar T076–T079 para que la CLI ejecute suites, notebooks, validaciones y el flujo `all` de forma
reproducible, aislada y transaccional.

## Decisión de arquitectura

`cli.py` conserva el parseo, el despacho y la publicación transaccional. El nuevo módulo
`validation.py` concentra comprobaciones sin efectos de escritura: documentación, enlaces locales,
PII, evidencia de notebooks, conciliación y artefactos. Las comprobaciones se pueden invocar desde
la CLI o desde tests sin depender de `argparse`.

`all` clona los argumentos hacia un directorio temporal bajo el padre de cada raíz de salida. Ejecuta
`inventory → audit → build → analyze → export → test → notebooks → validate` en ese espacio. Solo al
final sustituye las raíces reales; un error elimina el temporal y conserva las salidas aceptadas.

## Dependencia adelantada autorizada

T079 no puede terminar con éxito mientras `export` sea un esqueleto. Se adelanta una exportación
mínima de ocho CSV seguros y un `build_control.csv`; no crea `.pbix`, `.pbit`, visualizaciones ni
medidas de Power BI. Esta excepción se limita a proporcionar los artefactos que T079 valida y será
revisada contra T091–T092 cuando se aborde US4.

## Contratos

- `test --suite` lanza pytest por selección y emite conteos de aprobadas, fallidas, omitidas y total.
- `notebooks` escribe los tres notebooks ejecutados bajo `artifacts/executed_notebooks/`, valida su
  narrativa y usa salida 7 ante incumplimiento.
- `validate` no reconstruye datos; verifica archivos, conciliación, artefactos y documentación.
- `all` no publica resultados parciales y devuelve el código de la etapa fallida.
- Todas las salidas finales mantienen el resumen JSON existente y no incluyen nombres ni IDs raw.

## Pruebas

Los contratos existentes de `test_cli_all.py`, `test_documentation.py` y `test_performance.py` son
la línea base roja. Se añadirán pruebas focalizadas de CLI, validación y exportación antes de cada
implementación. La aceptación final exige que la suite completa esté verde y que `all` termine sobre
las seis fuentes dentro de los límites del contrato.
